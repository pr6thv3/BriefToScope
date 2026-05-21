from typing import Any, Dict, List


REQUIRED_SECTION_KEYS = [
    "project_overview",
    "objectives",
    "scope_of_work",
    "deliverables",
    "timeline",
    "payment_schedule",
    "client_responsibilities",
    "revision_policy",
    "out_of_scope",
    "assumptions",
    "acceptance_criteria",
    "signature_section",
]


class AIValidationService:
    """Deterministic quality gate after AI generation.

    This does not replace A7. It creates production-defensible checks that are
    stable, cheap, and easy to explain to users.
    """

    def validate_sow(self, content_json: Dict[str, Any]) -> Dict[str, Any]:
        sections = self._section_map(content_json)
        missing_sections = [
            key for key in REQUIRED_SECTION_KEYS
            if not sections.get(key, "").strip()
        ]

        missing_items: List[str] = []
        vague_phrases: List[str] = []
        risk_flags: List[dict] = []

        if not sections.get("timeline"):
            missing_items.append("Timeline")
            risk_flags.append(self._risk("timeline", "medium", "Timeline Missing", "No concrete timeline or phase structure is defined."))
        if not sections.get("payment_schedule"):
            missing_items.append("Payment schedule")
            risk_flags.append(self._risk("budget", "high", "Payment Schedule Missing", "Payment timing and milestone conditions are not defined."))
        if "revision" not in sections.get("revision_policy", "").lower():
            missing_items.append("Revision limits")
            risk_flags.append(self._risk("revisions", "medium", "Revision Limits Undefined", "The revision policy does not clearly limit rounds or change requests."))
        if not sections.get("client_responsibilities"):
            missing_items.append("Client responsibilities")
        if not sections.get("acceptance_criteria"):
            missing_items.append("Acceptance criteria")

        document_text = "\n".join(sections.values()).lower()
        for phrase in ["as needed", "ongoing support", "etc.", "unlimited", "later"]:
            if phrase in document_text:
                vague_phrases.append(phrase)

        quality_score = max(45, 100 - len(missing_items) * 8 - len(vague_phrases) * 4 - len(missing_sections) * 3)
        risk_score = min(100, len(risk_flags) * 18 + len(vague_phrases) * 5 + len(missing_items) * 7)

        return {
            "quality_score": quality_score,
            "risk_score": risk_score,
            "confidence_score": round(quality_score / 100, 2),
            "missing_sections": missing_sections,
            "missing_items": missing_items,
            "vague_phrases": vague_phrases,
            "risk_flags": risk_flags,
            "ready_for_export": quality_score >= 75 and not any(r["severity"] == "high" for r in risk_flags),
        }

    def _section_map(self, content_json: Dict[str, Any]) -> Dict[str, str]:
        if isinstance(content_json.get("sections"), list):
            return {
                section.get("section_key") or section.get("key", ""): section.get("content_markdown") or section.get("content", "")
                for section in content_json["sections"]
            }
        values = {}
        for key in REQUIRED_SECTION_KEYS:
            value = content_json.get(key, "")
            values[key] = "\n".join(value) if isinstance(value, list) else str(value or "")
        return values

    def _risk(self, category: str, severity: str, title: str, description: str) -> dict:
        return {
            "category": category,
            "severity": severity,
            "title": title,
            "description": description,
            "recommended_fix": "Clarify this point before sending the SOW to the client.",
            "status": "open",
        }

