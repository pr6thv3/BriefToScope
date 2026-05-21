# BriefToScope Backend

FastAPI backend for BriefToScope, an AI scope intelligence platform for agencies.

## Responsibilities

- Clerk JWT verification
- Workspace membership authorization
- AI generation orchestration
- SOW storage, versioning, section edits, and risk audit
- PDF export service
- DocuSign e-signature service boundary
- PayPal subscription checkout and webhook reconciliation
- Usage tracking and audit logs
- Celery/Redis-ready background jobs

## Local Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DEMO_MODE="true"
uvicorn app.main:app --reload --port 8000
```

OpenAPI docs: `http://localhost:8000/docs`

## Tests

```powershell
python -m pytest
```

## Worker

```powershell
$env:REDIS_URL="redis://localhost:6379/0"
$env:CELERY_ENABLED="true"
celery -A app.workers.celery_app.celery_app worker -Q ai --loglevel=info
```

## Production Environment

See `.env.example`. Required production values include:

- `DEMO_MODE=false`
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `CLERK_JWKS_URL`
- `CLERK_ISSUER`
- `PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`
- `PAYPAL_WEBHOOK_ID`
- `PAYPAL_PLAN_SOLO`
- `PAYPAL_PLAN_STUDIO`
- `PAYPAL_PLAN_AGENCY`
- `FRONTEND_URL`
- `BACKEND_URL`
- `REDIS_URL`

## API Groups

- `/health`
- `/generate-sow`
- `/api/auth/*`
- `/api/workspaces/*`
- `/api/generations/*`
- `/api/sows/*`
- `/api/billing/*`
- `/api/templates/*`
- `/api/admin/readiness`
- `/webhooks/paypal`
- `/webhooks/docusign`

## Deployment Notes

- API and worker should run as separate processes.
- Do not expose Supabase service role keys to the frontend.
- Do not enable `DEMO_MODE` in production.
- Set `ADMIN_EMAIL_ALLOWLIST` before exposing `/api/admin/readiness`.
- Use private storage and signed URLs for generated PDFs before paid launch.
