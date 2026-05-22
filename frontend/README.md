# BriefToScope Frontend

Next.js frontend for the BriefToScope MVP. It implements the PRD pages:

- `/` landing page
- `/dashboard` SOW history and intelligence summary
- `/generate` transcript-to-SOW workflow connected to FastAPI
- `/sow/[id]` editable SOW preview, PDF export, and e-sign actions
- `/settings` agency, brand, billing, and integration settings

## Local Development

Start the FastAPI backend in demo mode:

```bash
cd ../backend
$env:DEMO_MODE="true"
$env:FRONTEND_URL="http://localhost:3000"
python -m uvicorn app.main:app --reload --port 8000
```

Start the frontend:

```bash
cd ../frontend
npm install
copy .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## API Contract

The frontend uses `NEXT_PUBLIC_API_URL` plus Clerk sessions. Protected requests send:

- `Authorization: Bearer <Clerk JWT>`
- `X-Workspace-Id: <active BriefToScope workspace id>`

In local `DEMO_MODE=true`, the backend can still mock auth/storage, but the frontend no longer ships a hard-coded bearer token.

Connected endpoints:

- `GET /health`
- `POST /generate-sow`
- `GET /sows`
- `GET /sows/{id}`
- `PUT /sows/{id}`
- `POST /sows/{id}/export-pdf`
- `POST /sows/{id}/send-signature`
