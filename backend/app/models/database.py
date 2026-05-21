from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    clerk_user_id: str
    email: str
    name: str
    created_at: datetime


class Project(BaseModel):
    id: str
    user_id: str
    client_name: str
    project_name: str
    industry: str
    status: str = "active"
    created_at: datetime
    updated_at: datetime


class Transcript(BaseModel):
    id: str
    project_id: str
    raw_text: str
    cleaned_text: str
    metadata_json: dict
    created_at: datetime


class SOW(BaseModel):
    id: str
    project_id: str
    user_id: str
    title: str
    content_json: dict
    content_markdown: str
    risk_flags_json: list
    confidence_score: float
    status: str = "draft"
    pdf_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SOWVersion(BaseModel):
    id: str
    sow_id: str
    version_number: int
    content_json: dict
    content_markdown: str
    created_at: datetime


class UsageEvent(BaseModel):
    id: str
    user_id: str
    event_type: str
    token_count: int = 0
    estimated_cost: float = 0.0
    created_at: datetime


class ESignRequest(BaseModel):
    id: str
    sow_id: str
    provider: str
    status: str
    signing_url: Optional[str] = None
    envelope_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BillingSubscription(BaseModel):
    id: str
    user_id: str
    paypal_payer_id: str
    paypal_subscription_id: str
    plan: str
    status: str
    created_at: datetime
    updated_at: datetime
