import time
from typing import Any, Dict

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMTraceService:
    """Small provider-neutral trace hook for Langfuse/Helicone-compatible metadata.

    This intentionally avoids a hard dependency. When env vars are present we
    attach Helicone headers and write structured trace logs that can be forwarded
    by the runtime log drain or replaced by a Langfuse SDK later.
    """

    def __init__(self):
        self.settings = get_settings()

    def request_headers(self, provider: str, model: str) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.settings.helicone_api_key and provider == "openai":
            headers.update(
                {
                    "Helicone-Auth": f"Bearer {self.settings.helicone_api_key}",
                    "Helicone-Property-App": "BriefToScope",
                    "Helicone-Property-Model": model,
                }
            )
        return headers

    def start(self, provider: str, model: str) -> float:
        if self.settings.langfuse_public_key or self.settings.helicone_api_key:
            logger.info("[LLM_TRACE] start provider=%s model=%s", provider, model)
        return time.perf_counter()

    def finish(self, provider: str, model: str, started_at: float, metadata: Dict[str, Any] | None = None) -> None:
        if self.settings.langfuse_public_key or self.settings.helicone_api_key:
            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            logger.info(
                "[LLM_TRACE] finish provider=%s model=%s latency_ms=%s metadata=%s",
                provider,
                model,
                elapsed_ms,
                metadata or {},
            )
