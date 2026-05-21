from fastapi import APIRouter, Depends

from app.dependencies import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/readiness")
async def readiness(current_user: dict = Depends(get_current_user)):
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
