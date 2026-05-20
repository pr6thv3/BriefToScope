-- ==========================================
-- BriefToScope - Row Level Security (RLS) Policies
-- Stack: Supabase Auth & Clerk JWT Compatibility
-- ==========================================

-- Helper function to resolve the current active internal user UUID
-- This checks both the Clerk 'sub' claim inside the JWT and falls back to Supabase auth.uid()
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS UUID AS $$
DECLARE
    resolved_id UUID;
    jwt_sub TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Re-create to ensure no compilation issues
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS UUID AS $$
DECLARE
    resolved_id UUID;
    jwt_sub TEXT;
BEGIN
    -- Extract 'sub' claim from current JWT token (common for Clerk JWT integrations in Supabase)
    jwt_sub := NULLIF(current_setting('request.jwt.claims', true)::json->>'sub', '');
    
    IF jwt_sub IS NOT NULL THEN
        SELECT id INTO resolved_id
        FROM users
        WHERE clerk_user_id = jwt_sub;
    END IF;

    -- Fallback to native Supabase Auth UID mapping
    IF resolved_id IS NULL THEN
        SELECT id INTO resolved_id
        FROM users
        WHERE id = auth.uid();
    END IF;

    RETURN resolved_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Enable Row Level Security on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE sows ENABLE ROW LEVEL SECURITY;
ALTER TABLE sow_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE esign_requests ENABLE ROW LEVEL SECURITY;


-- ==========================================
-- 1. USERS POLICIES
-- ==========================================
CREATE POLICY "Users can view their own profile"
    ON users FOR SELECT
    USING (id = get_current_user_id() OR clerk_user_id = auth.jwt() ->> 'sub');

CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (id = get_current_user_id() OR clerk_user_id = auth.jwt() ->> 'sub')
    WITH CHECK (id = get_current_user_id() OR clerk_user_id = auth.jwt() ->> 'sub');

CREATE POLICY "Allow public/auth registration insertions"
    ON users FOR INSERT
    WITH CHECK (true); -- Allow registration triggers / webhook creation


-- ==========================================
-- 2. ORGANIZATIONS POLICIES
-- ==========================================
CREATE POLICY "Org members can view their organization"
    ON organizations FOR SELECT
    USING (
        owner_id = get_current_user_id()
        OR EXISTS (
            -- Scaffold check: check if user is a member of the org
            SELECT 1 FROM projects WHERE org_id = organizations.id AND user_id = get_current_user_id()
        )
    );

CREATE POLICY "Org owners can edit their organization"
    ON organizations FOR UPDATE
    USING (owner_id = get_current_user_id())
    WITH CHECK (owner_id = get_current_user_id());


-- ==========================================
-- 3. PROJECTS POLICIES
-- ==========================================
CREATE POLICY "Users can manage their own projects"
    ON projects FOR ALL
    USING (user_id = get_current_user_id())
    WITH CHECK (user_id = get_current_user_id());

CREATE POLICY "Org members can view projects within their org"
    ON projects FOR SELECT
    USING (org_id IN (
        SELECT id FROM organizations WHERE owner_id = get_current_user_id()
    ));


-- ==========================================
-- 4. TRANSCRIPTS POLICIES
-- ==========================================
CREATE POLICY "Users can manage transcripts of their projects"
    ON transcripts FOR ALL
    USING (project_id IN (
        SELECT id FROM projects WHERE user_id = get_current_user_id()
    ))
    WITH CHECK (project_id IN (
        SELECT id FROM projects WHERE user_id = get_current_user_id()
    ));


-- ==========================================
-- 5. SOWS POLICIES
-- ==========================================
CREATE POLICY "Users can manage their own SOWs"
    ON sows FOR ALL
    USING (user_id = get_current_user_id())
    WITH CHECK (user_id = get_current_user_id());

CREATE POLICY "Org members can view SOWs of projects in their org"
    ON sows FOR SELECT
    USING (project_id IN (
        SELECT id FROM projects WHERE org_id IN (
            SELECT id FROM organizations WHERE owner_id = get_current_user_id()
        )
    ));


-- ==========================================
-- 6. SOW_VERSIONS POLICIES
-- ==========================================
CREATE POLICY "Users can view SOW version history"
    ON sow_versions FOR SELECT
    USING (sow_id IN (
        SELECT id FROM sows WHERE user_id = get_current_user_id()
    ));

CREATE POLICY "Users can insert SOW versions"
    ON sow_versions FOR INSERT
    WITH CHECK (sow_id IN (
        SELECT id FROM sows WHERE user_id = get_current_user_id()
    ));


-- ==========================================
-- 7. AI_PIPELINE_RUNS POLICIES
-- ==========================================
CREATE POLICY "Users can manage pipeline runs of their projects"
    ON ai_pipeline_runs FOR ALL
    USING (project_id IN (
        SELECT id FROM projects WHERE user_id = get_current_user_id()
    ))
    WITH CHECK (project_id IN (
        SELECT id FROM projects WHERE user_id = get_current_user_id()
    ));


-- ==========================================
-- 8. TEMPLATES POLICIES (Read-only public directory)
-- ==========================================
CREATE POLICY "Anyone can view industry templates"
    ON templates FOR SELECT
    USING (true);


-- ==========================================
-- 9. USAGE_EVENTS POLICIES
-- ==========================================
CREATE POLICY "Users can view their usage events"
    ON usage_events FOR SELECT
    USING (user_id = get_current_user_id());

CREATE POLICY "System can record usage events"
    ON usage_events FOR INSERT
    WITH CHECK (user_id = get_current_user_id());


-- ==========================================
-- 10. BILLING_SUBSCRIPTIONS POLICIES
-- ==========================================
CREATE POLICY "Users can view their own subscriptions"
    ON billing_subscriptions FOR SELECT
    USING (user_id = get_current_user_id());


-- ==========================================
-- 11. ESIGN_REQUESTS POLICIES
-- ==========================================
CREATE POLICY "Users can manage e-sign requests for their SOWs"
    ON esign_requests FOR ALL
    USING (sow_id IN (
        SELECT id FROM sows WHERE user_id = get_current_user_id()
    ))
    WITH CHECK (sow_id IN (
        SELECT id FROM sows WHERE user_id = get_current_user_id()
    ));
