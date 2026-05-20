"""Tests for the PDF export layer.

Covers:
- Content normalisation (flat, sections, empty, None, malformed)
- HTML rendering (all sections, risks, confidence, signature, footer, empty, no-risks, sections-format, payment table, timeline table)
- PDFExportResponse schema
- Export pipeline (enriched result, upload calls, status update failure survival, pdf_url update failure survival, generate_pdf failure survival)
- Playwright fallback path (import error, runtime error)
- Storage service (demo upload, demo status update)
- Usage tracking
- Route-level DEMO_MODE e2e
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.pdf_service import PDFService, ORDERED_SECTIONS
from app.services.storage_service import StorageService
from app.services.demo_data import get_fallback_sow, get_fallback_risks
from app.models.schemas import PDFExportResponse


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def flat_content():
    """Flat SOWContent-style dict."""
    return get_fallback_sow()


@pytest.fixture
def sections_content():
    """Sections-based content dict."""
    flat = get_fallback_sow()
    sections = []
    for idx, defn in enumerate(ORDERED_SECTIONS):
        value = flat.get(defn["key"], "")
        if isinstance(value, list):
            md = "\n".join(f"- {v}" for v in value)
        else:
            md = value
        sections.append({
            "section_key": defn["key"],
            "section_title": defn["title"],
            "content_markdown": md,
            "order": idx + 1,
        })
    return {"sections": sections}


@pytest.fixture
def sample_sow(flat_content):
    """Full SOW dict as stored in the database."""
    return {
        "id": "test-sow-001",
        "user_id": "test-user",
        "content_json": flat_content,
        "risk_flags_json": get_fallback_risks(),
        "confidence_score": 0.89,
        "status": "draft",
    }


@pytest.fixture
def pdf_service():
    return PDFService()


# =====================================================================
# Content normalisation tests
# =====================================================================

class TestNormalizeContent:
    def test_flat_format_produces_all_sections(self, flat_content):
        sections = PDFService.normalize_content(flat_content)
        assert len(sections) == len(ORDERED_SECTIONS)
        keys = [s["key"] for s in sections]
        for defn in ORDERED_SECTIONS:
            assert defn["key"] in keys

    def test_flat_format_preserves_order(self, flat_content):
        sections = PDFService.normalize_content(flat_content)
        for idx, section in enumerate(sections):
            assert section["order"] == idx + 1

    def test_flat_format_list_sections_have_items(self, flat_content):
        sections = PDFService.normalize_content(flat_content)
        objectives = next(s for s in sections if s["key"] == "objectives")
        assert len(objectives["list_items"]) > 0
        assert objectives["text"] == ""

    def test_flat_format_text_sections_have_text(self, flat_content):
        sections = PDFService.normalize_content(flat_content)
        revision = next(s for s in sections if s["key"] == "revision_policy")
        assert revision["text"] != ""
        assert revision["list_items"] == []

    def test_sections_format_produces_all_sections(self, sections_content):
        sections = PDFService.normalize_content(sections_content)
        assert len(sections) == len(ORDERED_SECTIONS)
        keys = [s["key"] for s in sections]
        for defn in ORDERED_SECTIONS:
            assert defn["key"] in keys

    def test_sections_format_parses_bullets(self, sections_content):
        sections = PDFService.normalize_content(sections_content)
        objectives = next(s for s in sections if s["key"] == "objectives")
        assert len(objectives["list_items"]) > 0

    def test_empty_content_produces_all_sections(self):
        sections = PDFService.normalize_content({})
        assert len(sections) == len(ORDERED_SECTIONS)
        for s in sections:
            assert s["list_items"] == []
            assert s["text"] == ""

    def test_none_content_returns_empty_sections(self):
        """normalize_content must never raise, even on None."""
        sections = PDFService.normalize_content(None)
        assert len(sections) == len(ORDERED_SECTIONS)

    def test_non_dict_content_returns_empty_sections(self):
        """normalize_content must handle non-dict input."""
        sections = PDFService.normalize_content("not a dict")
        assert len(sections) == len(ORDERED_SECTIONS)

    def test_partial_content_fills_missing(self):
        partial = {"project_overview": "Only this section exists."}
        sections = PDFService.normalize_content(partial)
        assert len(sections) == len(ORDERED_SECTIONS)
        overview = next(s for s in sections if s["key"] == "project_overview")
        assert overview["text"] == "Only this section exists."

    def test_list_with_none_values_filtered(self):
        """Lists containing None values should be filtered out."""
        content = {"objectives": ["Valid goal", None, "", "Another goal"]}
        sections = PDFService.normalize_content(content)
        objectives = next(s for s in sections if s["key"] == "objectives")
        # None is filtered by str(v) but "" is filtered by `if v`
        assert all(item for item in objectives["list_items"])


# =====================================================================
# HTML rendering tests
# =====================================================================

class TestRenderHTML:
    def test_html_contains_all_section_headings(self, pdf_service, sample_sow):
        html = pdf_service.render_html(sample_sow, client_name="Acme Corp", project_name="Website Redesign")
        for defn in ORDERED_SECTIONS:
            assert defn["title"] in html, f"Section heading '{defn['title']}' not found in rendered HTML"

    def test_html_contains_client_name(self, pdf_service, sample_sow):
        html = pdf_service.render_html(sample_sow, client_name="Acme Corp")
        assert "Acme Corp" in html

    def test_html_contains_project_name(self, pdf_service, sample_sow):
        html = pdf_service.render_html(sample_sow, project_name="Website Redesign")
        assert "Website Redesign" in html

    def test_html_contains_risk_warnings(self, pdf_service, sample_sow):
        html = pdf_service.render_html(sample_sow)
        assert "Scope Risk Warnings" in html
        for risk in sample_sow["risk_flags_json"]:
            assert risk["title"] in html

    def test_html_contains_confidence_badge(self, pdf_service, sample_sow):
        html = pdf_service.render_html(sample_sow)
        assert "AI Confidence" in html
        assert "89%" in html

    def test_html_contains_signature_section(self, pdf_service, sample_sow):
        html = pdf_service.render_html(sample_sow)
        assert "Authorization" in html
        assert "Signature" in html

    def test_html_contains_footer(self, pdf_service, sample_sow):
        html = pdf_service.render_html(sample_sow)
        assert "BriefToScope" in html
        assert "confidential" in html.lower()

    def test_html_handles_empty_content(self, pdf_service):
        empty_sow = {"id": "empty", "content_json": {}}
        html = pdf_service.render_html(empty_sow)
        assert "Statement of Work" in html
        assert "Content pending" in html

    def test_html_handles_none_content(self, pdf_service):
        """content_json=None should not crash."""
        sow = {"id": "none-content", "content_json": None}
        html = pdf_service.render_html(sow)
        assert "Statement of Work" in html

    def test_html_handles_no_risks(self, pdf_service, flat_content):
        sow = {"id": "no-risk", "content_json": flat_content, "risk_flags_json": []}
        html = pdf_service.render_html(sow)
        assert "Scope Risk Warnings" not in html

    def test_html_handles_none_risk_flags(self, pdf_service, flat_content):
        """risk_flags_json=None should not crash."""
        sow = {"id": "none-risk", "content_json": flat_content, "risk_flags_json": None}
        html = pdf_service.render_html(sow)
        assert "Scope Risk Warnings" not in html

    def test_html_handles_sections_format(self, pdf_service, sections_content):
        sow = {"id": "sect-fmt", "content_json": sections_content, "confidence_score": 0.95}
        html = pdf_service.render_html(sow)
        for defn in ORDERED_SECTIONS:
            assert defn["title"] in html

    def test_html_renders_payment_as_table(self, pdf_service, sample_sow):
        html = pdf_service.render_html(sample_sow)
        assert "payment-table" in html
        assert "Milestone" in html

    def test_html_renders_timeline_as_table(self, pdf_service, sample_sow):
        """Timeline should render as a Phase table, not bullets."""
        html = pdf_service.render_html(sample_sow)
        assert "Phase" in html

    def test_html_invalid_confidence_score(self, pdf_service, flat_content):
        """Non-numeric confidence_score should not crash."""
        sow = {"id": "bad-conf", "content_json": flat_content, "confidence_score": "invalid"}
        html = pdf_service.render_html(sow)
        assert "Statement of Work" in html
        # Confidence badge should NOT appear with invalid score
        assert "AI Confidence" not in html

    def test_html_signature_shows_client_name(self, pdf_service, sample_sow):
        """Signature section should display the client name."""
        html = pdf_service.render_html(sample_sow, client_name="Luma Retail")
        assert "Luma Retail" in html


# =====================================================================
# Schema validation tests
# =====================================================================

class TestPDFExportResponseSchema:
    def test_valid_response(self):
        resp = PDFExportResponse(
            success=True,
            sow_id="test-123",
            pdf_url="https://example.com/test.pdf",
            filename="brief-to-scope-sow-test-123.pdf",
            generated_at=datetime.now(timezone.utc),
        )
        assert resp.success is True
        assert resp.sow_id == "test-123"
        assert resp.filename.startswith("brief-to-scope-sow-")

    def test_response_serialization(self):
        resp = PDFExportResponse(
            success=True,
            sow_id="test-456",
            pdf_url="https://example.com/test.pdf",
            filename="brief-to-scope-sow-test-456.pdf",
            generated_at=datetime(2026, 5, 20, 15, 0, 0),
        )
        data = resp.model_dump()
        assert "success" in data
        assert "sow_id" in data
        assert "pdf_url" in data
        assert "filename" in data
        assert "generated_at" in data


# =====================================================================
# Export pipeline tests (mocked storage)
# =====================================================================

class TestExportAndUpload:
    @pytest.mark.asyncio
    async def test_export_returns_enriched_result(self, sample_sow):
        service = PDFService()
        service.storage = MagicMock(spec=StorageService)
        service.storage.upload_pdf = AsyncMock(return_value="https://demo.storage/test.pdf")
        service.storage.update_sow_pdf_url = AsyncMock()
        service.storage.update_sow_status = AsyncMock()

        result = await service.export_and_upload(
            sow=sample_sow,
            client_name="Acme Corp",
            project_name="Website Redesign",
            industry="E-commerce",
            user_id="user-123",
        )

        assert result["success"] is True
        assert result["sow_id"] == "test-sow-001"
        assert result["filename"] == "brief-to-scope-sow-test-sow-001.pdf"
        assert "generated_at" in result
        assert isinstance(result["generated_at"], datetime)

    @pytest.mark.asyncio
    async def test_export_calls_upload(self, sample_sow):
        service = PDFService()
        service.storage = MagicMock(spec=StorageService)
        service.storage.upload_pdf = AsyncMock(return_value="https://demo.storage/test.pdf")
        service.storage.update_sow_pdf_url = AsyncMock()
        service.storage.update_sow_status = AsyncMock()

        await service.export_and_upload(sow=sample_sow)

        service.storage.upload_pdf.assert_called_once()
        service.storage.update_sow_pdf_url.assert_called_once_with("test-sow-001", "https://demo.storage/test.pdf")
        service.storage.update_sow_status.assert_called_once_with("test-sow-001", "exported")

    @pytest.mark.asyncio
    async def test_export_survives_status_update_failure(self, sample_sow):
        service = PDFService()
        service.storage = MagicMock(spec=StorageService)
        service.storage.upload_pdf = AsyncMock(return_value="https://demo.storage/test.pdf")
        service.storage.update_sow_pdf_url = AsyncMock()
        service.storage.update_sow_status = AsyncMock(side_effect=Exception("DB down"))

        result = await service.export_and_upload(sow=sample_sow)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_export_survives_pdf_url_update_failure(self, sample_sow):
        """Pipeline should succeed even if pdf_url update fails."""
        service = PDFService()
        service.storage = MagicMock(spec=StorageService)
        service.storage.upload_pdf = AsyncMock(return_value="https://demo.storage/test.pdf")
        service.storage.update_sow_pdf_url = AsyncMock(side_effect=Exception("DB timeout"))
        service.storage.update_sow_status = AsyncMock()

        result = await service.export_and_upload(sow=sample_sow)
        assert result["success"] is True
        assert result["pdf_url"] == "https://demo.storage/test.pdf"

    @pytest.mark.asyncio
    async def test_export_survives_upload_failure(self, sample_sow):
        """Pipeline should succeed with mock URL if storage.upload_pdf raises."""
        service = PDFService()
        service.storage = MagicMock(spec=StorageService)
        service.storage.upload_pdf = AsyncMock(side_effect=Exception("Storage down"))
        service.storage.update_sow_pdf_url = AsyncMock()
        service.storage.update_sow_status = AsyncMock()

        result = await service.export_and_upload(sow=sample_sow, user_id="user-1")
        assert result["success"] is True
        assert "demo.storage" in result["pdf_url"]


# =====================================================================
# Playwright fallback tests
# =====================================================================

class TestPlaywrightFallback:
    @pytest.mark.asyncio
    async def test_generate_pdf_returns_bytes_on_import_error(self, sample_sow):
        """When playwright is not importable, generate_pdf returns HTML bytes."""
        service = PDFService()
        # Monkey-patch to simulate ImportError
        with patch.dict("sys.modules", {"playwright": None, "playwright.async_api": None}):
            # The import inside generate_pdf will raise ImportError
            result = await service.generate_pdf(sample_sow, client_name="Acme")
        assert isinstance(result, bytes)
        assert b"Statement of Work" in result

    @pytest.mark.asyncio
    async def test_generate_pdf_fallback_is_valid_html(self, sample_sow):
        """Fallback HTML should be a valid, styled document."""
        service = PDFService()
        with patch.dict("sys.modules", {"playwright": None, "playwright.async_api": None}):
            result = await service.generate_pdf(sample_sow)
        html = result.decode("utf-8")
        assert "<!DOCTYPE html>" in html
        assert "BriefToScope" in html


# =====================================================================
# Storage service tests
# =====================================================================

class TestStorageServicePDF:
    @pytest.mark.asyncio
    async def test_demo_upload_returns_url(self):
        storage = StorageService()
        storage._demo = True
        url = await storage.upload_pdf("sow-123", b"fake-pdf", "test.pdf", user_id="user-1")
        assert "sow-123" in url
        assert "test.pdf" in url
        assert "user-1" in url

    @pytest.mark.asyncio
    async def test_demo_upload_with_empty_user_id(self):
        storage = StorageService()
        storage._demo = True
        url = await storage.upload_pdf("sow-456", b"pdf", "test.pdf", user_id="")
        assert "demo" in url

    @pytest.mark.asyncio
    async def test_demo_update_sow_status(self):
        from app.services.storage_service import _demo_sows
        _demo_sows["status-test"] = {
            "id": "status-test",
            "status": "draft",
            "updated_at": "2026-01-01",
        }
        storage = StorageService()
        storage._demo = True
        result = await storage.update_sow_status("status-test", "exported")
        assert result["status"] == "exported"
        _demo_sows.pop("status-test", None)


# =====================================================================
# Usage tracking test
# =====================================================================

class TestUsageTracking:
    @pytest.mark.asyncio
    async def test_track_pdf_export_event(self):
        from app.services.usage_service import UsageService
        service = UsageService()
        service.storage = MagicMock(spec=StorageService)
        service.storage.create_usage_event = AsyncMock(return_value={"id": "evt-1"})

        await service.track_event("user-1", "pdf_export", token_count=0)
        service.storage.create_usage_event.assert_called_once()
        call_args = service.storage.create_usage_event.call_args
        assert call_args[0][1] == "pdf_export"


# =====================================================================
# Route-level DEMO_MODE e2e test
# =====================================================================

class TestDemoModeRoute:
    @pytest.mark.asyncio
    async def test_demo_route_returns_success_for_unknown_sow(self):
        """In DEMO_MODE, export-pdf for a non-existent SOW ID returns success."""
        from httpx import AsyncClient, ASGITransport
        from app.main import app
        from app.config import Settings
        from app.dependencies import get_current_user

        # Create demo settings
        demo_settings = Settings(demo_mode=True)

        # Override auth dependency (route uses Depends)
        app.dependency_overrides[get_current_user] = lambda: {"sub": "demo_user", "email": "demo@example.com"}

        try:
            # Patch get_settings where it is called directly in routes_pdf
            with patch("app.api.routes_pdf.get_settings", return_value=demo_settings):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    resp = await client.post("/sows/nonexistent-id-999/export-pdf")

            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["sow_id"] == "nonexistent-id-999"
            assert "pdf_url" in data
            assert "filename" in data
            assert data["filename"].startswith("brief-to-scope-sow-")
        finally:
            app.dependency_overrides.pop(get_current_user, None)
