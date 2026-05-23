"""A5 — Clause Generator.

Generates commercially safe, agency-grade contract-style clauses based on
A1–A4 outputs.  Uses structured JSON-mode LLM calls with retry and fallback.
"""

import json
from typing import Any, Dict
from app.services.llm_client import LLMClient
from app.utils.logger import get_logger
from app.models.ai_schemas import (
    ClauseGeneratorOutput,
    RevisionPolicy,
    PaymentSchedule,
    PaymentMilestone,
    OutOfScopeClause,
    ClientResponsibilitiesClause,
    IPOwnershipClause,
    ChangeRequestProcess,
    TimelineAssumptionsClause,
    AdditionalProtectionClause,
)

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are a senior agency contract operations strategist. "
    "Your job is to generate commercially professional SOW clauses that reduce scope creep, "
    "revision abuse, timeline disputes, unclear ownership, payment issues, and delivery ambiguity. "
    "You are not acting as a lawyer.\n\n"
    "Rules:\n"
    "- Generate commercially practical language.\n"
    "- Use agency-grade professional wording.\n"
    "- Tailor clauses based on project risks and scope.\n"
    "- Reference detected risks from A4.\n"
    "- Add protections only when justified.\n"
    "- Do not overcomplicate language.\n"
    "- Avoid fake legal jargon.\n"
    "- Output valid JSON only."
)

MOCK_A5_OUTPUT = ClauseGeneratorOutput(
    revision_policy=RevisionPolicy(
        summary="Defines included revision rounds and handling of additional revisions.",
        clauses=[
            "Each major deliverable includes up to two rounds of revisions unless otherwise specified.",
            "Additional revisions beyond the included rounds may require a separate scope adjustment or additional billing.",
        ],
        limits_defined=True,
    ),
    payment_schedule=PaymentSchedule(
        summary="Milestone-based payment structure aligned to delivery phases.",
        milestones=[
            PaymentMilestone(label="Project Initiation", percentage="50%", condition="Due before project kickoff."),
            PaymentMilestone(label="Design Approval", percentage="25%", condition="Due upon approval of brand and website designs."),
            PaymentMilestone(label="Final Delivery", percentage="25%", condition="Due before final launch or transfer of deliverables."),
        ],
        late_payment_clause="Project timelines may pause if invoices remain unpaid beyond the agreed payment period.",
        payment_assumptions=["All invoices are payable within 7 days unless otherwise agreed."],
    ),
    out_of_scope_clause=OutOfScopeClause(
        summary="Defines excluded work and additional-request handling.",
        excluded_items=["Copywriting", "Photography", "Advanced custom animations", "Third-party integrations", "Post-launch maintenance"],
        formal_clause="Any work outside the explicitly defined scope may require a separate estimate, timeline adjustment, or written change request approval.",
    ),
    client_responsibilities_clause=ClientResponsibilitiesClause(
        summary="Defines client obligations for successful project delivery.",
        responsibilities=[
            "Provide final website copy",
            "Provide photography/assets",
            "Review deliverables in a timely manner",
            "Provide consolidated stakeholder feedback",
        ],
        formal_clause="Client delays in providing required content, approvals, or feedback may impact project timelines.",
    ),
    ip_ownership_clause=IPOwnershipClause(
        summary="Defines ownership transfer conditions.",
        ownership_model="Ownership transfers upon final payment.",
        formal_clause="Final approved deliverables become the property of the client upon receipt of full project payment.",
    ),
    change_request_process=ChangeRequestProcess(
        summary="Defines handling of new requests or scope changes.",
        workflow_steps=[
            "Client submits requested change",
            "Agency reviews impact on scope, timeline, and cost",
            "Agency provides updated estimate",
            "Work proceeds only after written approval",
        ],
        formal_clause="Requests outside the approved scope may require additional fees and timeline adjustments.",
    ),
    timeline_assumptions_clause=TimelineAssumptionsClause(
        summary="Defines assumptions affecting project timelines.",
        assumptions=[
            "Client provides required content on schedule",
            "Stakeholder approvals are completed within agreed review windows",
        ],
        delay_conditions=["Late content delivery", "Delayed approvals", "Additional revision cycles"],
        formal_clause="Project timelines are dependent on timely client communication, approvals, and delivery of required assets.",
    ),
    additional_protection_clauses=[
        AdditionalProtectionClause(
            title="Approval Consolidation",
            reason="Multiple stakeholder feedback loops were identified as a delivery risk.",
            formal_clause="Client agrees to provide consolidated stakeholder feedback during each review phase.",
        ),
    ],
    clause_generation_confidence_score=88,
    revision_policy_text="Each major deliverable includes up to two rounds of revisions unless otherwise specified.",
    out_of_scope=["Copywriting", "Photography", "Advanced custom animations", "Third-party integrations", "Post-launch maintenance"],
    assumptions=["Client provides all required assets on schedule", "Stakeholder approvals are completed within agreed review windows"],
    acceptance_criteria=["All approved deliverables are completed", "Website is responsive and functional", "Final payment is received"],
    client_responsibilities=["Provide final website copy", "Provide photography/assets", "Review deliverables promptly", "Provide consolidated stakeholder feedback"],
)


