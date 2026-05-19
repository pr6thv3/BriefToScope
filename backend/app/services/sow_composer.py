import json
from typing import Dict
from app.services.llm_client import LLMClient
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an SOW composer. Assemble all inputs into a polished Statement of Work document.
Return JSON with keys: project_overview (string), objectives (list), scope_of_work (list), deliverables (list), timeline (list), payment_schedule (list), client_responsibilities (list), revision_policy (string), out_of_scope (list), assumptions (list), acceptance_criteria (list), signature_section (string)."""


class SOWComposer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def compose(
        self, brief: Dict, scope: Dict, clauses: Dict, industry: str, tone: str
    ) -> Dict:
        prompt = f"""Industry: {industry}
Tone: {tone}
Brief:\n{json.dumps(brief, indent=2)}\n\nScope:\n{json.dumps(scope, indent=2)}\n\nClauses:\n{json.dumps(clauses, indent=2)}\n\nCompose the final SOW."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        try:
            raw = await self.llm.chat_completion(messages, temperature=0.3)
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("SOW composer returned non-JSON")
            return self._fallback_compose(brief, scope, clauses)
        except Exception as e:
            logger.error(f"SOW composition failed: {e}")
            return self._fallback_compose(brief, scope, clauses)

    def _fallback_compose(self, brief: Dict, scope: Dict, clauses: Dict) -> Dict:
        return {
            "project_overview": f"{brief.get('project_type', 'Project')} for {brief.get('client_name', 'Client')}.",
            "objectives": brief.get("goals", []),
            "scope_of_work": scope.get("scope_of_work", []),
            "deliverables": scope.get("deliverables", []),
            "timeline": scope.get("timeline", []),
            "payment_schedule": scope.get("payment_schedule", []),
            "client_responsibilities": clauses.get("client_responsibilities", []),
            "revision_policy": clauses.get("revision_policy", ""),
            "out_of_scope": clauses.get("out_of_scope", []),
            "assumptions": clauses.get("assumptions", []),
            "acceptance_criteria": clauses.get("acceptance_criteria", []),
            "signature_section": "[Signature section placeholder]",
        }
