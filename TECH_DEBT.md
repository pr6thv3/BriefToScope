# Technical Debt

## High Priority

| Item | Impact | Fix |
| --- | --- | --- |
| Frontend uses demo bearer token by default | Blocks secure production auth | Add Clerk provider, token retrieval, protected route guards |
| `StorageService` owns too many domains | Hard to reason about permissions and queries | Split into `UserRepository`, `WorkspaceRepository`, `SOWRepository`, `BillingRepository`, `JobRepository` |
| PDF storage can still fall back to public/demo URLs | Client document privacy risk | Enforce private Supabase bucket and signed URL records |
| Production migrations are additive SQL files without version tracking | Risk of duplicate/manual drift | Add migration tracking table or Supabase CLI migration workflow |
| Celery is wired but not deployed in infra | Long jobs can still run in API fallback | Add worker service in deployment blueprint |

## Medium Priority

| Item | Impact | Fix |
| --- | --- | --- |
| Legacy `/generate-sow` coexists with `/api/generations` | API surface confusion | Mark legacy endpoint deprecated after frontend migrates |
| SOW UI components are duplicated | Slower UI changes and inconsistent behavior | Consolidate around `components/sow-editor` |
| Missing frontend E2E tests | Regressions in paid workflows | Add Playwright tests for generate, edit, export, billing |
| In-process rate limiting | Insufficient for multiple API instances | Move enforcement to Cloudflare/Upstash |
| Python `datetime.utcnow()` warnings | Future compatibility issue | Replace with timezone-aware UTC helpers |

## Low Priority

| Item | Impact | Fix |
| --- | --- | --- |
| README screenshot placeholders need real captures | Less polished GitHub presentation | Add launch screenshots after final UI QA |
| Admin dashboard is a route shell | Limited ops value | Add job queues, webhook events, provider health |
| No public docs portal | Sales/support friction | Add `/docs` or external help center post-launch |

## Explicitly Postponed

- Multiplayer cursors
- Template marketplace
- Enterprise SSO
- Advanced legal review workflows
- Full Google Docs-style editor
- Vector memory personalization

These are valuable later, but not required before a focused paid beta.
