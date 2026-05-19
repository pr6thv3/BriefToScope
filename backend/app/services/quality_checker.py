import json
from typing import Dict
from app.services.llm_client import LLMClient
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a quality assurance assistant for SOW documents. Review a completed SOW and rate its quality.
Return JSON with key confidence_score (float 0.0-1.0) and optional suggestions (list of strings)."""


class QualityChecker:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def check(self, sow: Dict, brief: Dict) -> Dict:
        prompt = f"""Brief:\n{json.dumps(brief, indent=2)}\n\nSOW:\n{json.dumps(sow, indent=2)}\n\nRate quality and return confidence score."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        try:
            raw = await self.llm.chat_completion(messages, temperature=0.2)
            data = json.loads(raw)
            score = float(data.get("confidence_score", 0.75))
            return {"confidence_score": max(0.0, min(1.0, score)), "suggestions": data.get("suggestions", [])}
        except (json.JSONDecodeError, ValueError):
            logger.warning("Quality checker returned non-JSON")
            return {"confidence_score": 0.75, "suggestions": []}
        except Exception as e:
            logger.error(f"Quality check failed: {e}")
            return {"confidence_score": 0.75, "suggestions": []}
