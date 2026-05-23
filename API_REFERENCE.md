# API Reference

Base URL:

- Local: `http://localhost:8000`
- Production: `BACKEND_URL`

Protected routes require:

- `Authorization: Bearer <Clerk JWT>`
- `X-Workspace-Id: <organization uuid>` when a workspace is active

Demo auth is accepted only when `DEMO_MODE=true`.

## Health

### `GET /health`

Returns service health.

## Auth

### `POST /api/auth/sync`

Mirrors the Clerk user into PostgreSQL, ensures a workspace, and returns user/workspace state.

## Generation

### `POST /api/generations`

Creates a durable generation job after RBAC and quota checks.

```json
{
  "transcript_text": "Discovery notes...",
  "client_name": "Luma Retail Co.",
  "project_name": "Brand Identity + Webflow Website",
  "industry": "Web Design",
  "tone": "professional",
  "budget": "$25,000",
  "timeline": "8 weeks"
}
```

### `GET /api/generations/{generation_id}`

Returns job status.

### `GET /api/generations/{generation_id}/events`

Streams generation progress as Server-Sent Events.

### `POST /generate-sow`

Legacy synchronous endpoint for local/demo compatibility. In production with Celery enabled, use `/api/generations`.

## SOWs

### `GET /sows` and `GET /api/sows`

Lists workspace SOWs.

### `GET /sows/{id}` and `GET /api/sows/{id}`

Returns one SOW with structured content, markdown cache, quality scores, and risk flags.

### `PUT /sows/{id}` and `PUT /api/sows/{id}`

Updates SOW content and creates a version.

## Sections

### `GET /api/sows/{sow_id}/sections`

Lists structured sections.

### `PUT /api/sows/{sow_id}/sections/{section_key}`

Updates one section.

### `POST /api/sows/{sow_id}/regenerate-section`

Regenerates one section only.

### `POST /api/sows/{sow_id}/risk-audit`

Runs deterministic SOW quality/risk validation.

## PDF Exports

### `POST /sows/{id}/export-pdf` and `POST /api/sows/{id}/export-pdf`

Checks RBAC, subscription status, and PDF quota. In production with Celery enabled, returns a queued export. Otherwise generates a PDF, uploads it to private Supabase Storage, creates an export record, and returns a short-lived signed URL.

### `GET /api/sows/{sow_id}/exports/{export_id}/download-url`

Returns a fresh 10-minute signed download URL for a private PDF export.

## E-Sign

### `POST /sows/{id}/send-signature` and `POST /api/sows/{id}/send-signature`

Requires owner/admin, active plan with e-sign, and available e-sign quota.

```json
{
  "recipient_email": "client@example.com"
}
```

## Billing

### `GET /api/billing/plans`

Lists Free, Solo, Studio, Agency, and Enterprise plan metadata.

### `GET /api/billing/status`

Returns current plan, subscription status, renewal date, usage, limits, and available billing actions.

### `GET /api/billing/usage`

Returns monthly usage counters and quotas.

### `POST /api/billing/checkout`

Creates a PayPal subscription approval URL.

### `POST /api/billing/change-plan`

Starts PayPal approval for plan change.

### `POST /api/billing/cancel`

Cancels the active PayPal subscription from BriefToScope billing settings.

### `POST /api/billing/reactivate`

Reactivates a suspended/canceled local subscription when provider state allows it.

### `POST /webhooks/paypal` and `POST /api/webhooks/paypal`

Processes PayPal subscription and payment events idempotently. Production verifies PayPal signatures.

## Templates

### `GET /api/templates`

Lists supported industries.

### `GET /api/templates/{industry}`

Returns industry deliverables, exclusions, risk rules, hidden scope traps, acceptance criteria, and clause library data.

## Admin

### `GET /api/admin/readiness`

Admin allowlist-only readiness check.

### `GET /api/admin/workers/health`

Reports Redis connectivity, queue names, and worker health metadata.

## Errors

```json
{
  "detail": "Human-readable error message"
}
```

- `401`: missing or invalid JWT
- `403`: missing workspace permission
- `402`: inactive subscription, quota exhausted, or plan feature unavailable
- `404`: resource not found
- `429`: rate limit exceeded
- `500`: unexpected server error
