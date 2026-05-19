"""Tests for A1 — Transcript Cleaner.

Covers:
- Input validation
- DEMO_MODE mock output
- LLM retry logic
- Fallback behavior on failure
- Output schema validation
- User override application
"""

import pytest
import asyncio
from app.services.llm_client import LLMClient
from app.services.transcript_cleaner import TranscriptCleaner, MOCK_A1_OUTPUT
from app.models.ai_schemas import A1Output, RawSignals


# ── fixtures ──────────────────────────────────

@pytest.fixture
def demo_llm():
    """LLM client in demo mode."""
    llm = LLMClient()
    # Force demo mode via settings
    llm.settings.demo_mode = True
    return llm


@pytest.fixture
def real_llm():
    """LLM client NOT in demo mode (no keys = will fallback)."""
    llm = LLMClient()
    llm.settings.demo_mode = False
    llm.settings.openai_api_key = ""
    llm.settings.anthropic_api_key = ""
    return llm


# ── DEMO_MODE tests ─────────────────────────────

@pytest.mark.asyncio
async def test_demo_mode_returns_rich_mock(demo_llm):
    cleaner = TranscriptCleaner(demo_llm)
    result = await cleaner.clean(
        raw_text="Some messy transcript about a website redesign project...",
        industry="Web Design",
        tone="Professional",
    )
    assert isinstance(result, A1Output)
    assert result.client_name == "Luma Retail Co."
    assert len(result.goals) >= 3
    assert len(result.mentioned_deliverables) >= 2
    assert len(result.unclear_items) >= 1
    assert result.raw_signals.timeline_discussed is True
    assert result.raw_signals.pricing_discussed is True


@pytest.mark.asyncio
async def test_user_overrides_applied_in_demo(demo_llm):
    cleaner = TranscriptCleaner(demo_llm)
    result = await cleaner.clean(
        raw_text="Any text...",
        industry="Marketing",
        tone="Friendly",
        client_name="Override Corp",
        project_name="Override Project",
    )
    assert result.client_name == "Override Corp"
    assert result.project_name == "Override Project"


# ── Real mode / fallback tests ──────────────────

@pytest.mark.asyncio
async def test_no_keys_uses_fallback(real_llm):
    """When no API keys are set, cleaner should still return valid A1Output."""
    cleaner = TranscriptCleaner(real_llm)
    result = await cleaner.clean(
        raw_text="We need a new website. Budget is 50k. Timeline is 6 weeks.",
        industry="Web Design",
        tone="Professional",
    )
    assert isinstance(result, A1Output)
    assert result.cleaned_summary != ""
    assert result.raw_signals.pricing_discussed is True
    assert result.raw_signals.timeline_discussed is True
    assert "extract failed" in result.unclear_items[0].lower()


@pytest.mark.asyncio
async def test_empty_transcript_fallback(real_llm):
    cleaner = TranscriptCleaner(real_llm)
    result = await cleaner.clean(
        raw_text="Short note.",
        industry="",
        tone="",
    )
    assert isinstance(result, A1Output)
    assert result.cleaned_summary == "Short note."


# ── Schema validation tests ───────────────────

def test_a1_output_schema_validation():
    """A1Output must accept the full example schema."""
    data = {
        "client_name": "Test",
        "project_name": "Test Project",
        "project_type": "Web",
        "cleaned_summary": "A test summary.",
        "goals": ["Goal 1"],
        "mentioned_deliverables": ["Deliverable 1"],
        "budget_mentions": ["$10k"],
        "deadline_mentions": ["2 weeks"],
        "stakeholders": ["CEO"],
        "client_responsibilities": ["Provide content"],
        "agency_responsibilities": ["Design"],
        "dependencies": ["Content needed"],
        "tools_or_platforms": ["Figma"],
        "confirmed_items": ["Website"],
        "unclear_items": ["Hosting"],
        "potential_risks": ["Timeline slip"],
        "raw_signals": {
            "pricing_discussed": True,
            "timeline_discussed": True,
            "revision_discussed": False,
            "content_responsibility_discussed": False,
            "launch_date_discussed": True,
        },
    }
    output = A1Output.model_validate(data)
    assert output.client_name == "Test"
    assert output.raw_signals.launch_date_discussed is True


def test_raw_signals_defaults():
    signals = RawSignals()
    assert signals.pricing_discussed is False
    assert signals.timeline_discussed is False


# ── Pipeline integration test ───────────────────

@pytest.mark.asyncio
async def test_a1_pipeline_integration():
    """A1 output can be consumed by A2 (Brief Extractor) downstream."""
    from app.services.brief_extractor import BriefExtractor

    llm = LLMClient()
    llm.settings.demo_mode = True

    cleaner = TranscriptCleaner(llm)
    a1 = await cleaner.clean(
        raw_text="Client wants a mobile app. Budget 100k. 3 months.",
        industry="App Development",
        tone="Professional",
        client_name="TechCo",
    )

    # A1 produces clean structured data
    assert a1.client_name == "TechCo"
    assert len(a1.goals) > 0

    # A2 can consume it
    extractor = BriefExtractor(llm)
    brief_raw = await extractor.extract(a1.cleaned_summary)
    assert isinstance(brief_raw, dict)
    assert "client_name" in brief_raw


# ── Run tests if executed directly ──────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
