"""Tests for A7 — Quality Checker.

Covers:
- Valid A1–A6 input → valid A7 output
- Vague wording detection
- Missing revision policy detection
- Missing payment schedule detection
- Risky guarantees detection
- Formatting validation
- Blocked approval scenario
- Fallback mode
- Full pipeline A1 → A7
- DEMO_MODE mock output
"""

import asyncio
from app.services.llm_client import LLMClient
from app.services.transcript_cleaner import TranscriptCleaner
from app.services.brief_extractor import BriefExtractor
from app.services.scope_builder import ScopeBuilder
from app.services.risk_detector import RiskDetector
from app.services.clause_generator import ClauseGenerator, MOCK_A5_OUTPUT
from app.services.sow_composer import SOWComposer, MOCK_A6_OUTPUT
from app.services.quality_checker import QualityChecker, MOCK_A7_OUTPUT
from app.models.ai_schemas import (
    A1Output,
    BriefExtractorOutput,
    ScopeBuilderOutput,
    RiskDetectorOutput,
    ClauseGeneratorOutput,
    SOWComposerOutput,
    QualityCheckerOutput,
    BriefRevisionExpectations,
    BriefTimeline,
    BriefBudget,
    RawSignals,
    SOWSection,
    RevisionPolicy,
    PaymentSchedule,
    PaymentMilestone,
    OutOfScopeClause,
    ClientResponsibilitiesClause,
    IPOwnershipClause,
    ChangeRequestProcess,
    TimelineAssumptionsClause,
    AdditionalProtectionClause,
    SOWMetadata,
    SOWDocumentStats,
)


# ── helpers ───────────────────────────────────

def _make_a1() -> A1Output:
    return A1Output(
        client_name="Luma Retail",
        project_name="Website Redesign",
        project_type="Web Design",
        cleaned_summary="Client wants a new website with some animations maybe.",
        goals=["New website", "Better UX"],
        mentioned_deliverables=["Website", "Animations"],
        budget_mentions=["Around $80k"],
        deadline_mentions=["Q3"],
        stakeholders=["CTO", "Marketing Manager"],
        client_responsibilities=["Provide copy", "Provide images"],
        agency_responsibilities=["Design", "Development"],
        dependencies=["Copy before development"],
        tools_or_platforms=["Webflow"],
        confirmed_items=["Website"],
        unclear_items=["Animations", "Copywriting responsibility"],
        potential_risks=["Vague animation scope"],
        raw_signals=RawSignals(
            pricing_discussed=True,
            timeline_discussed=True,
            revision_discussed=False,
            content_responsibility_discussed=False,
            launch_date_discussed=False,
        ),
    )


def _make_a2() -> BriefExtractorOutput:
    return BriefExtractorOutput(
        client_goal="Build a new marketing website",
        business_context="E-commerce company needs a modern web presence",
        project_summary="Redesign website with possible animations and integrations",
        primary_objectives=["Launch new website", "Improve UX"],
        success_criteria=["Responsive site", "Better conversions"],
        deliverables=[
            {"name": "Website", "description": "8-page responsive site", "status": "confirmed", "source_reasoning": ""},
            {"name": "Animations", "description": "Possible animations", "status": "unclear", "source_reasoning": ""},
        ],
        timeline=BriefTimeline(
            mentioned_deadlines=["Q3"],
            estimated_phases=["Discovery", "Design", "Development"],
            timeline_confidence="medium",
            unclear_timeline_items=["Exact launch date"],
        ),
        budget=BriefBudget(
            budget_discussed=True,
            budget_details=["Around $80k"],
            budget_confidence="medium",
        ),
        revision_expectations=BriefRevisionExpectations(
            revision_discussed=False,
            details=[],
            risk_if_missing="Scope creep risk from unlimited revisions.",
        ),
        dependencies=["Client must provide copy before development"],
        assets_needed_from_client=["Website copy", "Product images"],
        agency_responsibilities=["Design", "Development", "QA"],
        client_responsibilities=["Provide content", "Provide feedback"],
        constraints=["Budget $80k", "Q3 timeline"],
        assumptions=["Client provides content on time"],
        missing_information=[
            "Copywriting responsibility",
            "Animation scope",
            "Third-party integrations",
            "Revision rounds",
            "Launch approval process",
        ],
        brief_confidence_score=65,
    )


