"""A7 — Quality Checker.

Final validation and quality assurance layer for the generated SOW.
Detects weak wording, missing sections, commercial ambiguity, and risky phrases.
Uses structured JSON-mode LLM calls with retry and fallback.
"""

import json
from typing import Any, Dict
from app.services.llm_client import LLMClient
from app.utils.logger import get_logger
from app.models.ai_schemas import (
    QualityCheckerOutput,
    SectionReview,
    VagueLanguageFlag,
    CommercialRiskFlag,
    TimelineReview,
    PaymentReview,
    ScopeReview,
    LegalSensitivityFlag,
    DocumentConsistencyReview,
)

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are a senior Statement of Work quality assurance reviewer.\n\n"
    "Your job is to audit the generated SOW for:\n"
    "- clarity\n"
    "- completeness\n"
    "- commercial safety\n"
    "- scope precision\n"
    "- operational quality\n"
    "- readability\n"
    "- delivery realism\n\n"
    "You are NOT rewriting the SOW unless necessary.\n\n"
    "Rules:\n"
    "- Detect vague or risky wording.\n"
    "- Detect commercial ambiguity.\n"
    "- Detect missing sections.\n"
    "- Detect unrealistic promises.\n"
    "- Detect inconsistent scope boundaries.\n"
    "- Detect operational weaknesses.\n"
    "- Preserve commercially professional tone.\n"
    "- Avoid legal overreach.\n"
    "- Output valid JSON only."
)

MOCK_A7_OUTPUT = QualityCheckerOutput(
    overall_quality_score=91,
    approval_status="approved_with_warnings",
    executive_review_summary="The SOW is commercially strong and well-structured, but several minor wording and scope clarification improvements are recommended before client delivery.",
    section_reviews=[
        SectionReview(
            section_title="Project Overview",
            quality_score=94,
            status="pass",
            issues_found=[],
            recommended_improvements=[],
        ),
        SectionReview(
            section_title="Scope of Work",
            quality_score=94,
            status="pass",
            issues_found=[],
            recommended_improvements=[],
        ),
        SectionReview(
            section_title="Timeline",
            quality_score=78,
            status="warning",
            issues_found=["Final launch approval process not clearly defined."],
            recommended_improvements=["Add stakeholder approval timeline assumptions."],
        ),
        SectionReview(
            section_title="Payment Schedule",
            quality_score=92,
            status="pass",
            issues_found=[],
            recommended_improvements=[],
        ),
        SectionReview(
            section_title="Revision Policy",
            quality_score=88,
            status="pass",
            issues_found=[],
            recommended_improvements=[],
        ),
        SectionReview(
            section_title="Out of Scope",
            quality_score=90,
            status="pass",
            issues_found=[],
            recommended_improvements=[],
        ),
    ],
    missing_sections=[],
    missing_critical_information=["Hosting responsibility"],
    vague_language_flags=[
        VagueLanguageFlag(
            phrase="modern animations as needed",
            reason="The phrase is open-ended and may imply unlimited animation work.",
            severity="high",
            recommended_replacement="Basic transition and interaction animations as specifically approved in scope.",
        ),
    ],
    commercial_risk_flags=[
        CommercialRiskFlag(
            issue="Copywriting responsibility remains partially unclear.",
            why_it_matters="Content delays commonly impact website project timelines.",
            severity="high",
            recommended_fix="Explicitly define content ownership responsibilities.",
        ),
    ],
    timeline_review=TimelineReview(
        status="warning",
        issues=["No formal approval response timeline defined."],
        recommendations=["Add stakeholder review windows."],
    ),
    payment_review=PaymentReview(
        status="pass",
        issues=[],
        recommendations=[],
    ),
    scope_review=ScopeReview(
        status="pass",
        issues=[],
        recommendations=["Clarify CMS limitations if ecommerce expansion is expected."],
    ),
    legal_sensitivity_flags=[
        LegalSensitivityFlag(
            statement="guaranteed conversion improvements",
            risk="Implies performance guarantee.",
            recommended_change="designed to support improved conversion performance",
        ),
    ],
    document_consistency_review=DocumentConsistencyReview(
        consistent_tone=True,
        consistent_scope_boundaries=True,
        consistent_responsibilities=True,
        formatting_valid=True,
    ),
    final_recommendations=[
        "Clarify hosting ownership.",
        "Clarify approval timelines.",
        "Replace vague animation wording.",
    ],
    blocking_issues=[],
    ready_for_export=True,
    quality_checker_confidence_score=93,
    confidence_score=0.91,
    suggestions=["Clarify hosting ownership.", "Clarify approval timelines.", "Replace vague animation wording."],
    strengths=["Strong scope boundaries", "Clear payment structure", "Professional tone"],
)


