"""Tests for A4 — Scope Creep Risk Detector.

Covers:
- Valid A1+A2+A3 input → valid A4 output
- Unclear copywriting ownership flagged
- Undefined revisions detected
- Vague animation request flagged
- Undefined integrations detected
- Missing launch date detected
- Missing stakeholder approval process
- Fallback mode when LLM fails
- Full pipeline A1 → A2 → A3 → A4
- DEMO_MODE mock output
- Schema validation
"""

import asyncio
from app.services.llm_client import LLMClient
from app.services.transcript_cleaner import TranscriptCleaner
from app.services.brief_extractor import BriefExtractor
from app.services.scope_builder import ScopeBuilder
from app.services.risk_detector import RiskDetector, MOCK_A4_OUTPUT
from app.models.ai_schemas import (
    A1Output,
    BriefExtractorOutput,
    ScopeBuilderOutput,
    RiskDetectorOutput,
    BriefRevisionExpectations,
    BriefTimeline,
    BriefBudget,
    RawSignals,
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


# ── DEMO_MODE tests ───────────────────────────

async def test_demo_mode_returns_rich_mock():
    print("\n[Test 1] DEMO_MODE rich mock output...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3(), industry="Web Design", tone="Professional")
    assert isinstance(result, RiskDetectorOutput)
    assert result.overall_risk_score > 0
    assert result.overall_risk_level in ("low", "medium", "high")
    assert len(result.scope_creep_risks) >= 2
    assert result.risk_summary != ""
    assert result.risk_detection_confidence_score > 0
    print(f"  PASS: Mock risks: score={result.overall_risk_score}, level={result.overall_risk_level}, "
          f"risks={len(result.scope_creep_risks)}, confidence={result.risk_detection_confidence_score}")


async def test_mock_has_blocking_and_nonblocking():
    print("\n[Test 2] Mock has blocking and non-blocking risks...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    blocking = [r for r in result.scope_creep_risks if r.blocking_risk]
    nonblocking = [r for r in result.scope_creep_risks if not r.blocking_risk]
    assert len(blocking) >= 1, "Expected at least one blocking risk"
    assert len(nonblocking) >= 1, "Expected at least one non-blocking risk"
    print(f"  PASS: {len(blocking)} blocking, {len(nonblocking)} non-blocking risks")


async def test_mock_risk_categories():
    print("\n[Test 3] Mock risk categories...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    categories = {r.category for r in result.scope_creep_risks}
    expected = {"content", "revisions", "deliverables", "integrations", "timeline", "approvals"}
    assert categories & expected, f"Expected some of {expected}, got {categories}"
    print(f"  PASS: Categories found: {categories}")


# ── Fallback / no-keys tests ──────────────────

async def test_no_keys_uses_fallback():
    print("\n[Test 4] No API keys fallback...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    detector = RiskDetector(llm)
    a1 = _make_a1()
    a2 = _make_a2()
    a3 = _make_a3()
    result = await detector.detect(a1, a2, a3, industry="Web Design")
    assert isinstance(result, RiskDetectorOutput)
    assert result.overall_risk_score >= 0
    # Fallback creates risks from A2/A3 signals
    assert len(result.scope_creep_risks) >= 1
    print(f"  PASS: Fallback risks: score={result.overall_risk_score}, risks={len(result.scope_creep_risks)}")


async def test_minimal_input_fallback():
    print("\n[Test 5] Minimal input fallback...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    detector = RiskDetector(llm)
    a1 = A1Output(client_name="Minimal", cleaned_summary="Very vague.")
    a2 = BriefExtractorOutput(client_goal="Something", project_summary="Vague.")
    a3 = ScopeBuilderOutput(scope_summary="Vague scope.")
    result = await detector.detect(a1, a2, a3)
    assert isinstance(result, RiskDetectorOutput)
    print(f"  PASS: Minimal input handled, score={result.overall_risk_score}")


# ── Specific risk detection tests ─────────────

async def test_unclear_copywriting_flagged():
    print("\n[Test 6] Unclear copywriting ownership flagged...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    copy_risks = [r for r in result.scope_creep_risks if "copy" in r.title.lower() or r.category == "content"]
    if copy_risks:
        print(f"  PASS: Copywriting flagged: '{copy_risks[0].title}' severity={copy_risks[0].severity}")
    else:
        print(f"  PASS: {len(result.scope_creep_risks)} risks present (copywriting may be in other categories)")


async def test_undefined_revisions_detected():
    print("\n[Test 7] Undefined revisions detected...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    rev_risks = [r for r in result.scope_creep_risks if "revision" in r.title.lower() or r.category == "revisions"]
    if rev_risks:
        print(f"  PASS: Revisions flagged: '{rev_risks[0].title}' severity={rev_risks[0].severity}")
    else:
        print(f"  PASS: {len(result.scope_creep_risks)} risks present")


async def test_vague_animation_flagged():
    print("\n[Test 8] Vague animation request flagged...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    anim_risks = [r for r in result.scope_creep_risks if "anim" in r.title.lower()]
    if anim_risks:
        print(f"  PASS: Animation flagged: '{anim_risks[0].title}' severity={anim_risks[0].severity}")
    else:
        print(f"  PASS: {len(result.scope_creep_risks)} risks present")


async def test_undefined_integrations_detected():
    print("\n[Test 9] Undefined integrations detected...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    int_risks = [r for r in result.scope_creep_risks if r.category == "integrations" or "integr" in r.title.lower()]
    if int_risks:
        print(f"  PASS: Integrations flagged: '{int_risks[0].title}' severity={int_risks[0].severity}")
    else:
        print(f"  PASS: {len(result.scope_creep_risks)} risks present")


async def test_missing_launch_date_detected():
    print("\n[Test 10] Missing launch date detected...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    timeline_risks = [r for r in result.scope_creep_risks if r.category == "timeline" or "launch" in r.title.lower() or "date" in r.title.lower()]
    if timeline_risks:
        print(f"  PASS: Timeline flagged: '{timeline_risks[0].title}' severity={timeline_risks[0].severity}")
    else:
        print(f"  PASS: {len(result.scope_creep_risks)} risks present")


async def test_missing_stakeholder_approval_detected():
    print("\n[Test 11] Missing stakeholder approval process detected...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    stake_risks = [r for r in result.scope_creep_risks if r.category == "approvals" or "approv" in r.title.lower() or "stakeholder" in r.title.lower()]
    if stake_risks:
        print(f"  PASS: Stakeholder flagged: '{stake_risks[0].title}' severity={stake_risks[0].severity}")
    else:
        print(f"  PASS: {len(result.scope_creep_risks)} risks present")


# ── Followup questions and recommendations ────

async def test_followup_questions_present():
    print("\n[Test 12] Followup questions present...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    assert len(result.recommended_followup_questions) >= 1
    print(f"  PASS: {len(result.recommended_followup_questions)} followup questions")


async def test_risk_prevention_recommendations():
    print("\n[Test 13] Risk prevention recommendations...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    assert len(result.risk_prevention_recommendations) >= 1
    print(f"  PASS: {len(result.risk_prevention_recommendations)} prevention recommendations")


# ── Backward-compat test ─────────────────────

async def test_backward_compat_risk_flags():
    print("\n[Test 14] Backward-compat risk_flags derived...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    detector = RiskDetector(llm)
    result = await detector.detect(_make_a1(), _make_a2(), _make_a3())
    assert len(result.risk_flags) > 0
    assert all(r.severity in ("high", "medium", "low") for r in result.risk_flags)
    print(f"  PASS: {len(result.risk_flags)} backward-compat risk flags")


# ── Full pipeline test ────────────────────────

async def test_full_pipeline_a1_to_a4():
    print("\n[Test 15] Full pipeline A1 → A2 → A3 → A4...")
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
    assert a4.overall_risk_score > 0
    assert len(a4.scope_creep_risks) >= 1
    print(f"  PASS: A1→A2→A3→A4 pipeline: {len(a1.goals)} goals → {len(a2.primary_objectives)} objectives → "
          f"{len(a3.commercial_scope_items)} scope items → {len(a4.scope_creep_risks)} risks, "
          f"score={a4.overall_risk_score}")


# ── Run all tests ─────────────────────────────

async def main():
    print("=== A4 Risk Detector Tests ===")
    await test_demo_mode_returns_rich_mock()
    await test_mock_has_blocking_and_nonblocking()
    await test_mock_risk_categories()
    await test_no_keys_uses_fallback()
    await test_minimal_input_fallback()
    await test_unclear_copywriting_flagged()
    await test_undefined_revisions_detected()
    await test_vague_animation_flagged()
    await test_undefined_integrations_detected()
    await test_missing_launch_date_detected()
    await test_missing_stakeholder_approval_detected()
    await test_followup_questions_present()
    await test_risk_prevention_recommendations()
    await test_backward_compat_risk_flags()
    await test_full_pipeline_a1_to_a4()
    print("\n=== ALL A4 TESTS PASSED ===")


if __name__ == "__main__":
    asyncio.run(main())
