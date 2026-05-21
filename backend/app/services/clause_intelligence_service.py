from typing import Dict, List

from app.services.ai_data_service import AIDataService


class ClauseIntelligenceService:
    """Industry-specific clause and scope-creep knowledge facade."""

    def __init__(self):
        self.ai_data = AIDataService()

    def get_scope_intelligence(self, industry: str) -> Dict[str, object]:
        template = self.ai_data.get_industry_template(industry)
        return {
            "industry": template.industry,
            "standard_deliverables": template.standard_deliverables,
            "common_exclusions": template.common_out_of_scope_items,
            "payment_schedule_options": [option.model_dump() for option in template.payment_schedule_options],
            "revision_policy": template.revision_policy,
            "risk_rules": [rule.model_dump() for rule in template.risk_rules],
            "clause_library": template.clause_library.model_dump(),
        }

    def predict_scope_traps(self, industry: str, text: str) -> List[dict]:
        rules = self.ai_data.get_risk_rules(industry)
        lower_text = text.lower()
        matches = []
        for rule in rules:
            terms = [term.lower() for term in rule.trigger_terms]
            if any(term in lower_text for term in terms):
                matches.append({
                    "title": rule.risk,
                    "severity": "medium",
                    "evidence": [term for term in terms if term in lower_text],
                    "recommended_fix": rule.recommended_fix,
                })
        return matches

