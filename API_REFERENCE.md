# API Reference

Base URL:

- Local: `http://localhost:8000`
- Production: `BACKEND_URL`

Authentication:

- Protected routes expect `Authorization: Bearer <Clerk JWT>`.
- Demo mode accepts `Bearer demo`.
- Workspace-scoped routes may accept `X-Workspace-Id`.

## Health

### `GET /health`

Returns API health and version metadata.

## Auth

### `POST /api/auth/sync`

Synchronizes the authenticated Clerk user into PostgreSQL and ensures a default workspace.

Response:

```json
{
  "user": {},
  "workspace": {}
}
```

## Workspaces

### `GET /api/workspaces`

Lists workspaces for the authenticated user.

### `POST /api/workspaces`

Creates a workspace.

### `GET /api/workspaces/{workspace_id}/members`

Lists workspace members. Requires membership.

### `POST /api/workspaces/{workspace_id}/invites`

Creates an invitation. Requires owner/admin.

### `GET /api/workspaces/{workspace_id}/brand-settings`

Returns workspace brand settings.

### `PUT /api/workspaces/{workspace_id}/brand-settings`

Updates workspace brand settings. Requires owner/admin.

## Generation

### `POST /generate-sow`

Legacy synchronous demo-compatible generation endpoint.

### `POST /api/generations`

Creates a durable generation job.

Request:

```json
{
  "transcript_text": "Discovery call notes...",
  "client_name": "Luma Retail Co.",
  "project_name": "Brand Identity + Webflow Website",
  "industry": "Web Design",
  "tone": "professional",
  "budget": "$25,000",
  "timeline": "8 weeks"
}
```

Response:

```json
{
  "id": "uuid",
  "org_id": "uuid",
  "user_id": "uuid",
  "status": "queued",
  "current_step": "queued",
  "progress": 0
}
```

### `GET /api/generations/{generation_id}`

Returns job status.

### `GET /api/generations/{generation_id}/events`

Streams job progress as Server-Sent Events.

## SOWs

### `GET /sows` and `GET /api/sows`

Lists SOWs for the authenticated user/workspace.

### `GET /sows/{id}` and `GET /api/sows/{id}`

Returns one SOW.

### `PUT /sows/{id}` and `PUT /api/sows/{id}`

Updates SOW content and creates a version.

## SOW Sections

### `GET /api/sows/{sow_id}/sections`

Lists structured SOW sections.

### `PUT /api/sows/{sow_id}/sections/{section_key}`

Updates one section.

### `POST /api/sows/{sow_id}/regenerate-section`

Regenerates one section with an instruction.

### `POST /api/sows/{sow_id}/risk-audit`

Runs deterministic risk/quality validation against the current SOW.

## Exports

### `POST /sows/{id}/export-pdf`

Exports PDF. In production this should enqueue work and return export status or URL.

## E-Sign

### `POST /sows/{id}/send-signature`

Sends SOW for e-signature through DocuSign or demo fallback.

### `POST /webhooks/docusign`

Receives DocuSign status updates.

## Billing

### `GET /api/billing/plans`

Lists available plan metadata.

### `POST /api/billing/checkout`

Creates a PayPal subscription approval URL.

Request:

```json
{
  "plan": "studio",
  "success_url": "https://app.example.com/settings/billing?success=1",
  "cancel_url": "https://app.example.com/settings/billing?cancel=1"
}
```

### `GET /api/billing/usage`

Returns usage summary and quotas.

### `POST /webhooks/paypal`

Receives PayPal subscription webhooks. Production verifies PayPal signature headers and stores events idempotently.

## Templates

### `GET /api/templates`

Lists industries.

### `GET /api/templates/{industry}`

Returns template and clause intelligence data for one industry.

## Error Format

```json
{
  "detail": "Human-readable error message"
}
```

Common statuses:

- `400`: invalid request
- `401`: missing or invalid JWT
- `403`: missing workspace permission
- `404`: entity not found
- `429`: rate limit exceeded
- `500`: unexpected server error
