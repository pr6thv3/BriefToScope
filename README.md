# BriefToScope

**AI-powered Statement of Work generation for agencies and freelancers.**

BriefToScope transforms messy agency discovery-call notes into polished, client-ready Statements of Work in 90 seconds.

---

## Architecture

```
Frontend (Next.js)  →  Backend (FastAPI)  →  AI Pipeline  →  Supabase PostgreSQL
     ↓                      ↓                    ↓                    ↓
  Vercel              Render / Fly          OpenAI / Anthropic    Supabase
```

### AI Pipeline

```
A1 Transcript Cleaner
  → A2 Brief Extractor
    → A3 Scope Builder
      → A4 Risk Detector
        → A5 Clause Generator
          → A6 SOW Composer
            → A7 Quality Checker
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion |
| Backend | FastAPI, Pydantic v2, Python 3.12+ |
| AI | OpenAI GPT-4o-mini, Anthropic Claude (optional) |
| Database | Supabase PostgreSQL, JSONB, RLS |
| PDF | Playwright, Jinja2 HTML templates |
| Auth | Clerk |
| E-Sign | DocuSign (sandbox) |
| Payments | Stripe (scaffold) |

---

## Local Setup

### Prerequisites

- Node.js 20+
- Python 3.12+
- Supabase project (or run with `DEMO_MODE=true`)

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt
cp .env.example .env    # Edit with your keys
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # Edit NEXT_PUBLIC_API_URL
npm run dev
```

### Demo Mode

Set `DEMO_MODE=true` in `backend/.env` to run without API keys, database, or auth. All AI responses, auth, and storage are mocked with realistic data.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DEMO_MODE` | No | Set `true` for hackathon demo (default: `false`) |
| `OPENAI_API_KEY` | Prod | OpenAI API key for GPT-4o-mini |
| `ANTHROPIC_API_KEY` | No | Anthropic Claude key (optional) |
| `SUPABASE_URL` | Prod | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Prod | Supabase service role key |
| `CLERK_SECRET_KEY` | Prod | Clerk authentication secret |
| `FRONTEND_URL` | No | Frontend origin for CORS |
| `BACKEND_URL` | No | Backend public URL |
| `DOCUSIGN_CLIENT_ID` | No | DocuSign sandbox client ID |
| `DOCUSIGN_CLIENT_SECRET` | No | DocuSign sandbox client secret |
| `DOCUSIGN_ACCOUNT_ID` | No | DocuSign sandbox account ID |
| `DOCUSIGN_BASE_URL` | No | DocuSign sandbox base URL |
| `STRIPE_SECRET_KEY` | No | Stripe secret (scaffold) |
| `STRIPE_WEBHOOK_SECRET` | No | Stripe webhook secret (scaffold) |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL (default: `http://localhost:8000`) |

---

## API Routes

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/generate-sow` | Run AI pipeline → generate SOW |
| `GET` | `/sows` | List user's SOWs |
| `GET` | `/sows/{id}` | Get SOW detail |
| `PUT` | `/sows/{id}` | Update SOW content |
| `POST` | `/sows/{id}/export-pdf` | Generate + upload PDF |
| `POST` | `/sows/{id}/send-signature` | Send for e-signature |
| `POST` | `/webhooks/docusign` | DocuSign status webhook |

---

## Database Schema

Core tables: `users`, `projects`, `transcripts`, `sows`, `sow_versions`, `usage_events`, `esign_requests`

See [`database/schema.sql`](database/schema.sql) for full DDL, [`database/indexes.sql`](database/indexes.sql) for performance indexes, and [`database/rls_policies.sql`](database/rls_policies.sql) for row-level security.

---

## Deployment

### Backend → Render

1. Connect GitHub repo, set root directory to `backend/`.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add all env vars from `.env.example`.

### Frontend → Vercel

1. Connect GitHub repo, set root directory to `frontend/`.
2. Framework preset: Next.js.
3. Set `NEXT_PUBLIC_API_URL` to your Render backend URL.

### Database → Supabase

1. Create a Supabase project.
2. Run `database/schema.sql` in the SQL Editor.
3. Run `database/indexes.sql` and `database/rls_policies.sql`.
4. Optionally run `database/seed.sql` for demo data.

---

## Testing

```bash
# Backend
cd backend
python -m pytest -v

# Frontend
cd frontend
npm run lint
npm run build
```

---

## License

Proprietary — Medo Hackathon 2026.
