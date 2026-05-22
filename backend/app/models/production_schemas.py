from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


OrgRole = Literal["owner", "admin", "member", "reviewer", "client_viewer"]
PlanKey = Literal["free", "solo", "studio", "agency", "enterprise"]
JobStatus = Literal["queued", "running", "completed", "failed"]


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: Optional[str] = Field(default=None, max_length=80)


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    slug: str
    plan: PlanKey = "free"
    role: OrgRole = "owner"
    status: str = "active"
    created_at: datetime


class WorkspaceMemberResponse(BaseModel):
    id: str
    user_id: str
    email: str
    name: str = ""
    role: OrgRole
    status: str = "active"
    created_at: datetime


class InviteCreateRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    role: OrgRole = "member"


class InviteResponse(BaseModel):
    id: str
    org_id: str
    email: str
    role: OrgRole
    status: str = "pending"
    expires_at: datetime
    created_at: datetime


class BrandSettingsRequest(BaseModel):
    logo_url: str = ""
    colors_json: Dict[str, Any] = Field(default_factory=dict)
    footer_text: str = "Protected against scope creep by BriefToScope AI"
    pdf_settings_json: Dict[str, Any] = Field(default_factory=dict)


class BrandSettingsResponse(BrandSettingsRequest):
    org_id: str
    updated_at: datetime


class GenerationCreateRequest(BaseModel):
    transcript_text: str = Field(..., min_length=10, max_length=50000)
    client_name: str = ""
    project_name: str = ""
    industry: str
    tone: str = "professional"
    budget: str = ""
    timeline: str = ""


class GenerationJobResponse(BaseModel):
    id: str
    org_id: str
    user_id: str
    status: JobStatus
    current_step: str = "queued"
    progress: int = Field(default=0, ge=0, le=100)
    project_id: Optional[str] = None
    transcript_id: Optional[str] = None
    sow_id: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SOWSectionUpdateRequest(BaseModel):
    content_markdown: str
    change_summary: str = "Section edited"


class SOWSectionResponse(BaseModel):
    id: str
    sow_id: str
    section_key: str
    title: str
    content_markdown: str
    order: int
    quality_score: int = 0
    locked: bool = False
    updated_at: datetime


class SectionRegenerateRequest(BaseModel):
    section_key: str
    instruction: str = "Rewrite this section with clearer agency-grade language."
    current_markdown: str = ""


class SectionRegenerateResponse(BaseModel):
    section: SOWSectionResponse
    quality_score: int
    risk_flags: List[Dict[str, Any]] = Field(default_factory=list)


class RiskAuditResponse(BaseModel):
    sow_id: str
    quality_score: int
    risk_score: int
    confidence_score: float
    missing_items: List[str] = Field(default_factory=list)
    vague_phrases: List[str] = Field(default_factory=list)
    risk_flags: List[Dict[str, Any]] = Field(default_factory=list)


class PlanFeature(BaseModel):
    key: str
    label: str
    included: bool = True


class BillingPlanResponse(BaseModel):
    key: PlanKey
    name: str
    price_monthly: int
    included_sows: int
    included_seats: int
    pdf_export: bool
    esign: bool
    watermark: bool
    features: List[PlanFeature]


class CheckoutRequest(BaseModel):
    plan: PlanKey
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    checkout_url: str
    demo_mode: bool = False


class UsageSummaryResponse(BaseModel):
    org_id: str
    plan: PlanKey
    sow_generations_used: int
    sow_generations_limit: int
    pdf_exports_used: int
    pdf_exports_limit: int
    esign_requests_used: int
    esign_requests_limit: int
    seats_used: int
    seats_limit: int
    billing_period_start: datetime
    billing_period_end: datetime


class BillingStatusResponse(BaseModel):
    plan: PlanKey
    status: str
    renewal_date: Optional[datetime] = None
    cancel_at_period_end: bool = False
    seat_quantity: int
    usage: UsageSummaryResponse
    limits: Dict[str, Any]
    available_actions: List[str]


class BillingActionResponse(BaseModel):
    status: str
    message: Optional[str] = None
    checkout_url: Optional[str] = None


class ChangePlanRequest(CheckoutRequest):
    pass
