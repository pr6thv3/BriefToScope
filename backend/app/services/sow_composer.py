"""A6 — SOW Composer.

Assembles A1–A5 outputs into a polished, client-facing Statement of Work document
with Markdown-formatted sections.  Uses structured JSON-mode LLM calls with
retry and fallback.
"""

import json
from typing import Any, Dict
from datetime import datetime, timezone
from app.services.llm_client import LLMClient
from app.utils.logger import get_logger
from app.models.ai_schemas import (
    SOWComposerOutput,
    SOWSection,
    SOWMetadata,
    SOWDocumentStats,
)

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are a senior agency Statement of Work composer. "
    "Your job is to transform structured project intelligence into a polished, client-facing Statement of Work.\n\n"
    "Rules:\n"
    "- Write professionally and clearly.\n"
    "- Avoid robotic AI wording.\n"
    "- Maintain commercial clarity.\n"
    "- Preserve scope boundaries.\n"
    "- Use structured formatting.\n"
    "- Keep language readable and premium.\n"
    "- Avoid fake legal jargon.\n"
    "- Maintain consistency across sections.\n"
    "- Reference earlier risk protections naturally.\n"
    "- Ensure all sections feel cohesive.\n"
    "- Output valid JSON only."
)

_MOCK_SOW_SECTIONS = [
    SOWSection(
        section_key="overview",
        section_title="Project Overview",
        content_markdown="This project includes the development of a refreshed brand identity and an 8-page Webflow marketing website for Luma Retail Co. The goal is to improve brand trust, modernize the company’s digital presence, and support customer conversion through a more professional online experience.",
        order=1,
    ),
    SOWSection(
        section_key="objectives",
        section_title="Objectives",
        content_markdown="- Refresh the company’s visual identity\n- Launch a responsive Webflow website\n- Improve trust and conversion\n- Create scalable brand assets",
        order=2,
    ),
    SOWSection(
        section_key="scope",
        section_title="Scope of Work",
        content_markdown="The agency will provide:\n- Brand strategy workshop\n- Logo identity system\n- Brand guidelines\n- Responsive Webflow website design and development\n- Up to 8 website pages\n\nExcluded:\n- Copywriting\n- Photography\n- Advanced custom integrations\n- Ongoing maintenance",
        order=3,
    ),
    SOWSection(
        section_key="deliverables",
        section_title="Deliverables",
        content_markdown="### Brand Identity Package\n- Logo system\n- Color palette\n- Typography system\n- Brand guidelines PDF\n\n### Website\n- Responsive Webflow website\n- Contact form setup\n- Basic SEO structure\n- CMS configuration if required",
        order=4,
    ),
    SOWSection(
        section_key="timeline",
        section_title="Timeline",
        content_markdown="Estimated project timeline: 6 weeks.\n\nPhases:\n1. Discovery & Strategy\n2. Brand Identity Design\n3. Website Design\n4. Webflow Development\n5. Review & Launch\n\nTimeline assumes timely delivery of client content and approvals.",
        order=5,
    ),
    SOWSection(
        section_key="payment",
        section_title="Payment Schedule",
        content_markdown="- 50% upfront before project kickoff\n- 25% upon design approval\n- 25% before final launch",
        order=6,
    ),
    SOWSection(
        section_key="client_responsibilities",
        section_title="Client Responsibilities",
        content_markdown="Client agrees to:\n- Provide website copy\n- Provide photography/assets\n- Review deliverables promptly\n- Consolidate stakeholder feedback",
        order=7,
    ),
    SOWSection(
        section_key="revision_policy",
        section_title="Revision Policy",
        content_markdown="Each major deliverable includes up to two rounds of revisions unless otherwise specified.\n\nAdditional revisions may require additional billing.",
        order=8,
    ),
    SOWSection(
        section_key="out_of_scope",
        section_title="Out of Scope",
        content_markdown="The following are excluded unless separately approved:\n- Copywriting\n- Photography\n- Advanced animations\n- Third-party integrations\n- Ongoing maintenance",
        order=9,
    ),
    SOWSection(
        section_key="assumptions",
        section_title="Assumptions",
        content_markdown="- Client provides all required assets on schedule\n- Stakeholder approvals are completed within agreed review windows",
        order=10,
    ),
    SOWSection(
        section_key="acceptance_criteria",
        section_title="Acceptance Criteria",
        content_markdown="Project completion is considered achieved once:\n- All approved deliverables are completed\n- Website is responsive and functional\n- Final payment is received",
        order=11,
    ),
    SOWSection(
        section_key="signature",
        section_title="Signature Section",
        content_markdown="Client Representative:\n_____________________\n\nAgency Representative:\n_____________________\n\nDate:\n_____________________",
        order=12,
    ),
]

