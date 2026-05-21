# Deployment Guide

## Recommended MVP Hosting

- Frontend: Vercel
- API: Render or Railway
- Worker: Render/Railway worker process using the backend image
- Redis: Upstash Redis
- Database/storage: Supabase
- DNS/WAF: Cloudflare

## Build Commands

Frontend:

```bash
cd frontend
npm ci
npm run build
```

Backend:

```bash
cd backend
pip install -r requirements.txt
playwright install chromium
python -m pytest
```

## Runtime Commands

API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Worker:

```bash
celery -A app.workers.celery_app.celery_app worker -Q ai --loglevel=info
```

## Required Production Environment

Backend:

- `DEMO_MODE=false`
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `CLERK_JWKS_URL`
- `CLERK_ISSUER`
- `PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`
- `PAYPAL_WEBHOOK_ID`
- `PAYPAL_MODE=live`
- `PAYPAL_PLAN_SOLO`
- `PAYPAL_PLAN_STUDIO`
- `PAYPAL_PLAN_AGENCY`
- `REDIS_URL`
- `CELERY_ENABLED=true`
- `FRONTEND_URL`
- `BACKEND_URL`

Frontend:

- `NEXT_PUBLIC_API_URL`

## Database Migration

Run base schema if the project is empty:

1. `database/schema.sql`
2. `database/indexes.sql`
3. `database/rls_policies.sql`
4. `database/seed.sql` if demo templates are desired

Run production upgrade:

```powershell
cd database
$env:DATABASE_URL="postgresql://..."
.\apply_production_migrations.ps1
```

This applies:

1. `production_foundation.sql`
2. `production_rls_policies.sql`

## PayPal Setup

1. Create a PayPal REST app.
2. Create subscription products/plans for Solo, Studio, and Agency.
3. Set the plan IDs in backend environment variables.
4. Register webhook endpoint: `POST {BACKEND_URL}/webhooks/paypal`.
5. Enable subscription lifecycle events:
   - `BILLING.SUBSCRIPTION.CREATED`
   - `BILLING.SUBSCRIPTION.ACTIVATED`
   - `BILLING.SUBSCRIPTION.UPDATED`
   - `BILLING.SUBSCRIPTION.CANCELLED`
   - `BILLING.SUBSCRIPTION.SUSPENDED`
   - `BILLING.SUBSCRIPTION.EXPIRED`
   - `PAYMENT.SALE.COMPLETED`
   - `PAYMENT.SALE.REFUNDED`
6. Store the PayPal webhook ID as `PAYPAL_WEBHOOK_ID`.

## Clerk Setup

1. Create a Clerk application.
2. Configure allowed redirect URLs for frontend production and previews.
3. Set `CLERK_JWKS_URL` and `CLERK_ISSUER`.
4. Mirror users/workspaces through `/api/auth/sync`.

## Release Process

1. Open a draft PR.
2. Verify CI passes.
3. Run production build locally.
4. Apply migrations in staging.
5. Smoke test auth, generation, editor, PDF, PayPal checkout, and webhooks.
6. Promote to production.
7. Monitor logs, Sentry, queue depth, and provider errors for 24 hours.

## Rollback

- Frontend: redeploy last known good Vercel deployment.
- API/worker: redeploy previous image.
- Database: production migrations are additive; roll forward with corrective migrations rather than destructive rollback.
