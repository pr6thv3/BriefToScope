from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user
from app.models.production_schemas import (
    RiskAuditResponse,
    SectionRegenerateRequest,
    SectionRegenerateResponse,
    SOWSectionResponse,
    SOWSectionUpdateRequest,
)
from app.services.audit_log_service import AuditLogService
from app.services.auth_service import AuthService
from app.services.sow_service import SOWService
from app.utils.errors import BriefToScopeError

router = APIRouter(prefix="/api/sows", tags=["SOW Sections"])


async def _user_id(current_user: dict) -> str:
    user = await AuthService().get_or_create_user(current_user["sub"], current_user.get("email", ""), "")
    return user["id"]


@router.get("/{sow_id}/sections", response_model=list[SOWSectionResponse])
async def list_sow_sections(sow_id: str, current_user: dict = Depends(get_current_user)):
    try:
        return await SOWService().list_sections(sow_id)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{sow_id}/sections/{section_key}", response_model=SOWSectionResponse)
async def update_sow_section(
    sow_id: str,
    section_key: str,
    req: SOWSectionUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        user_id = await _user_id(current_user)
        section = await SOWService().update_section(sow_id, section_key, req.content_markdown, req.change_summary)
        await AuditLogService().record(
            org_id="",
            actor_id=user_id,
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
    current_user: dict = Depends(get_current_user),
):
    try:
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
async def risk_audit_sow(sow_id: str, current_user: dict = Depends(get_current_user)):
    try:
        return await SOWService().audit_risks(sow_id)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