MOCK_A6_OUTPUT = SOWComposerOutput(
    document_title="Statement of Work",
    document_subtitle="Brand Identity + Webflow Website",
    executive_summary="A comprehensive brand refresh and 8-page Webflow website for Luma Retail Co., designed to modernize the digital presence and improve customer conversion.",
    sections=_MOCK_SOW_SECTIONS,
    metadata=SOWMetadata(
        client_name="Luma Retail",
        project_name="Brand Identity + Webflow Website",
        industry="Web Design",
        tone="Professional",
        generated_date=datetime.now(timezone.utc).isoformat(),
        document_version="1.0",
        prepared_by="BriefToScope AI",
    ),
    document_stats=SOWDocumentStats(
        estimated_page_count=6,
        total_sections=12,
        scope_items_count=5,
        risk_items_detected=6,
    ),
    export_ready=True,
    composer_confidence_score=92,
    project_overview="Brand Identity + Webflow Website for Luma Retail Co.",
    objectives=["Refresh visual identity", "Launch responsive Webflow website", "Improve trust and conversion", "Create scalable brand assets"],
    scope_of_work=["Brand strategy workshop", "Logo identity system", "Brand guidelines", "Responsive Webflow website design and development", "Up to 8 website pages"],
    deliverables=["Logo system", "Color palette", "Typography system", "Brand guidelines PDF", "Responsive Webflow website", "Contact form setup", "Basic SEO structure", "CMS configuration"],
    timeline=["Discovery & Strategy", "Brand Identity Design", "Website Design", "Webflow Development", "Review & Launch"],
    payment_schedule=["50% upfront before project kickoff", "25% upon design approval", "25% before final launch"],
    client_responsibilities=["Provide website copy", "Provide photography/assets", "Review deliverables promptly", "Consolidate stakeholder feedback"],
    revision_policy="Each major deliverable includes up to two rounds of revisions unless otherwise specified. Additional revisions may require additional billing.",
    out_of_scope=["Copywriting", "Photography", "Advanced animations", "Third-party integrations", "Ongoing maintenance"],
    assumptions=["Client provides all required assets on schedule", "Stakeholder approvals are completed within agreed review windows"],
    acceptance_criteria=["All approved deliverables are completed", "Website is responsive and functional", "Final payment is received"],
    signature_section="Client Representative: _____________________ Agency Representative: _____________________ Date: _____________________",
)


