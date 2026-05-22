from celery import Celery

from app.config import get_settings

settings = get_settings()

broker_url = settings.redis_url or "redis://localhost:6379/0"
result_backend = settings.celery_result_backend or broker_url

celery_app = Celery("brieftoscope", broker=broker_url, backend=result_backend)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_default_queue="ai_generation",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.workers.tasks.run_generation_job": {"queue": "ai_generation"},
        "app.workers.tasks.run_pdf_export_job": {"queue": "pdf_exports"},
        "app.workers.tasks.send_email_job": {"queue": "emails"},
        "app.workers.tasks.reconcile_billing_job": {"queue": "billing"},
    },
    task_time_limit=900,
    task_soft_time_limit=840,
)

QUEUE_NAMES = ["ai_generation", "pdf_exports", "emails", "billing"]
