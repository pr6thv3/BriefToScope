from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import RequestContext, require_permission
from app.models.production_schemas import (
    RiskAuditResponse,
    SectionRegenerateRequest,
    SectionRegenerateResponse,
    SOWSectionResponse,
    SOWSectionUpdateRequest,
)
from app.services.audit_log_service import AuditLogService
from app.services.sow_service import SOWService
from app.services.storage_service import StorageService
from app.utils.errors import BriefToScopeError

router = APIRouter(prefix="/api/sows", tags=["SOW Sections"])


@router.get("/{sow_id}/sections", response_model=list[SOWSectionResponse])
async def list_sow_sections(
    sow_id: str,
    context: RequestContext = Depends(require_permission("sow:view")),
):
    try:
        await _require_sow_in_workspace(sow_id, context)
        return await SOWService().list_sections(sow_id)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{sow_id}/sections/{section_key}", response_model=SOWSectionResponse)
async def update_sow_section(
    sow_id: str,
    section_key: str,
    req: SOWSectionUpdateRequest,
    context: RequestContext = Depends(require_permission("sow:edit")),
):
    try:
        await _require_sow_in_workspace(sow_id, context)
        section = await SOWService().update_section(sow_id, section_key, req.content_markdown, req.change_summary)
        await AuditLogService().record(
            org_id=context.org_id,
            actor_id=context.user_id,
            action="sow.section.updated",
            entity_type="sow_section",
            entity_id=section["id"],
            metadata={"sow_id": sow_id, "section_key": section_key},
        )
        return section
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{sow_id}/regenerate-section", response_model=SectionRegenerateResponse)
async def regenerate_sow_section(
    sow_id: str,
    req: SectionRegenerateRequest,
    context: RequestContext = Depends(require_permission("sow:edit")),
):
    try:
        await _require_sow_in_workspace(sow_id, context)
        section = await SOWService().regenerate_section(
            sow_id,
            req.section_key,
            req.instruction,
            req.current_markdown,
        )
        audit = await SOWService().audit_risks(sow_id)
        return {
            "section": section,
            "quality_score": audit["quality_score"],
            "risk_flags": audit["risk_flags"],
        }
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{sow_id}/risk-audit", response_model=RiskAuditResponse)
async def risk_audit_sow(
    sow_id: str,
    context: RequestContext = Depends(require_permission("sow:risk_audit")),
):
    try:
        await _require_sow_in_workspace(sow_id, context)
        return await SOWService().audit_risks(sow_id)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


async def _require_sow_in_workspace(sow_id: str, context: RequestContext) -> dict:
    sow = await StorageService().get_sow_by_id(sow_id)
    if not sow:
        from app.utils.errors import NotFoundError

        raise NotFoundError("SOW not found")
    if sow.get("org_id") and sow.get("org_id") != context.org_id:
        raise BriefToScopeError("Not authorized for this SOW", 403)
    if not sow.get("org_id") and sow.get("user_id") != context.user_id:
        raise BriefToScopeError("Not authorized for this SOW", 403)
    return sow

