# Cleanup Report

Date: 2026-05-21

## Scope

Audited repository structure, backend services, frontend app routes/components, database migrations, documentation, CI readiness, and production configuration.

## Completed Cleanup

- Removed active Stripe platform references and aligned billing architecture to PayPal.
- Added ordered production migration runner.
- Added backend security middleware for headers, request IDs, and basic rate limiting.
- Added centralized `BriefToScopeError` handling.
- Added frontend security headers and SEO metadata.
- Added GitHub-ready documentation and launch reports.
- Added Celery/Redis worker package and generation job dispatcher.
- Added PayPal webhook idempotency test.

## Folder Structure Findings

- `backend/app/api`: reasonable router split by product domain.
- `backend/app/services`: modular but several services still mix storage/provider/business logic.
- `frontend/src/components/sow` and `frontend/src/components/sow-editor`: overlapping SOW UI families should be consolidated.
- `database`: contains base schema plus additive production migrations; this is workable but needs migration versioning before team scale.
- `.github`: was missing and should be treated as required governance/CI surface.

## Code Quality Findings

- Demo mode is useful but production code paths must be tested with Supabase/Clerk/PayPal credentials before launch.
- `StorageService` is large and should be split into repositories by domain.
- Some legacy endpoints exist alongside `/api/*` aliases; keep for compatibility short-term, then version and deprecate.
- Several datetime uses rely on `datetime.utcnow()`, which emits Python 3.14 deprecation warnings.
- API client currently sends `Authorization: Bearer demo` by default; production Clerk token injection must replace this.

## Security Findings

- No hardcoded secrets found in tracked files.
- PayPal webhook verification exists outside demo mode.
- Clerk JWT verification requires JWKS outside demo mode.
- Rate limiting is currently in-process and should move to Cloudflare/Upstash for multi-instance deployments.
- Private PDF signed URL flow is documented but storage upload still needs full private-bucket enforcement.

## Frontend Findings

- Design direction is premium and consistent enough for a private beta.
- Route shells exist for production surfaces.
- Auth, onboarding, billing, and team settings need real data-bound flows.
- Mobile polish still requires browser QA across core workflows.

## Database Findings

- Production tenancy tables and RLS policies exist.
- RLS is defense-in-depth because backend uses service role.
- Need migration tracking/version table before repeated production releases.
- Need query plans once real data exists.

## Recommended Cleanup Next

1. Split `StorageService` into repositories.
2. Replace frontend demo bearer token with Clerk auth provider.
3. Move PDF storage to private bucket with signed URL records.
4. Consolidate SOW editor component families.
5. Add migration versioning and staging migration tests.
