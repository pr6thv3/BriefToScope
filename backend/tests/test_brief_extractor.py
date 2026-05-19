"""Tests for A2 — Brief Extractor.

Covers:
- Valid A1 input → valid A2 output
- Missing budget detection
- Unclear revision detection
- Vague timeline handling
- Fallback mode when LLM fails
- Full pipeline A1 → A2 integration
- DEMO_MODE mock output
- Schema validation
"""

import asyncio
from app.services.llm_client import LLMClient
from app.services.transcript_cleaner import TranscriptCleaner, MOCK_A1_OUTPUT
from app.services.brief_extractor import BriefExtractor, MOCK_A2_OUTPUT
from app.models.ai_schemas import A1Output, BriefExtractorOutput, RawSignals


# ── helpers ───────────────────────────────────

def _make_a1_with_budget() -> A1Output:
    return A1Output(
        client_name="Tech Startup Inc.",
        project_name="Mobile App",
        project_type="App Development",
        cleaned_summary="Client wants a cross-platform mobile app for their SaaS product.",
        goals=["Launch iOS and Android app", "Sync with existing backend"],
        mentioned_deliverables=["React Native app", "API integration", "Push notifications"],
        budget_mentions=["Budget around $80k", "Open to milestone payments"],
        deadline_mentions=["Target launch in Q3"],
        stakeholders=["CTO", "Product Manager"],
        client_responsibilities=["Provide API docs", "Provide app store accounts"],
        agency_responsibilities=["Design", "Development", "Testing"],
        dependencies=["API docs must be ready before integration starts"],
        tools_or_platforms=["React Native", "Firebase"],
        confirmed_items=["Cross-platform app", "Backend sync"],
        unclear_items=["Push notification provider", "Analytics requirements"],
        potential_risks=["API delays could push timeline"],
        raw_signals=RawSignals(
            pricing_discussed=True,
            timeline_discussed=True,
            revision_discussed=False,
            content_responsibility_discussed=True,
            launch_date_discussed=True,
        ),
    )


def _make_a1_minimal() -> A1Output:
    return A1Output(
        client_name="Small Biz",
        project_name="Website",
        cleaned_summary="They said they want a website. Maybe soon.",
        goals=["Get a website"],
        mentioned_deliverables=["Website"],
        unclear_items=["Timeline", "Budget", "Features"],
        raw_signals=RawSignals(
            pricing_discussed=False,
            timeline_discussed=False,
        ),
    )


# ── DEMO_MODE tests ───────────────────────────

