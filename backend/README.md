# BriefToScope Backend

FastAPI backend for BriefToScope — an AI SaaS that turns messy agency call notes into polished Statements of Work.

## Features

- **AI Pipeline**: 7-step modular pipeline (cleaner → extractor → scope builder → risk detector → clause generator → composer → quality checker)
- **SOW Management**: Create, list, view, update, and version SOWs
- **PDF Export**: Playwright-based professional PDF generation with HTML fallback
- **E-Signature**: DocuSign sandbox integration with automatic demo fallback
- **Billing**: Stripe webhook handling scaffolded
- **Demo Mode**: `DEMO_MODE=true` enables mock data for hackathon judging

## Tech Stack

- Python 3.11+
- FastAPI + Pydantic v2
- Supabase (PostgreSQL + Storage)
- OpenAI / Anthropic API
- Playwright (PDF export)
- Clerk (auth verification)
- Stripe (billing webhooks)

---

## Local Development

### 1. Clone and install

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`. For a quick hackathon demo without any external services:

```env
DEMO_MODE=true
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

For production, fill in all keys:

```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
CLERK_SECRET_KEY=sk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=https://your-app.vercel.app
BACKEND_URL=https://your-api.onrender.com
```

### 3. Run locally

```bash
# Standard
uvicorn app.main:app --reload --port 8000

# With demo mode
DEMO_MODE=true uvicorn app.main:app --reload --port 8000
```

OpenAPI docs: `http://localhost:8000/docs`

---

## Database Setup (Production)

Run these SQL commands in your Supabase SQL editor:

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_user_id TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL,
  name TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  client_name TEXT,
  project_name TEXT,
  industry TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE transcripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  raw_text TEXT,
  cleaned_text TEXT,
  metadata_json JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  user_id UUID REFERENCES users(id),
  title TEXT,
  content_json JSONB DEFAULT '{}',
  content_markdown TEXT,
  risk_flags_json JSONB DEFAULT '[]',
  confidence_score FLOAT DEFAULT 0,
  status TEXT DEFAULT 'draft',
  pdf_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sow_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sow_id UUID REFERENCES sows(id),
  version_number INT,
  content_json JSONB DEFAULT '{}',
  content_markdown TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE usage_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  event_type TEXT,
  token_count INT DEFAULT 0,
  estimated_cost FLOAT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE esign_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sow_id UUID REFERENCES sows(id),
  provider TEXT,
  status TEXT,
  signing_url TEXT,
  envelope_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE billing_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  plan TEXT,
  status TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

Enable Row Level Security (RLS) and add policies as needed.

---

## Deploy to Render

### Option A: Using Render Dashboard

1. Push your code to GitHub
2. Go to [dashboard.render.com](https://dashboard.render.com) → New Web Service
3. Connect your GitHub repository
4. Configure:
   - **Name**: `brief-to-scope-api`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && playwright install chromium
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
5. Add environment variables (copy from `.env`)
6. Click "Create Web Service"

### Option B: Using Render Blueprint (render.yaml)

Create a `render.yaml` in your repo root:

```yaml
services:
  - type: web
    name: brief-to-scope-api
    runtime: python
    plan: standard
    buildCommand: pip install -r requirements.txt && playwright install chromium
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DEMO_MODE
        value: false
      - key: OPENAI_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: CLERK_SECRET_KEY
        sync: false
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: FRONTEND_URL
        sync: false
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/generate-sow` | Generate SOW from transcript |
| GET | `/sows` | List user's SOWs |
| GET | `/sows/{id}` | Get SOW detail |
| PUT | `/sows/{id}` | Update SOW (creates version) |
| POST | `/sows/{id}/export-pdf` | Export PDF |
| POST | `/sows/{id}/send-signature` | Send e-signature request |
| POST | `/webhooks/stripe` | Stripe webhooks |
| POST | `/webhooks/docusign` | DocuSign webhooks |

### Quick Test (Demo Mode)

```bash
curl -X POST http://localhost:8000/generate-sow \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo" \
  -d '{
    "transcript_text": "We need a new website. Budget 100k. Timeline is end of year.",
    "industry": "Technology",
    "tone": "professional",
    "client_name": "Test Corp",
    "project_name": "New Website",
    "budget": "100k",
    "timeline": "EOY"
  }'
```

---

## Demo Mode

Set `DEMO_MODE=true` to run without any external API keys:

- **AI**: Returns realistic mock SOWs with rich sample data
- **Auth**: Skips Clerk JWT verification (accepts any Bearer token)
- **Storage**: Uses in-memory storage (no Supabase needed)
- **PDF**: Returns HTML fallback when Playwright is unavailable
- **E-Sign**: Returns mock DocuSign signing URLs
- **Billing**: Accepts Stripe webhooks without signature verification

This is the recommended configuration for hackathon judging and frontend development.

---

## Troubleshooting

### `playwright install chromium` fails on Render

Use the build command exactly as shown above. If it still fails, add:

```bash
apt-get update && apt-get install -y libnss3 libatk-bridge2.0-0 libxcomposite1
```

### CORS errors from Vercel frontend

Ensure `FRONTEND_URL` includes your Vercel domain. The backend automatically allows:
- `http://localhost:3000`
- `https://*.vercel.app`
- Your configured `FRONTEND_URL`

### AI pipeline returns low-quality output

- Use longer, more detailed transcripts (500+ words)
- Specify `industry` and `tone` explicitly
- Check `confidence_score` in the response; scores below 0.6 may need manual review

### PDF export fails

If Playwright is not installed, the backend returns a styled HTML document instead. You can:
1. Install Playwright: `playwright install chromium`
2. Or use browser print-to-PDF on the returned HTML

---

## License

MIT
