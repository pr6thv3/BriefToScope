from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.services.workspace_service import WorkspaceService
from app.utils.errors import BriefToScopeError

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/sync")
async def sync_auth_user(current_user: dict = Depends(get_current_user)):
    """Mirror Clerk identity into PostgreSQL and ensure a default workspace."""
    try:
        user = await AuthService().get_or_create_user(
            current_user["sub"],
            current_user.get("email", ""),
            current_user.get("name", ""),
        )
        workspace = await WorkspaceService().ensure_default_workspace(user)
        return {"user": user, "workspace": workspace}
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

