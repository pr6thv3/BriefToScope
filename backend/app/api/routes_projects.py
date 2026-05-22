from fastapi import APIRouter, Depends

from app.dependencies import RequestContext, require_permission
from app.services.storage_service import StorageService

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("")
async def list_projects(context: RequestContext = Depends(require_permission("sow:view"))):
    storage = StorageService()
    if storage._demo:
        from app.services.storage_service import _demo_projects

        return [
            project for project in _demo_projects.values()
            if project.get("org_id") == context.org_id
        ]

    resp = (
        storage._get_client()
        .table("projects")
        .select("*")
        .eq("org_id", context.org_id)
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []

