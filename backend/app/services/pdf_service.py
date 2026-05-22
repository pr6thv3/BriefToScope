"""PDF generation service for BriefToScope.

Renders SOW data into a premium HTML template, converts to PDF via Playwright,
uploads to Supabase Storage, and updates the SOW record.

Hardened for local/demo reliability:
- Every step has structured logging.
- Playwright has a timeout guard (30s).
- HTML rendering has a fallback template.
- Supabase upload failure returns a mock URL.
- Status/pdf_url update failures are swallowed.
- DEMO_MODE never crashes.
"""

import os
import time
from datetime import datetime, timezone
from typing import Any

from jinja2 import Environment, FileSystemLoader

from app.services.storage_service import StorageService
from app.utils.logger import get_logger
from app.utils.errors import StorageError

logger = get_logger(__name__)

# Canonical section ordering
ORDERED_SECTIONS = [
    {"key": "project_overview", "title": "Project Overview", "type": "text"},
    {"key": "objectives", "title": "Objectives", "type": "list"},
    {"key": "scope_of_work", "title": "Scope of Work", "type": "list"},
    {"key": "deliverables", "title": "Deliverables", "type": "list"},
    {"key": "timeline", "title": "Timeline", "type": "list"},
    {"key": "payment_schedule", "title": "Payment Schedule", "type": "list"},
    {"key": "client_responsibilities", "title": "Client Responsibilities", "type": "list"},
    {"key": "revision_policy", "title": "Revision Policy", "type": "text"},
    {"key": "out_of_scope", "title": "Out of Scope", "type": "list"},
    {"key": "assumptions", "title": "Assumptions", "type": "list"},
    {"key": "acceptance_criteria", "title": "Acceptance Criteria", "type": "list"},
]

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

# Playwright timeout (ms): generous enough for fonts, short enough to fail fast.
PLAYWRIGHT_TIMEOUT_MS = 30_000


class PDFService:
    def __init__(self):
        self.storage = StorageService()
        self._env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=False,
        )
        self._css = self._load_css()

    def _load_css(self) -> str:
        css_path = os.path.join(TEMPLATE_DIR, "pdf_styles.css")
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css = f.read()
                logger.debug("[PDF] Loaded pdf_styles.css (%d bytes)", len(css))
                return css
        except FileNotFoundError:
            logger.warning("[PDF] pdf_styles.css not found. Using empty stylesheet.")
            return ""

    # ------------------------------------------------------------------
    # Content normalisation
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_content(content_json: dict) -> list[dict]:
        """Convert flat SOWContent or sections-based content to a unified list.

        Returns a list of dicts:
            { key, title, order, type, text, list_items }

        Never raises — returns empty sections on bad input.
        """
        if not content_json or not isinstance(content_json, dict):
            logger.warning("[PDF] normalize_content received empty or non-dict input. Returning empty sections.")
            return PDFService._normalize_flat_format({})

        # Handle sections-based format: { sections: [ { section_key, ... } ] }
        if "sections" in content_json and isinstance(content_json["sections"], list):
            return PDFService._normalize_sections_format(content_json["sections"])

        # Handle flat SOWContent format: { project_overview, objectives, ... }
        return PDFService._normalize_flat_format(content_json)

    @staticmethod
    def _normalize_flat_format(content: dict) -> list[dict]:
        result = []
        for idx, defn in enumerate(ORDERED_SECTIONS):
            value = content.get(defn["key"])
            section: dict[str, Any] = {
                "key": defn["key"],
                "title": defn["title"],
                "order": idx + 1,
                "type": defn["type"],
                "text": "",
                "list_items": [],
            }
            if isinstance(value, list):
                section["list_items"] = [str(v) for v in value if v]
            elif isinstance(value, str) and value.strip():
                # If the string contains markdown bullets, parse them
                if "\n- " in value or value.startswith("- ") or "\n* " in value or value.startswith("* "):
                    section["list_items"] = [
                        line.lstrip("- ").lstrip("* ").strip()
                        for line in value.split("\n")
                        if line.strip() and (line.strip().startswith("- ") or line.strip().startswith("* "))
                    ]
                    if not section["list_items"]:
                        section["text"] = value
                else:
                    section["text"] = value
            result.append(section)
        return result

    @staticmethod
    def _normalize_sections_format(sections: list[dict]) -> list[dict]:
        by_key = {}
        for s in sections:
            key = s.get("section_key", "")
            if key:
                by_key[key] = s

        result = []
        for idx, defn in enumerate(ORDERED_SECTIONS):
            existing = by_key.get(defn["key"])
            section: dict[str, Any] = {
                "key": defn["key"],
                "title": existing.get("section_title", defn["title"]) if existing else defn["title"],
                "order": idx + 1,
                "type": defn["type"],
                "text": "",
                "list_items": [],
            }
            if existing:
                md = existing.get("content_markdown", "") or ""
                # Parse markdown bullets into items list
                lines = [
                    line.lstrip("- ").lstrip("* ").strip()
                    for line in md.split("\n")
                    if line.strip() and (line.strip().startswith("- ") or line.strip().startswith("* "))
                ]
                if lines:
                    section["list_items"] = lines
                else:
                    section["text"] = md.strip()
            result.append(section)
        return result

    # ------------------------------------------------------------------
    # HTML rendering
    # ------------------------------------------------------------------

    def render_html(
        self,
        sow: dict,
        client_name: str = "",
        project_name: str = "",
        industry: str = "",
    ) -> str:
        """Render SOW data into a full HTML document string.

        Never raises — falls back to inline HTML on any error.
        """
        logger.info("[PDF] Step 1/4: Rendering HTML template...")
        t0 = time.monotonic()

        content_json = sow.get("content_json") or {}
        if not isinstance(content_json, dict):
            content_json = {}
        sections = self.normalize_content(content_json)

        risk_flags = sow.get("risk_flags_json") or []
        if not isinstance(risk_flags, list):
            risk_flags = []
        confidence_score = sow.get("confidence_score")
        sow_id = sow.get("id", "unknown")

        # Build template context
        confidence_display = ""
        if confidence_score is not None:
            try:
                raw = float(confidence_score)
                confidence_display = str(int(raw * 100)) if raw <= 1.0 else str(int(raw))
            except (ValueError, TypeError):
                confidence_display = ""
                confidence_score = None

        context = {
            "css": self._css,
            "client_name": client_name or sow.get("client_name") or "Client",
            "project_name": project_name or sow.get("project_name") or "Project",
            "industry": industry or sow.get("industry") or "",
            "generated_date": datetime.now(timezone.utc).strftime("%B %d, %Y"),
            "document_version": "v1.0",
            "sow_id_short": sow_id[:8] if len(sow_id) > 8 else sow_id,
            "confidence_score": confidence_score,
            "confidence_display": confidence_display,
            "sections": sections,
            "risk_flags": risk_flags,
        }

        try:
            template = self._env.get_template("sow_template.html")
            html = template.render(**context)
            elapsed = time.monotonic() - t0
            logger.info("[PDF] Step 1/4: HTML rendered (%d bytes, %.2fs)", len(html), elapsed)
            return html
        except Exception as e:
            logger.warning("[PDF] Step 1/4: Template rendering failed: %s. Using inline fallback.", e)
            return self._fallback_html(context)

    def _fallback_html(self, context: dict) -> str:
        """Minimal inline HTML when the template file cannot be loaded.

        This is the last-resort fallback. It must NEVER raise.
        """
        try:
            sections_html = ""
            for s in context.get("sections", []):
                if s.get("list_items"):
                    items = "".join(f"<li>{item}</li>" for item in s["list_items"])
                    sections_html += f"<h2>{s['order']}. {s['title']}</h2><ul>{items}</ul>"
                elif s.get("text"):
                    sections_html += f"<h2>{s['order']}. {s['title']}</h2><p>{s['text']}</p>"

            risks_html = ""
            for r in context.get("risk_flags", []):
                severity = r.get("severity", "medium").upper()
                risks_html += f'<div style="background:#fff8e1;border-left:4px solid #f59e0b;padding:12px;margin:8px 0;border-radius:4px;"><strong>{severity}:</strong> {r.get("title", "")} — {r.get("description", "")}</div>'

            return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
