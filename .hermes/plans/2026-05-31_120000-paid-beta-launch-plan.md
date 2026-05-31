# Paid Beta Launch Plan for BriefToScope

## Goal
Implement the paid beta launch plan fully on the single `main` branch only. Do not create or leave feature branches. Commit all completed work to GitHub on `main`.

## Current Context / Assumptions
- Repository is at `/d/BriefToScope/repo`
- Backend: FastAPI (Python) in `/backend`
- Frontend: Next.js (TypeScript) in `/frontend`
- Existing features: Clerk auth, RBAC/quotas, private PDF signed URLs, PayPal billing APIs, Celery queue scaffolding, AI validation, tests passing.
- Deployment: Vercel (frontend), Render (backend and worker), Upstash Redis (implied by Render config)
- Environment variables are managed via Render and Vercel configurations.

## Proposed Approach
Follow the 10-step plan in order, ensuring each step is completed and tested before moving to the next. All work will be committed to `main` branch.

### Step 1: Production Deployment Readiness
- Verify Vercel frontend configuration (already has `vercel.json` with required env vars)
- Verify Render FastAPI service configuration (`render.yaml` shows web service)
- Verify Render Celery worker configuration (`render.yaml` shows worker service)
- Verify Upstash Redis config (via `REDIS_URL` sync in render.yaml)
- Ensure env validation fails clearly when required production env vars are missing (check `backend/app/config.py` validation function)
- Ensure `DEMO_MODE=false` production path never returns fake provider success (check LLm client and other services for demo mode guards)

### Step 2: Observability
- Add Sentry wiring for frontend and backend (already partially configured, need to verify and possibly enhance)
- Add PostHog frontend analytics events (need to add event tracking in frontend)
- Add Langfuse or Helicone-compatible LLM trace hooks if env vars exist (check backend LLM client)
- Track key events:
  - signup
  - workspace synced
  - generation started
  - generation completed
  - generation failed
  - SOW edited
  - PDF exported
  - signed URL requested
  - e-sign sent
  - checkout started
  - subscription changed
  - quota reached

### Step 3: AI Quality Hardening
- Create an `evals/` folder (already exists, need to verify contents)
- Add 20 realistic sample transcripts across:
  - web design
  - branding
  - SEO
  - marketing
  - copywriting
  - consulting
  - app development
  - video/video production
- Add an AI output evaluation script that scores:
  - clarity
  - deliverable specificity
  - timeline completeness
  - payment schedule presence
  - client responsibilities
  - revision policy
  - acceptance criteria
  - risk detection
- Store eval results as JSON/Markdown report.
- Ensure generated SOWs persist structured JSON as canonical data before Markdown/PDF.

### Step 4: Risk Intelligence Improvements
- Expand risk detector rules for:
  - unlimited revisions implied
  - SEO mentioned but not scoped
  - copywriting responsibility unclear
  - client assets missing
  - timeline dependency missing
  - third-party tools unspecified
  - custom animation complexity unclear
  - payment milestone missing
  - acceptance criteria missing
  - ownership/IP unclear
- Surface these warnings in the editor sidebar.
- Add tests for each risk case.

### Step 5: Clause/Template Improvements
- Expand industry templates and clause library for:
  - web design
  - branding
  - SEO
  - marketing
  - copywriting
  - consulting
  - app development
  - video production
- Each template must include:
  - standard deliverables
  - common out-of-scope items
  - revision policy
  - client responsibilities
  - payment milestone suggestions
  - acceptance criteria
  - hidden scope traps
- Add tests to verify templates load and contain required sections.

### Step 6: Editor and Onboarding Polish
- Improve empty states for dashboard/generate/settings.
- Improve quota reached state.
- Improve billing expired/past_due state.
- Improve export failed state.
- Improve generation failed state.
- Add onboarding checklist:
  - create workspace
  - generate first SOW
  - review risk warnings
  - export PDF
  - upgrade plan
- Keep UI simple. Do not rebuild the app.

### Step 7: Billing and Monetization Polish
- Verify PayPal live env vars are documented.
- Ensure billing page shows:
  - current plan
  - renewal date
  - subscription status
  - usage limits
  - used/remaining quota
  - upgrade/cancel/reactivate actions
- Ensure backend blocks expensive actions when:
  - plan quota is exhausted
  - subscription is canceled/past_due/suspended/unpaid
  - feature is not included in plan
- Add clear upgrade prompts.
- Use PayPal only for payment approval; BriefToScope owns in-app billing UX.
- PayPal webhooks must be idempotent and update local subscription state.