class QualityChecker:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def check(
        self,
        a1: Any,
        a2: Any,
        a3: Any,
        a4: Any,
        a5: Any,
        a6: Any,
        industry: str = "",
        tone: str = "Professional",
    ) -> QualityCheckerOutput:
        logger.info("[A7] Quality check STARTED")
        logger.info(f"[A7] Input validated: industry={industry}, tone={tone}")

        if self.llm.settings.demo_mode:
            logger.info("[A7] DEMO_MODE: returning rich mock A7 output")
            return MOCK_A7_OUTPUT

        if not self.llm.settings.openai_api_key and not self.llm.settings.anthropic_api_key:
            logger.warning("[A7] No API keys configured — using fallback quality review")
            return self._fallback_check(a1, a2, a3, a4, a5, a6)

        prompt = self._build_prompt(a1, a2, a3, a4, a5, a6, industry, tone)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        last_error: Exception | None = None
        for attempt in range(1, 3):
            try:
                raw = await self.llm.chat_completion(
                    messages,
                    temperature=0.2,
                    response_format={"type": "json_object"},
                    max_retries=1,
                )
                data = json.loads(raw)
                result = QualityCheckerOutput.model_validate(data)
                logger.info(
                    f"[A7] Quality check COMPLETED: score={result.overall_quality_score}, "
                    f"status={result.approval_status}, "
                    f"warnings={len([s for s in result.section_reviews if s.status == 'warning'])}, "
                    f"vague_flags={len(result.vague_language_flags)}, "
                    f"blocking={len(result.blocking_issues)}, "
                    f"ready={result.ready_for_export}, "
                    f"confidence={result.quality_checker_confidence_score}"
                )
                return result
            except (json.JSONDecodeError, Exception) as e:
                last_error = e
                logger.warning(f"[A7] Attempt {attempt}/2 failed: {e}")

        logger.error(f"[A7] Quality check FAILED after retries: {last_error}")
        return self._fallback_check(a1, a2, a3, a4, a5, a6)

    def _build_prompt(
        self, a1: Any, a2: Any, a3: Any, a4: Any, a5: Any, a6: Any, industry: str, tone: str
    ) -> str:
        def _dump(obj: Any) -> str:
            return json.dumps(obj.model_dump() if hasattr(obj, "model_dump") else dict(obj), indent=2, default=str)

        return (
            f"Industry: {industry}\n"
            f"Tone: {tone}\n\n"
            f"A1 Transcript Cleaner output:\n{_dump(a1)}\n\n"
            f"A2 Brief Extractor output:\n{_dump(a2)}\n\n"
            f"A3 Scope Builder output:\n{_dump(a3)}\n\n"
            f"A4 Risk Detector output:\n{_dump(a4)}\n\n"
            f"A5 Clause Generator output:\n{_dump(a5)}\n\n"
            f"A6 SOW Composer output:\n{_dump(a6)}\n\n"
            "Generate the QualityCheckerOutput JSON.\n"
            "Include overall_quality_score, approval_status, executive_review_summary, "
            "section_reviews (array with section_title, quality_score, status, issues_found, recommended_improvements), "
            "missing_sections, missing_critical_information, vague_language_flags, commercial_risk_flags, "
            "timeline_review, payment_review, scope_review, legal_sensitivity_flags, document_consistency_review, "
            "final_recommendations, blocking_issues, ready_for_export, and quality_checker_confidence_score."
        )

    def _fallback_check(self, a1: Any, a2: Any, a3: Any, a4: Any, a5: Any, a6: Any) -> QualityCheckerOutput:
        logger.warning("[A7] Using fallback quality check")

        sections = []
        if a6 and hasattr(a6, "sections"):
            for s in a6.sections:
                sections.append(SectionReview(
                    section_title=s.section_title,
                    quality_score=80,
                    status="pass",
                    issues_found=[],
                    recommended_improvements=[],
                ))
        else:
            for title in ["Project Overview", "Scope of Work", "Timeline", "Payment Schedule", "Revision Policy", "Out of Scope"]:
                sections.append(SectionReview(section_title=title, quality_score=75, status="pass"))

        vague_flags: list[VagueLanguageFlag] = []
        risky_phrases = [
            ("unlimited revisions", "Implies unlimited scope — revise to specific round counts."),
            ("guaranteed results", "Implies performance guarantee — remove or soften."),
            ("complete seo optimization", "Overpromising — specify scope of SEO work."),
            ("fully scalable enterprise system", "Vague and overpromising — define scalability limits."),
            ("all future updates included", "Implies indefinite maintenance — exclude or price separately."),
            ("any requested changes", "Open-ended scope risk — require change request process."),
            ("ongoing support included", "Ambiguous duration — define support period."),
            ("everything discussed", "Vague catch-all — list specific inclusions."),
            ("as needed", "Open-ended — specify quantity or limits."),
            ("future-proof", "Marketing fluff — remove or replace with specific capability."),
            ("best possible", "Subjective — define measurable criteria."),
        ]

        # Scan A6 sections for risky phrases
        if a6 and hasattr(a6, "sections"):
            for section in a6.sections:
                content = section.content_markdown.lower()
                for phrase, reason in risky_phrases:
                    if phrase in content:
                        vague_flags.append(VagueLanguageFlag(
                            phrase=phrase,
                            reason=reason,
                            severity="high",
                            recommended_replacement=f"Replace with specific, bounded language.",
                        ))

        # Detect missing sections
        missing = []
        expected_keys = {"overview", "objectives", "scope", "deliverables", "timeline", "payment", "revision_policy", "out_of_scope", "assumptions", "acceptance_criteria", "signature"}
        if a6 and hasattr(a6, "sections"):
            present_keys = {s.section_key for s in a6.sections}
            missing = sorted(list(expected_keys - present_keys))

        # Detect missing critical info from A4
        missing_critical = []
        if a4 and hasattr(a4, "critical_missing_items"):
            missing_critical = list(a4.critical_missing_items)

        blocking = []
        if a4 and hasattr(a4, "scope_creep_risks"):
            for risk in a4.scope_creep_risks:
                if risk.blocking_risk:
                    blocking.append(risk.title)

        score = max(0, 100 - len(missing) * 10 - len(vague_flags) * 8 - len(blocking) * 15)
        approval = "blocked" if blocking else ("needs_revision" if missing or vague_flags else ("approved_with_warnings" if missing_critical else "approved"))

        return QualityCheckerOutput(
            overall_quality_score=score,
            approval_status=approval,
            executive_review_summary="Fallback quality review based on structured analysis of pipeline outputs.",
            section_reviews=sections,
            missing_sections=missing,
            missing_critical_information=missing_critical,
            vague_language_flags=vague_flags,
            commercial_risk_flags=[],
            timeline_review=TimelineReview(status="pass"),
            payment_review=PaymentReview(status="pass"),
            scope_review=ScopeReview(status="pass"),
            legal_sensitivity_flags=[],
            document_consistency_review=DocumentConsistencyReview(),
            final_recommendations=[f"Review {len(vague_flags)} vague language flags" if vague_flags else "No major issues detected."],
            blocking_issues=blocking,
            ready_for_export=(not blocking and not missing),
            quality_checker_confidence_score=70,
            confidence_score=score / 100.0,
            suggestions=[f"Add missing section: {m}" for m in missing] + [f"Fix vague phrase: {v.phrase}" for v in vague_flags],
            strengths=["Structured review completed"],
        )
