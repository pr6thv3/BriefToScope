import time
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import RequestContext, require_permission
from app.models.api_schemas import GenerateSOWRequest, GenerateSOWResponse, SowDetails, QualityDetails, GenerationMetadata
from app.models.schemas import HealthResponse
from app.services.ai_orchestrator import AIOrchestrator
from app.services.ai_validation_service import AIValidationService
from app.services.storage_service import StorageService
from app.services.usage_service import UsageService
from app.config import get_settings
from app.utils.security import sanitize_transcript, validate_transcript_length
from app.utils.errors import BriefToScopeError
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")


@router.post("/generate-sow", response_model=GenerateSOWResponse)
async def generate_sow(
    req: GenerateSOWRequest,
    context: RequestContext = Depends(require_permission("sow:generate")),
):
    start_time = time.perf_counter()
    orchestrator = None
    storage = StorageService()
    project_id = ""

    try:
        settings = get_settings()
        if settings.celery_enabled and not settings.demo_mode:
            raise BriefToScopeError("Use /api/generations for asynchronous production generation", 409)

        # 1. Validate
        raw = sanitize_transcript(req.transcript_text)
        err = validate_transcript_length(raw)
        if err:
            raise BriefToScopeError(err, 422)

        logger.info(f"[GENERATE] Request from user={context.clerk_user_id} org={context.org_id} industry={req.industry} tone={req.tone}")

        usage = UsageService()
        await usage.assert_quota_available(
            context.org_id,
            context.plan,
            context.subscription_status,
            "sow_generated",
        )
        user_id = context.user_id
        logger.info(f"[GENERATE] User resolved: {user_id}")

        # 3. Create project with status = 'generating'
        project = await storage.create_project(
            user_id=user_id,
            client_name=req.client_name or "Unknown Client",
            project_name=req.project_name or "Untitled Project",
            industry=req.industry,
            status="generating",
            org_id=context.org_id,
        )
        project_id = project["id"]
        logger.info(f"[GENERATE] Project created: {project_id} (generating)")

        # 4. Create transcript row (cleaning status stored in metadata since table has no status column)
        transcript = await storage.create_transcript(
            project_id=project_id,
            raw_text=raw,
            cleaned_text=raw[:5000],
            metadata={"tone": req.tone, "status": "cleaning"},
        )
        transcript_id = transcript["id"]
        logger.info(f"[GENERATE] Transcript created: {transcript_id}")

        # Define inline callback to update DB status during execution
        async def db_status_callback(status: str):
            try:
                await storage.update_project_status(project_id, status)
                logger.info(f"[GENERATE] Updated project {project_id} status to '{status}'")
            except Exception as e:
                logger.error(f"[GENERATE] Failed to update project status in DB: {e}")

        # 5. Run AI pipeline
        orchestrator = AIOrchestrator()
        output = await orchestrator.generate_sow(
            transcript_text=raw,
            industry=req.industry,
            tone=req.tone,
            client_name=req.client_name,
            project_name=req.project_name,
            budget=req.budget,
            timeline=req.timeline,
            user_id=user_id,
            project_id=project_id,
            status_callback=db_status_callback,
        )
        logger.info(f"[GENERATE] AI pipeline complete: confidence={output.confidence_score:.2f} risks={len(output.risk_flags)}")

        # 6. Create SOW row (status = 'draft')
        sow_title = req.project_name or output.extracted_brief.project_type or "Untitled SOW"
        markdown_content = _to_markdown(output.sow, output.extracted_brief.client_name or req.client_name)
        
        sow_content_json = output.sow.model_dump()
        validation = AIValidationService().validate_sow(sow_content_json)
        merged_risk_flags = [r.model_dump() for r in output.risk_flags] + validation["risk_flags"]

        sow_record = await storage.create_sow(
            project_id=project_id,
            user_id=user_id,
            title=sow_title,
            content_json=sow_content_json,
            content_markdown=markdown_content,
            risk_flags=merged_risk_flags,
            confidence_score=validation["confidence_score"],
            org_id=context.org_id,
            quality_score=validation["quality_score"],
            risk_score=validation["risk_score"],
        )
        sow_id = sow_record["id"]
        logger.info(f"[GENERATE] SOW saved: {sow_id}")

        # 7. Update project status: 'completed'
        await storage.update_project_status(project_id, "completed")
        logger.info(f"[GENERATE] Project status finalized: completed")

        # 8. Track usage event
        await usage.track_event(
            context.org_id,
            user_id,
            "sow_generated",
            token_count=len(raw.split()),
            metadata={"sow_id": sow_id, "project_id": project_id},
        )

        # Map sections for response
        sow_sections = []
        if orchestrator.state.a6_sow and orchestrator.state.a6_sow.sections:
            for s in orchestrator.state.a6_sow.sections:
                sow_sections.append({
                    "key": s.section_key,
                    "title": s.section_title,
                    "content": s.content_markdown,
                    "order": s.order
                })

        # Map pipeline steps
        ai_pipeline = {
            "a1_transcript_cleaner": orchestrator.state.steps.get("a1", {}),
            "a2_brief_extractor": orchestrator.state.steps.get("a2", {}),
            "a3_scope_builder": orchestrator.state.steps.get("a3", {}),
            "a4_risk_detector": orchestrator.state.steps.get("a4", {}),
            "a5_clause_generator": orchestrator.state.steps.get("a5", {}),
            "a6_sow_composer": orchestrator.state.steps.get("a6", {}),
            "a7_quality_checker": orchestrator.state.steps.get("a7", {})
        }

        # Calculate final metadata timing
        total_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Build response
        return GenerateSOWResponse(
            success=True,
            project_id=project_id,
            transcript_id=transcript_id,
            sow_id=sow_id,
            status="generated",
            ai_pipeline=ai_pipeline,
            sow=SowDetails(
                title=sow_title,
                content_json=output.sow.model_dump(),
                content_markdown=markdown_content,
                sections=sow_sections
            ),
            extracted_brief=output.extracted_brief.model_dump(),
            confidence_score=validation["confidence_score"],
            risk_flags=merged_risk_flags,
            quality=QualityDetails(
                overall_quality_score=validation["quality_score"],
                approval_status=orchestrator.state.a7_quality.approval_status if orchestrator.state.a7_quality else "approved_with_warnings",
                ready_for_export=orchestrator.state.a7_quality.ready_for_export if orchestrator.state.a7_quality else True,
                warnings=orchestrator.state.a7_quality.suggestions if (orchestrator.state.a7_quality and hasattr(orchestrator.state.a7_quality, "suggestions")) else []
            ),
            metadata=GenerationMetadata(
                generation_time_ms=total_time_ms,
                demo_mode=storage._demo,
                model_used="gpt-4o-mini",
                fallback_used=orchestrator.state.fallback_used
            )
        )

    except BriefToScopeError as e:
        logger.warning(f"[GENERATE] Validation error: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"[GENERATE] UNEXPECTED ERROR: {e}", exc_info=True)
        # Attempt to mark project failed if we created it
        if project_id:
            try:
                await storage.update_project_status(project_id, "failed")
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if orchestrator:
            await orchestrator.close()


def _to_markdown(sow, client_name: str) -> str:
    lines = ["# Statement of Work", f"**Client:** {client_name or 'Valued Client'}", ""]
    lines.append(f"## Project Overview\n{sow.project_overview}\n")
    lines.append("## Objectives")
    for o in sow.objectives:
        lines.append(f"- {o}")
    lines.append("")
    lines.append("## Scope of Work")
    for s in sow.scope_of_work:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("## Deliverables")
    for d in sow.deliverables:
        lines.append(f"- {d}")
    lines.append("")
    lines.append("## Timeline")
    for t in sow.timeline:
        lines.append(f"- {t}")
    lines.append("")
    lines.append("## Payment Schedule")
    for p in sow.payment_schedule:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## Client Responsibilities")
    for r in sow.client_responsibilities:
        lines.append(f"- {r}")
    lines.append("")
    lines.append(f"## Revision Policy\n{sow.revision_policy}\n")
    lines.append("## Out of Scope")
    for o in sow.out_of_scope:
        lines.append(f"- {o}")
    lines.append("")
    lines.append("## Assumptions")
    for a in sow.assumptions:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## Acceptance Criteria")
    for a in sow.acceptance_criteria:
        lines.append(f"- {a}")
    lines.append("")
    lines.append(f"## Signature Section\n{sow.signature_section}\n")
    return "\n".join(lines)