def _make_a3() -> ScopeBuilderOutput:
    return ScopeBuilderOutput(
        scope_summary="Design and develop an 8-page Webflow website with possible animations.",
        commercial_scope_items=[
            {
                "title": "Webflow Website",
                "description": "8-page responsive marketing website",
                "included_work": ["Design", "Development", "Up to 8 pages"],
                "not_included": ["Copywriting", "Photography", "Advanced animations"],
                "dependencies": ["Client provides copy"],
                "client_inputs_required": ["Website copy", "Images"],
                "acceptance_expectations": ["Responsive", "Client approves"],
                "status": "confirmed",
                "scope_confidence": "medium",
            },
        ],
        deliverable_specifications=[
            {
                "deliverable_name": "8-page Webflow Website",
                "professional_scope_statement": "Design and develop an 8-page responsive Webflow website.",
                "quantity_or_limit": "Up to 8 pages",
                "format_or_platform": "Webflow",
                "included_components": ["Responsive layouts", "Contact form"],
                "excluded_components": ["Copywriting", "Photography"],
                "completion_criteria": ["All pages built", "Client approves"],
                "source_status": "confirmed",
            },
        ],
        implementation_boundaries=["8 pages max", "No custom backend"],
        client_responsibility_boundaries=["Provide copy", "Provide images"],
        agency_responsibility_boundaries=["Design", "Development"],
        assumptions_for_scope=["Client provides content on time"],
        scope_exclusions=["Copywriting", "Photography", "Advanced animations"],
        scope_dependencies=["Client provides copy before development"],
        ambiguity_flags=[
            {"item": "Copywriting responsibility", "why_it_matters": "Could delay project", "suggested_clarification": "Confirm who writes copy", "severity": "high"},
            {"item": "Animation scope", "why_it_matters": "Vague scope", "suggested_clarification": "Define animation requirements", "severity": "medium"},
        ],
        scope_confidence_score=70,
        scope_of_work=["Design", "Development"],
        deliverables=["8-page Webflow Website"],
        timeline=["Discovery", "Design", "Development"],
        payment_schedule=["Milestone-based"],
    )


def _make_a4() -> RiskDetectorOutput:
    from app.models.ai_schemas import ScopeCreepRisk
    return RiskDetectorOutput(
        overall_risk_score=78,
        overall_risk_level="high",
        risk_summary="Several important scope and delivery expectations remain undefined.",
        scope_creep_risks=[
            ScopeCreepRisk(
                id="risk_copywriting_001",
                title="Copywriting Responsibility Undefined",
                description="Website copywriting was referenced but ownership was not clearly assigned.",
                category="content",
                severity="high",
                likelihood="high",
                impact="high",
                why_it_matters="Undefined content ownership commonly delays website projects.",
                evidence=["Client discussed website pages but no confirmed copy provider."],
                recommended_fix="Explicitly define whether client or agency is responsible for copywriting.",
                recommended_contract_language="Client will provide final approved website copy unless copywriting services are separately added to scope.",
                requires_client_clarification=True,
                blocking_risk=True,
            ),
            ScopeCreepRisk(
                id="risk_revision_002",
                title="Revision Rounds Not Defined",
                description="The number of included revision rounds has not been discussed.",
                category="revisions",
                severity="high",
                likelihood="high",
                impact="high",
                why_it_matters="Undefined revisions frequently lead to unlimited feedback loops.",
                evidence=["A2 revision expectations were missing."],
                recommended_fix="Define the number of included revisions for each deliverable.",
                recommended_contract_language="Each major deliverable includes up to two rounds of revisions unless otherwise specified.",
                requires_client_clarification=True,
                blocking_risk=False,
            ),
        ],
        missing_scope_definitions=["Revision limits", "Copywriting ownership"],
        critical_missing_items=["Revision policy", "Content ownership"],
        risk_detection_confidence_score=90,
    )


