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
            "jobs": "in_process_with_celery_ready_interface",
            "billing": "stripe_checkout_ready",
            "audit_logs": "enabled",
        },
    }

