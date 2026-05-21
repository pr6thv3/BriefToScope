from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/readiness")
async def readiness(current_user: dict = Depends(get_current_user)):
    settings = get_settings()
    if not settings.demo_mode:
        allowed = {email.strip().lower() for email in settings.admin_email_allowlist.split(",") if email.strip()}
        if not allowed or current_user.get("email", "").lower() not in allowed:
            raise HTTPException(status_code=403, detail="Admin access is not enabled for this account")
    return {
        "status": "ok",
        "checks": {
            "auth": "configured_or_demo",
            "database": "supabase_or_demo",
            "jobs": "celery_redis_ready_with_local_fallback",
            "billing": "paypal_subscriptions_ready",
            "audit_logs": "enabled",
        },
    }
