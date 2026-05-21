# BriefToScope Database Subsystem (Supabase PostgreSQL)

This directory houses the PostgreSQL schema definitions, performance indices, row-level security (RLS) policies, and seed templates required to power the BriefToScope platform.

---

## 📂 Directory Layout

```
database/
├── schema.sql           # Database schema & update triggers
├── indexes.sql          # Performance and compound query indexes
├── rls_policies.sql     # Row Level Security configuration
└── seed.sql             # Industry SOW templates (10 sectors) and mock accounts
```

---

## 🚀 Setup & Execution Guide

To deploy this database layer directly onto your Supabase dashboard or local PostgreSQL instance, execute the files in the following sequential order:

1. **`schema.sql`**: Sets up base tables, timestamps triggers, and foreign keys.
2. **`indexes.sql`**: Optimizes the system for rapid SOW list retrieval and analytics operations.
3. **`rls_policies.sql`**: Applies row isolation barriers preventing cross-user data leaks.
4. **`seed.sql`**: Populates the industry template directory and inserts seed data for demo accounts.
5. **`production_foundation.sql`**: Adds launch SaaS tables for workspace membership, section storage, billing, exports, jobs, and audit logs.
6. **`production_rls_policies.sql`**: Upgrades RLS to organization-membership policies for production tenancy.

> [!TIP]
> You can run these commands directly inside the **SQL Editor** of your Supabase dashboard.

For the production pair, you can also use the ordered PowerShell runner:

```powershell
$env:DATABASE_URL="postgresql://..."
.\apply_production_migrations.ps1
```

---

## 🤖 AI Workflow & Trace Storage

To guarantee startup-grade reliability and facilitate future LLM evaluations, this architecture isolates all intermediate AI execution steps:

### 1. Multi-Agent Logs (`ai_pipeline_runs`)
The `ai_pipeline_runs` table records the isolated inputs and outputs for agents **A1 through A7** (Cleaner, Extractor, Builder, Risk Detector, Clause Writer, Composer, and Checker). This allows:
*   **Trace ID Correlation**: Link each execution run to a single client generation request.
*   **Pipeline Auditing**: Inspect intermediate outputs (e.g. what text did A1 clean, what risks did A4 detect) for developer diagnostics.
*   **Latency & Cost Analytics**: Tracks active model tokens, response latencies, and execution costs.

### 2. Revision Diffs & Human Feedback (`sow_versions`)
When a user updates a SOW, the system stores:
*   `change_summary`: User-supplied explanations or auto-extracted change descriptions.
*   `diff_json`: Structured before/after textual block differences. This feed provides raw dataset training cycles to fine-tune future extraction models.

---

## 🛡️ RLS & Authentication Architecture

BriefToScope is designed to support both native **Supabase Auth** and external JWT assertions (e.g. **Clerk Auth**). This is managed via the database helper function `get_current_user_id()`:

```sql
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS UUID AS $$
...
```

### How it Works:
1. **Clerk Integration**: When Clerk signatures are passed as bearer JWTs to Supabase, Supabase decodes the claims. The function checks for the `'sub'` key representing the Clerk user ID and fetches the matching internal UUID from the `users` table.
2. **Supabase Native Integration**: If using native Supabase Auth, it falls back directly to `auth.uid()` mapping to the primary key of the user.

All user policies (e.g. `projects`, `transcripts`, `sows`, `ai_pipeline_runs`) reference `get_current_user_id()` to enforce tenant boundary safety.

---

## ⚙️ Backend Integration Guide

To migrate from the mock in-memory stores to this Supabase database layer, update your backend environment configuration (`repo/backend/.env`):

```env
DEMO_MODE=false
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-secret-key
```

Once `DEMO_MODE` is disabled, the backend `StorageService` (`app/services/storage_service.py`) automatically initializes the Supabase Python Client and routes all queries directly to the tables configured by this schema.
