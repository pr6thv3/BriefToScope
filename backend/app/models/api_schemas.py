from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class GenerateSOWRequest(BaseModel):
    transcript_text: str = Field(..., description="Messy transcript notes or discovery call summary")
    client_name: str = Field(default="", description="Optional client name override")
    project_name: str = Field(default="", description="Optional project name override")
    industry: str = Field(..., description="Target industry for template matching")
    tone: str = Field(default="professional", description="Tone for SOW generation")
    budget: str = Field(default="", description="Optional budget override/detail")
    timeline: str = Field(default="", description="Optional timeline override/detail")

class SowDetails(BaseModel):
    title: str
    content_json: Dict[str, Any]
    content_markdown: str
    sections: List[Dict[str, Any]] = []

class QualityDetails(BaseModel):
    overall_quality_score: int
    approval_status: str
    ready_for_export: bool
    warnings: List[str] = []

class GenerationMetadata(BaseModel):
    generation_time_ms: int
    demo_mode: bool
    model_used: str
    fallback_used: bool

class GenerateSOWResponse(BaseModel):
    success: bool
    project_id: str
    transcript_id: str
    sow_id: str
    status: str = "generated"
    ai_pipeline: Dict[str, Any]
    sow: SowDetails
    extracted_brief: Dict[str, Any]
    confidence_score: float
    risk_flags: List[Dict[str, Any]] = []
    quality: QualityDetails
    metadata: GenerationMetadata