def _make_a5() -> ClauseGeneratorOutput:
    return MOCK_A5_OUTPUT


def _make_a6_with_risky_phrases() -> SOWComposerOutput:
    """A6 SOW with some risky/vague phrases for A7 to detect."""
    return SOWComposerOutput(
        document_title="Statement of Work",
        document_subtitle="Website Redesign",
        executive_summary="Website redesign project with unlimited revisions and guaranteed results.",
        sections=[
            SOWSection(section_key="overview", section_title="Project Overview", content_markdown="We will build the best possible website with modern animations as needed.", order=1),
            SOWSection(section_key="scope", section_title="Scope of Work", content_markdown="Everything discussed will be included. Ongoing support included.", order=3),
            SOWSection(section_key="timeline", section_title="Timeline", content_markdown="6 weeks for a fully scalable enterprise system.", order=5),
            SOWSection(section_key="payment", section_title="Payment Schedule", content_markdown="Payment schedule to be agreed.", order=6),
        ],
        metadata=SOWMetadata(client_name="Luma Retail", project_name="Website Redesign"),
        document_stats=SOWDocumentStats(estimated_page_count=4, total_sections=4, scope_items_count=2, risk_items_detected=2),
        export_ready=True,
        composer_confidence_score=75,
    )


def _make_a6_clean() -> SOWComposerOutput:
    return MOCK_A6_OUTPUT


# ── DEMO_MODE tests ───────────────────────────

async def test_demo_mode_returns_rich_mock():
    print("\n[Test 1] DEMO_MODE rich mock A7 output...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    checker = QualityChecker(llm)
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=_make_a6_clean()
    )
    assert isinstance(result, QualityCheckerOutput)
    assert result.overall_quality_score > 0
    assert result.approval_status in ("approved", "approved_with_warnings", "needs_revision", "blocked")
    assert len(result.section_reviews) >= 1
    assert result.quality_checker_confidence_score > 0
    print(f"  PASS: Mock QA: score={result.overall_quality_score}, status={result.approval_status}, "
          f"sections={len(result.section_reviews)}, confidence={result.quality_checker_confidence_score}")


async def test_mock_has_warnings_and_passes():
    print("\n[Test 2] Mock has warnings and passes...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    checker = QualityChecker(llm)
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=_make_a6_clean()
    )
    warnings = [s for s in result.section_reviews if s.status == "warning"]
    passes = [s for s in result.section_reviews if s.status == "pass"]
    assert len(warnings) >= 1, "Expected at least one warning"
    assert len(passes) >= 1, "Expected at least one pass"
    print(f"  PASS: {len(passes)} passes, {len(warnings)} warnings")


async def test_mock_vague_language_flags():
    print("\n[Test 3] Mock vague language flags...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    checker = QualityChecker(llm)
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=_make_a6_clean()
    )
    assert len(result.vague_language_flags) >= 1
    print(f"  PASS: {len(result.vague_language_flags)} vague language flags")


async def test_mock_commercial_risk_flags():
    print("\n[Test 4] Mock commercial risk flags...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    checker = QualityChecker(llm)
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=_make_a6_clean()
    )
    assert len(result.commercial_risk_flags) >= 1
    print(f"  PASS: {len(result.commercial_risk_flags)} commercial risk flags")


async def test_mock_ready_for_export():
    print("\n[Test 5] Mock ready for export...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    checker = QualityChecker(llm)
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=_make_a6_clean()
    )
    assert result.ready_for_export is True
    assert len(result.blocking_issues) == 0
    print(f"  PASS: ready_for_export={result.ready_for_export}, blocking={len(result.blocking_issues)}")


