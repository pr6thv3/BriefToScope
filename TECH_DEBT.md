# Technical Debt

## High Priority

| Item | Impact | Fix |
| --- | --- | --- |
| `StorageService` owns too many domains | Hard to reason about billing, jobs, SOWs, and workspace queries | Split into repositories after paid beta |
| E2E coverage is thin | Browser regressions can reach beta users | Add Playwright tests for auth, generate, edit, export, billing |
| Rate limiting is in-process | Multiple API instances need shared limits | Add Cloudflare WAF or Upstash-backed limiter |
| Production migration workflow is manual SQL | Operator error risk | Move to Supabase CLI migrations with migration history |

## Medium Priority

| Item | Impact | Fix |
| --- | --- | --- |
| Legacy `/generate-sow` remains | Confusing API surface | Deprecate after deployed `/api/generations` is stable |
| SOW components are partially duplicated | UI changes take longer | Consolidate legacy `components/sow` into `components/sow-editor` |
| Admin dashboard is minimal | Ops visibility is limited | Add queue depth, webhook events, failed jobs, provider status |
| Clerk user profile display is workspace-first | Less personalized UI | Add user name/avatar from Clerk context after beta |
| Legal docs are product-ready but not counsel-reviewed | Commercial risk | Review before broad public launch |

## Low Priority

| Item | Impact | Fix |
| --- | --- | --- |
| README screenshot placeholders need real captures | GitHub is less polished | Capture after production deploy |
| AI eval harness is deterministic only by default | Does not yet compare real model outputs automatically | Add CI eval mode after stable test fixtures are generated |
| No status page | Manual incident communication | Add hosted status page post-launch |

## Explicitly Postponed

- Marketplace
- Vector memory
- Enterprise SSO
- Multiplayer editing
- Full Google Docs-style editor
- Kubernetes
- Stripe migration

These are intentionally not blockers for the first paid beta.
