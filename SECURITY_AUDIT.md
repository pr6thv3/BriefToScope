# Security Audit

Date: 2026-05-23

## Current Score

Security score: 82/100

BriefToScope is ready for a controlled paid beta after production secrets and provider accounts are configured. The main remaining gaps are operational: live env setup, external rate limiting, legal review, and E2E proof across deployed services.

## Implemented Controls

- Clerk JWT verification via JWKS outside demo mode.
- Next.js protected route middleware.
- PostgreSQL-backed workspace membership and RBAC.
- Backend `RequestContext` permission checks on protected APIs.
- Quota and inactive-subscription gates before generation, PDF export, and e-signature.
- Supabase RLS production policies.
- Private PDF storage path model with signed download URLs.
- PayPal webhook signature verification outside demo mode.
- Idempotent webhook event storage.
- Admin allowlist enforcement for readiness/worker health.
- Security headers and in-process rate limiting.
- Transcript sanitization and length validation.
- Audit logging for generation, edits, PDF exports, signed URL requests, e-sign, billing, and workspace actions.
- Sentry hooks for frontend/backend.
- No committed PayPal plan IDs, provider keys, or production secrets.

## Remaining Risks

| Risk | Severity | Status | Required Action |
| --- | --- | --- | --- |
| Edge/distributed rate limiting not deployed | Medium | Open | Add Cloudflare WAF rules or Upstash-backed limiter before broad launch |
| Legal docs need attorney review | Medium | Open | Review privacy, terms, AI disclosure, retention, refund policy |
| E2E tests are not complete | Medium | Open | Add Playwright flows for sign-up, generate, edit, export, billing |
| Supabase bucket config is manual | Medium | Open | Verify `sow-pdfs` is private in production |
| Provider incident procedures are manual | Low | Open | Document outage playbooks for AI, PayPal, Supabase, Clerk |

## Production Requirements

1. `DEMO_MODE=false`.
2. Production env validation passes.
3. Vercel has only public frontend variables.
4. Render API/worker have backend-only secrets.
5. Supabase service role is never exposed to frontend.
6. `sow-pdfs` bucket is private.
7. PayPal webhook ID and live plan IDs are configured.
8. Clerk issuer/JWKS match the production app.
9. `ADMIN_EMAIL_ALLOWLIST` contains only internal operator emails.
10. Sentry alerts and support email are monitored.

## OWASP Notes

- Broken access control: mitigated through JWT verification, workspace RBAC, and RLS defense in depth.
- Cryptographic failures: secrets are env-based; PDF URLs are signed and short-lived.
- Injection: Supabase client APIs are used instead of raw request-built SQL.
- Insecure design: production startup fails if required env vars are missing.
- Security misconfiguration: demo mode must never be enabled in production.
- Vulnerable components: run `npm audit --audit-level=high` and scheduled dependency checks.
- Logging/monitoring: Sentry and audit logs are wired; production alert routing still needs setup.
