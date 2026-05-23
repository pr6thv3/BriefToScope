"""PDF export routes.

Production exports use private Supabase Storage objects and short-lived signed
download URLs. The API never returns public storage URLs or demo storage URLs.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.dependencies import RequestContext, require_permission
from app.models.schemas import PDFExportResponse
from app.services.demo_data import get_fallback_risks, get_fallback_sow
from app.services.audit_log_service import AuditLogService
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService
from app.services.usage_service import UsageService
from app.utils.errors import BriefToScopeError, NotFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/sows/{sow_id}/export-pdf", response_model=PDFExportResponse)
@router.post("/api/sows/{sow_id}/export-pdf", response_model=PDFExportResponse)
async def export_pdf(
    sow_id: str,
    context: RequestContext = Depends(require_permission("sow:export")),
):
    storage = StorageService()
    try:
        usage = UsageService()
        await usage.assert_quota_available(
            context.org_id,
            context.plan,
            context.subscription_status,
            "pdf_export",
        )

        sow = await storage.get_sow_by_id(sow_id)
        if not sow:
            if storage._demo:
                sow = _build_demo_sow(sow_id, context)
            else:
                raise NotFoundError("SOW not found")

        if not _sow_belongs_to_workspace(sow, context):
            raise BriefToScopeError("Not authorized to export this SOW", 403)

        if not sow.get("content_json"):
            if storage._demo:
                sow["content_json"] = get_fallback_sow()
                sow["risk_flags_json"] = get_fallback_risks()
            else:
                raise BriefToScopeError("SOW has no content to export", 422)

        client_name, project_name, industry = await _resolve_metadata(storage, sow, storage._demo)
        settings = get_settings()
        if settings.celery_enabled and not storage._demo:
            export = await storage.create_pdf_export(
                sow_id=sow_id,
                storage_path="",
                status="queued",
            )
            try:
                from app.workers.tasks import run_pdf_export_job

                run_pdf_export_job.delay(export["id"], sow_id, context.org_id, context.user_id)
            except Exception as exc:
                await storage.update_pdf_export(export["id"], {"status": "failed"})
                raise BriefToScopeError("Failed to dispatch PDF export job", 503) from exc

            await usage.track_event(
                context.org_id,
                context.user_id,
                "pdf_export",
                metadata={"sow_id": sow_id, "export_id": export["id"], "queued": True},
            )
            return PDFExportResponse(
                success=True,
                sow_id=sow_id,
                export_id=export["id"],
                status="queued",
                pdf_url=None,
                download_url=None,
                signed_url_expires_at=None,
                filename=f"brief-to-scope-sow-{sow_id}.pdf",
                generated_at=datetime.now(timezone.utc),
            )

        result = await PDFService().export_and_upload(
            sow=sow,
            client_name=client_name,
            project_name=project_name,
            industry=industry,
            user_id=context.user_id,
            org_id=context.org_id,
        )

        ttl_seconds = 600
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        download_url = await storage.create_signed_pdf_url(
            result["storage_path"],
            ttl_seconds=ttl_seconds,
        )
        await storage.update_pdf_export_signed_expiry(result["export_id"], expires_at.isoformat())

        await usage.track_event(
            context.org_id,
            context.user_id,
            "pdf_export",
            metadata={"sow_id": sow_id, "export_id": result["export_id"]},
        )
        await AuditLogService().record(
            org_id=context.org_id,
            actor_id=context.user_id,
            action="pdf.exported",
            entity_type="pdf_export",
            entity_id=result["export_id"],
            metadata={"sow_id": sow_id, "status": result.get("status", "ready")},
        )

        return PDFExportResponse(
            success=True,
            sow_id=sow_id,
            export_id=result["export_id"],
            status=result.get("status", "ready"),
            pdf_url=download_url,
            download_url=download_url,
            signed_url_expires_at=expires_at,
            filename=result["filename"],
            generated_at=result["generated_at"],
        )
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error("PDF export failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to export PDF")


@router.get("/api/sows/{sow_id}/exports/{export_id}/download-url")
async def get_pdf_download_url(
    sow_id: str,
    export_id: str,
    context: RequestContext = Depends(require_permission("sow:export")),
):
    storage = StorageService()
    sow = await storage.get_sow_by_id(sow_id)
    if not sow:
        raise HTTPException(status_code=404, detail="SOW not found")
    if not _sow_belongs_to_workspace(sow, context):
        raise HTTPException(status_code=403, detail="Not authorized to download this export")

    export = await storage.get_pdf_export(export_id, sow_id=sow_id)
    if not export:
        raise HTTPException(status_code=404, detail="PDF export not found")

    ttl_seconds = 600
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    download_url = await storage.create_signed_pdf_url(export["storage_path"], ttl_seconds=ttl_seconds)
    await storage.update_pdf_export_signed_expiry(export_id, expires_at.isoformat())
    await AuditLogService().record(
        org_id=context.org_id,
        actor_id=context.user_id,
        action="pdf.signed_url_requested",
        entity_type="pdf_export",
        entity_id=export_id,
        metadata={"sow_id": sow_id, "ttl_seconds": ttl_seconds},
    )
    return {
        "export_id": export_id,
        "download_url": download_url,
        "signed_url_expires_at": expires_at.isoformat(),
    }


def _build_demo_sow(sow_id: str, context: RequestContext) -> dict:
    return {
        "id": sow_id,
        "user_id": context.user_id,
        "org_id": context.org_id,
        "project_id": None,
        "client_name": "Luma Retail Co.",
        "project_name": "E-Commerce Platform Redesign",
        "industry": "E-commerce / Retail",
        "content_json": get_fallback_sow(),
        "content_markdown": "",
        "risk_flags_json": get_fallback_risks(),
        "confidence_score": 0.89,
        "status": "draft",
    }


async def _resolve_metadata(storage: StorageService, sow: dict, is_demo: bool) -> tuple[str, str, str]:
    project = await _get_project(storage, sow.get("project_id"))
    client_name = (project.get("client_name", "") if project else "") or sow.get("client_name", "")
    project_name = (project.get("project_name", "") if project else "") or sow.get("project_name", "")
    industry = (project.get("industry", "") if project else "") or sow.get("industry", "")
    if is_demo:
        client_name = client_name or "Luma Retail Co."
        project_name = project_name or "E-Commerce Platform Redesign"
        industry = industry or "E-commerce / Retail"
    return client_name, project_name, industry


async def _get_project(storage: StorageService, project_id: str):
    if not project_id:
        return None
    if storage._demo:
        from app.services.storage_service import _demo_projects

        return _demo_projects.get(project_id)
    try:
        resp = storage._get_client().table("projects").select("*").eq("id", project_id).single().execute()
        return resp.data
    except Exception:
        return None


def _sow_belongs_to_workspace(sow: dict, context: RequestContext) -> bool:
    if sow.get("org_id"):
        return sow.get("org_id") == context.org_id
    return sow.get("user_id") == context.user_id
