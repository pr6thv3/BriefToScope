from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("")
async def list_projects(current_user: dict = Depends(get_current_user)):
    storage = StorageService()
    user = await AuthService().get_or_create_user(current_user["sub"], current_user.get("email", ""), "")
    if storage._demo:
        from app.services.storage_service import _demo_projects

        return [
            project for project in _demo_projects.values()
            if project.get("user_id") == user["id"] or project.get("created_by") == user["id"]
        ]

    resp = (
        storage._get_client()
        .table("projects")
        .select("*")
        .or_(f"user_id.eq.{user['id']},created_by.eq.{user['id']}")
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []

