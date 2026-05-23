"""A4 — Scope Creep Risk Detector

Analyzes A1+A2+A3 outputs to identify risks that could cause scope creep,
delivery confusion, payment disputes, timeline delays, and hidden work expectations.
Behaves like a senior agency operations lead / scope creep prevention expert.
"""

import json
from typing import Optional
from app.services.llm_client import LLMClient
from app.models.ai_schemas import (
    RiskDetectorInput,
    RiskDetectorOutput,
    ScopeCreepRisk,
    RiskFlagData,
    A1Output,
    BriefExtractorOutput,
    ScopeBuilderOutput,
)
from app.utils.logger import get_logger
from app.services.scope_risk_rules import detect_rule_based_risks, risks_to_flags

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a senior agency scope-risk analyst and scope creep prevention strategist.

Your job is to analyze project discovery-call outputs and identify commercial, operational, and delivery risks that could cause:
- scope creep
- unclear expectations
- timeline delays
- payment disputes
- revision abuse
- technical misunderstandings
- stakeholder confusion

You are NOT writing the final SOW yet.

Rules:
- Detect implied risk, not only explicit risk.
- Cross-reference all prior pipeline outputs.
- Identify missing definitions and unclear ownership.
- Explain WHY each risk matters commercially.
- Suggest practical fixes.
- Suggest contract language recommendations where appropriate.
- Preserve uncertainty honestly.
- Do not hallucinate unsupported facts.
- Output valid JSON only. No markdown, no code fences, no commentary.

