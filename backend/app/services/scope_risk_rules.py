from dataclasses import dataclass
from typing import Iterable, List

from app.models.ai_schemas import RiskFlagData, ScopeCreepRisk


@dataclass(frozen=True)
class ScopeRiskRule:
    id: str
    title: str
    category: str
    severity: str
    trigger_terms: tuple[str, ...]
    description: str
    why_it_matters: str
    recommended_fix: str
    recommended_contract_language: str


RISK_RULES: tuple[ScopeRiskRule, ...] = (
    ScopeRiskRule(
        id="unlimited_revisions_implied",
        title="Unlimited Revisions Implied",
        category="revisions",
        severity="high",
        trigger_terms=("unlimited revisions", "revise until", "as many changes", "keep tweaking"),
        description="Revision expectations imply open-ended feedback rounds.",
        why_it_matters="Unlimited revisions create unpaid iteration loops and delay final approval.",
        recommended_fix="Define included revision rounds and change-request pricing.",
        recommended_contract_language="Each deliverable includes two revision rounds. Additional revisions require written approval and may affect fees and timeline.",
    ),
    ScopeRiskRule(
        id="seo_mentioned_not_scoped",
        title="SEO Mentioned But Not Scoped",
        category="deliverables",
        severity="medium",
        trigger_terms=("seo", "search ranking", "rank on google", "organic traffic"),
        description="SEO is mentioned without a clear deliverable boundary.",
        why_it_matters="SEO can expand into strategy, technical audits, content, reporting, and ongoing optimization.",
        recommended_fix="Specify whether SEO is metadata only, audit, content, or ongoing optimization.",
        recommended_contract_language="SEO services are limited to explicitly listed tasks. Ongoing SEO strategy, content, and reporting are excluded unless separately scoped.",
    ),
    ScopeRiskRule(
        id="copywriting_responsibility_unclear",
        title="Copywriting Responsibility Unclear",
        category="content",
        severity="high",
        trigger_terms=("copywriting", "website copy", "content for pages", "write the content", "copy for"),
        description="Content writing is referenced but ownership is not clearly assigned.",
        why_it_matters="Undefined copywriting ownership often delays web projects and creates unpaid writing expectations.",
        recommended_fix="State whether the client or agency provides final approved copy.",
        recommended_contract_language="Client will provide final approved copy unless copywriting services are separately included in the scope.",
    ),
    ScopeRiskRule(
        id="client_assets_missing",
        title="Client Assets Missing",
        category="content",
        severity="medium",
        trigger_terms=("need assets", "send photos later", "brand assets later", "logos later", "waiting on images"),
        description="The project depends on client-provided assets that are not yet available.",
        why_it_matters="Missing assets can block design and launch while compressing delivery timelines.",
        recommended_fix="List required assets and deadlines for client delivery.",
        recommended_contract_language="Timeline depends on receiving final assets by the agreed dates. Late assets may extend delivery.",
    ),
    ScopeRiskRule(
        id="timeline_dependency_missing",
        title="Timeline Dependency Missing",
        category="timeline",
        severity="medium",
        trigger_terms=("launch asap", "quick turnaround", "depends on approval", "waiting for feedback", "need it soon"),
        description="Timeline language depends on approvals or inputs but lacks a clear dependency clause.",
        why_it_matters="Unbounded dependencies make the agency responsible for delays outside its control.",
        recommended_fix="Tie milestones to client feedback, approval windows, and asset delivery.",
        recommended_contract_language="Timeline commitments depend on timely client feedback, approvals, content, and access. Delays extend corresponding milestones.",
    ),
    ScopeRiskRule(
        id="third_party_tools_unspecified",
        title="Third-party Tools Unspecified",
        category="integrations",
        severity="medium",
        trigger_terms=("integration", "connect to", "crm", "zapier", "hubspot", "mailchimp", "api"),
        description="Third-party tools or integrations are referenced without implementation detail.",
        why_it_matters="Unknown integrations can add discovery, API limitations, vendor costs, and QA work.",
        recommended_fix="Name each integration, owner, credentials needed, and testing responsibility.",
        recommended_contract_language="Third-party integrations are excluded unless specifically listed with platform, scope, and acceptance criteria.",
    ),
    ScopeRiskRule(
        id="custom_animation_complexity_unclear",
        title="Custom Animation Complexity Unclear",
        category="technical",
        severity="medium",
        trigger_terms=("custom animation", "animated", "motion", "microinteractions", "parallax", "3d"),
        description="Animation expectations are mentioned without quantity or complexity limits.",
        why_it_matters="Motion work can expand into advanced design, development, performance, and QA effort.",
        recommended_fix="Define allowed animation types and exclude advanced motion unless scoped.",
        recommended_contract_language="Advanced animation, parallax, 3D, and custom motion systems are excluded unless explicitly listed.",
    ),
    ScopeRiskRule(
        id="payment_milestone_missing",
        title="Payment Milestone Missing",
        category="budget",
        severity="high",
        trigger_terms=("budget", "price", "invoice", "payment", "deposit", "cost"),
        description="Commercial terms are discussed but milestone payment conditions are missing or incomplete.",
        why_it_matters="Missing payment milestones increases cash-flow risk and makes project pause rights unclear.",
        recommended_fix="Add deposit, milestone, and final-payment conditions before handoff or launch.",
        recommended_contract_language="Work begins after deposit. Final files, launch, or handoff occur after final payment is received.",
    ),
    ScopeRiskRule(
        id="acceptance_criteria_missing",
        title="Acceptance Criteria Missing",
        category="approvals",
        severity="medium",
        trigger_terms=("approval", "sign off", "done when", "complete when", "final approval"),
        description="Approval is referenced but final acceptance criteria are not explicit.",
        why_it_matters="Undefined acceptance criteria can cause disputes over whether delivery is complete.",
        recommended_fix="Define what must be true for final acceptance and sign-off.",
        recommended_contract_language="Deliverables are accepted when they match the approved scope and no blocking defects remain against agreed acceptance criteria.",
    ),
    ScopeRiskRule(
        id="ownership_ip_unclear",
        title="Ownership/IP Unclear",
        category="ownership",
        severity="medium",
        trigger_terms=("own the files", "source files", "ip", "intellectual property", "license", "figma files"),
        description="Ownership of source files, IP, licenses, or final assets is not clearly defined.",
        why_it_matters="IP ambiguity can create disputes over usage rights, handoff, and unpaid source-file requests.",
        recommended_fix="Define what transfers, when it transfers, and what remains pre-existing agency IP.",
        recommended_contract_language="Final approved deliverables transfer after full payment. Pre-existing tools, methods, and reusable systems remain agency IP unless otherwise agreed.",
    ),
)


def detect_rule_based_risks(text_parts: Iterable[object]) -> List[ScopeCreepRisk]:
    text = "\n".join(str(part or "") for part in text_parts).lower()
    matches: List[ScopeCreepRisk] = []
    for rule in RISK_RULES:
        evidence = [term for term in rule.trigger_terms if term in text]
        if not evidence:
            continue
        matches.append(
            ScopeCreepRisk(
                id=f"rule_{rule.id}",
                title=rule.title,
                description=rule.description,
                category=rule.category,
                severity=rule.severity,
                likelihood="high" if rule.severity == "high" else "medium",
                impact=rule.severity,
                why_it_matters=rule.why_it_matters,
                evidence=evidence,
                recommended_fix=rule.recommended_fix,
                recommended_contract_language=rule.recommended_contract_language,
                requires_client_clarification=True,
                blocking_risk=rule.severity == "high",
            )
        )
    return matches


def risks_to_flags(risks: Iterable[ScopeCreepRisk]) -> List[RiskFlagData]:
    return [
        RiskFlagData(
            severity=risk.severity,
            title=risk.title,
            description=risk.description,
            suggested_fix=risk.recommended_fix,
        )
        for risk in risks
    ]