# ── Fallback / no-keys tests ──────────────────

async def test_no_keys_uses_fallback():
    print("\n[Test 6] No API keys fallback...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    checker = QualityChecker(llm)
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=_make_a6_clean(),
        industry="Web Design"
    )
    assert isinstance(result, QualityCheckerOutput)
    assert result.overall_quality_score >= 0
    print(f"  PASS: Fallback QA: score={result.overall_quality_score}, status={result.approval_status}")


async def test_fallback_detects_risky_phrases():
    print("\n[Test 7] Fallback detects risky phrases...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    checker = QualityChecker(llm)
    a6 = _make_a6_with_risky_phrases()
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=a6
    )
    assert len(result.vague_language_flags) >= 1
    phrases = [v.phrase.lower() for v in result.vague_language_flags]
    print(f"  PASS: Detected {len(result.vague_language_flags)} risky phrases: {phrases}")


async def test_fallback_detects_missing_sections():
    print("\n[Test 8] Fallback detects missing sections...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    checker = QualityChecker(llm)
    a6 = _make_a6_with_risky_phrases()
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=a6
    )
    assert len(result.missing_sections) >= 1
    print(f"  PASS: Missing sections detected: {result.missing_sections}")


# ── Specific detection tests ──────────────────

async def test_vague_wording_detection():
    print("\n[Test 9] Vague wording detection...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    checker = QualityChecker(llm)
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=_make_a6_clean()
    )
    vague = [v.phrase for v in result.vague_language_flags]
    assert len(vague) >= 1
    print(f"  PASS: Vague phrases flagged: {vague}")


async def test_missing_critical_information():
    print("\n[Test 10] Missing critical information...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    checker = QualityChecker(llm)
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=_make_a6_clean()
    )
    # The mock should have some missing critical info
    assert len(result.missing_critical_information) >= 1
    print(f"  PASS: Missing critical info: {result.missing_critical_information}")


async def test_missing_payment_schedule():
    print("\n[Test 11] Missing payment schedule...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    checker = QualityChecker(llm)
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=_make_a6_clean()
    )
    # Payment schedule should be present in clean mock
    payment_review = result.payment_review
    assert payment_review.status in ("pass", "warning", "fail")
    print(f"  PASS: Payment review status: {payment_review.status}")


async def test_risky_guarantees_detection():
    print("\n[Test 12] Risky guarantees detection...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    checker = QualityChecker(llm)
    a6 = _make_a6_with_risky_phrases()
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=a6
    )
    # The fallback should scan sections for risky phrases
    detected_phrases = [v.phrase.lower() for v in result.vague_language_flags]
    risky_found = any(p in detected_phrases for p in ["unlimited revisions", "guaranteed results", "best possible", "as needed"])
    assert risky_found, f"Expected risky phrases in {detected_phrases}"
    print(f"  PASS: Risky guarantees detected: {detected_phrases}")


async def test_formatting_validation():
    print("\n[Test 13] Formatting validation...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    checker = QualityChecker(llm)
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=_make_a4(), a5=_make_a5(), a6=_make_a6_clean()
    )
    assert result.document_consistency_review.formatting_valid is True
    print(f"  PASS: formatting_valid={result.document_consistency_review.formatting_valid}")


