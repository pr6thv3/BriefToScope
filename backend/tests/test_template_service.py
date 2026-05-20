import os
import json
import pytest
from pydantic import ValidationError
from app.services.template_service import TemplateService
from app.models.template_schemas import SOWTemplate

def test_all_10_templates_load_correctly():
    """Verifies that all 10 standard industry JSON files load and pass schema validation."""
    service = TemplateService()
    
    industries = [
        "Web Design",
        "Branding",
        "Marketing",
        "Copywriting",
        "Social Media",
        "Video Production",
        "SEO",
        "App Development",
        "Consulting",
        "Ecommerce"
    ]
    
    for industry in industries:
        template = service.load_template(industry)
        assert isinstance(template, SOWTemplate)
        assert template.industry == industry
        assert len(template.default_sections) > 0
        assert len(template.standard_deliverables) > 0
        assert len(template.common_out_of_scope_items) > 0
        assert len(template.payment_schedule_options) > 0
        assert len(template.risk_rules) > 0
        
        # Verify cache works
        cached_template = service.load_template(industry)
        assert cached_template is template

def test_missing_industry_falls_back_safely():
    """Verifies that querying an unknown industry name falls back cleanly to the Consulting template."""
    service = TemplateService()
    template = service.load_template("Quantum Gardening")
    
    # Fallback to Consulting template
    assert isinstance(template, SOWTemplate)
    assert template.industry == "Consulting"

def test_invalid_template_fails_validation(tmp_path):
    """Verifies that a malformed JSON file triggers a fallback to Consulting instead of crashing."""
    # Write an invalid template JSON structure to a temp directory
    invalid_data = {
        "industry": "Broken Industry",
        "default_sections": "This should be a list, not a string",
        "standard_deliverables": []
    }
    
    invalid_dir = tmp_path / "templates"
    invalid_dir.mkdir()
    
    file_path = invalid_dir / "broken_industry.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(invalid_data, f)
        
    service = TemplateService(templates_dir=str(invalid_dir))
    
    template = service.load_template("Broken Industry")
    assert isinstance(template, SOWTemplate)
    assert template.industry == "Consulting"  # Cleany falls back to memory consulting template!

def test_web_design_template_returns_expected_exclusions():
    """Verifies specific details are loaded for the Web Design template."""
    service = TemplateService()
    template = service.load_template("Web Design")
    
    assert "Copywriting" in template.common_out_of_scope_items
    assert "Photography" in template.common_out_of_scope_items
    
    # Verify clause library contains revision policies
    assert len(template.clause_library.revision) > 0
    assert "rounds of revisions" in template.clause_library.revision[0]

def test_missing_directory_fallback_to_memory():
    """Verifies that if the templates directory does not exist, it falls back to DEFAULT_CONSULTING_TEMPLATE in memory."""
    service = TemplateService(templates_dir="non_existent_folder_xyz")
    template = service.load_template("Any Industry")
    
    assert isinstance(template, SOWTemplate)
    assert template.industry == "Consulting"
    assert "Discovery & Strategy Assessment" in template.standard_deliverables
    assert len(template.clause_library.revision) > 0

