from typing import List, Dict, Any
from pydantic import BaseModel, Field

class MilestoneOption(BaseModel):
    percentage: str = Field(..., description="The percentage of the total budget for this milestone (e.g. 50%)")
    condition: str = Field(..., description="The condition under which payment is triggered (e.g. Due before project kickoff)")

class PaymentScheduleOption(BaseModel):
    label: str = Field(..., description="The name of this payment schedule setup (e.g. Standard 50/25/25)")
    milestones: List[MilestoneOption] = Field(..., description="The milestones of this option")

class RiskRule(BaseModel):
    risk: str = Field(..., description="The summary description of the potential risk")
    trigger_terms: List[str] = Field(..., description="List of case-insensitive keyword trigger patterns")
    recommended_fix: str = Field(..., description="Recommended mitigation wording to put in assumptions or exclusions")

class ClauseLibrary(BaseModel):
    revision: List[str] = Field(default_factory=list, description="Revision rules and policy variants")
    payment: List[str] = Field(default_factory=list, description="Payment term clauses")
    out_of_scope: List[str] = Field(default_factory=list, description="Exclusion and out of scope scope clauses")
    client_responsibilities: List[str] = Field(default_factory=list, description="Responsibilities requirements clauses")
    ip_ownership: List[str] = Field(default_factory=list, description="Intellectual property and ownership clauses")
    change_request: List[str] = Field(default_factory=list, description="Change request protocols and fees")
    timeline: List[str] = Field(default_factory=list, description="Timeline and delivery delay assumptions")

class SOWTemplate(BaseModel):
    industry: str = Field(..., description="The specific industry category this template covers")
    default_sections: List[str] = Field(..., description="Standard ordering and title headers of sections")
    standard_deliverables: List[str] = Field(..., description="Typical in-scope deliverables for this industry")
    common_out_of_scope_items: List[str] = Field(..., description="Typical exclusions for this industry")
    revision_policy: str = Field(..., description="Standard revision policy details")
    payment_schedule_options: List[PaymentScheduleOption] = Field(..., description="Predefined payment options")
    risk_rules: List[RiskRule] = Field(..., description="Pre-loaded industry risk rules and triggers")
    client_responsibilities: List[str] = Field(..., description="Predefined client requirements")
    timeline_assumptions: List[str] = Field(..., description="Typical timeline constraints and assumptions")
    acceptance_criteria: List[str] = Field(..., description="Predefined approval standards")
    hidden_scope_traps: List[str] = Field(default_factory=list, description="Common hidden scope creep traps for this industry")
    clause_library: ClauseLibrary = Field(..., description="The catalog of clauses")