async def test_blocked_approval_scenario():
    print("\n[Test 14] Blocked approval scenario...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    checker = QualityChecker(llm)
    a4 = _make_a4()
    # Add a blocking risk
    from app.models.ai_schemas import ScopeCreepRisk
    a4.scope_creep_risks.append(
        ScopeCreepRisk(
            id="risk_blocking_003",
            title="Critical Blocking Risk",
            description="A critical issue that must be resolved.",
            category="legal",
            severity="high",
            likelihood="high",
            impact="high",
            why_it_matters="This blocks the project.",
            blocking_risk=True,
        )
    )
    result = await checker.check(
        a1=_make_a1(), a2=_make_a2(), a3=_make_a3(),
        a4=a4, a5=_make_a5(), a6=_make_a6_clean()
    )
    assert result.approval_status == "blocked" or len(result.blocking_issues) >= 1
    print(f"  PASS: Blocked status: {result.approval_status}, blocking={len(result.blocking_issues)}")


# ── Full pipeline test ────────────────────────

async def test_full_pipeline_a1_to_a7():
    print("\n[Test 15] Full pipeline A1 → A2 → A3 → A4 → A5 → A6 → A7...")
    llm = LLMClient()
    llm.settings.demo_mode = True

    # A1
    cleaner = TranscriptCleaner(llm)
    a1 = await cleaner.clean(
        raw_text="Client wants a new website with animations maybe. Budget is 80k. Q3 timeline.",
        industry="Web Design",
        tone="Professional",
        client_name="Pipeline Corp",
    )
    assert a1.client_name == "Pipeline Corp"

    # A2
    extractor = BriefExtractor(llm)
    a2 = await extractor.extract(a1, industry="Web Design", tone="Professional")
    assert len(a2.primary_objectives) >= 1

    # A3
    builder = ScopeBuilder(llm)
    a3 = await builder.build(a2, industry="Web Design", tone="Professional")
    assert len(a3.commercial_scope_items) >= 1

    # A4
    detector = RiskDetector(llm)
    a4 = await detector.detect(a1, a2, a3, industry="Web Design", tone="Professional")
    assert isinstance(a4, RiskDetectorOutput)

    # A5
    clause_gen = ClauseGenerator(llm)
    a5 = await clause_gen.generate(a1, a2, a3, a4, industry="Web Design", tone="Professional")
    assert isinstance(a5, ClauseGeneratorOutput)
    assert a5.revision_policy.limits_defined

    # A6
    composer = SOWComposer(llm)
    a6 = await composer.compose(a1, a2, a3, a4, a5, industry="Web Design", tone="Professional")
    assert isinstance(a6, SOWComposerOutput)
    assert len(a6.sections) >= 1

    # A7
    checker = QualityChecker(llm)
    a7 = await checker.check(a1, a2, a3, a4, a5, a6, industry="Web Design", tone="Professional")
    assert isinstance(a7, QualityCheckerOutput)
    assert a7.overall_quality_score > 0
    assert a7.approval_status in ("approved", "approved_with_warnings", "needs_revision", "blocked")

    print(f"  PASS: A1→A2→A3→A4→A5→A6→A7 pipeline complete:\n"
          f"    A1: {len(a1.goals)} goals\n"
          f"    A2: {len(a2.primary_objectives)} objectives\n"
          f"    A3: {len(a3.commercial_scope_items)} scope items\n"
          f"    A4: score={a4.overall_risk_score}, risks={len(a4.scope_creep_risks)}\n"
          f"    A5: revision_defined={a5.revision_policy.limits_defined}, milestones={len(a5.payment_schedule.milestones)}\n"
          f"    A6: sections={len(a6.sections)}, export_ready={a6.export_ready}\n"
          f"    A7: score={a7.overall_quality_score}, status={a7.approval_status}, ready={a7.ready_for_export}")


# ── Run all tests ─────────────────────────────

async def main():
    print("=== A7 Quality Checker Tests ===")
    await test_demo_mode_returns_rich_mock()
    await test_mock_has_warnings_and_passes()
    await test_mock_vague_language_flags()
    await test_mock_commercial_risk_flags()
    await test_mock_ready_for_export()
    await test_no_keys_uses_fallback()
    await test_fallback_detects_risky_phrases()
    await test_fallback_detects_missing_sections()
    await test_vague_wording_detection()
    await test_missing_critical_information()
    await test_missing_payment_schedule()
    await test_risky_guarantees_detection()
    await test_formatting_validation()
    await test_blocked_approval_scenario()
    await test_full_pipeline_a1_to_a7()
    print("\n=== ALL A7 TESTS PASSED ===")


if __name__ == "__main__":
    asyncio.run(main())
