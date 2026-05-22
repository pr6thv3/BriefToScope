from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import RequestContext, require_permission
from app.models.schemas import ESignResponse
from app.services.billing_service import BillingService
from app.services.esign_service import ESignService
from app.services.storage_service import StorageService
from app.services.usage_service import UsageService
from app.utils.errors import BriefToScopeError, NotFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class SendSignatureRequest(BaseModel):
    recipient_email: str | None = Field(default=None, max_length=255)


@router.post("/sows/{sow_id}/send-signature", response_model=ESignResponse)
@router.post("/api/sows/{sow_id}/send-signature", response_model=ESignResponse)
async def send_signature(
    sow_id: str,
    req: SendSignatureRequest = SendSignatureRequest(),
    context: RequestContext = Depends(require_permission("sow:esign")),
):
    try:
        BillingService().assert_feature_allowed(context.plan, "esign")
        usage = UsageService()
        await usage.assert_quota_available(
            context.org_id,
            context.plan,
            context.subscription_status,
            "esign_request",
        )

        storage = StorageService()
        sow = await storage.get_sow_by_id(sow_id)
        if not sow:
            raise NotFoundError("SOW not found")
        if not _sow_belongs_to_workspace(sow, context):
            raise BriefToScopeError("Not authorized", 403)

        result = await ESignService().send_signature_request(
            sow_id,
            {**sow, "recipient_email": req.recipient_email or ""},
        )
        await usage.track_event(
            context.org_id,
            context.user_id,
            "esign_request",
            metadata={"sow_id": sow_id, "envelope_id": result.get("envelope_id")},
        )
        return ESignResponse(**result)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("Send signature failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send signature request")


def _sow_belongs_to_workspace(sow: dict, context: RequestContext) -> bool:
    if sow.get("org_id"):
        return sow.get("org_id") == context.org_id
    return sow.get("user_id") == context.user_id
