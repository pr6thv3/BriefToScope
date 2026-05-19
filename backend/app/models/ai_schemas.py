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
# A4 — Risk Detector
# ───────────────────────────────────────────────

class RiskFlagData(BaseModel):
    severity: str = Field(..., pattern="^(high|medium|low)$")
    title: str
    description: str
    suggested_fix: str


class A4Input(BaseModel):
    brief: dict = Field(..., description="Brief from A2")
    scope: dict = Field(..., description="Scope from A3")


class A4Output(BaseModel):
    risk_flags: List[RiskFlagData] = Field(default_factory=list)


# ───────────────────────────────────────────────
# A5 — Clause Generator
# ───────────────────────────────────────────────

class A5Input(BaseModel):
    brief: dict = Field(..., description="Brief from A2")
    scope: dict = Field(..., description="Scope from A3")
    industry: str


class A5Output(BaseModel):
    revision_policy: str = ""
    out_of_scope: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    client_responsibilities: List[str] = Field(default_factory=list)


# ───────────────────────────────────────────────
# A6 — SOW Composer
# ───────────────────────────────────────────────

class A6Input(BaseModel):
    brief: dict = Field(..., description="Brief from A2")
    scope: dict = Field(..., description="Scope from A3")
    clauses: dict = Field(..., description="Clauses from A5")
    industry: str
    tone: str


class A6Output(BaseModel):
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


# ───────────────────────────────────────────────
# A7 — Quality Checker
# ───────────────────────────────────────────────

class A7Input(BaseModel):
    sow: dict = Field(..., description="Composed SOW from A6")
    brief: dict = Field(..., description="Original brief from A2")


class A7Output(BaseModel):
    confidence_score: float = Field(default=0.75, ge=0.0, le=1.0)
    suggestions: List[str] = Field(default_factory=list)
    missing_sections: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)


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
