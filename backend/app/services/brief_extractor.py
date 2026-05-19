"""A2 — Brief Extractor

Transforms cleaned discovery-call signals (A1 output) into a precise commercial project brief.
Behaves like a senior agency strategist / discovery-call analyst.
"""

import json
from typing import Optional
from app.services.llm_client import LLMClient
from app.models.ai_schemas import (
    A1Output,
    BriefExtractorInput,
    BriefExtractorOutput,
    BriefDeliverable,
    BriefTimeline,
    BriefStakeholder,
    BriefBudget,
    BriefRevisionExpectations,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a senior agency brief strategist. Your job is to transform cleaned discovery-call signals into a precise commercial project brief. You are NOT writing the Statement of Work yet. You are preparing structured project intelligence for downstream scope-building agents.

Rules:
- Do not invent facts.
- Use "inferred" only when the inference is strongly supported by the transcript.
- Preserve uncertainty honestly.
- Separate confirmed, inferred, and unclear items.
- Extract: client goals, business context, deliverables, timeline, budget, stakeholders, dependencies, revision expectations, and required client assets.
- Identify missing information that must be clarified before sending a final SOW.
- Output valid JSON only. No markdown, no code fences, no commentary.

Output schema (all keys required, use empty strings / empty arrays where unknown):
{
  "client_goal": "",
  "business_context": "",
  "project_summary": "",
  "target_audience": [],
  "primary_objectives": [],
  "success_criteria": [],
  "deliverables": [
    {"name": "", "description": "", "status": "confirmed|inferred|unclear", "source_reasoning": ""}
  ],
  "timeline": {
    "mentioned_deadlines": [],
    "estimated_phases": [],
    "timeline_confidence": "high|medium|low",
    "unclear_timeline_items": []
  },
  "stakeholders": [
    {"name_or_role": "", "responsibility": "", "status": "confirmed|inferred|unclear"}
  ],
  "budget": {
    "budget_discussed": false,
    "budget_details": [],
    "payment_expectations": [],
    "budget_confidence": "high|medium|low"
  },
  "revision_expectations": {
    "revision_discussed": false,
    "details": [],
    "risk_if_missing": ""
  },
  "dependencies": [],
  "assets_needed_from_client": [],
  "agency_responsibilities": [],
  "client_responsibilities": [],
  "constraints": [],
  "assumptions": [],
  "missing_information": [],
  "brief_confidence_score": 0
}"""

MOCK_A2_OUTPUT = BriefExtractorOutput(
    client_goal="Refresh Luma Retail Co.'s brand identity and launch a modern Webflow marketing website.",
    business_context=(
        "The client is a retail business that wants stronger brand trust, "
        "clearer positioning, and a higher-converting digital presence."
    ),
    project_summary=(
        "The project includes brand strategy, logo identity development, "
        "brand guidelines, and an 8-page Webflow website."
    ),
    target_audience=[
        "Retail customers",
        "Online shoppers",
        "Potential brand partners",
    ],
    primary_objectives=[
        "Create a refreshed brand identity",
        "Build a professional Webflow website",
        "Improve customer trust and conversion",
    ],
    success_criteria=[
        "Brand identity approved by client",
        "Website launched successfully",
        "All core pages delivered",
        "Client receives usable brand guidelines",
    ],
    deliverables=[
        BriefDeliverable(
            name="Brand Strategy Workshop",
            description="A collaborative workshop to define positioning, visual direction, and brand goals.",
            status="confirmed",
            source_reasoning="Mentioned directly in discovery notes.",
        ),
        BriefDeliverable(
            name="Logo System",
            description="Logo design system with 3 initial concepts.",
            status="confirmed",
            source_reasoning="The client discussed logo concepts.",
        ),
        BriefDeliverable(
            name="Website Copywriting",
            description="Website copy for the 8-page site.",
            status="unclear",
            source_reasoning="Copy was mentioned, but responsibility was not confirmed.",
        ),
    ],
    timeline=BriefTimeline(
        mentioned_deadlines=["Client wants launch within 6 weeks"],
        estimated_phases=[
            "Discovery and strategy",
            "Brand identity design",
            "Website design",
            "Webflow development",
            "Review and launch",
        ],
        timeline_confidence="medium",
        unclear_timeline_items=["Final launch date not confirmed"],
    ),
    stakeholders=[
        BriefStakeholder(name_or_role="Founder", responsibility="Final approval", status="confirmed"),
        BriefStakeholder(name_or_role="Marketing Manager", responsibility="Content and marketing feedback", status="confirmed"),
    ],
    budget=BriefBudget(
        budget_discussed=True,
        budget_details=["Flexible budget mentioned, but no final amount confirmed"],
        payment_expectations=["Likely milestone-based payment"],
        budget_confidence="low",
    ),
    revision_expectations=BriefRevisionExpectations(
        revision_discussed=False,
        details=[],
        risk_if_missing="Undefined revision rounds may cause scope creep.",
    ),
    dependencies=[
        "Client must provide copy and images before website build",
    ],
    assets_needed_from_client=[
        "Website copy",
        "Product photography",
        "Brand references",
        "Existing logo or brand assets if available",
    ],
    agency_responsibilities=[
        "Brand strategy",
        "Logo design",
        "Brand guidelines",
        "Webflow website design and development",
    ],
    client_responsibilities=[
        "Provide content",
        "Provide photography",
        "Review deliverables",
        "Approve milestones",
    ],
    constraints=[
        "6-week preferred launch timeline",
        "Budget not finalized",
    ],
    assumptions=[
        "Website will be built in Webflow",
        "Client will provide final website copy unless copywriting is added to scope",
    ],
    missing_information=[
        "Final budget",
        "Revision rounds",
        "Copywriting responsibility",
        "Final launch date",
        "Hosting and maintenance expectations",
    ],
    brief_confidence_score=78,
)


class BriefExtractor:
    """A2 — Brief Extractor

    Consumes validated A1 output and produces a structured commercial project brief.
    """

    MAX_RETRIES = 2

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def extract(self, a1_output: A1Output, industry: str = "", tone: str = "") -> BriefExtractorOutput:
        """Run the A2 brief extraction step with retry logic."""
        logger.info("[A2] Brief extraction STARTED")

        # Validate input
        try:
            validated_input = BriefExtractorInput(
                a1_output=a1_output.model_dump(),
                industry=industry,
                tone=tone,
            )
            logger.info(f"[A2] Input validated: industry={validated_input.industry}")
        except Exception as e:
            logger.warning(f"[A2] Input validation warning: {e}, proceeding with defaults")
            validated_input = BriefExtractorInput(a1_output=a1_output.model_dump())

        # DEMO_MODE: return rich mock data immediately
        if self.llm.settings.demo_mode:
            logger.info("[A2] DEMO_MODE: returning rich mock A2 output")
            return self._apply_overrides(MOCK_A2_OUTPUT, a1_output)

        # Build prompt
        user_prompt = self._build_prompt(validated_input)

        # Call LLM with retries
        parsed: Optional[BriefExtractorOutput] = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                raw = await self.llm.chat_completion(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    model="gpt-4o",
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                parsed = self._parse_and_validate(raw)
                if parsed:
                    break
                logger.warning(f"[A2] Attempt {attempt}/{self.MAX_RETRIES}: validation failed, retrying")
            except Exception as e:
                logger.warning(f"[A2] Attempt {attempt}/{self.MAX_RETRIES}: LLM call failed: {e}")

        if parsed is None:
            logger.warning("[A2] All retries exhausted. Returning fallback brief.")
            parsed = self._fallback_output(validated_input)

        # Apply A1-derived overrides
        result = self._apply_overrides(parsed, a1_output)
        logger.info(
            f"[A2] Brief extraction COMPLETED: "
            f"objectives={len(result.primary_objectives)}, "
            f"deliverables={len(result.deliverables)} "
            f"(confirmed={sum(1 for d in result.deliverables if d.status == 'confirmed')}), "
            f"missing={len(result.missing_information)}, "
            f"confidence={result.brief_confidence_score}"
        )
        return result

    # ─── internals ─────────────────────────────

    def _build_prompt(self, inp: BriefExtractorInput) -> str:
        a1 = inp.a1_output
        parts = [
            "Cleaned discovery-call signals:",
            json.dumps(a1, indent=2, ensure_ascii=False)[:10000],
        ]
        if inp.industry:
            parts.append(f"\nIndustry context: {inp.industry}")
        if inp.tone:
            parts.append(f"Tone target: {inp.tone}")
        return "\n".join(parts)

    def _parse_and_validate(self, raw: str) -> Optional[BriefExtractorOutput]:
        """Parse LLM JSON response and validate against BriefExtractorOutput."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning(f"[A2] JSON decode error: {e}")
            return None

        try:
            # Ensure nested objects exist
            if "timeline" not in data or not isinstance(data["timeline"], dict):
                data["timeline"] = {}
            if "budget" not in data or not isinstance(data["budget"], dict):
                data["budget"] = {}
            if "revision_expectations" not in data or not isinstance(data["revision_expectations"], dict):
                data["revision_expectations"] = {}
            return BriefExtractorOutput.model_validate(data)
        except Exception as e:
            logger.warning(f"[A2] Pydantic validation error: {e}")
            return None

    def _fallback_output(self, inp: BriefExtractorInput) -> BriefExtractorOutput:
        """Construct a minimal but valid brief when LLM fails."""
        a1 = inp.a1_output
        summary = a1.get("cleaned_summary", "") if isinstance(a1, dict) else ""
        goals = a1.get("goals", []) if isinstance(a1, dict) else []
        deliverables = []
        for d in a1.get("mentioned_deliverables", []) if isinstance(a1, dict) else []:
            deliverables.append(BriefDeliverable(name=d, description="", status="inferred", source_reasoning="From A1 cleaner"))

        budget_confidence = "low"
        budget_details = []
        if a1.get("budget_mentions") if isinstance(a1, dict) else []:
            budget_details = a1.get("budget_mentions", [])
            budget_confidence = "medium"

        timeline_confidence = "low"
        mentioned_deadlines = []
        if a1.get("deadline_mentions") if isinstance(a1, dict) else []:
            mentioned_deadlines = a1.get("deadline_mentions", [])
            timeline_confidence = "medium"

        return BriefExtractorOutput(
            client_goal=summary[:200],
            business_context="",
            project_summary=summary[:500],
            primary_objectives=goals,
            deliverables=deliverables,
            timeline=BriefTimeline(
                mentioned_deadlines=mentioned_deadlines,
                timeline_confidence=timeline_confidence,
            ),
            budget=BriefBudget(
                budget_discussed=bool(budget_details),
                budget_details=budget_details,
                budget_confidence=budget_confidence,
            ),
            revision_expectations=BriefRevisionExpectations(
                revision_discussed=a1.get("raw_signals", {}).get("revision_discussed", False) if isinstance(a1, dict) else False,
                risk_if_missing="Undefined revision rounds may cause scope creep.",
            ),
            assets_needed_from_client=a1.get("client_responsibilities", []) if isinstance(a1, dict) else [],
            agency_responsibilities=a1.get("agency_responsibilities", []) if isinstance(a1, dict) else [],
            client_responsibilities=a1.get("client_responsibilities", []) if isinstance(a1, dict) else [],
            missing_information=["Brief extraction failed — manual review required"] + (a1.get("unclear_items", []) if isinstance(a1, dict) else []),
            brief_confidence_score=30,
        )

    def _apply_overrides(self, output: BriefExtractorOutput, a1: A1Output) -> BriefExtractorOutput:
        """Enrich brief with A1-derived context that A2 may not explicitly output."""
        data = output.model_dump()
        # Promote A1 project_type if A2 left client_goal empty
        if not data.get("client_goal") and a1.project_type:
            data["client_goal"] = f"{a1.project_type} for {a1.client_name or 'the client'}."
        if not data.get("project_summary") and a1.cleaned_summary:
            data["project_summary"] = a1.cleaned_summary
        # Inherit A1 responsibilities if A2 didn't fill them
        if not data.get("client_responsibilities") and a1.client_responsibilities:
            data["client_responsibilities"] = a1.client_responsibilities
        if not data.get("agency_responsibilities") and a1.agency_responsibilities:
            data["agency_responsibilities"] = a1.agency_responsibilities
        if not data.get("dependencies") and a1.dependencies:
            data["dependencies"] = a1.dependencies
        return BriefExtractorOutput.model_validate(data)
