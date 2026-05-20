import os
# Force demo mode and mock settings via environment variables
os.environ["DEMO_MODE"] = "True"
os.environ["SUPABASE_URL"] = "http://localhost:54321"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "mock_key"

import pytest
from fastapi.testclient import TestClient
from app.config import get_settings
get_settings.cache_clear()  # Clear cache to ensure settings are re-read with env vars

from app.main import app

client = TestClient(app)

def test_generate_sow_endpoint_success():
    """Verifies that the /generate-sow endpoint runs successfully, updates project statuses,

    and returns the correct JSON response structure with full telemetry.
    """
    payload = {
        "transcript_text": "We need to redesign our corporate website. Our client is Acme Corp, and the project name is Corporate Website Redesign. The budget is $50,000 and it must launch by September. We need custom Figma designs, frontend development, and CMS integration.",
        "client_name": "Acme Corp",
        "project_name": "Corporate Website Redesign",
        "industry": "Web Design",
        "tone": "professional",
        "budget": "$50,000",
        "timeline": "September 2026"
    }
    
    response = client.post(
        "/generate-sow",
        json=payload,
        headers={"Authorization": "Bearer demo_token"}
    )
    
    assert response.status_code == 200, f"Error response: {response.text}"
    data = response.json()
    
    # 1. Base response checks
    assert data["success"] is True
    assert "project_id" in data
    assert "transcript_id" in data
    assert "sow_id" in data
    assert data["status"] == "generated"
    
    # 2. Pipeline telemetry validation
    pipeline = data["ai_pipeline"]
    stages = [
        "a1_transcript_cleaner",
        "a2_brief_extractor",
        "a3_scope_builder",
        "a4_risk_detector",
        "a5_clause_generator",
        "a6_sow_composer",
        "a7_quality_checker"
    ]
    for stage in stages:
        assert stage in pipeline, f"Missing pipeline stage {stage}"
        step_data = pipeline[stage]
        assert "status" in step_data
        assert "output" in step_data
        assert "duration_ms" in step_data
        assert step_data["status"] in ("success", "fallback")
        assert step_data["duration_ms"] >= 0

    # 3. SOW response format validation
    sow = data["sow"]
    assert sow["title"] == "Corporate Website Redesign"
    assert "content_json" in sow
    assert "content_markdown" in sow
    assert "sections" in sow
    assert len(sow["sections"]) > 0
    
    assert "extracted_brief" in data
    assert "confidence_score" in data
    assert data["confidence_score"] >= 0

    for s in sow["sections"]:
        assert "key" in s
        assert "title" in s
        assert "content" in s
        assert "order" in s

    # 4. Risks and Quality Checks
    assert isinstance(data["risk_flags"], list)
    quality = data["quality"]
    assert "overall_quality_score" in quality
    assert "approval_status" in quality
    assert "ready_for_export" in quality
    assert isinstance(quality["warnings"], list)

    # 5. Metadata Check
    metadata = data["metadata"]
    assert metadata["generation_time_ms"] > 0
    assert metadata["demo_mode"] is True
    assert "fallback_used" in metadata
    assert metadata["model_used"] == "gpt-4o-mini"
