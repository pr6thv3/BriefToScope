import pytest
from app.services.template_service import TemplateService
from app.services.ai_data_service import AIDataService
from app.models.template_schemas import SOWTemplate, ClauseLibrary

def test_ai_data_service_attribute_retrieval():
    """Tests retrieval of specific template details via AIDataService."""
    ai_data = AIDataService()
    
    # Standard deliverables
    delivs = ai_data.get_standard_deliverables("Web Design")
    assert "Website strategy" in delivs
    assert "Responsive page design" in delivs
    
    # Common exclusions
    excl = ai_data.get_common_exclusions("Web Design")
    assert "Copywriting" in excl
    assert "Ongoing maintenance" in excl
    
    # Revision policy
    policy = ai_data.get_default_revision_policy("Web Design")
    assert "two rounds of revisions" in policy.lower()
    
    # Payment schedules
    payments = ai_data.get_payment_schedule_options("Web Design")
    assert len(payments) > 0
    assert payments[0].label == "Standard 50/25/25"
    assert payments[0].milestones[0].percentage == "50%"
    
    # Risk rules
    risks = ai_data.get_risk_rules("Web Design")
    assert len(risks) > 0
    assert risks[0].risk == "Copywriting ownership unclear"
    assert "copy" in risks[0].trigger_terms
    
    # Clause library
    clauses = ai_data.get_clause_library("Web Design")
    assert isinstance(clauses, ClauseLibrary)
    assert len(clauses.revision) > 0
    assert len(clauses.payment) > 0
    assert len(clauses.out_of_scope) > 0

def test_enrich_pipeline_context_structure():
    """Verifies the context enrichment dictionary format for downstream pipeline agents."""
    ai_data = AIDataService()
    
    a1_cleaned = {"cleaned_text": "Cleaned call transcript details"}
    a2_brief = {"client_name": "Acme", "budget": "$20k"}
    a3_scope = {"deliverables": ["Custom frontend", "SEO audit"]}
    a4_risks = [{"risk": "Timeline is extremely aggressive"}]
    
    enriched = ai_data.enrich_pipeline_context(
        industry="Web Design",
        a1=a1_cleaned,
        a2=a2_brief,
        a3=a3_scope,
        a4=a4_risks
    )
    
    # Assert top-level structure
    assert "template" in enriched
    assert "pipeline_stages" in enriched
    
    # Assert template elements
    t = enriched["template"]
    assert t["industry"] == "Web Design"
    assert "Website strategy" in t["standard_deliverables"]
    assert "Copywriting" in t["common_out_of_scope_items"]
    assert len(t["clause_library"]["ip_ownership"]) > 0
    
    # Assert pipeline stages are correctly preserved
    stages = enriched["pipeline_stages"]
    assert stages["a1_cleaned_text"] == a1_cleaned
    assert stages["a2_extracted_brief"] == a2_brief
    assert stages["a3_scope_builder"] == a3_scope
    assert stages["a4_risk_detector"] == a4_risks
