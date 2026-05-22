-- ========================================================
-- BriefToScope Production Foundation Migration
-- Apply after schema.sql, indexes.sql, and seed data.
-- Adds workspace tenancy, section storage, audit, billing,
-- private export metadata, and webhook/job infrastructure.
-- ========================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------- Users / Organizations ----------
ALTER TABLE users ADD COLUMN IF NOT EXISTS default_org_id UUID;
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE organizations ADD COLUMN IF NOT EXISTS clerk_org_id VARCHAR(255) UNIQUE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS slug VARCHAR(120) UNIQUE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS owner_user_id UUID REFERENCES users(id) ON DELETE RESTRICT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active' NOT NULL;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

UPDATE organizations SET owner_user_id = owner_id WHERE owner_user_id IS NULL;
UPDATE organizations SET slug = lower(regexp_replace(name, '[^a-zA-Z0-9]+', '-', 'g')) WHERE slug IS NULL;

ALTER TABLE organizations DROP CONSTRAINT IF EXISTS chk_organization_plan;
ALTER TABLE organizations ADD CONSTRAINT chk_organization_plan
  CHECK (plan IN ('free', 'solo', 'studio', 'agency', 'enterprise'));

CREATE TABLE IF NOT EXISTS organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT unique_org_member UNIQUE (org_id, user_id),
    CONSTRAINT chk_org_member_role CHECK (role IN ('owner', 'admin', 'member', 'reviewer', 'client_viewer')),
    CONSTRAINT chk_org_member_status CHECK (status IN ('active', 'invited', 'disabled'))
);

CREATE TABLE IF NOT EXISTS invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    token_hash TEXT NOT NULL,
    invited_by UUID REFERENCES users(id) ON DELETE SET NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_invite_role CHECK (role IN ('admin', 'member', 'reviewer', 'client_viewer')),
    CONSTRAINT chk_invite_status CHECK (status IN ('pending', 'accepted', 'expired', 'revoked'))
);

CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) DEFAULT '',
    metadata_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ---------- Projects / SOW structure ----------
ALTER TABLE projects ADD COLUMN IF NOT EXISTS client_id UUID REFERENCES clients(id) ON DELETE SET NULL;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS name VARCHAR(255);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS metadata_json JSONB DEFAULT '{}'::jsonb NOT NULL;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
UPDATE projects SET created_by = user_id WHERE created_by IS NULL;
UPDATE projects SET name = project_name WHERE name IS NULL;

ALTER TABLE sows ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;
ALTER TABLE sows ADD COLUMN IF NOT EXISTS current_version_id UUID;
ALTER TABLE sows ADD COLUMN IF NOT EXISTS quality_score INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE sows ADD COLUMN IF NOT EXISTS risk_score INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE sows ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

CREATE TABLE IF NOT EXISTS sow_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sow_id UUID NOT NULL REFERENCES sows(id) ON DELETE CASCADE,
    section_key VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content_markdown TEXT NOT NULL DEFAULT '',
    "order" INTEGER NOT NULL,
    quality_score INTEGER DEFAULT 0 NOT NULL,
    locked BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT unique_sow_section_key UNIQUE (sow_id, section_key)
);

ALTER TABLE sow_versions ADD COLUMN IF NOT EXISTS snapshot_json JSONB DEFAULT '{}'::jsonb NOT NULL;
ALTER TABLE sow_versions ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE sow_versions ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

CREATE TABLE IF NOT EXISTS sow_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sow_id UUID NOT NULL REFERENCES sows(id) ON DELETE CASCADE,
    section_id UUID REFERENCES sow_sections(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,
    body TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'open' NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_sow_comment_status CHECK (status IN ('open', 'resolved'))
);

CREATE TABLE IF NOT EXISTS sow_risk_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sow_id UUID NOT NULL REFERENCES sows(id) ON DELETE CASCADE,
    section_id UUID REFERENCES sow_sections(id) ON DELETE SET NULL,
    category VARCHAR(100) DEFAULT 'other' NOT NULL,
    severity VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '' NOT NULL,
    evidence_json JSONB DEFAULT '[]'::jsonb NOT NULL,
    recommended_fix TEXT DEFAULT '' NOT NULL,
    status VARCHAR(50) DEFAULT 'open' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_sow_risk_severity CHECK (severity IN ('low', 'medium', 'high')),
    CONSTRAINT chk_sow_risk_status CHECK (status IN ('open', 'accepted', 'resolved', 'ignored'))
);

-- ---------- Templates / clauses / brand ----------
ALTER TABLE templates ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;
ALTER TABLE templates ADD COLUMN IF NOT EXISTS name VARCHAR(255);
ALTER TABLE templates ADD COLUMN IF NOT EXISTS visibility VARCHAR(50) DEFAULT 'system' NOT NULL;
ALTER TABLE templates ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
UPDATE templates SET name = template_name WHERE name IS NULL;

