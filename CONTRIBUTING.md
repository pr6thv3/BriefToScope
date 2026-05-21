# Contributing

## Development Principles

- Keep product behavior trustworthy before adding breadth.
- Prefer structured SOW data over raw generated Markdown.
- Enforce workspace authorization in the backend.
- Treat demo mode as local/demo-only.
- Keep AI/provider work behind service boundaries.

## Branching

- Use `codex/<description>` for Codex-authored branches.
- Use short feature branches for human work.
- Open draft PRs until tests and product QA pass.

## Local Checks

Backend:

```powershell
cd backend
python -m pytest
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

## Pull Request Requirements

- Explain what changed and why.
- Include screenshots for UI changes.
- Include tests or explain why they are not applicable.
- Update docs for API, schema, deployment, or env changes.
- Do not commit secrets or real customer data.

## Coding Standards

- Backend routes should call services, not embed business logic.
- Services should enforce permission-sensitive behavior explicitly.
- Frontend components should follow existing shadcn/Tailwind patterns.
- Avoid new global state unless a workflow needs it.
- Keep user-facing copy specific to agency scope intelligence.
