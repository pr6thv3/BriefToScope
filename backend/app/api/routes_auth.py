from fastapi import APIRouter, Depends, Header, HTTPException

from app.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.services.workspace_service import WorkspaceService
from app.utils.errors import BriefToScopeError

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/sync")
async def sync_auth_user(
    current_user: dict = Depends(get_current_user),
    x_workspace_id: str | None = Header(default=None, alias="X-Workspace-Id"),
):
    """Mirror Clerk identity into PostgreSQL and ensure a default workspace."""
    try:
        user = await AuthService().get_or_create_user(
            current_user["sub"],
            current_user.get("email", ""),
            current_user.get("name", ""),
        )
        workspace_service = WorkspaceService()
        workspaces = await workspace_service.list_workspaces(user["id"])
        if not workspaces:
            workspace = await workspace_service.ensure_default_workspace(user)
        else:
            workspace = next(
                (item for item in workspaces if item.get("id") == x_workspace_id),
                workspaces[0],
            )
        return {"user": user, "workspace": workspace}
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

