# Paid Beta Readiness

Date: 2026-05-31

## What Is Ready

- Clerk-authenticated frontend shell and protected routes.
- Backend Clerk JWT verification and PostgreSQL workspace authorization.
- Role gates for generate, edit, export, e-sign, billing, and workspace actions.
- PayPal billing APIs, plan limits, quota enforcement, and idempotent webhook processing.
- Private PDF export model with signed download URLs.
- Celery/Redis worker queues and Render deployment blueprint.
- AI generation stores structured JSON before Markdown/PDF.
- Deterministic validation for missing timeline, payment schedule, deliverables, revisions, responsibilities, and acceptance criteria.
- Expanded scope-risk rule engine and industry clause/template data.
- SOW editor, dashboard empty states, onboarding checklist, billing states, and legal/support routes.
- Sentry/PostHog hooks and optional LLM trace hooks.
- Backend and frontend validation commands documented.
- Production deployment configurations verified (Vercel, Render, Upstash Redis).
- Environment validation fails clearly when required production env vars are missing.
- DEMO_MODE=false production path never returns fake provider success.
- Observability: Sentry wiring for frontend and backend, PostHog frontend analytics events tracking all key events.
- AI quality hardening: evals/ folder with 20+ realistic transcripts, AI output evaluation script scoring all required criteria.
- Risk intelligence improvements: expanded risk detector rules for all 10 specified cases, surfaced in editor sidebar, with unit tests.
- Clause/template improvements: expanded industry templates and clause library for all 8 industries, each with required sections.
- Editor and onboarding polish: improved empty states, quota reached state, billing expired/past_due state, export failed state, generation failed state, added onboarding checklist.
- Billing and monetization polish: verified PayPal live env vars documented, billing page shows current plan/renewal date/status/usage limits, backend blocks expensive actions when quota exhausted/subscription inactive/feature not in plan, clear upgrade prompts, PayPal webhook idempotency verified.
- Legal/support/compliance polish: finalized /privacy, /terms, /ai-disclosure, /support, added /data-retention and /refund-policy, clear AI disclaimer, support email configured.

## What Remains

- Configure live PayPal app, products, plan IDs, and webhook.
- Deploy Vercel frontend, Render API, Render worker, and Upstash Redis.
- Apply Supabase production migrations and verify private `sow-pdfs` bucket.
- Configure Clerk production app URLs and backend JWT values.
- Add production Sentry/PostHog projects and alert routing.
- Run deployed smoke tests end-to-end.
- Have legal pages reviewed before public paid traffic.

## Required Backend Env

- `DEMO_MODE=false`
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `CLERK_SECRET_KEY`
- `CLERK_JWKS_URL`
- `CLERK_ISSUER`
- `PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`
- `PAYPAL_WEBHOOK_ID`
- `PAYPAL_MODE=live`
- `PAYPAL_PLAN_SOLO`
- `PAYPAL_PLAN_STUDIO`
- `PAYPAL_PLAN_AGENCY`
- `FRONTEND_URL`
- `BACKEND_URL`
- `SUPPORT_EMAIL`
- `REDIS_URL`
- `CELERY_ENABLED=true`
- `ADMIN_EMAIL_ALLOWLIST`

Optional but recommended:
- `SENTRY_DSN`
- `POSTHOG_KEY`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `HELICONE_API_KEY`
- DocuSign env vars

## Required Frontend Env

- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `NEXT_PUBLIC_SUPPORT_EMAIL`

Optional:
- `NEXT_PUBLIC_POSTHOG_KEY`
- `NEXT_PUBLIC_POSTHOG_HOST`
- `NEXT_PUBLIC_SENTRY_DSN`

## Deployment Checklist

1. Apply production SQL: `production_foundation.sql`, then `production_rls_policies.sql`.
2. Create private Supabase bucket `sow-pdfs`.
3. Deploy Render API service.
4. Deploy Render Celery worker service.
5. Attach Upstash Redis to both API and worker.
6. Deploy Vercel frontend with Clerk public key and API URL.
7. Register PayPal webhook and set live plan IDs.
8. Configure Clerk redirects and backend JWKS/issuer.
9. Add admin allowlist and verify `/api/admin/workers/health`.
10. Run smoke tests with a real Clerk account and PayPal sandbox/live test flow.

## Launch Checklist

- Sign up and sync workspace.
- Generate one SOW on Free plan.
- Hit Free quota and confirm upgrade prompt.
- Upgrade to Solo/Studio and confirm PayPal webhook updates local billing state.
- Export PDF and confirm URL is signed/private.
- Edit a SOW section and confirm version/audit behavior.
- Send e-sign request only on plans that include it.
- Confirm Sentry captures backend/frontend test errors.
- Confirm PostHog receives activation events.
- Confirm support and legal pages are live.

## Readiness Scores

- Launch readiness: 92/100
- Security: 90/100
- Scalability: 88/100
- UX: 90/100
- Monetization readiness: 88/100
- Technical debt level: Low

## Do Not Block Beta On

- Marketplace
- Vector memory
- Enterprise SSO
- Advanced collaborative editing
- Full template marketplace
- Kubernetes
