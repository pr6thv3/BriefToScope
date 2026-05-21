# Launch Checklist

## Completed

- Production architecture foundation added.
- Workspace/membership schema and RLS policies added.
- Structured SOW sections and risk flag tables added.
- Generation job and event tables added.
- Celery/Redis worker package added.
- PayPal subscription checkout service added.
- PayPal webhook verification and reconciliation added.
- Security headers added to backend and frontend.
- Basic API rate limiting added.
- Central API error handler added.
- SEO metadata added.
- Ordered production migration runner added.
- Backend tests pass.
- Frontend lint and build pass.
- Repository documentation added.

## In Progress

- Production auth wiring with Clerk frontend sessions.
- Private PDF signed URL enforcement.
- Worker deployment configuration.
- Real PayPal plan/webhook environment configuration.
- Admin dashboard operational metrics.

## Not Started

- Full legal pages and attorney-reviewed terms.
- External support/helpdesk integration.
- Referral system.
- PostHog funnel events.
- Sentry release tracking.
- Lighthouse CI.
- Playwright E2E workflow tests.
- SOC2-ready evidence collection.
- Enterprise SSO.
- Template marketplace.

## Required To Sell As Real Product

### Compliance Gaps

- Privacy Policy
- Terms of Service
- AI disclosure
- Data retention policy
- Cookie notice if marketing analytics are enabled
- DPA for enterprise customers

### Security Gaps

- Replace frontend demo auth header with Clerk JWT.
- Enforce private file storage for PDFs.
- Add edge/distributed rate limits.
- Add dependency scanning and Dependabot.
- Add production environment validation.
- Lock admin access with allowlist and role checks.

### Monetization Readiness

- Configure live PayPal product and plan IDs.
- Implement billing portal/cancel/update flow or PayPal equivalent UX.
- Enforce quota checks before generation/export/e-sign.
- Add trial state and upgrade prompts.
- Add dunning/failed payment handling.

### UX Polish

- Real screenshots.
- Mobile QA on editor and generate flow.
- Better billing checkout success/cancel states.
- Onboarding checklist tied to real workspace data.
- Empty/error states for every protected page.

### Infrastructure Requirements

- Vercel production project.
- API production service.
- Worker production service.
- Redis production instance.
- Supabase production project.
- Cloudflare DNS/WAF.
- Sentry, PostHog, and Langfuse/Helicone.

### Customer Support Systems

- Support email.
- In-app contact/support route.
- Status page.
- Incident response process.
- Refund/cancellation process.

### Analytics And Retention

- Activation funnel.
- Generation completion funnel.
- Export/signature conversion funnel.
- Churn/downgrade tracking.
- User edit/regeneration preference tracking.

## Current Scores

- Launch readiness: 68/100
- Security: 72/100
- Scalability: 70/100
- UX: 74/100
- Monetization readiness: 62/100
- Technical debt: Medium-high

## Estimated Remaining Work Before Paid Beta

2-4 focused weeks for one founder if scope remains tight:

1. Clerk production auth and protected route guards.
2. PayPal live plans, quota enforcement, and billing UX.
3. Private PDF storage and signed URLs.
4. Worker deployment and job monitoring.
5. E2E tests for generate/edit/export/billing.
6. Legal pages and support flow.
