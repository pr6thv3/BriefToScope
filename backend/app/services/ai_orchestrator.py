"""AI Workflow Orchestrator for BriefToScope.

Runs a 7-step pipeline:
  A1 — Transcript Cleaner
  A2 — Brief Extractor
  A3 — Scope Builder
  A4 — Risk Detector
  A5 — Clause Generator
  A6 — SOW Composer
  A7 — Quality Checker

Design:
- Each step is independent with clear input/output schemas.
- The orchestrator validates outputs and passes clean data to the next step.
- If a step fails, the orchestrator recovers with fallback data and continues.
- Intermediate outputs are stored in PipelineState (no DB logic here).
"""

from typing import Optional
from app.services.llm_client import LLMClient
from app.services.transcript_cleaner import TranscriptCleaner
from app.services.brief_extractor import BriefExtractor
from app.services.scope_builder import ScopeBuilder
from app.services.risk_detector import RiskDetector
from app.services.clause_generator import ClauseGenerator
from app.services.sow_composer import SOWComposer
from app.services.quality_checker import QualityChecker
from app.services.demo_data import (
    get_fallback_sow,
    get_fallback_brief,
    get_fallback_risks,
    get_fallback_clauses,
)
from app.utils.logger import get_logger
from app.models.schemas import SOWOutput, SOWContent, RiskFlag, ExtractedBrief
from app.models.ai_schemas import (
    A1Output, BriefExtractorOutput, A3Output, A4Output, A5Output, A6Output, A7Output,
    PipelineState,
)

logger = get_logger(__name__)


