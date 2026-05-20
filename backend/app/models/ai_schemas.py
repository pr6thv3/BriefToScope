"""Pydantic v2 schemas for the AI pipeline steps.

Each step has a clear Input and Output schema.
The orchestrator validates outputs and passes clean data to the next step.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ───────────────────────────────────────────────
# Shared / utility schemas
# ───────────────────────────────────────────────

class RawSignals(BaseModel):
    pricing_discussed: bool = False
    timeline_discussed: bool = False
    revision_discussed: bool = False
    content_responsibility_discussed: bool = False
    launch_date_discussed: bool = False


# ───────────────────────────────────────────────
# A1 — Transcript Cleaner
# ───────────────────────────────────────────────

class A1Input(BaseModel):
    raw_transcript: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="Raw call transcript or rough notes",
    )
    industry: str = Field(default="", description="Selected industry vertical")
    tone: str = Field(default="Professional", description="Desired SOW tone")
    client_name: str = Field(default="", description="Optional pre-filled client name")
    project_name: str = Field(default="", description="Optional pre-filled project name")


class A1Output(BaseModel):
    client_name: str = Field(default="", description="Detected or provided client name")
    project_name: str = Field(default="", description="Detected or provided project name")
    project_type: str = Field(default="", description="Categorized project type")
    cleaned_summary: str = Field(
        default="",
        description="Concise business summary of the cleaned transcript",
    )
    goals: List[str] = Field(default_factory=list)
    mentioned_deliverables: List[str] = Field(default_factory=list)
    budget_mentions: List[str] = Field(default_factory=list)
    deadline_mentions: List[str] = Field(default_factory=list)
    stakeholders: List[str] = Field(default_factory=list)
    client_responsibilities: List[str] = Field(default_factory=list)
    agency_responsibilities: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    tools_or_platforms: List[str] = Field(default_factory=list)
    confirmed_items: List[str] = Field(default_factory=list)
    unclear_items: List[str] = Field(default_factory=list)
    potential_risks: List[str] = Field(default_factory=list)
    raw_signals: RawSignals = Field(default_factory=RawSignals)


# ───────────────────────────────────────────────
# A2 — Brief Extractor
# ───────────────────────────────────────────────

class BriefExtractorInput(BaseModel):
    a1_output: dict = Field(..., description="Validated A1 Transcript Cleaner output")
    industry: str = Field(default="", description="Selected industry vertical")
    tone: str = Field(default="Professional", description="Desired SOW tone")


class BriefDeliverable(BaseModel):
    name: str = ""
    description: str = ""
    status: str = Field(default="unclear", pattern="^(confirmed|inferred|unclear)$")
    source_reasoning: str = ""


class BriefTimeline(BaseModel):
    mentioned_deadlines: List[str] = Field(default_factory=list)
    estimated_phases: List[str] = Field(default_factory=list)
    timeline_confidence: str = Field(default="low", pattern="^(high|medium|low)$")
    unclear_timeline_items: List[str] = Field(default_factory=list)


class BriefStakeholder(BaseModel):
    name_or_role: str = ""
    responsibility: str = ""
    status: str = Field(default="unclear", pattern="^(confirmed|inferred|unclear)$")


class BriefBudget(BaseModel):
    budget_discussed: bool = False
    budget_details: List[str] = Field(default_factory=list)
    payment_expectations: List[str] = Field(default_factory=list)
    budget_confidence: str = Field(default="low", pattern="^(high|medium|low)$")


class BriefRevisionExpectations(BaseModel):
    revision_discussed: bool = False
    details: List[str] = Field(default_factory=list)
    risk_if_missing: str = ""


class BriefExtractorOutput(BaseModel):
    client_goal: str = ""
    business_context: str = ""
    project_summary: str = ""
    target_audience: List[str] = Field(default_factory=list)
    primary_objectives: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    deliverables: List[BriefDeliverable] = Field(default_factory=list)
    timeline: BriefTimeline = Field(default_factory=BriefTimeline)
    stakeholders: List[BriefStakeholder] = Field(default_factory=list)
    budget: BriefBudget = Field(default_factory=BriefBudget)
    revision_expectations: BriefRevisionExpectations = Field(default_factory=BriefRevisionExpectations)
    dependencies: List[str] = Field(default_factory=list)
    assets_needed_from_client: List[str] = Field(default_factory=list)
    agency_responsibilities: List[str] = Field(default_factory=list)
    client_responsibilities: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    brief_confidence_score: int = Field(default=0, ge=0, le=100)


# Backward-compat aliases for internal orchestrator references
A2Input = BriefExtractorInput
A2Output = BriefExtractorOutput


# ───────────────────────────────────────────────
# A3 — Scope Builder
# ───────────────────────────────────────────────

class ScopeBuilderInput(BaseModel):
    brief: dict = Field(..., description="Validated A2 BriefExtractorOutput")
    industry: str = ""
    tone: str = "Professional"


class CommercialScopeItem(BaseModel):
    title: str = ""
    description: str = ""
    included_work: List[str] = Field(default_factory=list)
    not_included: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    client_inputs_required: List[str] = Field(default_factory=list)
    acceptance_expectations: List[str] = Field(default_factory=list)
    status: str = Field(default="unclear", pattern="^(confirmed|inferred|unclear)$")
    scope_confidence: str = Field(default="low", pattern="^(high|medium|low)$")


class DeliverableSpec(BaseModel):
    deliverable_name: str = ""
    professional_scope_statement: str = ""
    quantity_or_limit: str = ""
    format_or_platform: str = ""
    included_components: List[str] = Field(default_factory=list)
    excluded_components: List[str] = Field(default_factory=list)
    completion_criteria: List[str] = Field(default_factory=list)
    source_status: str = Field(default="unclear", pattern="^(confirmed|inferred|unclear)$")


class AmbiguityFlag(BaseModel):
    item: str = ""
    why_it_matters: str = ""
    suggested_clarification: str = ""
    severity: str = Field(default="medium", pattern="^(high|medium|low)$")


class ScopeBuilderOutput(BaseModel):
    scope_summary: str = ""
    commercial_scope_items: List[CommercialScopeItem] = Field(default_factory=list)
    deliverable_specifications: List[DeliverableSpec] = Field(default_factory=list)
    implementation_boundaries: List[str] = Field(default_factory=list)
    client_responsibility_boundaries: List[str] = Field(default_factory=list)
    agency_responsibility_boundaries: List[str] = Field(default_factory=list)
    assumptions_for_scope: List[str] = Field(default_factory=list)
    scope_exclusions: List[str] = Field(default_factory=list)
    scope_dependencies: List[str] = Field(default_factory=list)
    ambiguity_flags: List[AmbiguityFlag] = Field(default_factory=list)
    scope_confidence_score: int = Field(default=0, ge=0, le=100)
    # Backward-compat fields derived from commercial_scope_items for downstream steps
    scope_of_work: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    timeline: List[str] = Field(default_factory=list)
    payment_schedule: List[str] = Field(default_factory=list)


# Backward-compat aliases
A3Input = ScopeBuilderInput
A3Output = ScopeBuilderOutput


# ───────────────────────────────────────────────
# A4 — Risk Detector (rich schema)
# ───────────────────────────────────────────────

class RiskFlagData(BaseModel):
    severity: str = Field(..., pattern="^(high|medium|low)$")
    title: str
    description: str
    suggested_fix: str


class ScopeCreepRisk(BaseModel):
    id: str = ""
    title: str = ""
    description: str = ""
    category: str = Field(default="other", pattern="^(timeline|revisions|deliverables|content|integrations|approvals|budget|technical|communication|ownership|maintenance|legal|other)$")
    severity: str = Field(default="medium", pattern="^(high|medium|low)$")
    likelihood: str = Field(default="medium", pattern="^(high|medium|low)$")
    impact: str = Field(default="medium", pattern="^(high|medium|low)$")
    why_it_matters: str = ""
    evidence: List[str] = Field(default_factory=list)
    recommended_fix: str = ""
    recommended_contract_language: str = ""
    requires_client_clarification: bool = True
    blocking_risk: bool = False


class RiskDetectorInput(BaseModel):
    a1_output: dict = Field(..., description="A1 Transcript Cleaner output")
    a2_output: dict = Field(..., description="A2 Brief Extractor output")
    a3_output: dict = Field(..., description="A3 Scope Builder output")
    industry: str = ""
    tone: str = "Professional"


class RiskDetectorOutput(BaseModel):
    overall_risk_score: int = Field(default=0, ge=0, le=100)
    overall_risk_level: str = Field(default="low", pattern="^(low|medium|high)$")
    risk_summary: str = ""
    scope_creep_risks: List[ScopeCreepRisk] = Field(default_factory=list)
    missing_scope_definitions: List[str] = Field(default_factory=list)
    unclear_responsibilities: List[str] = Field(default_factory=list)
    timeline_risks: List[str] = Field(default_factory=list)
    technical_risks: List[str] = Field(default_factory=list)
    revision_risks: List[str] = Field(default_factory=list)
    dependency_risks: List[str] = Field(default_factory=list)
    payment_risks: List[str] = Field(default_factory=list)
    stakeholder_risks: List[str] = Field(default_factory=list)
    recommended_followup_questions: List[str] = Field(default_factory=list)
    critical_missing_items: List[str] = Field(default_factory=list)
    risk_prevention_recommendations: List[str] = Field(default_factory=list)
    risk_detection_confidence_score: int = Field(default=0, ge=0, le=100)
    # Backward-compat: simple risk_flags list for downstream consumption
    risk_flags: List[RiskFlagData] = Field(default_factory=list)


# Backward-compat aliases
A4Input = RiskDetectorInput
A4Output = RiskDetectorOutput


# ───────────────────────────────────────────────
# A5 — Clause Generator (rich schema)
# ───────────────────────────────────────────────

class PaymentMilestone(BaseModel):
    label: str = ""
    percentage: str = ""
    condition: str = ""


class RevisionPolicy(BaseModel):
    summary: str = ""
    clauses: List[str] = Field(default_factory=list)
    limits_defined: bool = False


class PaymentSchedule(BaseModel):
    summary: str = ""
    milestones: List[PaymentMilestone] = Field(default_factory=list)
    late_payment_clause: str = ""
    payment_assumptions: List[str] = Field(default_factory=list)


class OutOfScopeClause(BaseModel):
    summary: str = ""
    excluded_items: List[str] = Field(default_factory=list)
    formal_clause: str = ""


class ClientResponsibilitiesClause(BaseModel):
    summary: str = ""
    responsibilities: List[str] = Field(default_factory=list)
    formal_clause: str = ""


class IPOwnershipClause(BaseModel):
    summary: str = ""
    ownership_model: str = ""
    formal_clause: str = ""


class ChangeRequestProcess(BaseModel):
    summary: str = ""
    workflow_steps: List[str] = Field(default_factory=list)
    formal_clause: str = ""


class TimelineAssumptionsClause(BaseModel):
    summary: str = ""
    assumptions: List[str] = Field(default_factory=list)
    delay_conditions: List[str] = Field(default_factory=list)
    formal_clause: str = ""


class AdditionalProtectionClause(BaseModel):
    title: str = ""
    reason: str = ""
    formal_clause: str = ""


class ClauseGeneratorInput(BaseModel):
    a1_output: dict = Field(..., description="A1 Transcript Cleaner output")
    a2_output: dict = Field(..., description="A2 Brief Extractor output")
    a3_output: dict = Field(..., description="A3 Scope Builder output")
    a4_output: dict = Field(..., description="A4 Risk Detector output")
    industry: str = ""
    tone: str = "Professional"


class ClauseGeneratorOutput(BaseModel):
    revision_policy: RevisionPolicy = Field(default_factory=RevisionPolicy)
    payment_schedule: PaymentSchedule = Field(default_factory=PaymentSchedule)
    out_of_scope_clause: OutOfScopeClause = Field(default_factory=OutOfScopeClause)
    client_responsibilities_clause: ClientResponsibilitiesClause = Field(default_factory=ClientResponsibilitiesClause)
    ip_ownership_clause: IPOwnershipClause = Field(default_factory=IPOwnershipClause)
    change_request_process: ChangeRequestProcess = Field(default_factory=ChangeRequestProcess)
    timeline_assumptions_clause: TimelineAssumptionsClause = Field(default_factory=TimelineAssumptionsClause)
    additional_protection_clauses: List[AdditionalProtectionClause] = Field(default_factory=list)
    clause_generation_confidence_score: int = Field(default=0, ge=0, le=100)
    # Backward-compat fields
    revision_policy_text: str = ""
    out_of_scope: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    client_responsibilities: List[str] = Field(default_factory=list)


# Backward-compat aliases
A5Input = ClauseGeneratorInput
A5Output = ClauseGeneratorOutput


# ───────────────────────────────────────────────
# A6 — SOW Composer (rich schema)
# ───────────────────────────────────────────────

class SOWSection(BaseModel):
    section_key: str = ""
    section_title: str = ""
    content_markdown: str = ""
    order: int = 0


class SOWMetadata(BaseModel):
    client_name: str = ""
    project_name: str = ""
    industry: str = ""
    tone: str = ""
    generated_date: str = ""
    document_version: str = "1.0"
    prepared_by: str = "BriefToScope AI"


class SOWDocumentStats(BaseModel):
    estimated_page_count: int = 0
    total_sections: int = 0
    scope_items_count: int = 0
    risk_items_detected: int = 0


class SOWComposerInput(BaseModel):
    a1_output: dict = Field(..., description="A1 Transcript Cleaner output")
    a2_output: dict = Field(..., description="A2 Brief Extractor output")
    a3_output: dict = Field(..., description="A3 Scope Builder output")
    a4_output: dict = Field(..., description="A4 Risk Detector output")
    a5_output: dict = Field(..., description="A5 Clause Generator output")
    industry: str = ""
    tone: str = "Professional"


class SOWComposerOutput(BaseModel):
    document_title: str = ""
    document_subtitle: str = ""
    executive_summary: str = ""
    sections: List[SOWSection] = Field(default_factory=list)
    metadata: SOWMetadata = Field(default_factory=SOWMetadata)
    document_stats: SOWDocumentStats = Field(default_factory=SOWDocumentStats)
    export_ready: bool = False
    composer_confidence_score: int = Field(default=0, ge=0, le=100)
    # Backward-compat fields
    project_overview: str = ""
    objectives: List[str] = Field(default_factory=list)
    scope_of_work: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    timeline: List[str] = Field(default_factory=list)
    payment_schedule: List[str] = Field(default_factory=list)
    client_responsibilities: List[str] = Field(default_factory=list)
    revision_policy: str = ""
    out_of_scope: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    signature_section: str = "[Signature blocks]"


# Backward-compat aliases
A6Input = SOWComposerInput
A6Output = SOWComposerOutput


# ───────────────────────────────────────────────
# A7 — Quality Checker (rich schema)
# ───────────────────────────────────────────────

class SectionReview(BaseModel):
    section_title: str = ""
    quality_score: int = Field(default=0, ge=0, le=100)
    status: str = Field(default="pass", pattern="^(pass|warning|fail)$")
    issues_found: List[str] = Field(default_factory=list)
    recommended_improvements: List[str] = Field(default_factory=list)


class VagueLanguageFlag(BaseModel):
    phrase: str = ""
    reason: str = ""
    severity: str = Field(default="medium", pattern="^(low|medium|high)$")
    recommended_replacement: str = ""


class CommercialRiskFlag(BaseModel):
    issue: str = ""
    why_it_matters: str = ""
    severity: str = Field(default="medium", pattern="^(low|medium|high)$")
    recommended_fix: str = ""


class TimelineReview(BaseModel):
    status: str = Field(default="pass", pattern="^(pass|warning|fail)$")
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class PaymentReview(BaseModel):
    status: str = Field(default="pass", pattern="^(pass|warning|fail)$")
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class ScopeReview(BaseModel):
    status: str = Field(default="pass", pattern="^(pass|warning|fail)$")
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class LegalSensitivityFlag(BaseModel):
    statement: str = ""
    risk: str = ""
    recommended_change: str = ""


class DocumentConsistencyReview(BaseModel):
    consistent_tone: bool = True
    consistent_scope_boundaries: bool = True
    consistent_responsibilities: bool = True
    formatting_valid: bool = True


class QualityCheckerInput(BaseModel):
    a1_output: dict = Field(..., description="A1 Transcript Cleaner output")
    a2_output: dict = Field(..., description="A2 Brief Extractor output")
    a3_output: dict = Field(..., description="A3 Scope Builder output")
    a4_output: dict = Field(..., description="A4 Risk Detector output")
    a5_output: dict = Field(..., description="A5 Clause Generator output")
    a6_output: dict = Field(..., description="A6 SOW Composer output")
    industry: str = ""
    tone: str = "Professional"


class QualityCheckerOutput(BaseModel):
    overall_quality_score: int = Field(default=0, ge=0, le=100)
    approval_status: str = Field(default="approved", pattern="^(approved|approved_with_warnings|needs_revision|blocked)$")
    executive_review_summary: str = ""
    section_reviews: List[SectionReview] = Field(default_factory=list)
    missing_sections: List[str] = Field(default_factory=list)
    missing_critical_information: List[str] = Field(default_factory=list)
    vague_language_flags: List[VagueLanguageFlag] = Field(default_factory=list)
    commercial_risk_flags: List[CommercialRiskFlag] = Field(default_factory=list)
    timeline_review: TimelineReview = Field(default_factory=TimelineReview)
    payment_review: PaymentReview = Field(default_factory=PaymentReview)
    scope_review: ScopeReview = Field(default_factory=ScopeReview)
    legal_sensitivity_flags: List[LegalSensitivityFlag] = Field(default_factory=list)
    document_consistency_review: DocumentConsistencyReview = Field(default_factory=DocumentConsistencyReview)
    final_recommendations: List[str] = Field(default_factory=list)
    blocking_issues: List[str] = Field(default_factory=list)
    ready_for_export: bool = False
    quality_checker_confidence_score: int = Field(default=0, ge=0, le=100)
    # Backward-compat fields
    confidence_score: float = Field(default=0.75, ge=0.0, le=1.0)
    suggestions: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)


# Backward-compat aliases
A7Input = QualityCheckerInput
A7Output = QualityCheckerOutput


# ───────────────────────────────────────────────
# Orchestrator intermediate storage
# ───────────────────────────────────────────────

class PipelineState(BaseModel):
    a1_cleaned: Optional[A1Output] = None
    a2_brief: Optional[BriefExtractorOutput] = None
    a3_scope: Optional[A3Output] = None
    a4_risks: Optional[A4Output] = None
    a5_clauses: Optional[A5Output] = None
    a6_sow: Optional[A6Output] = None
    a7_quality: Optional[A7Output] = None
    
    request_id: str = ""
    project_id: str = ""
    user_id: str = ""
    started_at: str = ""
    completed_at: str = ""
    steps: dict = {}
    fallback_used: bool = False
    errors: list = []
