import json
from typing import Dict
from app.services.llm_client import LLMClient
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a legal clause assistant for SOW documents. Generate standard clauses based on project details.
Return JSON with keys: revision_policy (string), out_of_scope (list), assumptions (list), acceptance_criteria (list), client_responsibilities (list)."""


class ClauseGenerator:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def generate(self, brief: Dict, scope: Dict, industry: str) -> Dict:
        prompt = f"""Industry: {industry}
Brief:\n{json.dumps(brief, indent=2)}\n\nScope:\n{json.dumps(scope, indent=2)}\n\nGenerate clauses."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        try:
            raw = await self.llm.chat_completion(messages, temperature=0.3)
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Clause generator returned non-JSON")
            return {
                "revision_policy": "Two rounds of revisions included.",
                "out_of_scope": [],
                "assumptions": [],
                "acceptance_criteria": [],
                "client_responsibilities": [],
            }
        except Exception as e:
            logger.error(f"Clause generation failed: {e}")
            return {
                "revision_policy": "Two rounds of revisions included.",
                "out_of_scope": [],
                "assumptions": [],
                "acceptance_criteria": [],
                "client_responsibilities": [],
            }
