export type RiskSeverity = "high" | "medium" | "low";

export type GenerationStepStatus = "waiting" | "active" | "complete" | "warning" | "error";

export type GenerationStep = {
  id: string;
  label: string;
  description: string;
  status: GenerationStepStatus;
  icon: string;
  outputPreview?: string;
};

export type RiskFlag = {
  severity: RiskSeverity;
  title: string;
  description: string;
  suggested_fix: string;
};

export type SOWStatus = "draft" | "ready" | "sent" | "signed" | "final";

export type SOWSectionKey =
  | "project_overview"
  | "objectives"
  | "scope_of_work"
  | "deliverables"
  | "timeline"
  | "payment_schedule"
  | "client_responsibilities"
  | "revision_policy"
  | "out_of_scope"
  | "assumptions"
  | "acceptance_criteria"
  | "signature_section";

export type SOWSection = {
  section_key: SOWSectionKey;
  section_title: string;
  content_markdown: string;
  order: number;
  quality_score?: number;
  last_regenerated_at?: string;
};

export type ExtractedBrief = {
  client_name: string;
  project_type: string;
  goals: string[];
  deliverables: string[];
  budget_mentions: string[];
  deadline_mentions: string[];
  unclear_items: string[];
  timeline?: string;
  budget?: string;
  assets_needed?: string[];
  stakeholders?: string[];
};

export type SOWContent = {
  project_overview: string;
  objectives: string[];
  scope_of_work: string[];
  deliverables: string[];
  timeline: string[];
  payment_schedule: string[];
  client_responsibilities: string[];
  revision_policy: string;
  out_of_scope: string[];
  assumptions: string[];
  acceptance_criteria: string[];
  signature_section: string;
};

export type SOWSectionsContent = {
  sections: SOWSection[];
};

export type GenerateSOWRequest = {
  transcript_text: string;
  industry: string;
  tone: string;
  client_name?: string;
  project_name?: string;
  budget?: string;
  timeline?: string;
};

export type SowDetails = {
  title: string;
  content_json: SOWContent;
  content_markdown: string;
  sections: Record<string, unknown>[];
};

export type QualityDetails = {
  overall_quality_score: number;
  approval_status: string;
  ready_for_export: boolean;
  warnings: string[];
  extraction_confidence?: number;
  scope_clarity?: number;
  risk_confidence?: number;
  export_readiness?: number;
};

export type GenerationMetadata = {
  generation_time_ms: number;
  demo_mode: boolean;
  model_used: string;
  fallback_used: boolean;
};

export type GenerateSOWResponse = {
  success: boolean;
  project_id: string;
  transcript_id: string;
  sow_id: string;
  status: string;
  ai_pipeline: Record<string, unknown>;
  sow: SowDetails;
  extracted_brief: ExtractedBrief;
  confidence_score: number;
  risk_flags: RiskFlag[];
  quality: QualityDetails;
  metadata: GenerationMetadata;
};

export type SOWListItem = {
  id: string;
  title: string;
  client_name: string;
  project_name: string;
  industry: string;
  status: string;
  created_at: string;
  updated_at: string;
  confidence_score: number;
};

export type SOWDetail = {
  id: string;
  title: string;
  client_name: string;
  project_name: string;
  industry: string;
  status: SOWStatus | string;
  content_json: SOWContent | SOWSectionsContent | Record<string, unknown>;
  content_markdown: string;
  risk_flags?: RiskFlag[];
  risk_flags_json: RiskFlag[];
  quality_score?: number;
  confidence_score: number;
  scope_confidence_score?: number;
  risk_level?: "low" | "medium" | "high";
  missing_information?: string[];
  vague_warnings?: string[];
  pdf_url?: string | null;
  created_at: string;
  updated_at: string;
  transcript_summary: string;
  export_status: string;
  esign_status?: string | null;
};

export type UpdateSOWPayload = {
  content_json: SOWContent | SOWSectionsContent | Record<string, unknown>;
  content_markdown: string;
};

export type UpdateSOWResponse = {
  id: string;
  content_json: SOWContent | SOWSectionsContent | Record<string, unknown>;
  content_markdown: string;
  updated_at: string;
};

export type PDFExportResponse = {
  pdf_url: string;
};

export type ESignResponse = {
  signing_url: string;
  envelope_id: string;
  status: string;
};

export type SendSignaturePayload = {
  recipient_email?: string;
};

export type RegenerateSectionResponse = {
  section: SOWSection;
};
