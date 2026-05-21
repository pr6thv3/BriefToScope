# Performance Report

Date: 2026-05-21

## Current Performance Score

Score: 76/100

The frontend builds successfully with Next.js 16 and the backend test suite passes. The largest future performance risks are AI latency, PDF generation blocking, unbounded provider retries, and missing production cache/queue metrics.

## Implemented Performance Controls

- Next.js production build passes.
- Frontend uses static generation for many route shells.
- Heavy generation jobs have a Celery/Redis-ready dispatch path.
- SSE-style generation event stream is available.
- Database includes indexes for workspace membership, SOW sections, risks, usage events, audit logs, and jobs.
- AI pipeline records stage progress and can surface generation state to users.

## Frontend Opportunities

| Area | Recommendation |
| --- | --- |
| Bundle size | Add bundle analyzer before public launch |
| Route loading | Add route-level skeletons for protected pages |
| Editor performance | Use virtualization if SOW sections become long |
| Images | Add real optimized screenshots and use Next image handling |
| Mobile | Run Playwright/Lighthouse viewport checks for editor and generate flow |

## Backend Opportunities

| Area | Recommendation |
| --- | --- |
| AI latency | Queue generation, stream progress, cache clause templates |
| PDF generation | Move export fully to Celery worker |
| Database | Run `EXPLAIN ANALYZE` after real usage data exists |
| Caching | Add Redis cache for templates and plan metadata |
| Provider retries | Add bounded retries with dead-letter job states |

## Targets Before Launch

- Landing Lighthouse performance: 90+
- Dashboard TTFB: under 500 ms warm path
- Generation request response: under 300 ms to queued job
- Generation completion: under 90 seconds for normal briefs
- PDF export job: under 30 seconds for normal SOWs
- API p95 non-AI latency: under 300 ms

## Measurement Gaps

- No Lighthouse CI yet.
- No bundle size budget yet.
- No queue depth dashboard yet.
- No PostHog funnel instrumentation yet.
- No Sentry release tracking yet.
