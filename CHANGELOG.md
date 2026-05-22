# Changelog

## Unreleased

### Added

- Production architecture foundation.
- Workspace tenancy schema and RLS policies.
- SOW section storage and risk flag foundation.
- Generation job persistence and Celery/Redis worker dispatch.
- PayPal subscription checkout and webhook reconciliation.
- Security headers and basic rate limiting.
- Repository documentation, launch reports, and governance files.
- Scheduled dependency-audit workflow that does not create extra branches.

### Changed

- Billing architecture standardized on PayPal Subscriptions.
- README rewritten for production product positioning.

### Security

- Production auth requires Clerk JWKS validation.
- PayPal webhook verification required outside demo mode.
- API and frontend security headers added.
