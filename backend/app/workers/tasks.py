import asyncio

from app.services.generation_job_service import GenerationJobService
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService
from app.workers.celery_app import celery_app


@celery_app.task(
    name="app.workers.tasks.run_generation_job",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def run_generation_job(job_id: str) -> None:
    asyncio.run(GenerationJobService().run_job(job_id))


@celery_app.task(
    name="app.workers.tasks.run_pdf_export_job",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def run_pdf_export_job(export_id: str, sow_id: str, org_id: str, user_id: str) -> None:
    asyncio.run(_run_pdf_export_job(export_id, sow_id, org_id, user_id))


async def _run_pdf_export_job(export_id: str, sow_id: str, org_id: str, user_id: str) -> None:
    storage = StorageService()
    await storage.update_pdf_export(export_id, {"status": "generating"})
    try:
        sow = await storage.get_sow_by_id(sow_id)
        if not sow:
            await storage.update_pdf_export(export_id, {"status": "failed"})
            return

        filename = f"brief-to-scope-sow-{sow_id}.pdf"
        pdf_bytes = await PDFService().generate_pdf(
            sow,
            sow.get("client_name", ""),
            sow.get("project_name", ""),
            sow.get("industry", ""),
        )
        storage_path = await storage.upload_pdf_private(
            sow_id=sow_id,
            pdf_bytes=pdf_bytes,
            filename=filename,
            org_id=org_id,
            user_id=user_id,
        )
        await storage.update_pdf_export(
            export_id,
            {"status": "ready", "storage_path": storage_path},
        )
        await storage.update_sow_status(sow_id, "exported")
    except Exception:
        await storage.update_pdf_export(export_id, {"status": "failed"})
        raise