CREATE TABLE IF NOT EXISTS clause_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    industry VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    trigger_terms TEXT[] DEFAULT '{}'::text[] NOT NULL,
    clause_text TEXT NOT NULL,
    risk_weight INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS brand_settings (
    org_id UUID PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    logo_url TEXT DEFAULT '' NOT NULL,
    colors_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    footer_text TEXT DEFAULT 'Protected against scope creep by BriefToScope AI' NOT NULL,
    pdf_settings_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- ---------- Exports / billing / audit / jobs ----------
ALTER TABLE esign_requests ADD COLUMN IF NOT EXISTS recipient_email VARCHAR(255) DEFAULT '';

CREATE TABLE IF NOT EXISTS pdf_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sow_id UUID NOT NULL REFERENCES sows(id) ON DELETE CASCADE,
    version_id UUID REFERENCES sow_versions(id) ON DELETE SET NULL,
    storage_path TEXT NOT NULL,
    signed_url_expires_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'ready' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_pdf_export_status CHECK (status IN ('queued', 'generating', 'ready', 'failed'))
);
ALTER TABLE pdf_exports ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL;

CREATE TABLE IF NOT EXISTS billing_customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL UNIQUE REFERENCES organizations(id) ON DELETE CASCADE,
    paypal_payer_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL UNIQUE REFERENCES organizations(id) ON DELETE CASCADE,
    paypal_subscription_id VARCHAR(255) UNIQUE,
    paypal_plan_id VARCHAR(255),
    plan VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    seat_quantity INTEGER DEFAULT 1 NOT NULL,
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_subscription_plan CHECK (plan IN ('free', 'solo', 'studio', 'agency', 'enterprise'))
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(120) NOT NULL,
    entity_type VARCHAR(120) NOT NULL,
    entity_id UUID,
    metadata_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    ip VARCHAR(80) DEFAULT '',
    user_agent TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash TEXT NOT NULL UNIQUE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(80) NOT NULL,
    event_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    payload_json JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'received' NOT NULL,
    retry_count INTEGER DEFAULT 0 NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT unique_webhook_event UNIQUE (provider, event_id),
    CONSTRAINT chk_webhook_event_status CHECK (status IN ('received', 'processed', 'failed', 'ignored'))
);

CREATE TABLE IF NOT EXISTS generation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'queued' NOT NULL,
    current_step VARCHAR(100) DEFAULT 'queued' NOT NULL,
    progress INTEGER DEFAULT 0 NOT NULL,
    request_json JSONB NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    transcript_id UUID REFERENCES transcripts(id) ON DELETE SET NULL,
    sow_id UUID REFERENCES sows(id) ON DELETE SET NULL,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_generation_job_status CHECK (status IN ('queued', 'running', 'completed', 'failed'))
);

ALTER TABLE usage_events ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1 NOT NULL;
ALTER TABLE usage_events ADD COLUMN IF NOT EXISTS tokens INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE usage_events ADD COLUMN IF NOT EXISTS cost NUMERIC(12, 6) DEFAULT 0.000000 NOT NULL;
ALTER TABLE usage_events ADD COLUMN IF NOT EXISTS billing_period_start TIMESTAMP WITH TIME ZONE;
ALTER TABLE usage_events ADD COLUMN IF NOT EXISTS billing_period_end TIMESTAMP WITH TIME ZONE;

CREATE TABLE IF NOT EXISTS generation_job_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generation_job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    step VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    progress INTEGER DEFAULT 0 NOT NULL,
    message TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- ---------- Indexes ----------
CREATE INDEX IF NOT EXISTS idx_org_members_user_org ON organization_members(user_id, org_id);
CREATE INDEX IF NOT EXISTS idx_invitations_org_email ON invitations(org_id, email);
CREATE INDEX IF NOT EXISTS idx_clients_org_name ON clients(org_id, name);
CREATE INDEX IF NOT EXISTS idx_sow_sections_sow_order ON sow_sections(sow_id, "order");
CREATE INDEX IF NOT EXISTS idx_sow_risk_flags_sow_severity ON sow_risk_flags(sow_id, severity);
CREATE INDEX IF NOT EXISTS idx_pdf_exports_sow_created ON pdf_exports(sow_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_events_org_period ON usage_events(org_id, event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org_created ON audit_logs(org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_generation_jobs_org_created ON generation_jobs(org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_generation_job_events_job_created ON generation_job_events(generation_job_id, created_at);
CREATE INDEX IF NOT EXISTS idx_clause_library_industry_category ON clause_library(industry, category);

