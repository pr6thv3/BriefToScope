-- ==========================================
-- BriefToScope - Query Indexing Strategy
-- Target: Optimizing Dashboard, Audits, and Tenant Isolation
-- ==========================================

-- 1. Foreign Key Performance Indexes (Fast Joins & Cascade Safety)
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_org_id ON projects(org_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_project_id ON transcripts(project_id);
CREATE INDEX IF NOT EXISTS idx_sows_project_id ON sows(project_id);
CREATE INDEX IF NOT EXISTS idx_sows_user_id ON sows(user_id);
CREATE INDEX IF NOT EXISTS idx_sow_versions_sow_id ON sow_versions(sow_id);
CREATE INDEX IF NOT EXISTS idx_ai_pipeline_runs_sow_id ON ai_pipeline_runs(sow_id);
CREATE INDEX IF NOT EXISTS idx_ai_pipeline_runs_project_id ON ai_pipeline_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_ai_pipeline_runs_trace_id ON ai_pipeline_runs(trace_id);
CREATE INDEX IF NOT EXISTS idx_usage_events_user_id ON usage_events(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_events_org_id ON usage_events(org_id);
CREATE INDEX IF NOT EXISTS idx_billing_subscriptions_user_id ON billing_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_esign_requests_sow_id ON esign_requests(sow_id);

-- 2. Compound Sorting and Filter Indexes (Dashboard & History Feeds)
-- Optimizes: listing a user's latest SOW drafts in the history dashboard
CREATE INDEX IF NOT EXISTS idx_sows_user_created_status 
ON sows(user_id, created_at DESC, status);

-- Optimizes: listing a user's projects by active status
CREATE INDEX IF NOT EXISTS idx_projects_user_status 
ON projects(user_id, status);

-- Optimizes: pulling SOW versions chronologically
CREATE INDEX IF NOT EXISTS idx_sow_versions_sow_number 
ON sow_versions(sow_id, version_number DESC);

-- Optimizes: summing usage metrics and quotas within the current period
CREATE INDEX IF NOT EXISTS idx_usage_events_user_type_created 
ON usage_events(user_id, event_type, created_at DESC);

-- 3. JSONB GIN Indexes (Flexible AI metadata and structured content search)
-- Optimizes: querying metadata fields inside call transcripts (e.g. speakers, upload flags)
CREATE INDEX IF NOT EXISTS idx_transcripts_metadata_gin 
ON transcripts USING gin (metadata_json);

-- Optimizes: searching inside generated SOW risks and clause structures
CREATE INDEX IF NOT EXISTS idx_sows_risk_flags_gin 
ON sows USING gin (risk_flags_json);

-- 4. Template JSONB Performance GIN Indexes
CREATE INDEX IF NOT EXISTS idx_templates_structure_gin ON templates USING gin (structure_json);
CREATE INDEX IF NOT EXISTS idx_templates_clause_library_gin ON templates USING gin (clause_library_json);
CREATE INDEX IF NOT EXISTS idx_templates_risk_rules_gin ON templates USING gin (risk_rules_json);