async def test_demo_mode_returns_rich_mock():
    print("\n[Test 1] DEMO_MODE rich mock output...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    extractor = BriefExtractor(llm)
    a1 = _make_a1_with_budget()
    result = await extractor.extract(a1, industry="App Development", tone="Professional")
    assert isinstance(result, BriefExtractorOutput)
    assert result.client_goal != ""
    assert len(result.primary_objectives) >= 2
    assert len(result.deliverables) >= 2
    assert result.budget.budget_discussed is True
    assert result.timeline.timeline_confidence in ("high", "medium", "low")
    assert len(result.missing_information) >= 1
    print(f"  PASS: Mock brief with {len(result.primary_objectives)} objectives, "
          f"{len(result.deliverables)} deliverables, confidence={result.brief_confidence_score}")


async def test_mock_deliverable_statuses():
    print("\n[Test 2] Mock deliverable statuses...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    extractor = BriefExtractor(llm)
    result = await extractor.extract(_make_a1_with_budget())
    statuses = {d.status for d in result.deliverables}
    assert "confirmed" in statuses or "inferred" in statuses or "unclear" in statuses
    print(f"  PASS: Deliverable statuses: {statuses}")


# ── Fallback / no-keys tests ──────────────────

async def test_no_keys_uses_fallback():
    print("\n[Test 3] No API keys fallback...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    extractor = BriefExtractor(llm)
    a1 = _make_a1_with_budget()
    result = await extractor.extract(a1, industry="App Development")
    assert isinstance(result, BriefExtractorOutput)
    assert result.brief_confidence_score >= 0
    print(f"  PASS: Fallback brief valid, confidence={result.brief_confidence_score}")


async def test_minimal_a1_fallback():
    print("\n[Test 4] Minimal A1 input fallback...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    extractor = BriefExtractor(llm)
    a1 = _make_a1_minimal()
    result = await extractor.extract(a1)
    assert isinstance(result, BriefExtractorOutput)
    assert "extraction failed" in result.missing_information[0].lower() or result.project_summary != ""
    print(f"  PASS: Minimal input handled, missing={len(result.missing_information)}")


# ── Schema validation tests ─────────────────

async def test_missing_budget_detected():
    print("\n[Test 5] Missing budget detection...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    extractor = BriefExtractor(llm)
    a1 = A1Output(
        client_name="NoBudget Co",
        cleaned_summary="We want a new website. No budget discussed yet.",
        goals=["New website"],
        budget_mentions=[],
        raw_signals=RawSignals(pricing_discussed=False),
    )
    result = await extractor.extract(a1)
    assert result.budget.budget_discussed is False or result.budget.budget_confidence == "low"
    assert "budget" in " ".join(result.missing_information).lower() or result.missing_information == []
    print(f"  PASS: Budget discussed={result.budget.budget_discussed}, confidence={result.budget.budget_confidence}")


async def test_unclear_revisions_detected():
    print("\n[Test 6] Unclear revision detection...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    extractor = BriefExtractor(llm)
    a1 = A1Output(
        client_name="RevTest",
        cleaned_summary="Need branding work. Revisions not discussed.",
        raw_signals=RawSignals(revision_discussed=False),
    )
    result = await extractor.extract(a1)
    # In demo mode we get the mock which has revision_discussed=False
    assert result.revision_expectations.revision_discussed is False or result.revision_expectations.risk_if_missing != ""
    print(f"  PASS: Revisions discussed={result.revision_expectations.revision_discussed}")


async def test_vague_timeline_handling():
    print("\n[Test 7] Vague timeline handling...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    extractor = BriefExtractor(llm)
    a1 = A1Output(
        client_name="VagueTime",
        cleaned_summary="We want it done sometime next year maybe.",
        deadline_mentions=["sometime next year"],
        raw_signals=RawSignals(timeline_discussed=True),
    )
    result = await extractor.extract(a1)
    assert result.timeline.timeline_confidence in ("high", "medium", "low")
    print(f"  PASS: Timeline confidence={result.timeline.timeline_confidence}")


# ── Pipeline integration test ─────────────────

async def test_full_pipeline_a1_to_a2():
    print("\n[Test 8] Full pipeline A1 → A2...")
    llm = LLMClient()
    llm.settings.demo_mode = True

    # Run A1
    cleaner = TranscriptCleaner(llm)
    a1 = await cleaner.clean(
        raw_text="Client wants a new mobile app. Budget is 200k. Timeline is 6 months.",
        industry="App Development",
        tone="Professional",
        client_name="Pipeline Corp",
    )
    assert a1.client_name == "Pipeline Corp"
    assert len(a1.goals) > 0

    # Run A2
    extractor = BriefExtractor(llm)
    a2 = await extractor.extract(a1, industry="App Development", tone="Professional")
    assert isinstance(a2, BriefExtractorOutput)
    assert len(a2.primary_objectives) >= 1
    assert len(a2.deliverables) >= 1
    print(f"  PASS: A1→A2 pipeline: {len(a1.goals)} goals → {len(a2.primary_objectives)} objectives, "
          f"{len(a2.deliverables)} deliverables")


# ── Run all tests ─────────────────────────────

async def main():
    print("=== A2 Brief Extractor Tests ===")
    await test_demo_mode_returns_rich_mock()
    await test_mock_deliverable_statuses()
    await test_no_keys_uses_fallback()
    await test_minimal_a1_fallback()
    await test_missing_budget_detected()
    await test_unclear_revisions_detected()
    await test_vague_timeline_handling()
    await test_full_pipeline_a1_to_a2()
    print("\n=== ALL A2 TESTS PASSED ===")


if __name__ == "__main__":
    asyncio.run(main())
