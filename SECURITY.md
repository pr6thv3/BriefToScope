# Security Policy

## Supported Versions

The `main` branch is the only supported production line until formal versioning begins.

## Reporting A Vulnerability

Do not open a public GitHub issue for sensitive security reports.

Email: `security@brieftoscope.com`

Include:

- Affected route, component, or workflow
- Reproduction steps
- Impact assessment
- Any proof-of-concept payloads

Expected response target:

- Acknowledgement: 3 business days
- Initial triage: 7 business days

## Security Requirements

- Never commit secrets.
- Never enable `DEMO_MODE=true` in production.
- Keep Supabase service role keys backend-only.
- Verify Clerk JWTs in production.
- Verify PayPal webhooks in production.
- Store client documents in private storage.
- Audit sensitive actions.

## Dependency Security

Use GitHub Dependabot and CI audits before production launch. Critical dependency alerts should block release until resolved or formally accepted.
