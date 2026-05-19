import json
from typing import Dict, List
from app.services.llm_client import LLMClient
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a contract risk analyst. Review a project brief and scope to identify potential risks, ambiguities, and red flags.
Return JSON with key risk_flags (list of objects with severity: high|medium|low, title, description, suggested_fix)."""


class RiskDetector:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def detect(self, brief: Dict, scope: Dict) -> List[Dict]:
        prompt = f"""Brief:\n{json.dumps(brief, indent=2)}\n\nScope:\n{json.dumps(scope, indent=2)}\n\nIdentify risks."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        try:
            raw = await self.llm.chat_completion(messages, temperature=0.3)
            data = json.loads(raw)
            return data.get("risk_flags", [])
        except json.JSONDecodeError:
            logger.warning("Risk detector returned non-JSON")
            return []
        except Exception as e:
            logger.error(f"Risk detection failed: {e}")
            return []
