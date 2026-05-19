from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.models.schemas import PDFExportResponse
from app.services.storage_service import StorageService
from app.services.pdf_service import PDFService
from app.utils.errors import BriefToScopeError, NotFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/sows/{sow_id}/export-pdf", response_model=PDFExportResponse)
async def export_pdf(
    sow_id: str,
    current_user: dict = Depends(get_current_user),
):
    try:
        storage = StorageService()
        sow = await storage.get_sow_by_id(sow_id)
        if not sow:
            raise NotFoundError("SOW not found")
        user = await storage.get_user_by_clerk_id(current_user["sub"])
        if user and sow.get("user_id") != user.get("id"):
            raise BriefToScopeError("Not authorized", 403)

        project = await _get_project(storage, sow.get("project_id"))
        pdf_service = PDFService()
        pdf_url = await pdf_service.export_and_upload(
            sow=sow,
            client_name=project.get("client_name", "") if project else "",
            project_name=project.get("project_name", "") if project else "",
            industry=project.get("industry", "") if project else "",
        )
        return PDFExportResponse(pdf_url=pdf_url)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"PDF export failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to export PDF")


async def _get_project(storage: StorageService, project_id: str):
    if storage._demo:
        from app.services.storage_service import _demo_projects
        return _demo_projects.get(project_id)
    try:
        resp = storage._get_client().table("projects").select("*").eq("id", project_id).single().execute()
        return resp.data
    except Exception:
        return None