class ClauseGenerator:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def generate(
        self,
        a1: Any,
        a2: Any,
        a3: Any,
        a4: Any,
        industry: str = "",
        tone: str = "Professional",
    ) -> ClauseGeneratorOutput:
        logger.info("[A5] Clause generation STARTED")
        logger.info(f"[A5] Input validated: industry={industry}, tone={tone}")

        if self.llm.settings.demo_mode:
            logger.info("[A5] DEMO_MODE: returning rich mock A5 output")
            return MOCK_A5_OUTPUT

        if not self.llm.settings.openai_api_key and not self.llm.settings.anthropic_api_key:
            logger.warning("[A5] No API keys configured — using fallback clauses")
            return self._fallback_generate(a2, a3, a4)

        prompt = self._build_prompt(a1, a2, a3, a4, industry, tone)
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
                result = ClauseGeneratorOutput.model_validate(data)
                logger.info(
                    f"[A5] Clause generation COMPLETED: confidence={result.clause_generation_confidence_score}, "
                    f"revision_defined={result.revision_policy.limits_defined}, "
                    f"milestones={len(result.payment_schedule.milestones)}, "
                    f"protections={len(result.additional_protection_clauses)}"
                )
                return result
            except (json.JSONDecodeError, Exception) as e:
                last_error = e
                logger.warning(f"[A5] Attempt {attempt}/2 failed: {e}")

        logger.error(f"[A5] Clause generation FAILED after retries: {last_error}")
        return self._fallback_generate(a2, a3, a4)

    def _build_prompt(
        self, a1: Any, a2: Any, a3: Any, a4: Any, industry: str, tone: str
    ) -> str:
        a1_json = json.dumps(a1.model_dump() if hasattr(a1, "model_dump") else dict(a1), indent=2, default=str)
        a2_json = json.dumps(a2.model_dump() if hasattr(a2, "model_dump") else dict(a2), indent=2, default=str)
        a3_json = json.dumps(a3.model_dump() if hasattr(a3, "model_dump") else dict(a3), indent=2, default=str)
        a4_json = json.dumps(a4.model_dump() if hasattr(a4, "model_dump") else dict(a4), indent=2, default=str)
        
        clause_library_str = ""
        if industry:
            try:
                from app.services.ai_data_service import AIDataService
                ai_data = AIDataService()
                clauses = ai_data.get_clause_library(industry)
                template = ai_data.get_industry_template(industry)
                clause_library_str = (
                    f"\nUse the following industry-specific clauses from our pre-approved Clause Library as references/starters:\n"
                    f"Revision Clauses: {json.dumps(clauses.revision)}\n"
                    f"Payment Clauses: {json.dumps(clauses.payment)}\n"
                    f"Out of Scope Clauses: {json.dumps(clauses.out_of_scope)}\n"
                    f"Client Responsibility Clauses: {json.dumps(clauses.client_responsibilities)}\n"
                    f"IP Ownership Clauses: {json.dumps(clauses.ip_ownership)}\n"
                    f"Change Request Clauses: {json.dumps(clauses.change_request)}\n"
                    f"Timeline Clauses: {json.dumps(clauses.timeline)}\n"
                    f"Hidden Scope Traps To Protect Against: {json.dumps(template.hidden_scope_traps)}\n"
                )
            except Exception as e:
                logger.warning(f"[A5] Failed to load clause library context for prompt enrichment: {e}")
                
        return (
            f"Industry: {industry}\n"
            f"Tone: {tone}\n\n"
            f"{clause_library_str}\n"
            f"A1 Transcript Cleaner output:\n{a1_json}\n\n"
            f"A2 Brief Extractor output:\n{a2_json}\n\n"
            f"A3 Scope Builder output:\n{a3_json}\n\n"
            f"A4 Risk Detector output:\n{a4_json}\n\n"
            "Generate the ClauseGeneratorOutput JSON.\n"
            "Include revision_policy, payment_schedule, out_of_scope_clause, "
            "client_responsibilities_clause, ip_ownership_clause, change_request_process, "
            "timeline_assumptions_clause, additional_protection_clauses, and clause_generation_confidence_score."
        )

    def _fallback_generate(self, a2: Any, a3: Any, a4: Any) -> ClauseGeneratorOutput:
        logger.warning("[A5] Using fallback clause generation")
        output = ClauseGeneratorOutput(
            revision_policy=RevisionPolicy(
                summary="Standard revision policy applied.",
                clauses=["Each major deliverable includes up to two rounds of revisions."],
                limits_defined=True,
            ),
            payment_schedule=PaymentSchedule(
                summary="Standard milestone-based payment structure.",
                milestones=[
                    PaymentMilestone(label="Project Initiation", percentage="50%", condition="Due before kickoff."),
                    PaymentMilestone(label="Final Delivery", percentage="50%", condition="Due before launch."),
                ],
                late_payment_clause="Project timelines may pause if invoices remain unpaid.",
                payment_assumptions=["Invoices payable within 7 days."],
            ),
            out_of_scope_clause=OutOfScopeClause(
                summary="Work outside defined scope requires separate approval.",
                excluded_items=["Content creation", "Photography", "Ongoing maintenance"],
                formal_clause="Any work outside the explicitly defined scope may require a separate estimate and written approval.",
            ),
            client_responsibilities_clause=ClientResponsibilitiesClause(
                summary="Client must provide required inputs and timely feedback.",
                responsibilities=["Provide content and assets", "Review deliverables promptly"],
                formal_clause="Client delays in providing required content or feedback may impact timelines.",
            ),
            ip_ownership_clause=IPOwnershipClause(
                summary="Ownership transfers upon final payment.",
                ownership_model="Ownership transfers upon final payment.",
                formal_clause="Final approved deliverables become client property upon receipt of full payment.",
            ),
            change_request_process=ChangeRequestProcess(
                summary="Scope changes require written approval and updated estimates.",
                workflow_steps=["Submit change request", "Agency reviews impact", "Provide updated estimate", "Work proceeds after approval"],
                formal_clause="Requests outside approved scope may require additional fees and timeline adjustments.",
            ),
            timeline_assumptions_clause=TimelineAssumptionsClause(
                summary="Timelines depend on timely client inputs and approvals.",
                assumptions=["Client provides content on schedule"],
                delay_conditions=["Late content delivery", "Delayed approvals"],
                formal_clause="Project timelines depend on timely client communication and delivery of required assets.",
            ),
            clause_generation_confidence_score=65,
            revision_policy_text="Each major deliverable includes up to two rounds of revisions.",
            out_of_scope=["Content creation", "Photography", "Ongoing maintenance"],
            assumptions=["Client provides content on schedule"],
            acceptance_criteria=["All deliverables approved", "Final payment received"],
            client_responsibilities=["Provide content and assets", "Review deliverables promptly"],
        )
        # Derive additional protections from A4 risks if available
        if a4 and hasattr(a4, "scope_creep_risks"):
            for risk in a4.scope_creep_risks:
                if risk.severity in ("high", "medium"):
                    output.additional_protection_clauses.append(
                        AdditionalProtectionClause(
                            title=risk.title,
                            reason=risk.why_it_matters or "Detected risk from A4 analysis.",
                            formal_clause=risk.recommended_contract_language or "Refer to scope and risk assessment.",
                        )
                    )
        return output
