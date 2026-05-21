-- ========================================================
-- BriefToScope Production RLS Policies
-- Apply after production_foundation.sql.
-- Uses organization_members as tenant authority.
-- ========================================================

CREATE OR REPLACE FUNCTION is_org_member(target_org_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM organization_members om
    WHERE om.org_id = target_org_id
      AND om.user_id = get_current_user_id()
      AND om.status = 'active'
      AND om.deleted_at IS NULL
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION has_org_role(target_org_id UUID, allowed_roles TEXT[])
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM organization_members om
    WHERE om.org_id = target_org_id
      AND om.user_id = get_current_user_id()
      AND om.status = 'active'
      AND om.role = ANY(allowed_roles)
      AND om.deleted_at IS NULL
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

ALTER TABLE organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE sow_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE sow_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE sow_risk_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE clause_library ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE pdf_exports ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing_customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_job_events ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Org members can view memberships" ON organization_members;
CREATE POLICY "Org members can view memberships"
  ON organization_members FOR SELECT
  USING (is_org_member(org_id));

DROP POLICY IF EXISTS "Owners and admins can manage memberships" ON organization_members;
CREATE POLICY "Owners and admins can manage memberships"
  ON organization_members FOR ALL
  USING (has_org_role(org_id, ARRAY['owner', 'admin']))
  WITH CHECK (has_org_role(org_id, ARRAY['owner', 'admin']));

DROP POLICY IF EXISTS "Owners and admins can manage invites" ON invitations;
CREATE POLICY "Owners and admins can manage invites"
  ON invitations FOR ALL
  USING (has_org_role(org_id, ARRAY['owner', 'admin']))
  WITH CHECK (has_org_role(org_id, ARRAY['owner', 'admin']));

DROP POLICY IF EXISTS "Org members can manage clients" ON clients;
CREATE POLICY "Org members can manage clients"
  ON clients FOR ALL
  USING (is_org_member(org_id))
  WITH CHECK (is_org_member(org_id));

DROP POLICY IF EXISTS "Org members can read sections" ON sow_sections;
CREATE POLICY "Org members can read sections"
  ON sow_sections FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM sows WHERE sows.id = sow_sections.sow_id AND is_org_member(sows.org_id)
  ));

DROP POLICY IF EXISTS "Org members can edit sections" ON sow_sections;
CREATE POLICY "Org members can edit sections"
  ON sow_sections FOR ALL
  USING (EXISTS (
    SELECT 1 FROM sows WHERE sows.id = sow_sections.sow_id AND has_org_role(sows.org_id, ARRAY['owner', 'admin', 'member'])
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM sows WHERE sows.id = sow_sections.sow_id AND has_org_role(sows.org_id, ARRAY['owner', 'admin', 'member'])
  ));

DROP POLICY IF EXISTS "Org members can view risks" ON sow_risk_flags;
CREATE POLICY "Org members can view risks"
  ON sow_risk_flags FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM sows WHERE sows.id = sow_risk_flags.sow_id AND is_org_member(sows.org_id)
  ));

DROP POLICY IF EXISTS "Editors can manage risks" ON sow_risk_flags;
CREATE POLICY "Editors can manage risks"
  ON sow_risk_flags FOR ALL
  USING (EXISTS (
    SELECT 1 FROM sows WHERE sows.id = sow_risk_flags.sow_id AND has_org_role(sows.org_id, ARRAY['owner', 'admin', 'member'])
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM sows WHERE sows.id = sow_risk_flags.sow_id AND has_org_role(sows.org_id, ARRAY['owner', 'admin', 'member'])
  ));

DROP POLICY IF EXISTS "Org members can view comments" ON sow_comments;
CREATE POLICY "Org members can view comments"
  ON sow_comments FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM sows WHERE sows.id = sow_comments.sow_id AND is_org_member(sows.org_id)
  ));

DROP POLICY IF EXISTS "Org members can manage comments" ON sow_comments;
CREATE POLICY "Org members can manage comments"
  ON sow_comments FOR ALL
  USING (EXISTS (
    SELECT 1 FROM sows WHERE sows.id = sow_comments.sow_id AND is_org_member(sows.org_id)
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM sows WHERE sows.id = sow_comments.sow_id AND is_org_member(sows.org_id)
  ));

DROP POLICY IF EXISTS "Org members can view workspace clauses" ON clause_library;
CREATE POLICY "Org members can view workspace clauses"
  ON clause_library FOR SELECT
  USING (org_id IS NULL OR is_org_member(org_id));

DROP POLICY IF EXISTS "Owners and admins can manage workspace clauses" ON clause_library;
CREATE POLICY "Owners and admins can manage workspace clauses"
  ON clause_library FOR ALL
  USING (org_id IS NOT NULL AND has_org_role(org_id, ARRAY['owner', 'admin']))
  WITH CHECK (org_id IS NOT NULL AND has_org_role(org_id, ARRAY['owner', 'admin']));

DROP POLICY IF EXISTS "Org members can view brand settings" ON brand_settings;
CREATE POLICY "Org members can view brand settings"
  ON brand_settings FOR SELECT
  USING (is_org_member(org_id));

DROP POLICY IF EXISTS "Owners and admins can manage brand settings" ON brand_settings;
CREATE POLICY "Owners and admins can manage brand settings"
  ON brand_settings FOR ALL
  USING (has_org_role(org_id, ARRAY['owner', 'admin']))
  WITH CHECK (has_org_role(org_id, ARRAY['owner', 'admin']));

DROP POLICY IF EXISTS "Org members can view exports" ON pdf_exports;
CREATE POLICY "Org members can view exports"
  ON pdf_exports FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM sows WHERE sows.id = pdf_exports.sow_id AND is_org_member(sows.org_id)
  ));

DROP POLICY IF EXISTS "Owners and admins can view billing customers" ON billing_customers;
CREATE POLICY "Owners and admins can view billing customers"
  ON billing_customers FOR SELECT
  USING (has_org_role(org_id, ARRAY['owner', 'admin']));

DROP POLICY IF EXISTS "Owners and admins can view subscriptions" ON subscriptions;
CREATE POLICY "Owners and admins can view subscriptions"
  ON subscriptions FOR SELECT
  USING (has_org_role(org_id, ARRAY['owner', 'admin']));

DROP POLICY IF EXISTS "Org members can view audit logs" ON audit_logs;
CREATE POLICY "Org members can view audit logs"
  ON audit_logs FOR SELECT
  USING (is_org_member(org_id));

DROP POLICY IF EXISTS "Owners and admins can manage api keys" ON api_keys;
CREATE POLICY "Owners and admins can manage api keys"
  ON api_keys FOR ALL
  USING (has_org_role(org_id, ARRAY['owner', 'admin']))
  WITH CHECK (has_org_role(org_id, ARRAY['owner', 'admin']));

DROP POLICY IF EXISTS "Org members can view generation jobs" ON generation_jobs;
CREATE POLICY "Org members can view generation jobs"
  ON generation_jobs FOR SELECT
  USING (is_org_member(org_id));

DROP POLICY IF EXISTS "Org members can view generation events" ON generation_job_events;
CREATE POLICY "Org members can view generation events"
  ON generation_job_events FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM generation_jobs
    WHERE generation_jobs.id = generation_job_events.generation_job_id
      AND is_org_member(generation_jobs.org_id)
  ));

