# Testing Strategy

## Current Coverage

Backend tests cover:

- AI data service
- Transcript cleaning
- Brief extraction
- Scope building
- Risk detection
- Quality checking
- Template service
- PDF export
- Synchronous generation endpoint
- PayPal webhook idempotency

Frontend currently has lint/build validation but no automated browser E2E tests.

## Required Checks

```powershell
cd backend
python -m pytest

cd frontend
npm run lint
npm run build
```

## E2E Tests To Add

1. New user onboarding creates workspace.
2. User generates SOW from transcript.
3. User edits one SOW section.
4. User regenerates one section.
5. User exports PDF.
6. User starts PayPal checkout.
7. Admin views readiness dashboard.

## API Tests To Add

- Clerk JWT failure cases.
- Workspace role permission matrix.
- Quota enforcement.
- PayPal webhook signature failure.
- Generation job failure and retry.
- Private PDF signed URL expiration.

## Manual QA Checklist

- Landing page responsive.
- Pricing page plan copy clear.
- Generate page handles loading/failure.
- SOW editor handles save/cancel/regenerate.
- Risk sidebar remains readable at desktop and tablet sizes.
- Billing settings show plan/usage state.
- Public share/sign routes never leak workspace controls.