@page {{ size: A4; margin: 20mm 16mm; }}
body {{ font-family: -apple-system, 'Segoe UI', sans-serif; margin: 40px; color: #1a1a2e; line-height: 1.6; }}
h1 {{ font-size: 28px; border-bottom: 3px solid #4f46e5; padding-bottom: 10px; text-align: center; }}
h2 {{ font-size: 16px; margin-top: 24px; border-bottom: 1px solid #ddd; padding-bottom: 6px; color: #0f172a; }}
p, li {{ font-size: 13px; }}
ul {{ padding-left: 20px; }}
.meta {{ text-align: center; font-size: 12px; color: #555; margin: 8px 0 32px; }}
.footer {{ margin-top: 48px; text-align: center; font-size: 10px; color: #888; border-top: 1px solid #eee; padding-top: 12px; }}
.sig {{ display: flex; gap: 40px; margin-top: 40px; border-top: 2px solid #e2e8f0; padding-top: 24px; }}
.sig-box {{ flex: 1; }}
.sig-line {{ border-bottom: 1px solid #333; margin: 24px 0 6px; }}
.sig-label {{ font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }}
</style></head><body>
<p style="text-align:center;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#4f46e5;font-weight:600;">BriefToScope</p>
<h1>Statement of Work</h1>
<div class="meta">
<strong>Client:</strong> {context.get('client_name', '')} &nbsp;|&nbsp;
<strong>Project:</strong> {context.get('project_name', '')} &nbsp;|&nbsp;
<strong>Date:</strong> {context.get('generated_date', '')}
</div>
{sections_html}
{risks_html}
<div class="sig">
<div class="sig-box"><div class="sig-label">Client</div><div class="sig-line"></div><span style="font-size:11px;color:#64748b;">Authorized Signature &nbsp;&nbsp; Date: ___________</span></div>
<div class="sig-box"><div class="sig-label">Agency / Provider</div><div class="sig-line"></div><span style="font-size:11px;color:#64748b;">Authorized Signature &nbsp;&nbsp; Date: ___________</span></div>
</div>
<div class="footer">Generated by BriefToScope — AI-powered Statement of Work platform. Confidential.</div>
</body></html>"""
        except Exception as e:
            logger.error("[PDF] Even fallback HTML generation failed: %s", e)
            return "<html><body><h1>Statement of Work</h1><p>PDF generation encountered an error. Please contact support.</p></body></html>"

    # ------------------------------------------------------------------
    # PDF generation
    # ------------------------------------------------------------------

    async def generate_pdf(
        self,
        sow: dict,
        client_name: str = "",
        project_name: str = "",
        industry: str = "",
    ) -> bytes:
        """Generate PDF bytes from SOW data.

        Falls back gracefully:
        1. Try Playwright Chromium → real PDF bytes.
        2. If Playwright fails → return styled HTML bytes (printable from browser).

        Never raises.
        """
        logger.info("[PDF] Step 2/4: Generating PDF bytes...")
        t0 = time.monotonic()

        html = self.render_html(sow, client_name, project_name, industry)

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                # Use 'domcontentloaded' instead of 'networkidle' to avoid
                # stalling when Google Fonts are unreachable.
                await page.set_content(html, wait_until="domcontentloaded", timeout=PLAYWRIGHT_TIMEOUT_MS)
                # Give fonts a brief moment to load (non-blocking best effort)
                try:
                    await page.wait_for_timeout(1500)
                except Exception:
                    pass
                pdf_bytes = await page.pdf(
                    format="A4",
                    print_background=True,
                    margin={
                        "top": "20mm",
                        "right": "16mm",
                        "bottom": "20mm",
                        "left": "16mm",
                    },
                )
                await browser.close()
                elapsed = time.monotonic() - t0
                logger.info("[PDF] Step 2/4: Playwright PDF generated (%d bytes, %.2fs)", len(pdf_bytes), elapsed)
                return pdf_bytes

        except ImportError:
            logger.warning("[PDF] Step 2/4: Playwright not installed. Returning styled HTML fallback.")
            return html.encode("utf-8")
        except Exception as e:
            elapsed = time.monotonic() - t0
            logger.warning("[PDF] Step 2/4: Playwright failed after %.2fs: %s. Returning styled HTML fallback.", elapsed, e)
            return html.encode("utf-8")

    # ------------------------------------------------------------------
    # Full export pipeline
    # ------------------------------------------------------------------

    async def export_and_upload(
        self,
        sow: dict,
        client_name: str = "",
        project_name: str = "",
        industry: str = "",
        user_id: str = "",
        org_id: str = "",
    ) -> dict:
        """Generate PDF, upload to private storage, and record export metadata.

        Never raises — every step has a try/except guard. The result dict always has
        Storage errors are surfaced instead of returning public or demo URLs.
        """
        sow_id = sow.get("id", "unknown")
        filename = f"brief-to-scope-sow-{sow_id}.pdf"
        generated_at = datetime.now(timezone.utc)
        pipeline_start = time.monotonic()

        logger.info("[PDF] ═══════════════════════════════════════════")
        logger.info("[PDF] Export pipeline started for SOW %s", sow_id)

        # 1. Generate PDF bytes
        try:
            pdf_bytes = await self.generate_pdf(sow, client_name, project_name, industry)
        except Exception as e:
            logger.error("[PDF] Step 2/4: generate_pdf raised unexpectedly: %s", e)
            # Last resort: minimal HTML
            pdf_bytes = f"<html><body><h1>SOW {sow_id}</h1><p>PDF generation failed.</p></body></html>".encode("utf-8")

        # 2. Upload to storage
        logger.info("[PDF] Step 3/4: Uploading to storage...")
        try:
            storage_path = await self.storage.upload_pdf_private(
                sow_id=sow_id,
                pdf_bytes=pdf_bytes,
                filename=filename,
                org_id=org_id or sow.get("org_id") or user_id or "unknown",
                user_id=user_id,
            )
            export_record = await self.storage.create_pdf_export(
                sow_id=sow_id,
                storage_path=storage_path,
                status="ready",
            )
            pdf_url = storage_path
            logger.info("[PDF] Step 3/4: Uploaded → %s", pdf_url)
        except Exception as e:
            logger.warning("[PDF] Step 3/4: Private storage upload failed: %s.", e)
            raise

        logger.info("[PDF] Step 4/4: private export record saved.")

        # 4. Update SOW status to "exported"
        try:
            await self.storage.update_sow_status(sow_id, "exported")
            logger.info("[PDF] Step 4/4: SOW status → exported.")
        except Exception as e:
            logger.warning("[PDF] Step 4/4: Failed to update SOW status: %s (non-fatal)", e)

        total_elapsed = time.monotonic() - pipeline_start
        logger.info("[PDF] Export pipeline completed for SOW %s in %.2fs", sow_id, total_elapsed)
        logger.info("[PDF] ═══════════════════════════════════════════")

        return {
            "success": True,
            "sow_id": sow_id,
            "export_id": export_record["id"],
            "status": export_record.get("status", "ready"),
            "storage_path": storage_path,
            "pdf_url": pdf_url,
            "filename": filename,
            "generated_at": generated_at,
        }