### Step 8: Legal/Support/Compliance Polish
- Finalize `/privacy`, `/terms`, `/ai-disclosure`, `/support`.
- Add `/data-retention`.
- Add `/refund-policy`.
- Add clear AI disclaimer:
  - SOWs are AI-assisted drafts
  - user must review before sending
  - not legal advice
- Add support email env/config.

### Step 9: Tests and Validation
- Add/extend tests for:
  - auth required
  - RBAC denied
  - quota exhausted
  - inactive subscription blocked
  - private PDF signed URL only
  - PayPal webhook idempotency
  - AI validation failure
  - risk detection rules
  - template required fields
- Run:
  - backend `python -m pytest`
  - frontend `npm run lint`
  - frontend `npm run build`
  - `npm audit --audit-level=high`
  - `git diff --check`

### Step 10: Documentation Update
- Update:
  - README.md
  - ARCHITECTURE.md
  - API_REFERENCE.md
  - DEPLOYMENT.md
  - SECURITY_AUDIT.md
  - LAUNCH_CHECKLIST.md
  - TECH_DEBT.md
- Add a final `PAID_BETA_READINESS.md` with:
  - what is ready
  - what remains
  - env vars needed
  - deployment checklist
  - launch checklist

## Files Likely to Change
### Backend
- `app/config.py` - validation and settings
- `app/main.py` - lifespan and observability init
- `app/services/llm_client.py` - demo mode and LLM tracing
- `app/services/risk_detector.py` - risk rules expansion
- `app/services/*` - various services for tracking, blocking, etc.
- `app/api/routes_*` - route handlers for events and blocking
- `app/models/*` - possibly for storing structured JSON SOWs
- `app/services/storage_service.py` - for structured JSON persistence
- `app/services/sow_composer.py` - for structured JSON output
- `tests/` - new and updated tests

### Frontend
- `frontend/vercel.json` - ensure all required env vars are present
- `frontend/src/app/` - page components for empty states, onboarding, billing page
- `frontend/src/components/` - reusable components for risk warnings, etc.
- `frontend/src/lib/` - analytics and tracking utilities
- `frontend/src/app/(page)/layout.tsx` - for adding analytics wrappers
- `frontend/src/app/onboarding/page.tsx` - onboarding checklist
- `frontend/src/app/settings/billing/page.tsx` - billing page enhancements
- `frontend/src/app/(page)/error.tsx` - error states

### Evals
- `evals/sample_transcripts.json` - add 20 transcripts
- `evals/evaluate_outputs.py` - enhance scoring script
- `evals/reports/` - store evaluation results

### Documentation
- All markdown files in root: README.md, ARCHITECTURE.md, etc.
- New file: PAID_BETA_READINESS.md

## Tests / Validation
### Backend
- Unit tests for risk detector rules
- Integration tests for billing blocking (quota, subscription status)
- End-to-end tests for SOW generation flow with structured JSON
- Tests for template loading and validation
- Observability: test that events are tracked (mock PostHog/Sentry)
- Production config validation: test missing env vars raise clear errors

### Frontend
- Component tests for empty states and onboarding
- E2E tests (if using Cypress/Playwright) for key user flows
- Linting and build checks
- Audit for high severity vulnerabilities

### Deployment
- Verify Render and Vercel deployments work with prod config
- Check that health endpoints return 200
- Verify worker processes jobs from queues

## Risks, Tradeoffs, and Open Questions
### Risks
- Missing environment variables in production causing downtime
- Over-blocking legitimate users due to strict quota/subscription checks
- AI quality evaluation being too strict or not correlating with user satisfaction
- PayPal webhook idempotency issues leading to duplicate subscription updates
- Legal pages not being reviewed by actual counsel (though we are adding disclaimers)

### Tradeoffs
- Simplicity vs. completeness: We are avoiding enterprise features, marketplace, vector memory, etc. to keep it solo-founder maintainable.
- Using PayPal only limits payment options but simplifies compliance and reduces scope.
- Not using Clerk Organizations as source of truth means we manage our own workspace/role mapping in PostgreSQL.

### Open Questions
- What is the exact structure for structured JSON SOW persistence? (Should follow AI-generated schema)
- Which specific risk detector rules are currently implemented and which need to be added?
- What are the current industry templates and what sections are missing?
- What is the current state of the onboarding flow and empty states?
- Are there any existing tests for the billing webhook idempotency?

## Next Steps
After creating this plan, the next phase would be to begin implementation starting with Step 1, verifying each component and moving forward only when each step is complete and tested.
