import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.models.production_schemas import GenerationCreateRequest
from app.services.ai_orchestrator import AIOrchestrator
from app.services.audit_log_service import AuditLogService
from app.services.auth_service import AuthService
from app.services.storage_service import StorageService
from app.services.usage_service import UsageService
from app.services.workspace_service import WorkspaceService
from app.utils.security import sanitize_transcript, validate_transcript_length

_demo_generation_jobs: Dict[str, dict] = {}
_demo_generation_events: Dict[str, List[dict]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GenerationJobService:
    """Generation job facade.

    This is intentionally API-compatible with future Celery/Redis workers while
    still running in-process for local/demo development.
    """

    def __init__(self):
        self.storage = StorageService()
        self.workspace_service = WorkspaceService()

    async def create_job(self, payload: GenerationCreateRequest, current_user: dict, org_id: Optional[str] = None) -> dict:
        auth_service = AuthService()
        user = await auth_service.get_or_create_user(current_user["sub"], current_user.get("email", ""), "")
        workspace = await self.workspace_service.ensure_default_workspace(user)
        active_org_id = org_id or workspace["id"]
        await self.workspace_service.require_membership(user["id"], active_org_id)

        job = {
            "id": str(uuid.uuid4()),
            "org_id": active_org_id,
            "user_id": user["id"],
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
        _demo_generation_jobs[job["id"]] = job
        _demo_generation_events[job["id"]] = [self._event("queued", 0, "Generation queued")]
        return job

    async def get_job(self, job_id: str) -> Optional[dict]:
        return _demo_generation_jobs.get(job_id)

    async def get_events(self, job_id: str) -> List[dict]:
        return _demo_generation_events.get(job_id, [])

    async def run_job(self, job_id: str) -> None:
        job = _demo_generation_jobs.get(job_id)
        if not job:
            return

        payload = GenerationCreateRequest.model_validate(job["request_json"])
        raw = sanitize_transcript(payload.transcript_text)
        validation_error = validate_transcript_length(raw)
        if validation_error:
            self._mark_failed(job_id, validation_error)
            return

        orchestrator = AIOrchestrator()
        try:
            self._update(job_id, "running", "cleaning", 10, "Cleaning transcript")
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
            job["project_id"] = project["id"]
            job["transcript_id"] = transcript["id"]

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
                self._update(job_id, "running", step, progress, step.replace("_", " ").title())

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

            markdown = _to_markdown(output.sow, output.extracted_brief.client_name or payload.client_name)
            sow = await self.storage.create_sow(
                project_id=project["id"],
                user_id=job["user_id"],
                org_id=job["org_id"],
                title=payload.project_name or output.extracted_brief.project_type or "Untitled SOW",
                content_json=output.sow.model_dump(),
                content_markdown=markdown,
                risk_flags=[risk.model_dump() for risk in output.risk_flags],
                confidence_score=output.confidence_score,
            )
            await self.storage.update_project_status(project["id"], "completed")
            await UsageService().track_event(job["user_id"], "sow_generated", token_count=len(raw.split()))
            await AuditLogService().record(
                org_id=job["org_id"],
                actor_id=job["user_id"],
                action="sow.generated",
                entity_type="sow",
                entity_id=sow["id"],
                metadata={"generation_job_id": job_id},
            )

            job["sow_id"] = sow["id"]
            self._update(job_id, "completed", "completed", 100, "SOW generated")
        except Exception as e:
            self._mark_failed(job_id, str(e))
            if job.get("project_id"):
                try:
                    await self.storage.update_project_status(job["project_id"], "failed")
                except Exception:
                    pass
        finally:
            await orchestrator.close()

    def _update(self, job_id: str, status: str, step: str, progress: int, message: str) -> None:
        job = _demo_generation_jobs[job_id]
        job.update({"status": status, "current_step": step, "progress": progress, "updated_at": _now()})
        _demo_generation_events.setdefault(job_id, []).append(self._event(step, progress, message, status=status))

    def _mark_failed(self, job_id: str, error: str) -> None:
        job = _demo_generation_jobs[job_id]
        job.update({"status": "failed", "current_step": "failed", "error": error, "updated_at": _now()})
        _demo_generation_events.setdefault(job_id, []).append(self._event("failed", job.get("progress", 0), error, status="failed"))

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

