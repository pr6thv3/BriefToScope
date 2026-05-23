import os
import json
import logging
from typing import Dict
from app.models.template_schemas import SOWTemplate

logger = logging.getLogger(__name__)

DEFAULT_CONSULTING_TEMPLATE = {
    "industry": "Consulting",
    "default_sections": [
        "overview",
        "objectives",
        "scope",
        "deliverables",
        "timeline",
        "payment",
        "client_responsibilities",
        "revision_policy",
        "out_of_scope",
        "assumptions",
        "acceptance_criteria",
        "signature"
    ],
    "standard_deliverables": [
        "Discovery & Strategy Assessment",
        "Advisory Consulting Sessions",
        "Final Roadmap & Recommendations Report"
    ],
    "common_out_of_scope_items": [
        "Technical implementation",
        "Ongoing operational support",
        "Third-party vendor fees"
    ],
    "revision_policy": "Each deliverable includes up to two rounds of revisions. Additional revisions billed at standard hourly rates.",
    "payment_schedule_options": [
        {
            "label": "Standard 50/50",
            "milestones": [
                {"percentage": "50%", "condition": "Due before project kickoff"},
                {"percentage": "50%", "condition": "Due upon delivery of final report"}
            ]
        }
    ],
    "risk_rules": [
        {
            "risk": "Implementation scope expected",
            "trigger_terms": ["build", "develop", "implement", "code", "install"],
            "recommended_fix": "Clarify that the scope of this engagement is strictly advisory, and any technical implementation or custom software development is excluded unless added via written change order."
        }
    ],
    "client_responsibilities": [
        "Access to stakeholders",
        "Timely delivery of internal metrics and assets",
        "Prompt feedback on drafts within 5 business days"
    ],
    "timeline_assumptions": [
        "Timelines depend on client providing inputs on schedule",
        "Delays in client feedback will extend deadlines accordingly"
    ],
    "acceptance_criteria": [
        "Deliverable documents submitted in PDF or agreed format",
        "Presentation of findings completed",
        "Client signs off on completion of milestones"
    ],
    "hidden_scope_traps": [
        "Advisory work being treated as implementation",
        "Undefined stakeholder availability",
        "Decision-making authority not assigned"
    ],
    "clause_library": {
        "revision": [
            "Each major deliverable includes up to two rounds of revisions unless otherwise specified.",
            "Additional revisions beyond the included rounds will be billed at our standard advisory rate of $150/hr."
        ],
        "payment": [
            "Invoices are payable within 7 business days from date of receipt.",
            "Timelines may pause if payments are delayed beyond the agreed schedule."
        ],
        "out_of_scope": [
            "Implementation support is excluded and may be scoped separately.",
            "Travel expenses and third-party tools are not included in the fixed fee."
        ],
        "client_responsibilities": [
            "Client will designate a single coordinator with authority to approve deliverables.",
            "Client must provide requested business data within 3 business days of request."
        ],
        "ip_ownership": [
            "Pre-existing materials remain the property of their respective creators.",
            "Ownership of the final custom advisory report transfers to the Client upon final payment receipt."
        ],
        "change_request": [
            "Scope changes require a formal written Change Order signed by both parties.",
            "No work on new scope items will begin prior to execution of a Change Order."
        ],
        "timeline": [
            "Project schedules are estimates and depend on client responsiveness.",
            "Delays of more than 10 business days in client inputs may result in project suspension."
        ]
    }
}

class TemplateService:
    """Service to load, validate, cache, and manage SOW industry templates."""
    
    def __init__(self, templates_dir: str = None):
        if not templates_dir:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(os.path.dirname(current_dir))
            templates_dir = os.path.join(backend_dir, "templates")
            
        self.templates_dir = templates_dir
        self._cache: Dict[str, SOWTemplate] = {}

    def _get_template_path(self, industry: str) -> str:
        filename = industry.lower().strip().replace(" ", "_").replace("&", "and") + ".json"
        return os.path.join(self.templates_dir, filename)

    def load_template(self, industry: str) -> SOWTemplate:
        """Loads and validates a template by industry name.
        Falls back to consulting.json on disk, and finally to hardcoded
        in-memory DEFAULT_CONSULTING_TEMPLATE if the template files are missing or unreadable.
        """
        normalized_industry = industry.strip()
        if normalized_industry in self._cache:
            return self._cache[normalized_industry]

        path = self._get_template_path(normalized_industry)
        try:
            if not os.path.exists(path):
                # Attempt to fallback to consulting.json
                path = os.path.join(self.templates_dir, "consulting.json")
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Template files missing at {self.templates_dir}")

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            template = SOWTemplate.model_validate(data)
            self._cache[normalized_industry] = template
            return template

        except Exception as e:
            logger.warning(
                f"Failed to load SOW template '{industry}' from disk (Error: {e}). "
                f"Falling back to hardcoded in-memory DEFAULT_CONSULTING_TEMPLATE."
            )
            try:
                # Use in-memory default consulting template
                template = SOWTemplate.model_validate(DEFAULT_CONSULTING_TEMPLATE)
                # Cache it for this requested industry so we don't repeat the warning/loading logic
                self._cache[normalized_industry] = template
                return template
            except Exception as validation_err:
                logger.critical(f"Hardcoded DEFAULT_CONSULTING_TEMPLATE validation failed: {validation_err}")
                raise validation_err

    def get_template(self, industry: str) -> SOWTemplate:
        """Convenience method alias for load_template."""
        return self.load_template(industry)

    def clear_cache(self):
        """Clears the in-memory template cache."""
        self._cache.clear()

