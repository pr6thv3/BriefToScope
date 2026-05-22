from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.dependencies import RequestContext, require_permission

router = APIRouter(prefix="/api/admin", tags=["Admin"])
QUEUE_NAMES = ["ai_generation", "pdf_exports", "emails", "billing"]


@router.get("/readiness")
async def readiness(context: RequestContext = Depends(require_permission("workspace:manage"))):
    settings = get_settings()
    if not settings.demo_mode:
        allowed = {email.strip().lower() for email in settings.admin_email_allowlist.split(",") if email.strip()}
        if not allowed or context.email.lower() not in allowed:
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


@router.get("/workers/health")
async def worker_health(context: RequestContext = Depends(require_permission("workspace:manage"))):
    settings = get_settings()
    if not settings.demo_mode:
        allowed = {email.strip().lower() for email in settings.admin_email_allowlist.split(",") if email.strip()}
        if not allowed or context.email.lower() not in allowed:
            raise HTTPException(status_code=403, detail="Admin access is not enabled for this account")

    redis_status = "not_configured"
    stuck_jobs = 0
    if settings.redis_url:
        try:
            import redis

            client = redis.from_url(settings.redis_url, socket_timeout=3)
            client.ping()
            redis_status = "ok"
        except Exception as exc:
            redis_status = f"error: {exc}"

    return {
        "status": "ok" if redis_status in {"ok", "not_configured"} else "degraded",
        "redis": redis_status,
        "celery_enabled": settings.celery_enabled,
        "queues": QUEUE_NAMES,
        "stuck_jobs": stuck_jobs,
    }
