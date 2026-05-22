from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import RequestContext, get_current_user, require_permission
from app.models.production_schemas import (
    BrandSettingsRequest,
    BrandSettingsResponse,
    InviteCreateRequest,
    InviteResponse,
    WorkspaceCreateRequest,
    WorkspaceMemberResponse,
    WorkspaceResponse,
)
from app.services.auth_service import AuthService
from app.services.billing_service import PLAN_LIMITS
from app.services.workspace_service import WorkspaceService
from app.utils.errors import BriefToScopeError

router = APIRouter(prefix="/api/workspaces", tags=["Workspaces"])


async def _current_user_record(current_user: dict) -> dict:
    return await AuthService().get_or_create_user(
        current_user["sub"], current_user.get("email", ""), current_user.get("name", "")
    )


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(current_user: dict = Depends(get_current_user)):
    user = await _current_user_record(current_user)
    return await WorkspaceService().list_workspaces(user["id"])


@router.post("", response_model=WorkspaceResponse)
async def create_workspace(req: WorkspaceCreateRequest, current_user: dict = Depends(get_current_user)):
    user = await _current_user_record(current_user)
    return await WorkspaceService().create_workspace(user["id"], req.name, req.slug)


@router.get("/{org_id}/members", response_model=list[WorkspaceMemberResponse])
async def list_members(org_id: str, current_user: dict = Depends(get_current_user)):
    try:
        user = await _current_user_record(current_user)
        service = WorkspaceService()
        await service.require_membership(user["id"], org_id)
        return await service.list_members(org_id)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{org_id}/invites", response_model=InviteResponse)
async def create_invite(
    org_id: str,
    req: InviteCreateRequest,
    context: RequestContext = Depends(require_permission("members:invite")),
):
    try:
        if context.org_id != org_id:
            raise BriefToScopeError("Not authorized for this workspace", 403)
        service = WorkspaceService()
        members = await service.list_members(org_id)
        seat_limit = PLAN_LIMITS.get(context.plan, PLAN_LIMITS["free"])["included_seats"]
        if len([member for member in members if member.get("status") == "active"]) >= seat_limit:
            raise BriefToScopeError("Seat limit reached for this plan", 402)
        return await service.create_invite(org_id, req.email, req.role, context.user_id)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{org_id}/brand", response_model=BrandSettingsResponse)
async def get_brand_settings(org_id: str, current_user: dict = Depends(get_current_user)):
    try:
        user = await _current_user_record(current_user)
        service = WorkspaceService()
        await service.require_membership(user["id"], org_id)
        return await service.get_brand_settings(org_id)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{org_id}/brand", response_model=BrandSettingsResponse)
async def update_brand_settings(org_id: str, req: BrandSettingsRequest, current_user: dict = Depends(get_current_user)):
    try:
        user = await _current_user_record(current_user)
        service = WorkspaceService()
        await service.require_membership(user["id"], org_id, ["owner", "admin"])
        return await service.upsert_brand_settings(org_id, req.model_dump())
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

