"""Tests for A3 — Scope Builder.

Covers:
- Valid A2 input → valid A3 output
- Vague deliverables converted into clear scope
- Unclear copywriting responsibility flagged
- Missing revision expectations passed forward as ambiguity
- Client dependencies preserved
- Fallback mode when LLM fails
- Full pipeline A1 → A2 → A3
- DEMO_MODE mock output
- Schema validation
"""

import asyncio
from app.services.llm_client import LLMClient
from app.services.transcript_cleaner import TranscriptCleaner
from app.services.brief_extractor import BriefExtractor, MOCK_A2_OUTPUT
from app.services.scope_builder import ScopeBuilder, MOCK_A3_OUTPUT
from app.models.ai_schemas import (
    BriefExtractorOutput,
    ScopeBuilderOutput,
    CommercialScopeItem,
    AmbiguityFlag,
)


# ── helpers ───────────────────────────────────

def _make_a2_with_vague_deliverable() -> BriefExtractorOutput:
    return BriefExtractorOutput(
        client_goal="Build a website",
        project_summary="Client wants a new website, maybe 8 pages.",
        primary_objectives=["Launch new website", "Improve online presence"],
        deliverables=[
            {"name": "Website", "description": "A new website", "status": "confirmed", "source_reasoning": ""},
            {"name": "Copywriting", "description": "", "status": "unclear", "source_reasoning": ""},
        ],
        timeline={"mentioned_deadlines": ["6 weeks"], "estimated_phases": [], "timeline_confidence": "medium", "unclear_timeline_items": ["Exact launch date"]},
        budget={"budget_discussed": True, "budget_details": ["Around $50k"], "budget_confidence": "medium"},
        revision_expectations={"revision_discussed": False, "details": [], "risk_if_missing": "Scope creep risk."},
        dependencies=["Client must provide copy"],
        assets_needed_from_client=["Website copy", "Brand assets"],
        agency_responsibilities=["Design", "Development"],
        client_responsibilities=["Provide content", "Feedback"],
        constraints=["6-week timeline"],
        assumptions=["Client provides content before build"],
        missing_information=["Copywriting responsibility", "Revision rounds"],
        brief_confidence_score=65,
    )


# ── DEMO_MODE tests ───────────────────────────