Output schema (all keys required, use empty strings / empty arrays where unknown):
{
  "overall_risk_score": 0,
  "overall_risk_level": "low|medium|high",
  "risk_summary": "",
  "scope_creep_risks": [
    {
      "id": "",
      "title": "",
      "description": "",
      "category": "timeline|revisions|deliverables|content|integrations|approvals|budget|technical|communication|ownership|maintenance|legal|other",
      "severity": "low|medium|high",
      "likelihood": "low|medium|high",
      "impact": "low|medium|high",
      "why_it_matters": "",
      "evidence": [],
      "recommended_fix": "",
      "recommended_contract_language": "",
      "requires_client_clarification": true,
      "blocking_risk": false
    }
  ],
  "missing_scope_definitions": [],
  "unclear_responsibilities": [],
  "timeline_risks": [],
  "technical_risks": [],
  "revision_risks": [],
  "dependency_risks": [],
  "payment_risks": [],
  "stakeholder_risks": [],
  "recommended_followup_questions": [],
  "critical_missing_items": [],
  "risk_prevention_recommendations": [],
  "risk_detection_confidence_score": 0,
  "risk_flags": []
}"""

MOCK_A4_OUTPUT = RiskDetectorOutput(
    overall_risk_score=78,
    overall_risk_level="high",
    risk_summary="Several important scope and delivery expectations remain undefined, particularly around content ownership, revisions, advanced website functionality, and launch approval responsibilities.",
    scope_creep_risks=[
        ScopeCreepRisk(
            id="risk_copywriting_001",
            title="Copywriting Responsibility Undefined",
            description="Website copywriting was referenced during the discovery discussion, but ownership was not clearly assigned.",
            category="content",
            severity="high",
            likelihood="high",
            impact="high",
            why_it_matters="Undefined content ownership commonly delays website projects and creates unpaid copywriting expectations.",
            evidence=[
                "Client discussed website pages but no confirmed copy provider exists.",
                "A3 excluded copywriting from confirmed deliverables.",
            ],
            recommended_fix="Explicitly define whether the client or agency is responsible for website copywriting.",
            recommended_contract_language="Client will provide final approved website copy unless copywriting services are separately added to scope.",
            requires_client_clarification=True,
            blocking_risk=True,
        ),
        ScopeCreepRisk(
            id="risk_revision_002",
            title="Revision Rounds Not Defined",
            description="The number of included revision rounds has not been discussed or documented.",
            category="revisions",
            severity="high",
            likelihood="high",
            impact="high",
            why_it_matters="Undefined revisions frequently lead to unlimited feedback loops and scope expansion.",
            evidence=[
                "A2 revision expectations were missing.",
                "No revision limits defined in A3 scope.",
            ],
            recommended_fix="Define the number of included revisions for each deliverable.",
            recommended_contract_language="Each major deliverable includes up to two rounds of revisions unless otherwise specified.",
            requires_client_clarification=True,
            blocking_risk=False,
        ),
        ScopeCreepRisk(
            id="risk_animation_003",
            title="Vague Animation Request",
            description="Client mentioned 'maybe some animations' without specifying scope, quantity, or complexity.",
            category="deliverables",
            severity="medium",
            likelihood="high",
            impact="medium",
            why_it_matters="Vague animation expectations can expand into complex motion design work not priced into the scope.",
            evidence=[
                "Discovery notes referenced animations without specification.",
                "A3 scope did not include animation deliverables.",
            ],
            recommended_fix="Clarify whether animations are required and define quantity/complexity limits.",
            recommended_contract_language="Animations beyond basic transitions are excluded unless separately scoped and approved.",
            requires_client_clarification=True,
            blocking_risk=False,
        ),
        ScopeCreepRisk(
            id="risk_integration_004",
            title="Third-party Integrations Undefined",
            description="Possible integrations were mentioned but not specified in scope.",
            category="integrations",
            severity="medium",
            likelihood="medium",
            impact="high",
            why_it_matters="Unspecified integrations can require significant additional development effort and delay delivery.",
            evidence=[
                "Discovery notes hinted at integrations without naming specific platforms.",
            ],
            recommended_fix="List all required integrations explicitly and scope their implementation effort.",
            recommended_contract_language="Third-party integrations are excluded unless explicitly listed in the approved scope.",
            requires_client_clarification=True,
            blocking_risk=False,
        ),
        ScopeCreepRisk(
            id="risk_launch_005",
            title="Launch Date Not Finalized",
            description="A target timeline was discussed but no firm launch date or approval milestone was set.",
            category="timeline",
            severity="medium",
            likelihood="high",
            impact="medium",
            why_it_matters="Without a firm launch date, stakeholders may delay approvals indefinitely and compress the build phase.",
            evidence=[
                "A2 timeline confidence was marked as medium.",
                "A3 scope did not include a firm go-live milestone.",
            ],
            recommended_fix="Set a target launch date with internal and external milestone checkpoints.",
            recommended_contract_language="Target launch date will be confirmed within 5 business days of SOW approval. Delays caused by client feedback will extend the timeline accordingly.",
            requires_client_clarification=True,
            blocking_risk=False,
        ),
        ScopeCreepRisk(
            id="risk_stakeholder_006",
            title="Approval Authority Unclear",
            description="Multiple stakeholders were mentioned but final approval authority was not defined.",
            category="approvals",
            severity="medium",
            likelihood="medium",
            impact="medium",
            why_it_matters="Unclear approval chains cause design-by-committee delays and conflicting feedback.",
            evidence=[
                "A2 listed stakeholders but did not define decision-maker.",
            ],
            recommended_fix="Designate a single point of contact with final approval authority.",
            recommended_contract_language="Client will designate a single point of contact with final approval authority. Feedback from other stakeholders must be consolidated by this contact.",
            requires_client_clarification=True,
            blocking_risk=False,
        ),
    ],
    missing_scope_definitions=[
        "Revision limits",
        "Copywriting ownership",
        "Hosting responsibility",
        "Post-launch maintenance expectations",
    ],
    unclear_responsibilities=[
        "Who provides final website copy",
        "Who manages hosting setup",
    ],
    timeline_risks=["Launch date discussed but not finalized"],
    technical_risks=["Possible animations mentioned without implementation definition"],
    revision_risks=["Unlimited revisions risk"],
    dependency_risks=["Website launch depends on client-delivered content"],
    payment_risks=["No formal milestone payment structure discussed"],
    stakeholder_risks=["Final approval authority not clearly defined"],
    recommended_followup_questions=[
        "Will the client provide final website copy?",
        "How many revision rounds should be included?",
        "Are advanced animations required?",
        "Who will manage hosting after launch?",
    ],
    critical_missing_items=[
        "Revision policy",
        "Content ownership",
        "Launch approval process",
    ],
    risk_prevention_recommendations=[
        "Add explicit revision limits.",
        "Define excluded work clearly.",
        "Require milestone approvals before moving phases.",
        "Define ownership of copy, hosting, and integrations.",
    ],
    risk_detection_confidence_score=90,
    risk_flags=[
        RiskFlagData(severity="high", title="Copywriting Responsibility Undefined", description="Content ownership not clearly assigned.", suggested_fix="Define copywriting responsibility in SOW."),
        RiskFlagData(severity="high", title="Revision Rounds Not Defined", description="Unlimited revision risk.", suggested_fix="Set revision limits per deliverable."),
        RiskFlagData(severity="medium", title="Vague Animation Request", description="Animations mentioned without scope.", suggested_fix="Clarify animation requirements."),
    ],
)


class RiskDetector:
    """A4 — Scope Creep Risk Detector

    Analyzes all prior pipeline outputs (A1+A2+A3) to identify scope-creep risks.
    """

    MAX_RETRIES = 2

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def detect(
        self,
        a1: A1Output,
        a2: BriefExtractorOutput,
        a3: ScopeBuilderOutput,
        industry: str = "",
        tone: str = "",
    ) -> RiskDetectorOutput:
        """Run the A4 risk detection step with retry logic."""
        logger.info("[A4] Risk detection STARTED")

        # Validate input
        try:
            validated_input = RiskDetectorInput(
                a1_output=a1.model_dump(),
                a2_output=a2.model_dump(),
                a3_output=a3.model_dump(),
                industry=industry,
                tone=tone,
            )
            logger.info(f"[A4] Input validated: industry={validated_input.industry}, tone={validated_input.tone}")
        except Exception as e:
            logger.warning(f"[A4] Input validation warning: {e}, proceeding with defaults")
            validated_input = RiskDetectorInput(a1_output={}, a2_output={}, a3_output={})

        # DEMO_MODE: return rich mock data immediately
        if self.llm.settings.demo_mode:
            logger.info("[A4] DEMO_MODE: returning rich mock A4 output")
            return MOCK_A4_OUTPUT

        # Build prompt
        user_prompt = self._build_prompt(validated_input)

        # Call LLM with retries
        parsed: Optional[RiskDetectorOutput] = None
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
                logger.warning(f"[A4] Attempt {attempt}/{self.MAX_RETRIES}: validation failed, retrying")
            except Exception as e:
                logger.warning(f"[A4] Attempt {attempt}/{self.MAX_RETRIES}: LLM call failed: {e}")

        if parsed is None:
            logger.warning("[A4] All retries exhausted. Returning fallback risk output.")
            parsed = self._fallback_output(a1, a2, a3)

        # Derive backward-compat risk_flags from rich scope_creep_risks
        result = self._apply_rule_engine(self._derive_compat_fields(parsed), a1, a2, a3)
        logger.info(
            f"[A4] Risk detection COMPLETED: "
            f"score={result.overall_risk_score}, "
            f"level={result.overall_risk_level}, "
            f"risks={len(result.scope_creep_risks)}, "
            f"blocking={sum(1 for r in result.scope_creep_risks if r.blocking_risk)}, "
            f"confidence={result.risk_detection_confidence_score}"
        )
        return result

    # ─── internals ─────────────────────────────

    def _build_prompt(self, inp: RiskDetectorInput) -> str:
        parts = [
            "Analyze the following project discovery outputs for scope creep and delivery risks.",
            "",
            "=== A1 — Transcript Signals ===",
            json.dumps(inp.a1_output, indent=2, ensure_ascii=False)[:5000],
            "",
            "=== A2 — Extracted Brief ===",
            json.dumps(inp.a2_output, indent=2, ensure_ascii=False)[:5000],
            "",
            "=== A3 — Commercial Scope ===",
            json.dumps(inp.a3_output, indent=2, ensure_ascii=False)[:5000],
        ]
        if inp.industry:
            parts.append(f"\nIndustry context: {inp.industry}")
            try:
                from app.services.ai_data_service import AIDataService
                ai_data = AIDataService()
                risk_rules = ai_data.get_risk_rules(inp.industry)
                parts.append("\nStandard Industry Risk Evaluation Rules:")
                parts.append(json.dumps([r.model_dump() for r in risk_rules]))
            except Exception as e:
                logger.warning(f"[A4] Failed to load risk rules for prompt enrichment: {e}")
        if inp.tone:
            parts.append(f"Tone target: {inp.tone}")
        return "\n".join(parts)

    def _parse_and_validate(self, raw: str) -> Optional[RiskDetectorOutput]:
        """Parse LLM JSON response and validate against RiskDetectorOutput."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning(f"[A4] JSON decode error: {e}")
            return None

        try:
            # Ensure nested lists exist
            for key in ["scope_creep_risks", "missing_scope_definitions", "unclear_responsibilities",
                        "timeline_risks", "technical_risks", "revision_risks", "dependency_risks",
                        "payment_risks", "stakeholder_risks", "recommended_followup_questions",
                        "critical_missing_items", "risk_prevention_recommendations", "risk_flags"]:
                if key not in data or not isinstance(data[key], list):
                    data[key] = []
            return RiskDetectorOutput.model_validate(data)
        except Exception as e:
            logger.warning(f"[A4] Pydantic validation error: {e}")
            return None

    def _fallback_output(
        self, a1: A1Output, a2: BriefExtractorOutput, a3: ScopeBuilderOutput
    ) -> RiskDetectorOutput:
        """Construct a minimal but valid risk analysis when LLM fails."""
        risks = []
        flags = []

        # Copywriting risk
        if a2.revision_expectations and not a2.revision_expectations.revision_discussed:
            risks.append(ScopeCreepRisk(
                id="risk_revision_fallback",
                title="Revision Rounds Not Defined",
                description="No revision expectations were captured in the brief.",
                category="revisions",
                severity="high",
                likelihood="high",
                impact="high",
                why_it_matters="Undefined revisions lead to scope creep and unpaid work.",
                evidence=["A2 revision_expectations.revision_discussed is False"],
                recommended_fix="Define revision limits per deliverable in the SOW.",
                recommended_contract_language="Each major deliverable includes up to two rounds of revisions unless otherwise specified.",
                requires_client_clarification=True,
                blocking_risk=False,
            ))
            flags.append(RiskFlagData(
                severity="high",
                title="Revision Rounds Not Defined",
                description="No revision expectations captured.",
                suggested_fix="Define revision limits.",
            ))

        # Timeline risk
        if a2.timeline and a2.timeline.timeline_confidence == "low":
            risks.append(ScopeCreepRisk(
                id="risk_timeline_fallback",
                title="Timeline Confidence Low",
                description="Timeline information is vague or missing.",
                category="timeline",
                severity="medium",
                likelihood="high",
                impact="medium",
                why_it_matters="Vague timelines cause delivery pressure and rushed work.",
                evidence=["A2 timeline_confidence is low"],
                recommended_fix="Confirm firm dates and milestone checkpoints.",
                recommended_contract_language="",
                requires_client_clarification=True,
                blocking_risk=False,
            ))
            flags.append(RiskFlagData(
                severity="medium",
                title="Timeline Confidence Low",
                description="Timeline information is vague.",
                suggested_fix="Confirm firm dates.",
            ))

        # Ambiguity flags from A3
        for amb in a3.ambiguity_flags:
            risks.append(ScopeCreepRisk(
                id=f"risk_ambiguity_{amb.item.lower().replace(' ', '_')[:20]}",
                title=amb.item,
                description=amb.why_it_matters,
                category="other",
                severity=amb.severity,
                likelihood="high",
                impact="medium" if amb.severity == "medium" else "high",
                why_it_matters=amb.why_it_matters,
                evidence=[f"A3 ambiguity flag: {amb.item}"],
                recommended_fix=amb.suggested_clarification,
                recommended_contract_language="",
                requires_client_clarification=True,
                blocking_risk=amb.severity == "high",
            ))
            flags.append(RiskFlagData(
                severity=amb.severity,
                title=amb.item,
                description=amb.why_it_matters,
                suggested_fix=amb.suggested_clarification,
            ))

        missing = a2.missing_information if a2.missing_information else []
        critical = missing[:5] if missing else []
        followup = [f"Clarify: {m}" for m in missing[:5]] if missing else []

        score = min(40 + len(risks) * 10 + len(missing) * 5, 100)
        level = "low" if score < 40 else ("medium" if score < 70 else "high")

        return RiskDetectorOutput(
            overall_risk_score=score,
            overall_risk_level=level,
            risk_summary="Fallback risk analysis based on A2/A3 signals. Review recommended.",
            scope_creep_risks=risks,
            missing_scope_definitions=missing,
            unclear_responsibilities=a2.client_responsibilities[:3] if a2.client_responsibilities else [],
            timeline_risks=a2.timeline.unclear_timeline_items if a2.timeline else [],
            technical_risks=[],
            revision_risks=["Revision limits undefined"],
            dependency_risks=a2.dependencies[:3] if a2.dependencies else [],
            payment_risks=["Payment structure not detailed"],
            stakeholder_risks=[],
            recommended_followup_questions=followup,
            critical_missing_items=critical,
            risk_prevention_recommendations=["Add explicit revision limits.", "Define content ownership."],
            risk_detection_confidence_score=50,
            risk_flags=flags,
        )

    def _derive_compat_fields(self, output: RiskDetectorOutput) -> RiskDetectorOutput:
        """Ensure backward-compat risk_flags are populated from rich scope_creep_risks."""
        data = output.model_dump()
        if not data.get("risk_flags") and data.get("scope_creep_risks"):
            flags = []
            for r in data["scope_creep_risks"]:
                flags.append({
                    "severity": r.get("severity", "medium"),
                    "title": r.get("title", ""),
                    "description": r.get("description", ""),
                    "suggested_fix": r.get("recommended_fix", ""),
                })
            data["risk_flags"] = flags
        return RiskDetectorOutput.model_validate(data)

    def _apply_rule_engine(
        self,
        output: RiskDetectorOutput,
        a1: A1Output,
        a2: BriefExtractorOutput,
        a3: ScopeBuilderOutput,
    ) -> RiskDetectorOutput:
        data = output.model_dump()
        rule_risks = detect_rule_based_risks([
            a1.model_dump_json(),
            a2.model_dump_json(),
            a3.model_dump_json(),
        ])
        existing_ids = {risk.get("id") for risk in data.get("scope_creep_risks", [])}
        new_risks = [risk for risk in rule_risks if risk.id not in existing_ids]
        if not new_risks:
            return output

        data["scope_creep_risks"].extend([risk.model_dump() for risk in new_risks])
        data["risk_flags"].extend([flag.model_dump() for flag in risks_to_flags(new_risks)])
        data["overall_risk_score"] = min(100, max(data.get("overall_risk_score", 0), 45 + len(data["scope_creep_risks"]) * 7))
        if data["overall_risk_score"] >= 70:
            data["overall_risk_level"] = "high"
        elif data["overall_risk_score"] >= 40:
            data["overall_risk_level"] = "medium"
        for risk in new_risks:
            if risk.title not in data.get("critical_missing_items", []):
                data["critical_missing_items"].append(risk.title)
        return RiskDetectorOutput.model_validate(data)
