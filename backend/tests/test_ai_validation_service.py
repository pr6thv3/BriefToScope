from app.services.ai_validation_service import AIValidationService


def test_ai_validation_blocks_incomplete_sow_from_export_ready_state():
    result = AIValidationService().validate_sow(
        {
            "project_overview": "A short website project.",
            "deliverables": ["Website"],
            "revision_policy": "",
        }
    )

    assert result["ready_for_export"] is False
    assert "Timeline" in result["missing_items"]
    assert "Payment schedule" in result["missing_items"]
    assert "Revision limits" in result["missing_items"]
    assert any(flag["severity"] == "high" for flag in result["risk_flags"])


def test_ai_validation_accepts_structured_complete_sow_sections():
    result = AIValidationService().validate_sow(
        {
            "sections": [
                {"section_key": "project_overview", "content_markdown": "A scoped brand website project."},
                {"section_key": "objectives", "content_markdown": "- Increase conversion\n- Clarify offer"},
                {"section_key": "scope_of_work", "content_markdown": "- Strategy\n- Design\n- Build"},
                {"section_key": "deliverables", "content_markdown": "- 8 responsive pages\n- CMS setup\n- Launch QA"},
                {"section_key": "timeline", "content_markdown": "- Week 1 kickoff\n- Week 6 launch"},
                {"section_key": "payment_schedule", "content_markdown": "- 50% kickoff\n- 25% design approval\n- 25% launch"},
                {"section_key": "client_responsibilities", "content_markdown": "- Provide final copy and assets"},
                {"section_key": "revision_policy", "content_markdown": "Two rounds of revisions are included."},
                {"section_key": "out_of_scope", "content_markdown": "- Copywriting\n- Photography"},
                {"section_key": "assumptions", "content_markdown": "- Client feedback within 3 business days"},
                {"section_key": "acceptance_criteria", "content_markdown": "- Approved pages built and tested"},
                {"section_key": "signature_section", "content_markdown": "Authorized signatures."},
            ]
        }
    )

    assert result["quality_score"] >= 75
    assert result["ready_for_export"] is True
