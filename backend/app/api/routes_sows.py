from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.models.schemas import (
    SOWListItem, SOWDetailResponse, UpdateSOWRequest, UpdateSOWResponse
)
from app.services.storage_service import StorageService
from app.utils.errors import BriefToScopeError, NotFoundError
from app.utils.logger import get_logger
from typing import List

logger = get_logger(__name__)
router = APIRouter()


@router.get("/sows", response_model=List[SOWListItem])
async def list_sows(current_user: dict = Depends(get_current_user)):
    try:
        storage = StorageService()
        user = await storage.get_user_by_clerk_id(current_user["sub"])
        if not user:
            return []
        sows = await storage.get_sows_by_user(user["id"])
        result = []
        for s in sows:
            project = await _get_project(storage, s.get("project_id"))
            result.append(SOWListItem(
                id=s["id"],
                title=s.get("title", ""),
                client_name=project.get("client_name", "") if project else "",
                project_name=project.get("project_name", "") if project else "",
                industry=project.get("industry", "") if project else "",
                status=s.get("status", "draft"),
                created_at=s["created_at"],
                updated_at=s["updated_at"],
                confidence_score=s.get("confidence_score", 0.0),
            ))
        return result
    except Exception as e:
        logger.error(f"List SOWs failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list SOWs")


@router.get("/sows/{sow_id}", response_model=SOWDetailResponse)
async def get_sow(sow_id: str, current_user: dict = Depends(get_current_user)):
    try:
        storage = StorageService()
        sow = await storage.get_sow_by_id(sow_id)
        if not sow:
            raise NotFoundError("SOW not found")
        user = await storage.get_user_by_clerk_id(current_user["sub"])
        if user and sow.get("user_id") != user.get("id"):
            raise BriefToScopeError("Not authorized to view this SOW", 403)
        project = await _get_project(storage, sow.get("project_id"))
        esign = await _get_esign(storage, sow_id)
        return SOWDetailResponse(
            id=sow["id"],
            title=sow.get("title", ""),
            client_name=project.get("client_name", "") if project else "",
            project_name=project.get("project_name", "") if project else "",
            industry=project.get("industry", "") if project else "",
            status=sow.get("status", "draft"),
            content_json=sow.get("content_json", {}),
            content_markdown=sow.get("content_markdown", ""),
            risk_flags_json=sow.get("risk_flags_json", []),
            confidence_score=sow.get("confidence_score", 0.0),
            pdf_url=sow.get("pdf_url"),
            created_at=sow["created_at"],
            updated_at=sow["updated_at"],
            transcript_summary=sow.get("content_json", {}).get("project_overview", ""),
            export_status="ready" if sow.get("pdf_url") else "pending",
            esign_status=esign.get("status") if esign else None,
        )
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Get SOW failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get SOW")


@router.put("/sows/{sow_id}", response_model=UpdateSOWResponse)
async def update_sow(
    sow_id: str,
    req: UpdateSOWRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        storage = StorageService()
        sow = await storage.get_sow_by_id(sow_id)
        if not sow:
            raise NotFoundError("SOW not found")
        user = await storage.get_user_by_clerk_id(current_user["sub"])
        if user and sow.get("user_id") != user.get("id"):
            raise BriefToScopeError("Not authorized to update this SOW", 403)

        versions = await storage.get_sow_versions(sow_id)
        version_number = len(versions) + 1
        await storage.create_sow_version(
            sow_id=sow_id,
            version_number=version_number,
            content_json=req.content_json,
            content_markdown=req.content_markdown,
        )
        updated = await storage.update_sow(sow_id, req.content_json, req.content_markdown)
        return UpdateSOWResponse(
            id=updated["id"],
            content_json=updated["content_json"],
            content_markdown=updated["content_markdown"],
            updated_at=updated["updated_at"],
        )
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Update SOW failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update SOW")


async def _get_project(storage: StorageService, project_id: str):
    if storage._demo:
        from app.services.storage_service import _demo_projects
        return _demo_projects.get(project_id)
    try:
        resp = storage._get_client().table("projects").select("*").eq("id", project_id).single().execute()
        return resp.data
    except Exception:
        return None


async def _get_esign(storage: StorageService, sow_id: str):
    if storage._demo:
        from app.services.storage_service import _demo_esign
        matches = [e for e in _demo_esign.values() if e.get("sow_id") == sow_id]
        return max(matches, key=lambda x: x.get("created_at", "")) if matches else None
    try:
        resp = storage._get_client().table("esign_requests").select("*").eq("sow_id", sow_id).order("created_at", desc=True).limit(1).execute()
        return resp.data[0] if resp.data else None
    except Exception:
        return None
