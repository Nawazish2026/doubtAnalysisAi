# Frontend console and Supabase live-backend integration

There are two faculty experiences in this repository:

- `/index.html`: original, polished assignment demo. It uses precomputed `CONSOLE_DATA` and browser-localStorage audit entries.
- `/frontend/live-console.html`: login-protected starter console. It signs in through Supabase Auth, calls the FastAPI backend, reads the Supabase-backed faculty queue/audit, and subscribes to Supabase Realtime.

The live page is a separate integration path; it does not silently change the static demo into a database-backed application.

## Production wiring (Vercel)

Deploy the repository root as the **frontend Vercel project**. Keep the FastAPI project deployed separately with Root Directory `backend`.

The frontend project needs these Environment Variables (Production, Preview only if you use preview deployments too):

| Variable | Value |
|---|---|
| `SUPABASE_PUBLISHABLE_KEY` | Supabase project's public publishable key (legacy anon key is accepted as `SUPABASE_ANON_KEY`) |
| `SUPABASE_URL` | `https://pxhkyznkdytcrrgdeqjq.supabase.co` (already used as the runtime default) |
| `ACADZA_API_BASE_URL` | `https://doubt-analysis-ai-e8rm.vercel.app` (already used as the runtime default) |

The `/api/config` Vercel function reads these values server-side and emits a small JavaScript object for the browser. The Supabase publishable/anon key is intentionally public browser configuration. **Never set a database password, Supabase service-role key, or JWT signing secret in this frontend project.**

After adding the key, redeploy the frontend project. Open:
- `https://doubt-analysis-ai.vercel.app/frontend/live-console.html`
- `https://doubt-analysis-ai.vercel.app/api/config` to verify `configured: true` and an empty `missing` array (the response intentionally includes the public publishable key).

## Backend Vercel environment

Set these only in the separate backend Vercel project (Root Directory `backend`):

- `DATABASE_URL`: Supabase PostgreSQL **Transaction Pooler** URL (port 6543) for the serverless API. Use your rotated database password; URL-encode reserved characters.
- `SUPABASE_URL`: `https://pxhkyznkdytcrrgdeqjq.supabase.co`
- `CORS_ORIGINS`: `https://doubt-analysis-ai.vercel.app,http://localhost:3000,http://127.0.0.1:3000`
- `APP_ENV`: `production`
- `SUPABASE_JWT_SECRET`: only for a legacy HS256 signing configuration; keep it server-side.

Redeploy the backend after changing environment variables. Confirm `/api/health` returns `{"ok":true,"service":"ac adza-api","database":"connected"}`. If it returns an error, inspect the latest Vercel Runtime Logs; the root `/` JSON response by itself is not a database health check.

## Database setup

1. In Supabase SQL Editor, run `backend/migrations/001_initial_schema.sql` once (it is safe to rerun for the objects it defines).
2. From the repository root, create `backend/.env` from `backend/.env.example` and set a local `DATABASE_URL`. Keep this file out of Git.
3. Install importer dependencies with `python3 -m pip install -r backend/requirements.txt`.
4. Run `python3 backend/scripts/seed_demo.py` from the repository root. It imports the supplied fixture's questions, reports and 44 precomputed triage results. The importer uses SSL and disables statement caching for pooler compatibility; it is idempotent for the fixture IDs.
5. Create a user in Supabase Authentication. The migration's trigger creates a `student` profile. Promote your own intended faculty account in SQL Editor using its Auth user UUID:
   `update public.profiles set role = 'faculty' where id = 'YOUR-AUTH-USER-UUID';`
6. Open the live console and sign in with that faculty account.

Do not put the database connection string in frontend code, browser config, GitHub, or the Loom recording.

## Local frontend

Copy `frontend/config.example.js` to `frontend/config.js`, fill in the API origin, Supabase URL and publishable/anon key, then serve the repository over HTTP:

```bash
python3 -m http.server 3000
```

Open `http://127.0.0.1:3000/frontend/live-console.html`.

## Public demo review actions (no login)

The root `/` dashboard is now connected to the Supabase-backed public demo API. Its Reject / Dismiss, Save Edited Fix and Approve buttons write to the database; question changes are versioned, proposals and decisions are recorded, and the dashboard refreshes its view and audit history from the database. Apply `backend/migrations/003_public_demo_actions.sql` in Supabase SQL Editor after running the demo seed script.

No login is required for this shared demo. Public write access is restricted server-side to the fixture report IDs `R001`–`R044` present when the allowlist migration runs. Any visitor can alter those shared demo records, so do not add real student reports to this allowlist. The separate `/frontend/live-console.html` remains the authenticated faculty workflow for non-demo records.

## Realtime and write flow

- Supabase Auth provides the user's access token.
- The browser sends that token as a Bearer token to FastAPI.
- FastAPI verifies the token and checks `public.profiles.role`.
- The faculty queue and audit history are read from PostgreSQL.
- Faculty creates a taxonomy-scoped proposal; approval checks the question version and exact-match patch, then atomically writes the question change, version snapshot, review decision and audit event.
- Supabase Realtime sends table-change notifications; the browser refreshes queue and audit data from the API (the database remains the source of truth).

If Realtime is disconnected, the page displays the status and the Refresh Queue button still fetches current data.

## Known limitations

- New live reports are sent to manual faculty review. The fixture-specific deterministic engine is not called for arbitrary new report IDs.
- No generalized LLM triage worker is connected yet.
- The original homepage demo's audit drawer remains browser-local; use the **Live Backend** link to access the database-backed page.
- Validate the database seed, faculty role, API health and two-browser Realtime behavior before claiming the full workflow is production-verified.
