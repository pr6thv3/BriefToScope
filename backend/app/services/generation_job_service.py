import uuid
from datetime import datetime, timezone
from typing import List, Optional

from app.dependencies import RequestContext
from app.models.production_schemas import GenerationCreateRequest
from app.services.ai_orchestrator import AIOrchestrator
from app.services.ai_validation_service import AIValidationService
from app.services.audit_log_service import AuditLogService
from app.services.storage_service import StorageService
from app.services.usage_service import UsageService
from app.utils.security import sanitize_transcript, validate_transcript_length


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GenerationJobService:
    """Generation job facade backed by Postgres in production.

    API requests create durable jobs/events. Celery workers can execute the job
    in a separate process because state is read from `generation_jobs`, while
    demo/local development can still run the same method in FastAPI background
    tasks without Redis.
    """

    def __init__(self):
        self.storage = StorageService()

    async def create_job(self, payload: GenerationCreateRequest, context: RequestContext) -> dict:
        await UsageService().assert_quota_available(
            context.org_id,
            context.plan,
            context.subscription_status,
            "sow_generated",
        )

        job = {
            "id": str(uuid.uuid4()),
            "org_id": context.org_id,
            "user_id": context.user_id,
            "status": "queued",
            "current_step": "queued",
            "progress": 0,
            "project_id": None,
            "transcript_id": None,
            "sow_id": None,
            "error": None,
            "request_json": payload.model_dump(),
            "created_at": _now(),
            "updated_at": _now(),
        }
        await self.storage.create_generation_job(job)
        await self.storage.create_generation_job_event(job["id"], self._event("queued", 0, "Generation queued", status="queued"))
        return job

    async def get_job(self, job_id: str) -> Optional[dict]:
        return await self.storage.get_generation_job(job_id)

    async def get_events(self, job_id: str) -> List[dict]:
        return await self.storage.get_generation_job_events(job_id)

    async def run_job(self, job_id: str) -> None:
        job = await self.storage.get_generation_job(job_id)
        if not job:
            return
        if job.get("status") == "completed":
            return

        payload = GenerationCreateRequest.model_validate(job["request_json"])
        raw = sanitize_transcript(payload.transcript_text)
        validation_error = validate_transcript_length(raw)
        if validation_error:
            await self.mark_failed(job_id, validation_error)
            return

        orchestrator = AIOrchestrator()
        try:
            await self._update(job_id, "running", "cleaning", 10, "Cleaning transcript")
            project = await self.storage.create_project(
                user_id=job["user_id"],
                org_id=job["org_id"],
                client_name=payload.client_name or "Unknown Client",
                project_name=payload.project_name or "Untitled Project",
                industry=payload.industry,
                status="generating",
            )
            transcript = await self.storage.create_transcript(
                project_id=project["id"],
                raw_text=raw,
                cleaned_text=raw[:5000],
                metadata={"tone": payload.tone, "generation_job_id": job_id},
            )
            await self.storage.update_generation_job(job_id, {"project_id": project["id"], "transcript_id": transcript["id"]})

            async def status_callback(step: str):
                progress = {
                    "cleaning": 15,
                    "extracting": 28,
                    "building_scope": 42,
                    "detecting_risks": 56,
                    "clauses": 68,
                    "composing": 82,
                    "validating": 92,
                }.get(step, 50)
                await self._update(job_id, "running", step, progress, step.replace("_", " ").title())

            output = await orchestrator.generate_sow(
                transcript_text=raw,
                industry=payload.industry,
                tone=payload.tone,
                client_name=payload.client_name,
                project_name=payload.project_name,
                budget=payload.budget,
                timeline=payload.timeline,
                user_id=job["user_id"],
                project_id=project["id"],
                status_callback=status_callback,
            )

            sow_content_json = output.sow.model_dump()
            validation = AIValidationService().validate_sow(sow_content_json)
            merged_risk_flags = [risk.model_dump() for risk in output.risk_flags] + validation["risk_flags"]
            markdown = _to_markdown(output.sow, output.extracted_brief.client_name or payload.client_name)
            sow = await self.storage.create_sow(
                project_id=project["id"],
                user_id=job["user_id"],
                org_id=job["org_id"],
                title=payload.project_name or output.extracted_brief.project_type or "Untitled SOW",
                content_json=sow_content_json,
                content_markdown=markdown,
                risk_flags=merged_risk_flags,
                confidence_score=validation["confidence_score"],
                quality_score=validation["quality_score"],
                risk_score=validation["risk_score"],
            )
            await self.storage.update_project_status(project["id"], "completed")
            await UsageService().track_event(
                job["org_id"],
                job["user_id"],
                "sow_generated",
                token_count=len(raw.split()),
                metadata={"sow_id": sow["id"], "generation_job_id": job_id},
            )
            await AuditLogService().record(
                org_id=job["org_id"],
                actor_id=job["user_id"],
                action="sow.generated",
                entity_type="sow",
                entity_id=sow["id"],
                metadata={"generation_job_id": job_id},
            )

            await self.storage.update_generation_job(job_id, {"sow_id": sow["id"]})
            await self._update(job_id, "completed", "completed", 100, "SOW generated")
        except Exception as e:
            await self.mark_failed(job_id, str(e))
            latest = await self.storage.get_generation_job(job_id)
            if latest and latest.get("project_id"):
                try:
                    await self.storage.update_project_status(latest["project_id"], "failed")
                except Exception:
                    pass
        finally:
            await orchestrator.close()

    async def mark_failed(self, job_id: str, error: str) -> None:
        await self.storage.update_generation_job(
            job_id,
            {"status": "failed", "current_step": "failed", "error": error},
        )
        job = await self.storage.get_generation_job(job_id)
        await self.storage.create_generation_job_event(
            job_id,
            self._event("failed", job.get("progress", 0) if job else 0, error, status="failed"),
        )

    async def _update(self, job_id: str, status: str, step: str, progress: int, message: str) -> None:
        await self.storage.update_generation_job(
            job_id,
            {"status": status, "current_step": step, "progress": progress, "error": None},
        )
        await self.storage.create_generation_job_event(job_id, self._event(step, progress, message, status=status))

    def _event(self, step: str, progress: int, message: str, status: str = "running") -> dict:
        return {
            "step": step,
            "progress": progress,
            "message": message,
            "status": status,
            "created_at": _now(),
        }


def _to_markdown(sow, client_name: str) -> str:
    lines = ["# Statement of Work", f"**Client:** {client_name or 'Valued Client'}", ""]
    for key, title in [
        ("project_overview", "Project Overview"),
        ("objectives", "Objectives"),
        ("scope_of_work", "Scope of Work"),
        ("deliverables", "Deliverables"),
        ("timeline", "Timeline"),
        ("payment_schedule", "Payment Schedule"),
        ("client_responsibilities", "Client Responsibilities"),
        ("revision_policy", "Revision Policy"),
        ("out_of_scope", "Out of Scope"),
        ("assumptions", "Assumptions"),
        ("acceptance_criteria", "Acceptance Criteria"),
        ("signature_section", "Signature Section"),
    ]:
        value = getattr(sow, key)
        lines.append(f"## {title}")
        if isinstance(value, list):
            lines.extend(f"- {item}" for item in value)
        else:
            lines.append(value)
        lines.append("")
    return "\n".join(lines)
