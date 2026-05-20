import json
from typing import Optional
from app.services.llm_client import LLMClient
from app.models.ai_schemas import A1Input, A1Output, RawSignals
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a senior agency discovery-call analyst.
Your job is to clean messy client call notes and extract only commercially relevant project information.
You are NOT writing the SOW yet. You are preparing clean structured input for later agents.

Rules:
- Do not invent missing details.
- Preserve uncertainty.
- Extract exact useful facts.
- Separate confirmed details from unclear items.
- Detect budget, timeline, deliverables, goals, and risks.
- Ignore greetings, small talk, filler words, and repeated statements.
- If something is vague, place it in unclear_items.
- Output valid JSON only. No markdown, no code fences, no commentary.

Output schema (all keys required, use empty strings / empty arrays where unknown):
{
  "client_name": "",
  "project_name": "",
  "project_type": "",
  "cleaned_summary": "",
  "goals": [],
  "mentioned_deliverables": [],
  "budget_mentions": [],
  "deadline_mentions": [],
  "stakeholders": [],
  "client_responsibilities": [],
  "agency_responsibilities": [],
  "dependencies": [],
  "tools_or_platforms": [],
  "confirmed_items": [],
  "unclear_items": [],
  "potential_risks": [],
  "raw_signals": {
    "pricing_discussed": false,
    "timeline_discussed": false,
    "revision_discussed": false,
    "content_responsibility_discussed": false,
    "launch_date_discussed": false
  }
}"""

MOCK_A1_OUTPUT = A1Output(
    client_name="Luma Retail Co.",
    project_name="Brand Identity + Webflow Website",
    project_type="Brand Identity and Website Design",
    cleaned_summary=(
        "The client wants a refreshed brand identity and an 8-page Webflow marketing website "
        "for a retail business. They discussed logo concepts, brand guidelines, launch timeline, "
        "and a phased payment structure."
    ),
    goals=[
        "Refresh brand identity",
        "Launch a modern marketing website",
        "Improve trust and conversion for retail customers",
    ],
    mentioned_deliverables=[
        "Brand strategy workshop",
        "Logo system with 3 initial concepts",
        "Brand guidelines",
        "8-page Webflow website",
    ],
    budget_mentions=[
        "Client mentioned a flexible budget but no final amount confirmed",
    ],
    deadline_mentions=[
        "Client wants launch within 6 weeks",
    ],
    stakeholders=[
        "Founder",
        "Marketing manager",
    ],
    client_responsibilities=[
        "Provide brand references",
        "Provide website copy",
        "Provide product photography",
    ],
    agency_responsibilities=[
        "Brand strategy",
        "Logo design",
        "Webflow design and development",
    ],
    dependencies=[
        "Client must provide copy and images before website build",
    ],
    tools_or_platforms=[
        "Webflow",
    ],
    confirmed_items=[
        "8-page website",
        "Brand identity required",
        "Webflow platform",
    ],
    unclear_items=[
        "Copywriting responsibility not confirmed",
        "Revision rounds not discussed",
        "Final project budget not confirmed",
    ],
    potential_risks=[
        "Content delays may affect launch timeline",
        "Undefined revisions may cause scope creep",
    ],
    raw_signals=RawSignals(
        pricing_discussed=True,
        timeline_discussed=True,
        revision_discussed=False,
        content_responsibility_discussed=False,
        launch_date_discussed=True,
    ),
)


class TranscriptCleaner:
    """A1 — Transcript Cleaner

    Accepts messy call transcripts or rough notes.
    Returns structured project signals (A1Output).
    """

    MAX_RETRIES = 2

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def clean(self, raw_text: str, **kwargs) -> A1Output:
        """Run the A1 cleaning step with retry logic."""
        logger.info("[A1] Transcript cleaning STARTED")

        # Validate input
        try:
            validated_input = A1Input(raw_transcript=raw_text, **kwargs)
            logger.info(f"[A1] Input validated: industry={validated_input.industry}, tone={validated_input.tone}")
        except Exception as e:
            logger.warning(f"[A1] Input validation warning: {e}, proceeding with defaults")
            validated_input = A1Input(raw_transcript=raw_text)

        # DEMO_MODE: return rich mock data immediately
        if self.llm.settings.demo_mode:
            logger.info("[A1] DEMO_MODE: returning rich mock A1 output")
            return self._apply_overrides(MOCK_A1_OUTPUT, validated_input)

        if not self.llm.settings.openai_api_key and not self.llm.settings.anthropic_api_key:
            logger.warning("[A1] No provider keys configured. Returning fallback A1 output.")
            parsed = self._fallback_output(validated_input)
            result = self._apply_overrides(parsed, validated_input)
            logger.info(
                f"[A1] Transcript cleaning COMPLETED: "
                f"client={result.client_name}, "
                f"deliverables={len(result.mentioned_deliverables)}, "
                f"unclear={len(result.unclear_items)}, "
                f"risks={len(result.potential_risks)}"
            )
            return result

        # Build prompt
        user_prompt = self._build_prompt(validated_input)

        # Call LLM with retries
        parsed: Optional[A1Output] = None
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
                logger.warning(f"[A1] Attempt {attempt}/{self.MAX_RETRIES}: validation failed, retrying")
            except Exception as e:
                logger.warning(f"[A1] Attempt {attempt}/{self.MAX_RETRIES}: LLM call failed: {e}")

        if parsed is None:
            logger.warning("[A1] All retries exhausted. Returning fallback A1 output.")
            parsed = self._fallback_output(validated_input)

        # Apply user overrides
        result = self._apply_overrides(parsed, validated_input)
        logger.info(
            f"[A1] Transcript cleaning COMPLETED: "
            f"client={result.client_name}, "
            f"deliverables={len(result.mentioned_deliverables)}, "
            f"unclear={len(result.unclear_items)}, "
            f"risks={len(result.potential_risks)}"
        )
        return result

    # ─── internals ─────────────────────────────

    def _build_prompt(self, inp: A1Input) -> str:
        parts = [f"Raw transcript:\n{inp.raw_transcript[:12000]}"]
        if inp.industry:
            parts.append(f"\nIndustry context: {inp.industry}")
        if inp.tone:
            parts.append(f"Tone target: {inp.tone}")
        if inp.client_name:
            parts.append(f"Pre-known client: {inp.client_name}")
        if inp.project_name:
            parts.append(f"Pre-known project: {inp.project_name}")
        return "\n".join(parts)

    def _parse_and_validate(self, raw: str) -> Optional[A1Output]:
        """Parse LLM JSON response and validate against A1Output."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning(f"[A1] JSON decode error: {e}")
            return None

        try:
            # Ensure raw_signals exists
            if "raw_signals" not in data or not isinstance(data["raw_signals"], dict):
                data["raw_signals"] = {}
            return A1Output.model_validate(data)
        except Exception as e:
            logger.warning(f"[A1] Pydantic validation error: {e}")
            return None

    def _fallback_output(self, inp: A1Input) -> A1Output:
        """Construct a minimal but valid A1Output from raw text when LLM fails."""
        text = inp.raw_transcript
        budget_hints = [w for w in ["$", "k", "budget", "cost", "price", "fee"] if w in text.lower()]
        timeline_hints = [w for w in ["week", "month", "day", "q1", "q2", "q3", "q4", "deadline", "timeline"] if w in text.lower()]
        return A1Output(
            client_name=inp.client_name,
            project_name=inp.project_name,
            project_type="",
            cleaned_summary=text[:500] + ("..." if len(text) > 500 else ""),
            goals=[],
            mentioned_deliverables=[],
            budget_mentions=[] if not budget_hints else ["Budget discussed (extract failed - manual review needed)"],
            deadline_mentions=[] if not timeline_hints else ["Timeline discussed (extract failed - manual review needed)"],
            stakeholders=[],
            client_responsibilities=[],
            agency_responsibilities=[],
            dependencies=[],
            tools_or_platforms=[],
            confirmed_items=[],
            unclear_items=["Extract failed due to LLM error - review transcript manually"],
            potential_risks=["Could not automatically assess risks from transcript"],
            raw_signals=RawSignals(
                pricing_discussed=bool(budget_hints),
                timeline_discussed=bool(timeline_hints),
            ),
        )

    def _apply_overrides(self, output: A1Output, inp: A1Input) -> A1Output:
        """Apply user-provided client_name / project_name over LLM-detected values."""
        data = output.model_dump()
        if inp.client_name:
            data["client_name"] = inp.client_name
        if inp.project_name:
            data["project_name"] = inp.project_name
        return A1Output.model_validate(data)
