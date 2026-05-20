from typing import Dict, Any, List
from app.services.template_service import TemplateService
from app.models.template_schemas import SOWTemplate, ClauseLibrary, RiskRule, PaymentScheduleOption

class AIDataService:
    """Service to bridge template configurations and AI orchestrator stages."""

    def __init__(self, template_service: TemplateService = None):
        self.template_service = template_service or TemplateService()

    def get_industry_template(self, industry: str) -> SOWTemplate:
        """Retrieves the full validation template object for a given industry."""
        return self.template_service.load_template(industry)

    def get_clause_library(self, industry: str) -> ClauseLibrary:
        """Retrieves the clause library configuration block for a given industry."""
        return self.get_industry_template(industry).clause_library

    def get_risk_rules(self, industry: str) -> List[RiskRule]:
        """Retrieves the risk detection dictionary rules for a given industry."""
        return self.get_industry_template(industry).risk_rules

    def get_standard_deliverables(self, industry: str) -> List[str]:
        """Retrieves standard in-scope deliverables for a given industry."""
        return self.get_industry_template(industry).standard_deliverables

    def get_common_exclusions(self, industry: str) -> List[str]:
        """Retrieves common exclusions/out-of-scope clauses for a given industry."""
        return self.get_industry_template(industry).common_out_of_scope_items

    def get_default_revision_policy(self, industry: str) -> str:
        """Retrieves the default revision rules for a given industry."""
        return self.get_industry_template(industry).revision_policy

    def get_payment_schedule_options(self, industry: str) -> List[PaymentScheduleOption]:
        """Retrieves standard milestone options for a given industry."""
        return self.get_industry_template(industry).payment_schedule_options

    def enrich_pipeline_context(self, industry: str, a1: Any, a2: Any, a3: Any, a4: Any) -> Dict[str, Any]:
        """Merges industry standard configurations with active pipeline agent states
        to form enriched contextual directives for downstream generators (A5–A7).
        """
        template = self.get_industry_template(industry)
        return {
            "template": {
                "industry": template.industry,
                "default_sections": template.default_sections,
                "standard_deliverables": template.standard_deliverables,
                "common_out_of_scope_items": template.common_out_of_scope_items,
                "revision_policy": template.revision_policy,
                "payment_schedule_options": [o.model_dump() for o in template.payment_schedule_options],
                "client_responsibilities": template.client_responsibilities,
                "timeline_assumptions": template.timeline_assumptions,
                "acceptance_criteria": template.acceptance_criteria,
                "clause_library": template.clause_library.model_dump()
            },
            "pipeline_stages": {
                "a1_cleaned_text": a1,
                "a2_extracted_brief": a2,
                "a3_scope_builder": a3,
                "a4_risk_detector": a4
            }
        }
