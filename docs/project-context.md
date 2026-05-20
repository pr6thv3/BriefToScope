# BriefToScope Project Context

This repo is now organized around the product PRD in `C:\Users\Preethve\Downloads\PRD.pdf`.

## Product Goal

BriefToScope converts messy discovery-call notes into a complete Statement of Work in roughly 90 seconds. The MVP must show the full loop:

1. User pastes transcript notes and selects an industry.
2. FastAPI validates the request and runs the AI pipeline.
3. The pipeline returns extracted facts, risk warnings, clauses, and a composed SOW.
4. The frontend presents live progress, extracted intelligence, editable SOW preview, PDF export, e-sign actions, history, and brand settings.

## Current Connected Surface

- Frontend: `frontend/`
  - Next.js App Router, TypeScript, Tailwind CSS v4, shadcn/ui, Framer Motion.
  - Routes: `/`, `/dashboard`, `/generate`, `/sow/[id]`, `/settings`.
  - API client: `frontend/src/lib/api.ts`.
- Backend: `backend/`
  - FastAPI endpoints: `/generate-sow`, `/sows`, `/sows/{id}`, `/sows/{id}/export-pdf`, `/sows/{id}/send-signature`.
  - Demo mode supports local full-flow development without Clerk, Supabase, provider keys, Playwright browser install, Stripe, or DocuSign credentials.

## Next Architecture Phase

Database architecture should formalize Supabase/Postgres ownership for:

- users, projects, transcripts, sows, sow_versions
- risk flags and extracted brief snapshots
- usage events, billing subscriptions, e-sign requests
- file/PDF storage metadata

AI data architecture should formalize:

- versioned agent inputs and outputs for A1 through A7
- trace IDs for generation runs
- prompt/template versions
- confidence/risk score provenance
- review/edit feedback loops for future model improvement
