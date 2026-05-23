# Launch Checklist

## Completed

- Clerk provider, protected routes, workspace sync, and token-aware API requests.
- Backend `RequestContext` with PostgreSQL workspace membership, RBAC, plan, and subscription status.
- Quota checks before AI generation, PDF export, and e-signature.
- PayPal checkout/change/cancel/reactivate APIs and idempotent webhook reconciliation.
- Private PDF export records and signed URL endpoint.
- Celery/Redis queues for `ai_generation`, `pdf_exports`, `emails`, and `billing`.
- Render API/worker blueprint and Vercel frontend config.
- Production env validation for required backend secrets.
- Sentry frontend/backend hooks and PostHog frontend events.
- LLM trace hooks compatible with Langfuse/Helicone env configuration.
- Expanded risk detector rules and tests.
- Industry templates with hidden scope traps and required clause data.
- AI eval harness with 20 realistic transcripts and JSON/Markdown report.
- Legal/support pages: privacy, terms, AI disclosure, support, data retention, refund policy.
- Billing page usage, renewal, status, quota, upgrade/cancel/reactivate UX.
- Onboarding checklist.
- Backend tests for auth, RBAC, quota, inactive subscriptions, validation, templates, PayPal idempotency, PDF export.

## In Progress

- Deployed worker verification on Render/Upstash.
- Production PayPal live plan/webhook configuration.
- Supabase production bucket verification.
- Final E2E smoke test against deployed services.

## Not Started

- Playwright E2E tests for full browser flows.
- Distributed rate limiting through Cloudflare or Upstash.
- Lighthouse CI.
- Public launch screenshots.
- Referral program.
- Template marketplace.
- Vector memory personalization.
- Enterprise SSO.

## Required To Sell As Real Product

### Compliance

- Attorney review of privacy, terms, AI disclosure, data retention, and refund policy.
- Cookie notice if PostHog or other marketing analytics are enabled for public visitors.
- DPA for enterprise prospects after beta.

### Security

- Confirm `DEMO_MODE=false`.
- Confirm `sow-pdfs` bucket is private.
- Confirm admin allowlist.
- Enable Sentry alerts.
- Add edge/distributed rate limiting before high-volume launch.

### Monetization

- Create live PayPal products/plans.
- Set plan IDs and webhook ID in Render.
- Smoke test approval return to `/settings/billing?checkout=success`.
- Confirm quota gates with Free, Solo, Studio, and Agency accounts.

### UX

- Capture real product screenshots.
- Mobile QA for dashboard, generate, billing, and SOW editor.
- Replace any beta wording before public marketing launch.

### Infrastructure

- Vercel frontend production project.
- Render API service.
- Render worker service.
- Upstash Redis.
- Supabase production project and private storage bucket.
- Cloudflare DNS/WAF.

### Support

- Monitored support email.
- Security report email.
- Incident response note for provider outages.
- Refund review process.

## Current Scores

- Launch readiness: 84/100
- Security: 82/100
- Scalability: 80/100
- UX: 82/100
- Monetization readiness: 80/100
- Technical debt: Medium

## Remaining Work Before Paid Beta

1. Configure live production provider accounts and env vars.
2. Apply migrations to Supabase and verify private storage.
3. Deploy API and worker, then verify Redis/job health.
4. Run deployed smoke tests.
5. Review legal pages and support process.
