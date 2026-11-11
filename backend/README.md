# Acadza FastAPI backend

This backend is the first live-state implementation. It keeps the existing deterministic triage engine separate and uses Supabase Auth + PostgreSQL as the source of truth.

## Implemented
- Supabase access-token verification (JWKS for asymmetric signing keys; legacy HS256 supported with a server-only JWT secret).
- Server-side role checks from public.profiles.
- Student report submission and personal report retrieval.
- Faculty review queue with imported triage fixture details.
- Taxonomy-validated repair proposals.
- Version-checked, transactional approval/rejection.
- Question version snapshots and append-only review/audit records.
- Demo JSON importer for questions, reports and results.

New live submissions are routed to faculty_review. The existing triage_engine.py has assignment-specific report-ID rules; it is not safe to run against arbitrary production reports. A generalized triage provider/worker is intentionally not included yet.

## Files
backend/app/main.py: FastAPI app and routers.
backend/app/config.py: environment configuration.
backend/app/db.py: asyncpg pool and dependency.
backend/app/security.py: Supabase JWT verification.
backend/app/dependencies.py: user and faculty authorization guards.
backend/app/schemas.py: request validation.
backend/app/taxonomy.py: loads the existing taxonomy.
backend/app/routers/: report, question, review and audit endpoints.
backend/app/services/proposals.py: repair scope and exact-edit validation.
backend/app/services/approval.py: atomic review and question mutation.
backend/migrations/001_initial_schema.sql: tables, RLS and Realtime publication.
backend/scripts/seed_demo.py: imports anonymized fixture JSON.
backend/tests/test_proposals.py: proposal validation tests.

## 1. Create Supabase project
Create a project at https://supabase.com. Copy the project URL, publishable/anon browser key, and PostgreSQL connection string. Add your local and deployed frontend URLs in Auth > URL Configuration.
Use an asymmetric JWT signing key (ES256 recommended). The API verifies it through the project's JWKS endpoint. If the project still uses legacy HS256, put SUPABASE_JWT_SECRET only in backend/.env.
Never put the database password, JWT secret, service_role key, or secret API key in the frontend.

## 2. Apply migration
Open Supabase SQL Editor and run backend/migrations/001_initial_schema.sql. It creates the profile trigger, tables, indexes, RLS policies and Realtime publication entries.

## 3. Configure backend
From repository root: cp backend/.env.example backend/.env
Edit backend/.env with DATABASE_URL, SUPABASE_URL, optional SUPABASE_JWT_SECRET, CORS_ORIGINS and APP_ENV. Use a persistent-compatible Supabase direct or Session Pooler connection for asyncpg; do not assume a transaction pooler supports long-lived connections.

## 4. Install and run
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Open http://127.0.0.1:8000/docs and /api/health.
The app loads backend/.env from the backend working directory. Keep it out of Git.

## 5. Import demo data
From backend directory with the virtual environment active, run: python scripts/seed_demo.py
The importer expects data/questions.json, data/reports.json and results.json at repository root. It imports external report IDs and student fixture IDs as references, not real Supabase user IDs. Existing rows are not overwritten.

## 6. Create a faculty account
Sign up a user through Supabase Auth. A database trigger creates a student profile by default. In Supabase SQL Editor, promote the intended faculty user's Auth UUID explicitly:

    update public.profiles set role = 'faculty' where id = 'REPLACE-WITH-AUTH-USER-UUID';

Never let public signup metadata choose a role. Keep at least one separately controlled admin account.

## 7. Frontend setup
Copy frontend/config.example.js to frontend/config.js and set apiBaseUrl, supabaseUrl and supabasePublishableKey. Serve repository root with python3 -m http.server 3000. Open http://127.0.0.1:3000/frontend/live-console.html and sign in with the faculty account.
The static root index.html remains the original demo. It has not been replaced or automatically switched to live mode.

## API endpoints
POST /api/reports
GET /api/reports
GET /api/reports/{report_id}
GET /api/faculty/queue?status=open
POST /api/reports/{report_id}/proposals
POST /api/reports/{report_id}/proposals/{proposal_id}/approve
POST /api/reports/{report_id}/proposals/{proposal_id}/reject
GET /api/questions
GET /api/questions/{question_id}
GET /api/questions/{question_id}/history
GET /api/audit-logs
GET /api/health

## Known limits
- The new faculty page is a functional starter; the old root console is preserved.
- New reports enter faculty review; generalized AI triage is not implemented.
- Image/diagram changes and non-text field edits are not supported by the first surgical-edit service.
- FastAPI uses a server-side database connection and enforces app roles. Keep credentials secret and never use elevated credentials in frontend code.
- Before production: add rate limiting, tracing, monitoring, backups, alerting, notification delivery, data-retention controls and an independent security review.