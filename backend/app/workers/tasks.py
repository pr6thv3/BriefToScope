import asyncio

from app.services.generation_job_service import GenerationJobService
from app.workers.celery_app import celery_app


@celery_app.task(
    name="app.workers.tasks.run_generation_job",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def run_generation_job(job_id: str) -> None:
    asyncio.run(GenerationJobService().run_job(job_id))