class SOWComposer:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def compose(
        self,
        a1: Any,
        a2: Any,
        a3: Any,
        a4: Any,
        a5: Any,
        industry: str = "",
        tone: str = "Professional",
    ) -> SOWComposerOutput:
        logger.info("[A6] SOW composition STARTED")
        logger.info(f"[A6] Input validated: industry={industry}, tone={tone}")

        if self.llm.settings.demo_mode:
            logger.info("[A6] DEMO_MODE: returning rich mock A6 output")
            return MOCK_A6_OUTPUT

        if not self.llm.settings.openai_api_key and not self.llm.settings.anthropic_api_key:
            logger.warning("[A6] No API keys configured — using fallback SOW")
            return self._fallback_compose(a1, a2, a3, a4, a5)

        prompt = self._build_prompt(a1, a2, a3, a4, a5, industry, tone)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        last_error: Exception | None = None
        for attempt in range(1, 3):
            try:
                raw = await self.llm.chat_completion(
                    messages,
                    temperature=0.3,
                    response_format={"type": "json_object"},
                    max_retries=1,
                )
                data = json.loads(raw)
                result = SOWComposerOutput.model_validate(data)
                logger.info(
                    f"[A6] SOW composition COMPLETED: sections={len(result.sections)}, "
                    f"export_ready={result.export_ready}, "
                    f"confidence={result.composer_confidence_score}"
                )
                return result
            except (json.JSONDecodeError, Exception) as e:
                last_error = e
                logger.warning(f"[A6] Attempt {attempt}/2 failed: {e}")

        logger.error(f"[A6] SOW composition FAILED after retries: {last_error}")
        return self._fallback_compose(a1, a2, a3, a4, a5)

    def _build_prompt(
        self, a1: Any, a2: Any, a3: Any, a4: Any, a5: Any, industry: str, tone: str
    ) -> str:
        def _dump(obj: Any) -> str:
            return json.dumps(obj.model_dump() if hasattr(obj, "model_dump") else dict(obj), indent=2, default=str)

        return (
            f"Industry: {industry}\n"
            f"Tone: {tone}\n\n"
            f"A1 Transcript Cleaner output:\n{_dump(a1)}\n\n"
            f"A2 Brief Extractor output:\n{_dump(a2)}\n\n"
            f"A3 Scope Builder output:\n{_dump(a3)}\n\n"
            f"A4 Risk Detector output:\n{_dump(a4)}\n\n"
            f"A5 Clause Generator output:\n{_dump(a5)}\n\n"
            "Generate the SOWComposerOutput JSON.\n"
            "Include document_title, document_subtitle, executive_summary, sections (array of SOWSection with section_key, section_title, content_markdown, order), "
            "metadata (client_name, project_name, industry, tone, generated_date, document_version, prepared_by), "
            "document_stats (estimated_page_count, total_sections, scope_items_count, risk_items_detected), "
            "export_ready, and composer_confidence_score."
        )

    def _fallback_compose(self, a1: Any, a2: Any, a3: Any, a4: Any, a5: Any) -> SOWComposerOutput:
        logger.warning("[A6] Using fallback SOW composition")
        client_name = ""
        project_name = ""
        if a1 and hasattr(a1, "client_name"):
            client_name = a1.client_name or ""
        if a1 and hasattr(a1, "project_name"):
            project_name = a1.project_name or ""

        objectives = a2.primary_objectives if a2 and hasattr(a2, "primary_objectives") else []
        scope_items = a3.commercial_scope_items if a3 and hasattr(a3, "commercial_scope_items") else []
        deliverables = a3.deliverable_specifications if a3 and hasattr(a3, "deliverable_specifications") else []
        risks = a4.scope_creep_risks if a4 and hasattr(a4, "scope_creep_risks") else []

        sections = [
            SOWSection(section_key="overview", section_title="Project Overview", content_markdown=f"Project for {client_name}.", order=1),
            SOWSection(section_key="objectives", section_title="Objectives", content_markdown="\n".join(f"- {o}" for o in objectives) or "- Define project objectives", order=2),
            SOWSection(section_key="scope", section_title="Scope of Work", content_markdown="\n".join(f"- {s.title}: {s.description}" for s in scope_items) or "- Scope to be defined", order=3),
            SOWSection(section_key="deliverables", section_title="Deliverables", content_markdown="\n".join(f"- {d.deliverable_name}" for d in deliverables) or "- Deliverables to be defined", order=4),
            SOWSection(section_key="timeline", section_title="Timeline", content_markdown="Timeline to be agreed upon.", order=5),
            SOWSection(section_key="payment", section_title="Payment Schedule", content_markdown="Payment schedule to be agreed upon.", order=6),
            SOWSection(section_key="client_responsibilities", section_title="Client Responsibilities", content_markdown="Client agrees to provide required inputs and timely feedback.", order=7),
            SOWSection(section_key="revision_policy", section_title="Revision Policy", content_markdown="Each major deliverable includes up to two rounds of revisions unless otherwise specified.", order=8),
            SOWSection(section_key="out_of_scope", section_title="Out of Scope", content_markdown="Work outside the defined scope requires separate approval.", order=9),
            SOWSection(section_key="assumptions", section_title="Assumptions", content_markdown="Project assumes timely delivery of client inputs and approvals.", order=10),
            SOWSection(section_key="acceptance_criteria", section_title="Acceptance Criteria", content_markdown="Project completion achieved once all approved deliverables are delivered.", order=11),
            SOWSection(section_key="signature", section_title="Signature Section", content_markdown="Client Representative: _____________________ Agency Representative: _____________________ Date: _____________________", order=12),
        ]

        return SOWComposerOutput(
            document_title="Statement of Work",
            document_subtitle=project_name or "Project",
            executive_summary=f"Statement of Work for {client_name} — {project_name}.",
            sections=sections,
            metadata=SOWMetadata(
                client_name=client_name,
                project_name=project_name,
                generated_date=datetime.now(timezone.utc).isoformat(),
                prepared_by="BriefToScope AI",
            ),
            document_stats=SOWDocumentStats(
                estimated_page_count=len(sections),
                total_sections=len(sections),
                scope_items_count=len(scope_items),
                risk_items_detected=len(risks),
            ),
            export_ready=True,
            composer_confidence_score=70,
            project_overview=f"Project for {client_name}.",
            objectives=objectives,
            scope_of_work=[s.title for s in scope_items],
            deliverables=[d.deliverable_name for d in deliverables],
            timeline=["To be agreed"],
            payment_schedule=["To be agreed"],
            client_responsibilities=["Provide required inputs", "Timely feedback"],
            revision_policy="Each major deliverable includes up to two rounds of revisions unless otherwise specified.",
            out_of_scope=["Work outside defined scope"],
            assumptions=["Timely client inputs"],
            acceptance_criteria=["All approved deliverables completed"],
            signature_section="Client Representative: _____________________ Agency Representative: _____________________ Date: _____________________",
        )
