import json
from typing import Any, Dict, Optional
import httpx
from app.config import get_settings
from app.utils.logger import get_logger
from app.utils.errors import AIServiceError
from app.services.demo_data import (
    get_fallback_sow,
    get_fallback_brief,
    get_fallback_risks,
    get_fallback_clauses,
)

logger = get_logger(__name__)


class LLMClient:
    def __init__(self):
        self.settings = get_settings()
        self._client = httpx.AsyncClient(timeout=120.0)

    async def chat_completion(
        self,
        messages: list,
        model: str = "gpt-4o",
        temperature: float = 0.3,
        response_format: Optional[dict] = None,
        max_retries: int = 2,
    ) -> str:
        """Send a chat completion with retry logic and provider fallbacks.

        Priority: DEMO_MODE -> OpenAI -> Anthropic -> mock fallback.
        """
        if self.settings.demo_mode:
            logger.info("[LLM] DEMO_MODE: returning mock response")
            return self._mock_response(messages)

        last_error: Optional[Exception] = None

        # Try OpenAI
        api_key = self.settings.openai_api_key
        if api_key:
            for attempt in range(1, max_retries + 1):
                try:
                    return await self._openai_call(messages, model, temperature, response_format)
                except Exception as e:
                    last_error = e
                    logger.warning(f"[LLM] OpenAI attempt {attempt}/{max_retries} failed: {e}")
            logger.warning("[LLM] OpenAI exhausted retries, trying Anthropic...")

        # Try Anthropic
        api_key = self.settings.anthropic_api_key
        if api_key:
            for attempt in range(1, max_retries + 1):
                try:
                    return await self._anthropic_call(messages, model, temperature)
                except Exception as e:
                    last_error = e
                    logger.warning(f"[LLM] Anthropic attempt {attempt}/{max_retries} failed: {e}")
            logger.warning("[LLM] Anthropic exhausted retries.")

        logger.warning("[LLM] No provider succeeded. Using mock fallback.")
        return self._mock_response(messages)

    async def _openai_call(
        self, messages: list, model: str, temperature: float, response_format: Optional[dict]
    ) -> str:
        api_key = self.settings.openai_api_key
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format:
            payload["response_format"] = response_format

        logger.debug(f"[LLM] OpenAI request: model={model}, temp={temperature}")
        resp = await self._client.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        logger.debug(f"[LLM] OpenAI response received: {len(content)} chars")
        return content

    async def _anthropic_call(
        self, messages: list, model: str, temperature: float
    ) -> str:
        api_key = self.settings.anthropic_api_key
        url = "https://api.anthropic.com/v1/messages"
        system_msg = ""
        user_messages = []
        for m in messages:
            if m.get("role") == "system":
                system_msg = m.get("content", "")
            else:
                user_messages.append(m)

        payload = {
            "model": model if "claude" in model else "claude-3-sonnet-20240229",
            "max_tokens": 4096,
            "temperature": temperature,
            "messages": user_messages,
        }
        if system_msg:
            payload["system"] = system_msg

        logger.debug(f"[LLM] Anthropic request: model={payload['model']}, temp={temperature}")
        resp = await self._client.post(
            url,
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["content"][0]["text"]
        logger.debug(f"[LLM] Anthropic response received: {len(content)} chars")
        return content

    def _mock_response(self, messages: list) -> str:
        """Return context-aware mock JSON based on prompt content."""
        # Check all messages (system + user) for step identification
        full_text = " ".join(m.get("content", "") for m in messages).lower()
        user_text = messages[-1].get("content", "")
        lower = user_text.lower()

        # A1 — Transcript Cleaner
        if "senior agency discovery-call analyst" in full_text or "clean messy client call notes" in full_text:
            from app.services.transcript_cleaner import MOCK_A1_OUTPUT
            return json.dumps(MOCK_A1_OUTPUT.model_dump())

        # A2 — Brief Extractor
        if "senior agency brief strategist" in full_text or "brief strategist" in full_text:
            from app.services.brief_extractor import MOCK_A2_OUTPUT
            return json.dumps(MOCK_A2_OUTPUT.model_dump())

        # Legacy A2 detection
        if "extract brief" in lower:
            return json.dumps({
                "client_name": "Acme Corp",
                "project_type": "Web Redesign",
                "goals": ["Modernize website", "Improve conversions"],
                "deliverables": ["Homepage", "Product pages"],
                "budget_mentions": ["$50k"],
                "deadline_mentions": ["Q3"],
                "unclear_items": ["CMS choice"],
            })

        # A3 — Scope Builder
        if "senior agency scope strategist" in full_text or "scope strategist" in full_text:
            from app.services.scope_builder import MOCK_A3_OUTPUT
            return json.dumps(MOCK_A3_OUTPUT.model_dump())

        # Legacy A3 detection
        if "build the scope" in lower:
            return json.dumps({
                "scope_of_work": ["UI/UX design", "Frontend development"],
                "deliverables": ["Figma files", "React components"],
                "timeline": ["Week 1-2: Discovery", "Week 3-6: Design"],
                "payment_schedule": ["50% upfront", "50% on delivery"],
            })

        # A4 — Risk Detector
        if "identify risks" in lower:
            return json.dumps({
                "risk_flags": [
                    {
                        "severity": "medium",
                        "title": "Unclear CMS requirements",
                        "description": "Client has not specified preferred CMS.",
                        "suggested_fix": "Clarify CMS and platform requirements.",
                    }
                ]
            })

        # A5 — Clause Generator
        if "generate clauses" in lower:
            return json.dumps({
                "revision_policy": "Two rounds of revisions included.",
                "out_of_scope": ["Content creation", "SEO"],
                "assumptions": ["Client provides brand assets"],
                "acceptance_criteria": ["All pages approved via Figma comments"],
                "client_responsibilities": ["Provide brand assets", "Provide content"],
            })

        # A6 — SOW Composer
        if "compose the final sow" in lower or ("compose the final" in lower and "clauses" in lower):
            return json.dumps({
                "project_overview": "Redesign Acme Corp website for improved UX.",
                "objectives": ["Increase conversion rate", "Improve mobile experience"],
                "scope_of_work": ["Discovery", "UI/UX design", "Frontend dev"],
                "deliverables": ["Design system", "React components"],
                "timeline": ["Discovery: 2 weeks", "Design: 4 weeks", "Dev: 6 weeks"],
                "payment_schedule": ["50% upfront", "50% on delivery"],
                "client_responsibilities": ["Provide brand assets", "Provide content"],
                "revision_policy": "Two rounds of revisions included.",
                "out_of_scope": ["Content creation", "SEO"],
                "assumptions": ["Client provides brand assets within 3 days"],
                "acceptance_criteria": ["All pages approved via Figma"],
                "signature_section": "[Signature blocks]",
            })

        # A7 — Quality Checker
        if "rate quality" in lower:
            return json.dumps({"confidence_score": 0.85, "suggestions": ["Add more timeline detail"]})

        # Default: full SOW fallback
        return json.dumps(get_fallback_sow())

    async def close(self):
        await self._client.aclose()
