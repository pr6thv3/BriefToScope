from fastapi import APIRouter, Request, HTTPException
from app.config import get_settings
from app.services.billing_service import BillingService
from app.services.esign_service import ESignService
from app.utils.errors import BriefToScopeError
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/webhooks/paypal")
@router.post("/api/webhooks/paypal")
async def paypal_webhook(request: Request):
    payload = await request.body()
    logger.info(f"PayPal webhook received, payload length: {len(payload)}")
    import json

    try:
        event = json.loads(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON webhook payload")

    try:
        return await BillingService().handle_paypal_webhook(event, dict(request.headers), payload)
    except BriefToScopeError as exc:
        logger.error(f"PayPal webhook processing failed: {exc.message}")
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except Exception as exc:
        logger.error(f"PayPal webhook processing error: {exc}")
        raise HTTPException(status_code=500, detail="PayPal webhook processing failed")


@router.post("/webhooks/docusign")
async def docusign_webhook(request: Request):
    settings = get_settings()
    payload = await request.body()
    logger.info(f"DocuSign webhook received, payload length: {len(payload)}")

    import json
    try:
        event = json.loads(payload)
    except Exception:
        event = {}

    esign_service = ESignService()
    result = await esign_service.handle_webhook(event)
    logger.info(f"DocuSign webhook processed: {result}")
    return {"status": "ok"}
