# Deployment Guide

## Target Paid-Beta Topology

- Frontend: Vercel
- API: Render web service
- Worker: Render worker service using the same backend image
- Redis: Upstash Redis
- Database/storage: Supabase
- Payments: PayPal Subscriptions
- Observability: Sentry, PostHog, optional Langfuse/Helicone

## Frontend

Vercel uses [frontend/vercel.json](frontend/vercel.json).

Required env:

- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `NEXT_PUBLIC_POSTHOG_KEY` optional
- `NEXT_PUBLIC_POSTHOG_HOST` optional
- `NEXT_PUBLIC_SENTRY_DSN` optional
- `NEXT_PUBLIC_SUPPORT_EMAIL`

## Backend API

Render uses [render.yaml](render.yaml). API command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Production startup fails clearly when required env vars are missing and `DEMO_MODE=false`.

## Celery Worker

Worker command:

```bash
celery -A app.workers.celery_app.celery_app worker -Q ai_generation,pdf_exports,emails,billing --loglevel=info
```

Set `CELERY_ENABLED=true` and `REDIS_URL` for production. API and worker must share the same Supabase, PayPal, Clerk, storage, and observability env values.

## Backend Required Env

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

Optional:

- `ANTHROPIC_API_KEY`
- `DOCUSIGN_CLIENT_ID`
- `DOCUSIGN_CLIENT_SECRET`
- `DOCUSIGN_ACCOUNT_ID`
- `DOCUSIGN_BASE_URL`
- `SENTRY_DSN`
- `POSTHOG_KEY`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `HELICONE_API_KEY`
- `ADMIN_EMAIL_ALLOWLIST`

## Supabase

1. Create a production Supabase project.
2. Apply `database/production_foundation.sql`.
3. Apply `database/production_rls_policies.sql`.
4. Ensure the `sow-pdfs` bucket is private.
5. Store only the service-role key on the backend, never in Vercel public env.

## PayPal

1. Create live PayPal app credentials.
2. Create Solo, Studio, and Agency subscription plans.
3. Add live plan IDs to backend env.
4. Register webhook endpoint: `{BACKEND_URL}/webhooks/paypal`.
5. Subscribe to subscription lifecycle, payment completed, payment failed/denied, canceled, suspended, refund, and reversal events.
6. Copy PayPal webhook ID to `PAYPAL_WEBHOOK_ID`.

## Clerk

1. Configure production frontend URL and callback URLs.
2. Set `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` in Vercel.
3. Set `CLERK_SECRET_KEY`, `CLERK_JWKS_URL`, and `CLERK_ISSUER` in Render.
4. Confirm protected routes redirect to `/sign-in`.
5. Confirm `/api/auth/sync` creates the workspace in PostgreSQL.

## Smoke Test

After deploy:

1. Sign up with Clerk.
2. Confirm workspace sync.
3. Generate one SOW.
4. Review risk sidebar.
5. Edit and save a section.
6. Export private PDF and open signed URL.
7. Start PayPal checkout on a test paid plan or live plan.
8. Send a webhook test from PayPal and confirm local subscription status changes.
9. Confirm `/api/admin/workers/health` is locked to allowlisted admins.

## Rollback

- Vercel: redeploy previous successful frontend deployment.
- Render API/worker: redeploy previous image.
- Database: migrations are additive; roll forward with corrective SQL instead of destructive rollback.
