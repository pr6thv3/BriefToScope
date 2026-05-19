from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RiskFlag(BaseModel):
    severity: str = Field(..., pattern="^(high|medium|low)$", examples=["medium"])
    title: str = Field(examples=["Unclear CMS requirements"])
    description: str = Field(examples=["Client has not specified preferred CMS."])
    suggested_fix: str = Field(examples=["Clarify CMS and platform requirements."])


class ExtractedBrief(BaseModel):
    client_name: str = Field(examples=["Acme Corp"])
    project_type: str = Field(examples=["Web Redesign"])
    goals: List[str] = Field(examples=[["Modernize website", "Improve conversions"]])
    deliverables: List[str] = Field(examples=[["Homepage", "Product pages"]])
    budget_mentions: List[str] = Field(examples=[["$120,000"]])
    deadline_mentions: List[str] = Field(examples=[["End of September soft launch"]])
    unclear_items: List[str] = Field(examples=[["CMS choice"]])


class SOWContent(BaseModel):
    project_overview: str = Field(examples=["Redesign Acme Corp website for improved UX and conversions."])
    objectives: List[str] = Field(examples=[["Increase conversion rate", "Improve mobile experience"]])
    scope_of_work: List[str] = Field(examples=[["Discovery", "UI/UX design", "Frontend dev"]])
    deliverables: List[str] = Field(examples=[["Design system", "React components"]])
    timeline: List[str] = Field(examples=[["Discovery: 2 weeks", "Design: 4 weeks", "Dev: 6 weeks"]])
    payment_schedule: List[str] = Field(examples=[["50% upfront", "50% on delivery"]])
    client_responsibilities: List[str] = Field(examples=[["Provide brand assets", "Provide content"]])
    revision_policy: str = Field(examples=["Two rounds of revisions included."])
    out_of_scope: List[str] = Field(examples=[["Content creation", "SEO"]])
    assumptions: List[str] = Field(examples=[["Client provides brand assets within 3 days"]])
    acceptance_criteria: List[str] = Field(examples=[["All pages approved via Figma"]])
    signature_section: str = Field(examples=["[Signature blocks]"])


class SOWOutput(BaseModel):
    sow: SOWContent
    risk_flags: List[RiskFlag]
    extracted_brief: ExtractedBrief
    confidence_score: float = Field(..., ge=0.0, le=1.0, examples=[0.85])


class GenerateSOWRequest(BaseModel):
    transcript_text: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        examples=["We need to redesign our website. Budget is around 50k. Timeline is Q3."],
    )
    industry: str = Field(examples=["Technology / SaaS"])
    tone: str = Field(default="professional", examples=["professional"])
    client_name: str = Field(default="", examples=["Acme Corp"])
    project_name: str = Field(default="", examples=["Website Redesign"])
    budget: str = Field(default="", examples=["$50,000"])
    timeline: str = Field(default="", examples=["Q3 2024"])
    user_id: str = Field(default="", examples=["user_123"])


class GenerateSOWResponse(BaseModel):
    sow: SOWContent
    risk_flags: List[RiskFlag]
    extracted_brief: ExtractedBrief
    confidence_score: float = Field(examples=[0.85])
    sow_id: str = Field(examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"])


class SOWListItem(BaseModel):
    id: str
    title: str
    client_name: str
    project_name: str
    industry: str
    status: str
    created_at: datetime
    updated_at: datetime
    confidence_score: float


class SOWDetailResponse(BaseModel):
    id: str
    title: str
    client_name: str
    project_name: str
    industry: str
    status: str
    content_json: dict
    content_markdown: str
    risk_flags_json: List[RiskFlag]
    confidence_score: float
    pdf_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    transcript_summary: str
    export_status: str
    esign_status: Optional[str]


class UpdateSOWRequest(BaseModel):
    content_json: dict
    content_markdown: str


class UpdateSOWResponse(BaseModel):
    id: str
    content_json: dict
    content_markdown: str
    updated_at: datetime


class PDFExportResponse(BaseModel):
    pdf_url: str = Field(examples=["https://storage.example.com/sow-pdfs/xxx/sow-xxx.pdf"])


class ESignResponse(BaseModel):
    signing_url: str = Field(examples=["https://demo.docusign.net/demo-sign/xxx"])
    envelope_id: str = Field(examples=["demo-abc123"])
    status: str = Field(examples=["sent"])


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    version: str = Field(default="1.0.0", examples=["1.0.0"])
