from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.models.schemas import GenerateSOWRequest, GenerateSOWResponse, HealthResponse
from app.services.ai_orchestrator import AIOrchestrator
from app.services.storage_service import StorageService
from app.services.usage_service import UsageService
from app.services.auth_service import AuthService
from app.services.demo_data import SAMPLE_TRANSCRIPT
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
    current_user: dict = Depends(get_current_user),
):
    orchestrator = None
    try:
        # Validate
        raw = sanitize_transcript(req.transcript_text)
        err = validate_transcript_length(raw)
        if err:
            raise BriefToScopeError(err, 422)

        logger.info(f"[GENERATE] Request from user={current_user.get('sub')} industry={req.industry} tone={req.tone}")

        # Get or create user
        auth_service = AuthService()
        user = await auth_service.get_or_create_user(
            current_user["sub"], current_user.get("email", ""), ""
        )
        user_id = user["id"]
        logger.info(f"[GENERATE] User resolved: {user_id}")

        # AI pipeline
        orchestrator = AIOrchestrator()
        output = await orchestrator.generate_sow(
            transcript_text=raw,
            industry=req.industry,
            tone=req.tone,
            client_name=req.client_name,
            project_name=req.project_name,
            budget=req.budget,
            timeline=req.timeline,
        )
        logger.info(f"[GENERATE] AI pipeline complete: confidence={output.confidence_score:.2f} risks={len(output.risk_flags)}")

        # Save to database
        storage = StorageService()
        project = await storage.create_project(
            user_id=user_id,
            client_name=req.client_name or output.extracted_brief.client_name or "Unknown Client",
            project_name=req.project_name or output.extracted_brief.project_type or "Untitled Project",
            industry=req.industry,
        )
        logger.info(f"[GENERATE] Project created: {project['id']}")

        transcript = await storage.create_transcript(
            project_id=project["id"],
            raw_text=raw,
            cleaned_text=raw[:5000],
            metadata={"tone": req.tone},
        )
        logger.info(f"[GENERATE] Transcript saved: {transcript['id']}")

        sow = await storage.create_sow(
            project_id=project["id"],
            user_id=user_id,
            title=req.project_name or output.extracted_brief.project_type or "Untitled SOW",
            content_json=output.sow.model_dump(),
            content_markdown=_to_markdown(output.sow, output.extracted_brief.client_name),
            risk_flags=[r.model_dump() for r in output.risk_flags],
            confidence_score=output.confidence_score,
        )
        logger.info(f"[GENERATE] SOW saved: {sow['id']}")

        # Track usage
        usage = UsageService()
        await usage.track_event(user_id, "sow_generated", token_count=len(raw.split()))

        return GenerateSOWResponse(
            sow=output.sow,
            risk_flags=output.risk_flags,
            extracted_brief=output.extracted_brief,
            confidence_score=output.confidence_score,
            sow_id=sow["id"],
        )
    except BriefToScopeError as e:
        logger.warning(f"[GENERATE] Validation/auth error: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"[GENERATE] UNEXPECTED ERROR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate SOW. Please try again or contact support.")
    finally:
        if orchestrator:
            await orchestrator.close()


def _to_markdown(sow, client_name: str) -> str:
    lines = ["# Statement of Work", f"**Client:** {client_name}", ""]
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
