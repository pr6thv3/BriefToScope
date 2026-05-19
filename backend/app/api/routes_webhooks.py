from fastapi import APIRouter, Request, HTTPException, Header
from app.config import get_settings
from app.services.storage_service import StorageService
from app.services.esign_service import ESignService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(default="")):
    settings = get_settings()
    payload = await request.body()
    logger.info(f"Stripe webhook received, payload length: {len(payload)}")

    if not settings.demo_mode:
        import stripe as stripe_lib
        stripe_lib.api_key = settings.stripe_secret_key
        try:
            event = stripe_lib.Webhook.construct_event(
                payload, stripe_signature, settings.stripe_webhook_secret
            )
        except Exception as e:
            logger.error(f"Stripe webhook verification failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        import json
        try:
            event = json.loads(payload)
        except Exception:
            event = {"type": "demo"}

    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})
    logger.info(f"Stripe event: {event_type}")

    storage = StorageService()
    try:
        if event_type in [
            "customer.subscription.created",
            "customer.subscription.updated",
        ]:
            customer_id = data.get("customer")
            sub_id = data.get("id")
            status = data.get("status", "active")
            plan = data.get("plan", {}).get("nickname", "default")
            # Find user by stripe_customer_id (would need users table to have this field)
            logger.info(f"Subscription {sub_id} status {status}")
        elif event_type == "customer.subscription.deleted":
            logger.info(f"Subscription cancelled: {data.get('id')}")
        elif event_type == "invoice.paid":
            logger.info(f"Invoice paid: {data.get('id')}")
        elif event_type == "invoice.payment_failed":
            logger.info(f"Invoice failed: {data.get('id')}")
    except Exception as e:
        logger.error(f"Stripe webhook processing error: {e}")

    return {"status": "ok"}


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