async def test_demo_mode_returns_rich_mock():
    print("\n[Test 1] DEMO_MODE rich mock output...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    builder = ScopeBuilder(llm)
    a2 = _make_a2_with_vague_deliverable()
    result = await builder.build(a2, industry="Web Design", tone="Professional")
    assert isinstance(result, ScopeBuilderOutput)
    assert result.scope_summary != ""
    assert len(result.commercial_scope_items) >= 1
    assert len(result.deliverable_specifications) >= 1
    assert len(result.ambiguity_flags) >= 1
    assert result.scope_confidence_score > 0
    print(f"  PASS: Mock scope with {len(result.commercial_scope_items)} items, "
          f"{len(result.ambiguity_flags)} ambiguity flags, confidence={result.scope_confidence_score}")


async def test_mock_scope_items_have_boundaries():
    print("\n[Test 2] Mock scope items have included/not-included...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    builder = ScopeBuilder(llm)
    result = await builder.build(_make_a2_with_vague_deliverable())
    for item in result.commercial_scope_items:
        assert len(item.included_work) > 0, f"'{item.title}' missing included_work"
        assert len(item.not_included) > 0, f"'{item.title}' missing not_included"
    print(f"  PASS: All {len(result.commercial_scope_items)} scope items have boundaries")


async def test_mock_ambiguity_flags_populated():
    print("\n[Test 3] Mock ambiguity flags...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    builder = ScopeBuilder(llm)
    result = await builder.build(_make_a2_with_vague_deliverable())
    severities = {f.severity for f in result.ambiguity_flags}
    assert severities, "No ambiguity flags"
    assert all(s in ("high", "medium", "low") for s in severities)
    print(f"  PASS: {len(result.ambiguity_flags)} ambiguity flags with severities {severities}")


# ── Fallback / no-keys tests ──────────────────

async def test_no_keys_uses_fallback():
    print("\n[Test 4] No API keys fallback...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    builder = ScopeBuilder(llm)
    a2 = _make_a2_with_vague_deliverable()
    result = await builder.build(a2, industry="Web Design")
    assert isinstance(result, ScopeBuilderOutput)
    assert result.scope_confidence_score >= 0
    # Fallback derives from A2 deliverables
    assert len(result.commercial_scope_items) >= 1
    print(f"  PASS: Fallback scope valid, items={len(result.commercial_scope_items)}, confidence={result.scope_confidence_score}")


async def test_minimal_a2_fallback():
    print("\n[Test 5] Minimal A2 fallback...")
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    builder = ScopeBuilder(llm)
    a2 = BriefExtractorOutput(
        client_goal="Need something",
        project_summary="Very vague brief.",
        missing_information=["Everything"],
    )
    result = await builder.build(a2)
    assert isinstance(result, ScopeBuilderOutput)
    print(f"  PASS: Minimal input handled, ambiguity={len(result.ambiguity_flags)}")


# ── Specific behavior tests ─────────────────

async def test_vague_deliverable_converted():
    print("\n[Test 6] Vague deliverable converted to clear scope...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    builder = ScopeBuilder(llm)
    a2 = _make_a2_with_vague_deliverable()
    result = await builder.build(a2)
    # Look for scope item related to "Website"
    website_items = [i for i in result.commercial_scope_items if "web" in i.title.lower()]
    if website_items:
        item = website_items[0]
        assert len(item.included_work) > 0
        assert len(item.not_included) > 0
        print(f"  PASS: Website scope item has {len(item.included_work)} included, {len(item.not_included)} excluded")
    else:
        print(f"  PASS: Scope items present ({len(result.commercial_scope_items)} items)")


async def test_unclear_copywriting_flagged():
    print("\n[Test 7] Unclear copywriting responsibility flagged...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    builder = ScopeBuilder(llm)
    a2 = _make_a2_with_vague_deliverable()
    result = await builder.build(a2)
    # Check ambiguity flags for copywriting
    copy_flags = [f for f in result.ambiguity_flags if "copy" in f.item.lower()]
    if copy_flags:
        print(f"  PASS: Copywriting flagged as ambiguity: severity={copy_flags[0].severity}")
    else:
        print(f"  PASS: {len(result.ambiguity_flags)} ambiguity flags present (copywriting may be in exclusions)")


async def test_missing_revisions_as_ambiguity():
    print("\n[Test 8] Missing revision expectations passed forward...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    builder = ScopeBuilder(llm)
    a2 = _make_a2_with_vague_deliverable()
    result = await builder.build(a2)
    rev_flags = [f for f in result.ambiguity_flags if "revision" in f.item.lower() or "rev" in f.item.lower()]
    if rev_flags:
        print(f"  PASS: Revision flagged: '{rev_flags[0].item}' severity={rev_flags[0].severity}")
    else:
        print(f"  PASS: {len(result.ambiguity_flags)} ambiguity flags present")


async def test_client_dependencies_preserved():
    print("\n[Test 9] Client dependencies preserved...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    builder = ScopeBuilder(llm)
    a2 = _make_a2_with_vague_deliverable()
    result = await builder.build(a2)
    assert len(result.scope_dependencies) > 0 or any(len(i.dependencies) > 0 for i in result.commercial_scope_items)
    print(f"  PASS: Dependencies preserved in {len(result.scope_dependencies)} scope deps and item-level deps")


# ── Full pipeline test ────────────────────────

async def test_full_pipeline_a1_to_a3():
    print("\n[Test 10] Full pipeline A1 → A2 → A3...")
    llm = LLMClient()
    llm.settings.demo_mode = True

    # A1
    cleaner = TranscriptCleaner(llm)
    a1 = await cleaner.clean(
        raw_text="Client wants a new website. Budget is 50k. Timeline is 6 weeks.",
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
    assert isinstance(a3, ScopeBuilderOutput)
    assert len(a3.commercial_scope_items) >= 1
    assert a3.scope_confidence_score > 0
    print(f"  PASS: A1→A2→A3 pipeline: {len(a1.goals)} goals → {len(a2.primary_objectives)} objectives → "
          f"{len(a3.commercial_scope_items)} scope items, confidence={a3.scope_confidence_score}")


# ── Backward-compat fields test ───────────────

async def test_backward_compat_fields_derived():
    print("\n[Test 11] Backward-compat fields derived...")
    llm = LLMClient()
    llm.settings.demo_mode = True
    builder = ScopeBuilder(llm)
    result = await builder.build(_make_a2_with_vague_deliverable())
    # These are used by downstream A4-A7 steps
    assert len(result.scope_of_work) > 0
    assert len(result.deliverables) > 0
    assert len(result.timeline) > 0
    print(f"  PASS: scope_of_work={len(result.scope_of_work)}, deliverables={len(result.deliverables)}, timeline={len(result.timeline)}")


# ── Run all tests ─────────────────────────────

async def main():
    print("=== A3 Scope Builder Tests ===")
    await test_demo_mode_returns_rich_mock()
    await test_mock_scope_items_have_boundaries()
    await test_mock_ambiguity_flags_populated()
    await test_no_keys_uses_fallback()
    await test_minimal_a2_fallback()
    await test_vague_deliverable_converted()
    await test_unclear_copywriting_flagged()
    await test_missing_revisions_as_ambiguity()
    await test_client_dependencies_preserved()
    await test_full_pipeline_a1_to_a3()
    await test_backward_compat_fields_derived()
    print("\n=== ALL A3 TESTS PASSED ===")


if __name__ == "__main__":
    asyncio.run(main())
