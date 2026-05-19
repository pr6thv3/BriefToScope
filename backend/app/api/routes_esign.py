from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.models.schemas import ESignResponse
from app.services.storage_service import StorageService
from app.services.esign_service import ESignService
from app.utils.errors import BriefToScopeError, NotFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/sows/{sow_id}/send-signature", response_model=ESignResponse)
async def send_signature(
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

        esign_service = ESignService()
        result = await esign_service.send_signature_request(sow_id, sow)
        return ESignResponse(**result)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Send signature failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send signature request")
