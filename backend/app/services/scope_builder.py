"""A3 — Scope Builder

Transforms structured brief data into precise commercial scope language.
Behaves like a senior agency scope strategist / scope creep prevention expert.
"""

import json
from typing import Optional
from app.services.llm_client import LLMClient
from app.models.ai_schemas import (
    ScopeBuilderInput,
    ScopeBuilderOutput,
    CommercialScopeItem,
    DeliverableSpec,
    AmbiguityFlag,
    BriefExtractorOutput,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a senior agency scope strategist. Your job is to convert a structured project brief into precise commercial scope language that can later be used inside a Statement of Work.

You are NOT writing the final SOW yet.

Rules:
- Do not invent hard facts.
- You may make commercially standard assumptions only when clearly marked as inferred.
- Convert vague deliverables into specific bounded deliverables.
- Add limits where needed: page count, revision boundaries, asset responsibility, platform, format, timeline assumptions.
- Identify what is included and not included.
- Separate agency responsibilities from client responsibilities.
- Flag ambiguity that could cause scope creep.
- Output valid JSON only. No markdown, no code fences, no commentary.

Scope Writing Rules:
For each deliverable:
- state what will be produced
- state quantity/limit if available
- state format/platform if available
- state what is included
- state what is excluded
- state dependency on client inputs
- state acceptance/completion criteria

Output schema (all keys required, use empty strings / empty arrays where unknown):
{
  "scope_summary": "",
  "commercial_scope_items": [
    {
      "title": "",
      "description": "",
      "included_work": [],
      "not_included": [],
      "dependencies": [],
      "client_inputs_required": [],
      "acceptance_expectations": [],
      "status": "confirmed|inferred|unclear",
      "scope_confidence": "high|medium|low"
    }
  ],
  "deliverable_specifications": [
    {
      "deliverable_name": "",
      "professional_scope_statement": "",
      "quantity_or_limit": "",
      "format_or_platform": "",
      "included_components": [],
      "excluded_components": [],
      "completion_criteria": [],
      "source_status": "confirmed|inferred|unclear"
    }
  ],
  "implementation_boundaries": [],
  "client_responsibility_boundaries": [],
  "agency_responsibility_boundaries": [],
  "assumptions_for_scope": [],
  "scope_exclusions": [],
  "scope_dependencies": [],
  "ambiguity_flags": [
    {"item": "", "why_it_matters": "", "suggested_clarification": "", "severity": "high|medium|low"}
  ],
  "scope_confidence_score": 0,
  "scope_of_work": [],
  "deliverables": [],
  "timeline": [],
  "payment_schedule": []
}"""

MOCK_A3_OUTPUT = ScopeBuilderOutput(
    scope_summary="The project scope includes brand strategy, visual identity development, brand guidelines, and design/development of an 8-page Webflow marketing website for Luma Retail Co.",
    commercial_scope_items=[
        CommercialScopeItem(
            title="Brand Identity Development",
            description="Develop a refreshed brand identity system for Luma Retail Co., including strategic direction, logo exploration, and foundational brand guidelines.",
            included_work=[
                "Brand strategy workshop",
                "Visual direction exploration",
                "Logo system development",
                "Up to 3 initial logo concepts",
                "Final logo refinement",
                "Brand guidelines document",
            ],
            not_included=[
                "Naming strategy",
                "Full packaging design",
                "Ongoing brand management",
            ],
            dependencies=[
                "Client must provide brand references and existing brand assets",
            ],
            client_inputs_required=[
                "Brand references",
                "Existing logo files if available",
                "Stakeholder feedback",
            ],
            acceptance_expectations=[
                "Final approved logo system",
                "Brand guidelines delivered in PDF format",
            ],
            status="confirmed",
            scope_confidence="high",
        ),
        CommercialScopeItem(
            title="Webflow Website Design and Development",
            description="Design and develop an 8-page responsive marketing website in Webflow, including core standard pages and up to three additional standard content pages.",
            included_work=[
                "Responsive website design",
                "Webflow development",
                "Up to 8 total website pages",
                "Basic on-page SEO structure",
                "Contact form setup",
                "CMS setup if required for standard content sections",
            ],
            not_included=[
                "Website copywriting unless separately approved",
                "Product photography",
                "Advanced custom animations",
                "Complex third-party integrations",
                "Ongoing website maintenance",
            ],
            dependencies=[
                "Client must provide final website copy",
                "Client must provide product images or photography",
                "Client must approve brand direction before website design begins",
            ],
            client_inputs_required=[
                "Website copy",
                "Product photography",
                "Domain and hosting access if needed",
                "Business contact details",
            ],
            acceptance_expectations=[
                "Website is responsive across desktop and mobile",
                "All approved pages are published or ready for launch in Webflow",
                "Contact form is tested",
            ],
            status="confirmed",
            scope_confidence="medium",
        ),
    ],
    deliverable_specifications=[
        DeliverableSpec(
            deliverable_name="8-page Webflow Website",
            professional_scope_statement="Design and develop an 8-page responsive Webflow marketing website including Home, About, Services, Case Studies, Contact, and up to three additional standard content pages.",
            quantity_or_limit="Up to 8 pages",
            format_or_platform="Webflow",
            included_components=[
                "Responsive page layouts",
                "Core marketing pages",
                "Contact form setup",
                "Basic SEO metadata structure",
            ],
            excluded_components=[
                "Copywriting",
                "Photography",
                "Advanced animations",
                "Custom backend functionality",
            ],
            completion_criteria=[
                "All approved pages are built in Webflow",
                "Site is responsive",
                "Client approves final preview",
            ],
            source_status="confirmed",
        ),
    ],
    implementation_boundaries=[
        "Website scope is limited to 8 standard marketing pages.",
        "Advanced integrations or custom backend functionality are excluded unless separately scoped.",
        "Copywriting and photography are excluded unless explicitly added.",
    ],
    client_responsibility_boundaries=[
        "Client is responsible for providing final website copy.",
        "Client is responsible for providing photography and product images.",
        "Client is responsible for timely feedback and approvals.",
    ],
    agency_responsibility_boundaries=[
        "Agency is responsible for brand strategy, logo design, brand guidelines, website design, and Webflow development.",
        "Agency is responsible for implementing approved content and assets into the website.",
    ],
    assumptions_for_scope=[
        "Client will provide content and assets before the website build phase.",
        "Website pages are standard marketing pages and do not require custom application logic.",
    ],
    scope_exclusions=[
        "Copywriting",
        "Photography",
        "Advanced custom animations",
        "Third-party integrations",
        "Post-launch maintenance",
    ],
    scope_dependencies=[
        "Final content must be provided before Webflow development.",
        "Brand approval is required before website design begins.",
    ],
    ambiguity_flags=[
        AmbiguityFlag(
            item="Copywriting responsibility",
            why_it_matters="If copywriting is not assigned, website delivery may be delayed or additional work may be expected from the agency.",
            suggested_clarification="Confirm whether the client will provide final website copy or whether copywriting should be added as a paid deliverable.",
            severity="high",
        ),
        AmbiguityFlag(
            item="Revision rounds",
            why_it_matters="Undefined revision rounds can lead to unlimited design changes and scope creep.",
            suggested_clarification="Define the number of included revision rounds for brand and website deliverables.",
            severity="high",
        ),
    ],
    scope_confidence_score=82,
    scope_of_work=[
        "Brand strategy workshop",
        "Visual direction exploration",
        "Logo system development (up to 3 concepts)",
        "Brand guidelines document",
        "Responsive website design",
        "Webflow development (up to 8 pages)",
        "Contact form setup",
        "Basic SEO structure",
    ],
    deliverables=[
        "Brand strategy workshop",
        "Logo system with up to 3 concepts",
        "Brand guidelines",
        "8-page Webflow website",
        "Responsive page layouts",
    ],
    timeline=[
        "Brand strategy and discovery",
        "Brand identity design",
        "Website design",
        "Webflow development",
        "Review and launch",
    ],
    payment_schedule=["Milestone-based payment structure"],
)


class ScopeBuilder:
    """A3 — Scope Builder

    Consumes validated A2 brief and produces precise commercial scope language.
    """

    MAX_RETRIES = 2

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def build(self, brief: BriefExtractorOutput, industry: str = "", tone: str = "") -> ScopeBuilderOutput:
        """Run the A3 scope building step with retry logic."""
        logger.info("[A3] Scope builder STARTED")

        # Validate input
        try:
            validated_input = ScopeBuilderInput(
                brief=brief.model_dump(),
                industry=industry,
                tone=tone,
            )
            logger.info(f"[A3] Input validated: industry={validated_input.industry}, tone={validated_input.tone}")
        except Exception as e:
            logger.warning(f"[A3] Input validation warning: {e}, proceeding with defaults")
            validated_input = ScopeBuilderInput(brief=brief.model_dump())

        # DEMO_MODE: return rich mock data immediately
        if self.llm.settings.demo_mode:
            logger.info("[A3] DEMO_MODE: returning rich mock A3 output")
            return MOCK_A3_OUTPUT

        # Build prompt
        user_prompt = self._build_prompt(validated_input)

        # Call LLM with retries
        parsed: Optional[ScopeBuilderOutput] = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                raw = await self.llm.chat_completion(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    model="gpt-4o",
                    temperature=0.3,
                    response_format={"type": "json_object"},
                )
                parsed = self._parse_and_validate(raw)
                if parsed:
                    break
                logger.warning(f"[A3] Attempt {attempt}/{self.MAX_RETRIES}: validation failed, retrying")
            except Exception as e:
                logger.warning(f"[A3] Attempt {attempt}/{self.MAX_RETRIES}: LLM call failed: {e}")

        if parsed is None:
            logger.warning("[A3] All retries exhausted. Returning fallback scope.")
            parsed = self._fallback_output(brief)

        # Derive backward-compat fields from rich output
        result = self._derive_compat_fields(parsed)
        logger.info(
            f"[A3] Scope builder COMPLETED: "
            f"items={len(result.commercial_scope_items)}, "
            f"specs={len(result.deliverable_specifications)}, "
            f"ambiguity={len(result.ambiguity_flags)}, "
            f"confidence={result.scope_confidence_score}"
        )
        return result

    # ─── internals ─────────────────────────────

    def _build_prompt(self, inp: ScopeBuilderInput) -> str:
        parts = [
            "Structured project brief:",
            json.dumps(inp.brief, indent=2, ensure_ascii=False)[:12000],
        ]
        if inp.industry:
            parts.append(f"\nIndustry context: {inp.industry}")
            try:
                from app.services.ai_data_service import AIDataService
                ai_data = AIDataService()
                template = ai_data.get_industry_template(inp.industry)
                parts.append("\nStandard Industry Scope Recommendations:")
                parts.append(f"Standard Deliverables: {json.dumps(template.standard_deliverables)}")
                parts.append(f"Common Out-of-Scope Items (Exclusions): {json.dumps(template.common_out_of_scope_items)}")
                parts.append(f"Hidden Scope Traps To Prevent: {json.dumps(template.hidden_scope_traps)}")
            except Exception as e:
                logger.warning(f"[A3] Failed to load template context for prompt enrichment: {e}")
        if inp.tone:
            parts.append(f"Tone target: {inp.tone}")
        return "\n".join(parts)

    def _parse_and_validate(self, raw: str) -> Optional[ScopeBuilderOutput]:
        """Parse LLM JSON response and validate against ScopeBuilderOutput."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning(f"[A3] JSON decode error: {e}")
            return None

        try:
            # Ensure nested lists exist
            for key in ["commercial_scope_items", "deliverable_specifications", "ambiguity_flags"]:
                if key not in data or not isinstance(data[key], list):
                    data[key] = []
            for key in ["scope_of_work", "deliverables", "timeline", "payment_schedule"]:
                if key not in data or not isinstance(data[key], list):
                    data[key] = []
            return ScopeBuilderOutput.model_validate(data)
        except Exception as e:
            logger.warning(f"[A3] Pydantic validation error: {e}")
            return None

    def _fallback_output(self, brief: BriefExtractorOutput) -> ScopeBuilderOutput:
        """Construct a minimal but valid scope when LLM fails."""
        scope_items = []
        for d in brief.deliverables:
            scope_items.append(CommercialScopeItem(
                title=d.name,
                description=d.description,
                status=d.status,
                scope_confidence="low",
                included_work=[d.name] if d.name else [],
            ))

        ambiguity = []
        for missing in brief.missing_information[:5]:
            ambiguity.append(AmbiguityFlag(
                item=missing,
                why_it_matters="Information missing from discovery call.",
                suggested_clarification="Clarify with client before finalizing SOW.",
                severity="medium",
            ))

        return ScopeBuilderOutput(
            scope_summary=brief.project_summary[:300],
            commercial_scope_items=scope_items,
            scope_of_work=brief.agency_responsibilities,
            deliverables=[d.name for d in brief.deliverables],
            timeline=brief.timeline.mentioned_deadlines + brief.timeline.estimated_phases,
            payment_schedule=brief.budget.payment_expectations,
            assumptions_for_scope=brief.assumptions,
            scope_exclusions=[],
            scope_dependencies=brief.dependencies,
            ambiguity_flags=ambiguity,
            client_responsibility_boundaries=brief.client_responsibilities,
            agency_responsibility_boundaries=brief.agency_responsibilities,
            scope_confidence_score=40,
        )

    def _derive_compat_fields(self, output: ScopeBuilderOutput) -> ScopeBuilderOutput:
        """Ensure backward-compat fields are populated from rich fields."""
        data = output.model_dump()
        # Derive scope_of_work from commercial_scope_items if empty
        if not data.get("scope_of_work"):
            scope_work = []
            for item in data.get("commercial_scope_items", []):
                scope_work.extend(item.get("included_work", []))
            data["scope_of_work"] = scope_work
        # Derive deliverables from deliverable_specifications if empty
        if not data.get("deliverables"):
            specs = data.get("deliverable_specifications", [])
            data["deliverables"] = [s.get("deliverable_name", "") for s in specs if s.get("deliverable_name")]
        # Derive timeline from scope_summary + estimated_phases hints
        if not data.get("timeline"):
            # Try to extract phases from ambiguity or scope items
            timeline = []
            for item in data.get("commercial_scope_items", []):
                if item.get("title"):
                    timeline.append(item["title"])
            data["timeline"] = timeline
        return ScopeBuilderOutput.model_validate(data)
