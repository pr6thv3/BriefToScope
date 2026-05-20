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

import time
import uuid
from datetime import datetime
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
    ClauseGeneratorOutput, RevisionPolicy, PaymentSchedule, PaymentMilestone,
    SOWComposerOutput, SOWSection,
    QualityCheckerOutput,
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
        user_id: str = "",
        project_id: str = "",
        status_callback = None,
    ) -> SOWOutput:
        logger.info("[PIPELINE] === Starting AI Pipeline ===")
        self.state = PipelineState()
        self.state.request_id = str(uuid.uuid4())
        self.state.user_id = user_id
        self.state.project_id = project_id
        self.state.started_at = datetime.utcnow().isoformat()
        self.state.steps = {}
        self.state.errors = []
        self.state.fallback_used = False

        # ── A1 ──────────────────────────────────────
        if status_callback:
            await status_callback("cleaning")
        t0 = time.perf_counter()
        a1 = await self._run_a1(transcript_text, industry, tone, client_name, project_name)
        d1 = int((time.perf_counter() - t0) * 1000)
        self.state.a1_cleaned = a1
        self.state.steps["a1"] = {
            "status": "fallback" if any("fallback" in err.lower() for err in self.state.errors) or (hasattr(a1, "unclear_items") and a1.unclear_items and "A1 extraction failed" in a1.unclear_items[0]) else "success",
            "output": a1.model_dump(),
            "duration_ms": d1
        }

        # ── A2 ──────────────────────────────────────
        if status_callback:
            await status_callback("extracting")
        t0 = time.perf_counter()
        a2 = await self._run_a2(a1, industry, tone)
        d2 = int((time.perf_counter() - t0) * 1000)
        
        # Apply user overrides from the form into the brief
        if budget and budget not in a2.budget.budget_details:
            a2.budget.budget_details.append(budget)
            a2.budget.budget_discussed = True
        if timeline and timeline not in a2.timeline.mentioned_deadlines:
            a2.timeline.mentioned_deadlines.append(timeline)
            a2.timeline.timeline_confidence = "medium"

        self.state.a2_brief = a2
        self.state.steps["a2"] = {
            "status": "fallback" if any("a2" in err.lower() for err in self.state.errors) else "success",
            "output": a2.model_dump(),
            "duration_ms": d2
        }

        # ── A3 ──────────────────────────────────────
        if status_callback:
            await status_callback("building_scope")
        t0 = time.perf_counter()
        a3 = await self._run_a3(a2, industry, tone)
        d3 = int((time.perf_counter() - t0) * 1000)
        self.state.a3_scope = a3
        self.state.steps["a3"] = {
            "status": "fallback" if any("a3" in err.lower() for err in self.state.errors) else "success",
            "output": a3.model_dump(),
            "duration_ms": d3
        }

        # ── A4 ──────────────────────────────────────
        if status_callback:
            await status_callback("detecting_risks")
        t0 = time.perf_counter()
        a4 = await self._run_a4(a1, a2, a3, industry, tone)
        d4 = int((time.perf_counter() - t0) * 1000)
        self.state.a4_risks = a4
        self.state.steps["a4"] = {
            "status": "fallback" if any("a4" in err.lower() for err in self.state.errors) else "success",
            "output": a4.model_dump(),
            "duration_ms": d4
        }

        # ── A5 ──────────────────────────────────────
        t0 = time.perf_counter()
        a5 = await self._run_a5(a1, a2, a3, a4, industry, tone)
        d5 = int((time.perf_counter() - t0) * 1000)
        self.state.a5_clauses = a5
        self.state.steps["a5"] = {
            "status": "fallback" if any("a5" in err.lower() for err in self.state.errors) else "success",
            "output": a5.model_dump(),
            "duration_ms": d5
        }

        # ── A6 ──────────────────────────────────────
        t0 = time.perf_counter()
        a6 = await self._run_a6(a1, a2, a3, a4, a5, industry, tone)
        d6 = int((time.perf_counter() - t0) * 1000)
        self.state.a6_sow = a6
        self.state.steps["a6"] = {
            "status": "fallback" if any("a6" in err.lower() for err in self.state.errors) else "success",
            "output": a6.model_dump(),
            "duration_ms": d6
        }

        # ── A7 ──────────────────────────────────────
        t0 = time.perf_counter()
        a7 = await self._run_a7(a1, a2, a3, a4, a5, a6, industry, tone)
        d7 = int((time.perf_counter() - t0) * 1000)
        self.state.a7_quality = a7
        self.state.steps["a7"] = {
            "status": "fallback" if any("a7" in err.lower() for err in self.state.errors) else "success",
            "output": a7.model_dump(),
            "duration_ms": d7
        }

        self.state.completed_at = datetime.utcnow().isoformat()

        blocking = sum(1 for r in a4.scope_creep_risks if r.blocking_risk)
        warnings = sum(1 for s in a7.section_reviews if s.status == "warning")
        logger.info(
            f"[PIPELINE] === Completed: quality={a7.overall_quality_score}, "
            f"approval={a7.approval_status}, warnings={warnings}, "
            f"risk_score={a4.overall_risk_score}, level={a4.overall_risk_level}, "
            f"risks={len(a4.scope_creep_risks)}, blocking={blocking}, "
            f"missing={a7.missing_sections}, ready={a7.ready_for_export} ==="
        )

        # Map to public API schema — prefer rich scope_creep_risks, fall back to risk_flags
        source_risks = a4.scope_creep_risks if a4.scope_creep_risks else a4.risk_flags
        risk_flags = []
        for r in source_risks:
            d = r.model_dump()
            # ScopeCreepRisk uses "recommended_fix"; RiskFlag expects "suggested_fix"
            if "recommended_fix" in d:
                d["suggested_fix"] = d.pop("recommended_fix")
            risk_flags.append(RiskFlag(**d))
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
            self.state.fallback_used = True
            self.state.errors.append(f"A1 failed: {str(e)}")
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
            self.state.fallback_used = True
            self.state.errors.append(f"A2 failed: {str(e)}")
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
            self.state.fallback_used = True
            self.state.errors.append(f"A3 failed: {str(e)}")
            fallback = get_fallback_sow()
            return A3Output(
                scope_of_work=fallback["scope_of_work"],
                deliverables=fallback["deliverables"],
                timeline=fallback["timeline"],
                payment_schedule=fallback["payment_schedule"],
            )

    async def _run_a4(
        self, a1: A1Output, a2: BriefExtractorOutput, a3: A3Output, industry: str, tone: str
    ) -> A4Output:
        logger.info("[PIPELINE] A4 — Risk Detector started")
        try:
            result = await self.risk_detector.detect(
                a1=a1, a2=a2, a3=a3, industry=industry, tone=tone
            )
            blocking = sum(1 for r in result.scope_creep_risks if r.blocking_risk)
            logger.info(
                f"[PIPELINE] A4 — OK: score={result.overall_risk_score}, "
                f"level={result.overall_risk_level}, "
                f"risks={len(result.scope_creep_risks)}, "
                f"blocking={blocking}, "
                f"confidence={result.risk_detection_confidence_score}"
            )
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A4 — FAILED: {e}, using fallback risks")
            self.state.fallback_used = True
            self.state.errors.append(f"A4 failed: {str(e)}")
            fallback_risks = get_fallback_risks()
            return A4Output(
                overall_risk_score=50,
                overall_risk_level="medium",
                risk_summary="Risk detection failed — fallback used.",
                scope_creep_risks=[],
                risk_flags=fallback_risks,
                risk_detection_confidence_score=30,
            )

    async def _run_a5(
        self, a1: A1Output, a2: BriefExtractorOutput, a3: A3Output, a4: A4Output, industry: str, tone: str
    ) -> A5Output:
        logger.info("[PIPELINE] A5 — Clause Generator started")
        try:
            result = await self.clause_generator.generate(
                a1=a1, a2=a2, a3=a3, a4=a4, industry=industry, tone=tone
            )
            logger.info(
                f"[PIPELINE] A5 — OK: revision_defined={result.revision_policy.limits_defined}, "
                f"milestones={len(result.payment_schedule.milestones)}, "
                f"confidence={result.clause_generation_confidence_score}"
            )
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A5 — FAILED: {e}, using fallback clauses")
            self.state.fallback_used = True
            self.state.errors.append(f"A5 failed: {str(e)}")
            return ClauseGeneratorOutput(
                revision_policy=RevisionPolicy(summary="Fallback revision policy", clauses=["Two rounds of revisions included"], limits_defined=True),
                payment_schedule=PaymentSchedule(
                    summary="Fallback payment schedule",
                    milestones=[PaymentMilestone(label="Project Start", percentage="50%", condition="Before kickoff"), PaymentMilestone(label="Final Delivery", percentage="50%", condition="Before launch")],
                ),
                clause_generation_confidence_score=50,
            )

    async def _run_a6(
        self, a1: A1Output, a2: BriefExtractorOutput, a3: A3Output, a4: A4Output, a5: A5Output, industry: str, tone: str
    ) -> A6Output:
        logger.info("[PIPELINE] A6 — SOW Composer started")
        try:
            result = await self.sow_composer.compose(
                a1=a1, a2=a2, a3=a3, a4=a4, a5=a5, industry=industry, tone=tone
            )
            logger.info(
                f"[PIPELINE] A6 — OK: sections={len(result.sections)}, "
                f"export_ready={result.export_ready}, "
                f"confidence={result.composer_confidence_score}"
            )
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A6 — FAILED: {e}, using fallback SOW")
            self.state.fallback_used = True
            self.state.errors.append(f"A6 failed: {str(e)}")
            fallback = get_fallback_sow()
            return SOWComposerOutput(
                document_title="Statement of Work",
                sections=[SOWSection(section_key=k, section_title=k.replace("_", " ").title(), content_markdown=v if isinstance(v, str) else "\n".join(f"- {i}" for i in v), order=idx + 1) for idx, (k, v) in enumerate(fallback.items())],
                composer_confidence_score=50,
            )

    async def _run_a7(
        self, a1: A1Output, a2: BriefExtractorOutput, a3: A3Output, a4: A4Output, a5: A5Output, a6: A6Output, industry: str, tone: str
    ) -> A7Output:
        logger.info("[PIPELINE] A7 — Quality Checker started")
        try:
            result = await self.quality_checker.check(
                a1=a1, a2=a2, a3=a3, a4=a4, a5=a5, a6=a6, industry=industry, tone=tone
            )
            warnings = sum(1 for s in result.section_reviews if s.status == "warning")
            logger.info(
                f"[PIPELINE] A7 — OK: score={result.overall_quality_score}, "
                f"status={result.approval_status}, warnings={warnings}, "
                f"vague={len(result.vague_language_flags)}, blocking={len(result.blocking_issues)}, "
                f"ready={result.ready_for_export}, confidence={result.quality_checker_confidence_score}"
            )
            return result
        except Exception as e:
            logger.warning(f"[PIPELINE] A7 — FAILED: {e}, using default quality")
            self.state.fallback_used = True
            self.state.errors.append(f"A7 failed: {str(e)}")
            return QualityCheckerOutput(
                overall_quality_score=70,
                approval_status="approved_with_warnings",
                executive_review_summary="Quality check failed — manual review recommended.",
                ready_for_export=True,
                quality_checker_confidence_score=50,
                confidence_score=0.70,
                suggestions=["Quality check failed — manual review recommended"],
            )

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
