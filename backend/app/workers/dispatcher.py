from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def dispatch_generation_job(job_id: str) -> bool:
    """Dispatch a generation job to Celery when explicitly enabled.

    Returns False when the API should use its local BackgroundTasks fallback.
    Raises RuntimeError when Celery was requested but dispatch failed.
    """

    settings = get_settings()
    if not settings.celery_enabled:
        return False
    if not settings.redis_url:
        raise RuntimeError("CELERY_ENABLED=true requires REDIS_URL")

    try:
        from app.workers.tasks import run_generation_job

        run_generation_job.delay(job_id)
        return True
    except Exception as exc:
        logger.error(f"Failed to dispatch generation job to Celery: {exc}")
        raise RuntimeError("Failed to dispatch generation job to Celery") from exc