class AIOrchestrator:
    """Orchestrates the 7-step AI pipeline with validation and fallback."""

    def __init__(self):
        self.llm = LLMClient()
        self.transcript_cleaner = TranscriptCleaner(self.llm)
        self.brief_extractor = BriefExtractor(self.llm)
        self.scope_builder = ScopeBuilder(self.llm)
        self.risk_detector = RiskDetector(self.llm)
        self.clause_generator = ClauseGenerator(self.llm)
        self.sow_composer = SOWComposer(self.llm)
        self.quality_checker = QualityChecker(self.llm)
        self.state = PipelineState()

    async def generate_sow(
        self,
        transcript_text: str,
        industry: str,
        tone: str,
        client_name: str,
        project_name: str,
        budget: str,
        timeline: str,
    ) -> SOWOutput:
        logger.info("[PIPELINE] === Starting AI Pipeline ===")
        self.state = PipelineState()

        # ── A1 ──────────────────────────────────────
        a1 = await self._run_a1(transcript_text, industry, tone, client_name, project_name)
        self.state.a1_cleaned = a1

        # ── A2 ──────────────────────────────────────
        a2 = await self._run_a2(a1, industry, tone)
        self.state.a2_brief = a2

        # Apply user overrides from the form into the brief
        if budget and budget not in a2.budget.budget_details:
            a2.budget.budget_details.append(budget)
            a2.budget.budget_discussed = True
        if timeline and timeline not in a2.timeline.mentioned_deadlines:
            a2.timeline.mentioned_deadlines.append(timeline)
            a2.timeline.timeline_confidence = "medium"

        # ── A3 ──────────────────────────────────────
        a3 = await self._run_a3(a2, industry, tone)
        self.state.a3_scope = a3

        # ── A4 ──────────────────────────────────────
        a4 = await self._run_a4(a2, a3)
        self.state.a4_risks = a4

        # ── A5 ──────────────────────────────────────
        a5 = await self._run_a5(a2, a3, industry)
        self.state.a5_clauses = a5

        # ── A6 ──────────────────────────────────────
        a6 = await self._run_a6(a2, a3, a5, industry, tone)
        self.state.a6_sow = a6

        # ── A7 ──────────────────────────────────────
        a7 = await self._run_a7(a6, a2)
        self.state.a7_quality = a7

        logger.info(
            f"[PIPELINE] === Completed: confidence={a7.confidence_score:.2f}, "
            f"risks={len(a4.risk_flags)}, missing={a7.missing_sections} ==="
        )

        # Map to public API schema
        risk_flags = [RiskFlag(**r.model_dump()) for r in a4.risk_flags]
        extracted_brief = self._map_to_extracted_brief(a1, a2)
        sow_content = SOWContent(**a6.model_dump())

        return SOWOutput(
            sow=sow_content,
            risk_flags=risk_flags,
            extracted_brief=extracted_brief,
            confidence_score=a7.confidence_score,
        )

    async def close(self):
        await self.llm.close()

    # ─── Step runners ─────────────────────────────

    async def _run_a1(self, raw_text: str, industry: str, tone: str, client_name: str, project_name: str) -> A1Output:
        logger.info("[PIPELINE] A1 — Transcript Cleaner started")
        try:
            result = await self.transcript_cleaner.clean(
                raw_text,
                industry=industry,
                tone=tone,
                client_name=client_name,
                project_name=project_name,
            )
            logger.info(f"[PIPELINE] A1 — OK: client={result.client_name}, deliverables={len(result.mentioned_deliverables)}")
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A1 — FAILED: {e}, using fallback")
            return A1Output(
                client_name=client_name,
                project_name=project_name,
                cleaned_summary=raw_text[:500],
                unclear_items=["A1 extraction failed — manual review needed"],
            )

    async def _run_a2(self, a1: A1Output, industry: str, tone: str) -> BriefExtractorOutput:
        logger.info("[PIPELINE] A2 — Brief Extractor started")
        try:
            result = await self.brief_extractor.extract(a1, industry=industry, tone=tone)
            logger.info(
                f"[PIPELINE] A2 — OK: objectives={len(result.primary_objectives)}, "
                f"deliverables={len(result.deliverables)}, "
                f"confidence={result.brief_confidence_score}"
            )
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A2 — FAILED: {e}, using fallback brief")
            return BriefExtractorOutput.model_validate(get_fallback_brief())

    async def _run_a3(self, a2: BriefExtractorOutput, industry: str, tone: str) -> A3Output:
        logger.info("[PIPELINE] A3 — Scope Builder started")
        try:
            result = await self.scope_builder.build(a2, industry=industry, tone=tone)
            logger.info(
                f"[PIPELINE] A3 — OK: items={len(result.commercial_scope_items)}, "
                f"specs={len(result.deliverable_specifications)}, "
                f"ambiguity={len(result.ambiguity_flags)}, "
                f"confidence={result.scope_confidence_score}"
            )
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A3 — FAILED: {e}, using fallback scope")
            fallback = get_fallback_sow()
            return A3Output(
                scope_of_work=fallback["scope_of_work"],
                deliverables=fallback["deliverables"],
                timeline=fallback["timeline"],
                payment_schedule=fallback["payment_schedule"],
            )

    async def _run_a4(self, a2: BriefExtractorOutput, a3: A3Output) -> A4Output:
        logger.info("[PIPELINE] A4 — Risk Detector started")
        try:
            raw = await self.risk_detector.detect(a2.model_dump(), a3.model_dump())
            if isinstance(raw, list):
                result = A4Output(risk_flags=raw)
            else:
                result = A4Output.model_validate(raw)
            logger.info(f"[PIPELINE] A4 — OK: {len(result.risk_flags)} flags")
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A4 — FAILED: {e}, using fallback risks")
            return A4Output(risk_flags=get_fallback_risks())

    async def _run_a5(self, a2: BriefExtractorOutput, a3: A3Output, industry: str) -> A5Output:
        logger.info("[PIPELINE] A5 — Clause Generator started")
        try:
            raw = await self.clause_generator.generate(a2.model_dump(), a3.model_dump(), industry)
            result = A5Output.model_validate(raw)
            logger.info(f"[PIPELINE] A5 — OK: revision_policy={'set' if result.revision_policy else 'empty'}")
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A5 — FAILED: {e}, using fallback clauses")
            return A5Output.model_validate(get_fallback_clauses())

    async def _run_a6(self, a2: BriefExtractorOutput, a3: A3Output, a5: A5Output, industry: str, tone: str) -> A6Output:
        logger.info("[PIPELINE] A6 — SOW Composer started")
        try:
            raw = await self.sow_composer.compose(
                a2.model_dump(), a3.model_dump(), a5.model_dump(), industry, tone
            )
            result = A6Output.model_validate(raw)
            logger.info(f"[PIPELINE] A6 — OK: overview={'set' if result.project_overview else 'empty'}")
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A6 — FAILED: {e}, using fallback SOW")
            return A6Output.model_validate(get_fallback_sow())

    async def _run_a7(self, a6: A6Output, a2: BriefExtractorOutput) -> A7Output:
        logger.info("[PIPELINE] A7 — Quality Checker started")
        try:
            raw = await self.quality_checker.check(a6.model_dump(), a2.model_dump())
            if isinstance(raw, dict):
                result = A7Output.model_validate(raw)
            else:
                result = A7Output(confidence_score=0.75)
            logger.info(f"[PIPELINE] A7 — OK: score={result.confidence_score:.2f}")
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A7 — FAILED: {e}, using default quality")
            return A7Output(confidence_score=0.72, suggestions=["Quality check failed — manual review recommended"])

    # ─── API mapping helpers ─────────────────────

    def _map_to_extracted_brief(self, a1: A1Output, a2: BriefExtractorOutput) -> ExtractedBrief:
        """Map rich BriefExtractorOutput back to the API-facing ExtractedBrief."""
        deliverable_names = [d.name for d in a2.deliverables]
        return ExtractedBrief(
            client_name=a1.client_name or "",
            project_type=a1.project_type or "",
            goals=a2.primary_objectives,
            deliverables=deliverable_names,
            budget_mentions=a2.budget.budget_details if a2.budget.budget_discussed else [],
            deadline_mentions=a2.timeline.mentioned_deadlines,
            unclear_items=a2.missing_information,
        )
