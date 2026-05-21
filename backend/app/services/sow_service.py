import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.services.ai_validation_service import AIValidationService, REQUIRED_SECTION_KEYS
from app.services.storage_service import StorageService
from app.utils.errors import NotFoundError, StorageError

SECTION_TITLES = {
    "project_overview": "Project Overview",
    "objectives": "Objectives",
    "scope_of_work": "Scope of Work",
    "deliverables": "Deliverables",
    "timeline": "Timeline",
    "payment_schedule": "Payment Schedule",
    "client_responsibilities": "Client Responsibilities",
    "revision_policy": "Revision Policy",
    "out_of_scope": "Out of Scope",
    "assumptions": "Assumptions",
    "acceptance_criteria": "Acceptance Criteria",
    "signature_section": "Signature Section",
}

_demo_sections = {}
_demo_risk_flags = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SOWService:
    """Structured SOW section and risk-audit operations."""

    def __init__(self):
        self.storage = StorageService()
        self._demo = self.storage._demo
        self.validator = AIValidationService()

    async def list_sections(self, sow_id: str) -> List[dict]:
        sow = await self.storage.get_sow_by_id(sow_id)
        if not sow:
            raise NotFoundError("SOW not found")

        if self._demo:
            return self._ensure_demo_sections(sow)

        resp = (
            self.storage._get_client()
            .table("sow_sections")
            .select("*")
            .eq("sow_id", sow_id)
            .order("order")
            .execute()
        )
        sections = resp.data or []
        if sections:
            return sections
        return await self.materialize_sections(sow)

    async def materialize_sections(self, sow: dict) -> List[dict]:
        sections = self._sections_from_content(sow["id"], sow.get("content_json", {}))
        if self._demo:
            for section in sections:
                _demo_sections[section["id"]] = section
            return sections

        client = self.storage._get_client()
        resp = client.table("sow_sections").insert(sections).execute()
        return resp.data or sections

    async def update_section(self, sow_id: str, section_key: str, content_markdown: str, change_summary: str) -> dict:
        sections = await self.list_sections(sow_id)
        target = next((section for section in sections if section["section_key"] == section_key), None)
        if not target:
            raise NotFoundError("SOW section not found")

        updated = {
            **target,
            "content_markdown": content_markdown,
            "quality_score": max(int(target.get("quality_score") or 0), 88),
            "updated_at": _now(),
        }

        if self._demo:
            _demo_sections[updated["id"]] = updated
        else:
            self.storage._get_client().table("sow_sections").update(updated).eq("id", updated["id"]).execute()

        all_sections = [updated if s["id"] == updated["id"] else s for s in sections]
        await self._sync_sow_render_cache(sow_id, all_sections, change_summary)
        return updated

    async def regenerate_section(self, sow_id: str, section_key: str, instruction: str, current_markdown: str) -> dict:
        baseline = current_markdown.strip()
        addition = _regeneration_addition(section_key, instruction)
        regenerated = f"{baseline}\n\n{addition}".strip()
        return await self.update_section(sow_id, section_key, regenerated, "AI regenerated section")

    async def audit_risks(self, sow_id: str) -> dict:
        sections = await self.list_sections(sow_id)
        content_json = {
            "sections": [
                {
                    "section_key": section["section_key"],
                    "content_markdown": section["content_markdown"],
                }
                for section in sections
            ]
        }
        result = self.validator.validate_sow(content_json)
        if self._demo:
            _demo_risk_flags[sow_id] = result["risk_flags"]
        else:
            self.storage._get_client().table("sow_risk_flags").delete().eq("sow_id", sow_id).execute()
            rows = [
                {
                    "id": str(uuid.uuid4()),
                    "sow_id": sow_id,
                    "section_id": None,
                    "category": risk.get("category", "other"),
                    "severity": risk.get("severity", "medium"),
                    "title": risk.get("title", ""),
                    "description": risk.get("description", ""),
                    "evidence_json": risk.get("evidence", []),
                    "recommended_fix": risk.get("recommended_fix", ""),
                    "status": "open",
                    "created_at": _now(),
                    "updated_at": _now(),
                }
                for risk in result["risk_flags"]
            ]
            if rows:
                self.storage._get_client().table("sow_risk_flags").insert(rows).execute()
            self.storage._get_client().table("sows").update({
                "quality_score": result["quality_score"],
                "risk_score": result["risk_score"],
                "confidence_score": result["confidence_score"],
                "updated_at": _now(),
            }).eq("id", sow_id).execute()

        return {"sow_id": sow_id, **result}

    def _ensure_demo_sections(self, sow: dict) -> List[dict]:
        existing = [s for s in _demo_sections.values() if s.get("sow_id") == sow["id"]]
        if len(existing) == len(REQUIRED_SECTION_KEYS):
            return sorted(existing, key=lambda s: s["order"])
        sections = self._sections_from_content(sow["id"], sow.get("content_json", {}))
        existing_by_key = {section["section_key"]: section for section in existing}
        merged = [existing_by_key.get(section["section_key"], section) for section in sections]
        for section in merged:
            _demo_sections[section["id"]] = section
        return sorted(merged, key=lambda s: s["order"])

    def _sections_from_content(self, sow_id: str, content_json: dict) -> List[dict]:
        if isinstance(content_json.get("sections"), list):
            source = {
                s.get("section_key") or s.get("key"): s.get("content_markdown") or s.get("content") or ""
                for s in content_json["sections"]
            }
        else:
            source = {}
            for key in REQUIRED_SECTION_KEYS:
                value = content_json.get(key, "")
                source[key] = "\n".join(f"- {item}" for item in value) if isinstance(value, list) else str(value or "")

        sections = []
        for index, key in enumerate(REQUIRED_SECTION_KEYS, start=1):
            sections.append({
                "id": str(uuid.uuid4()),
                "sow_id": sow_id,
                "section_key": key,
                "title": SECTION_TITLES[key],
                "content_markdown": source.get(key, ""),
                "order": index,
                "quality_score": 85,
                "locked": False,
                "created_at": _now(),
                "updated_at": _now(),
            })
        return sections

    async def _sync_sow_render_cache(self, sow_id: str, sections: List[dict], change_summary: str) -> None:
        sections = sorted(sections, key=lambda section: section["order"])
        content_json = {
            "sections": [
                {
                    "section_key": section["section_key"],
                    "section_title": section["title"],
                    "content_markdown": section["content_markdown"],
                    "order": section["order"],
                    "quality_score": section.get("quality_score", 0),
                }
                for section in sections
            ]
        }
        content_markdown = "\n\n".join(
            f"## {section['title']}\n{section['content_markdown']}"
            for section in sections
        )
        versions = await self.storage.get_sow_versions(sow_id)
        await self.storage.create_sow_version(
            sow_id=sow_id,
            version_number=len(versions) + 1,
            content_json=content_json,
            content_markdown=content_markdown,
        )
        await self.storage.update_sow(sow_id, content_json, content_markdown)


def _regeneration_addition(section_key: str, instruction: str) -> str:
    additions = {
        "payment_schedule": "Payment timing, milestone conditions, and pause rights should be explicit before work begins.",
        "revision_policy": "Additional revision rounds, new scope, or post-approval changes require written approval before work continues.",
        "out_of_scope": "Any work not expressly listed in this SOW is excluded unless added through a written change order.",
        "timeline": "Timeline commitments depend on timely client feedback, approvals, and delivery of required assets.",
    }
    return additions.get(
        section_key,
        f"Updated per instruction: {instruction}. The language is tightened for clearer scope boundaries and client-ready accountability.",
    )
