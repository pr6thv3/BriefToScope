-- ==========================================
-- BriefToScope - Core Schema Definitions
-- Stack: Supabase PostgreSQL
-- Design: UUIDs, Cascading deletes, Timestamp Triggers
-- ==========================================

-- Enable UUID extension (standard for PostgreSQL, pre-enabled in Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trigger function to automatically update updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- 1. USERS
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) DEFAULT '',
    avatar_url TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE TRIGGER trigger_update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- 2. ORGANIZATIONS (Future multi-tenancy & team support)
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    plan VARCHAR(50) DEFAULT 'free' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_organization_plan CHECK (plan IN ('free', 'solo', 'agency', 'agency_plus'))
);

CREATE TRIGGER trigger_update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- 3. PROJECTS (Top-level client workspace container)
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    client_name VARCHAR(255) NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'active' NOT NULL,
    tone VARCHAR(50) DEFAULT 'Professional' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_project_status CHECK (status IN ('active', 'generating', 'completed', 'failed', 'archived'))
);

CREATE TRIGGER trigger_update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- 4. TRANSCRIPTS (Meeting notes input layer)
CREATE TABLE IF NOT EXISTS transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    cleaned_text TEXT NOT NULL,
    metadata_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    source VARCHAR(50) DEFAULT 'manual' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_transcript_source CHECK (source IN ('manual', 'upload', 'integration'))
);


-- 5. SOWS (Generated SOW documents)
CREATE TABLE IF NOT EXISTS sows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content_json JSONB NOT NULL,
    content_markdown TEXT NOT NULL,
    risk_flags_json JSONB DEFAULT '[]'::jsonb NOT NULL,
    confidence_score NUMERIC(5, 2) DEFAULT 0.00 NOT NULL,
    status VARCHAR(50) DEFAULT 'draft' NOT NULL,
    pdf_url TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_sow_status CHECK (status IN ('draft', 'ready', 'exported', 'final', 'signed'))
);

CREATE TRIGGER trigger_update_sows_updated_at
    BEFORE UPDATE ON sows
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- 6. SOW_VERSIONS (Track SOW revisions/edits history)
CREATE TABLE IF NOT EXISTS sow_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sow_id UUID NOT NULL REFERENCES sows(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content_json JSONB NOT NULL,
    content_markdown TEXT NOT NULL,
    change_summary TEXT DEFAULT '' NOT NULL,
    diff_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT unique_sow_version UNIQUE (sow_id, version_number)
);


-- 7. AI_PIPELINE_RUNS (Detailed trace logging for AI agent pipeline runs)
CREATE TABLE IF NOT EXISTS ai_pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sow_id UUID REFERENCES sows(id) ON DELETE SET NULL,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    trace_id UUID NOT NULL,
    model_configurations JSONB DEFAULT '{}'::jsonb NOT NULL,
    prompt_versions JSONB DEFAULT '{}'::jsonb NOT NULL,
    a1_cleaned JSONB DEFAULT '{}'::jsonb,
    a2_brief JSONB DEFAULT '{}'::jsonb,
    a3_scope JSONB DEFAULT '{}'::jsonb,
    a4_risks JSONB DEFAULT '{}'::jsonb,
    a5_clauses JSONB DEFAULT '{}'::jsonb,
    a6_sow JSONB DEFAULT '{}'::jsonb,
    a7_quality JSONB DEFAULT '{}'::jsonb,
    latency_ms INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);


-- 8. TEMPLATES (Industry clause and structure configuration)
CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry VARCHAR(100) UNIQUE NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    structure_json JSONB NOT NULL,
    clause_library_json JSONB NOT NULL,
    risk_rules_json JSONB DEFAULT '[]'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE TRIGGER trigger_update_templates_updated_at
    BEFORE UPDATE ON templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- 9. USAGE_EVENTS (Telemetry for billing and quota restrictions)
CREATE TABLE IF NOT EXISTS usage_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    token_count INTEGER DEFAULT 0 NOT NULL,
    estimated_cost NUMERIC(10, 5) DEFAULT 0.00000 NOT NULL,
    metadata_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);


-- 10. BILLING_SUBSCRIPTIONS (Stripe sync mappings)
CREATE TABLE IF NOT EXISTS billing_subscriptions (
    id VARCHAR(255) PRIMARY KEY, -- Stripe Subscription ID
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR(255) NOT NULL,
    stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
    plan VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_billing_status CHECK (status IN ('active', 'trialing', 'past_due', 'canceled', 'incomplete', 'unpaid'))
);

CREATE TRIGGER trigger_update_billing_subscriptions_updated_at
    BEFORE UPDATE ON billing_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- 11. ESIGN_REQUESTS (E-Signature transaction logs)
CREATE TABLE IF NOT EXISTS esign_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sow_id UUID NOT NULL REFERENCES sows(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- e.g., 'docusign', 'pandadoc'
    status VARCHAR(50) NOT NULL,
    signing_url TEXT DEFAULT '',
    envelope_id VARCHAR(255) UNIQUE NOT NULL,
    signed_document_url TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_esign_provider CHECK (provider IN ('docusign', 'pandadoc', 'demo', 'mock')),
    CONSTRAINT chk_esign_status CHECK (status IN ('sent', 'delivered', 'completed', 'declined', 'voided', 'mock_signed'))
);

CREATE TRIGGER trigger_update_esign_requests_updated_at
    BEFORE UPDATE ON esign_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
