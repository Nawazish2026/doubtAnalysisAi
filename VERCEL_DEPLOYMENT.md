# Vercel Deployment — Separate Faculty Console and API

The repository contains two distinct applications. They must be deployed as **two Vercel projects**.

| App | Repository root directory | What its home page should show |
|---|---|---|
| Faculty console (static assignment demo) | repository root: `./` | Acadza dark faculty review UI |
| FastAPI backend | `backend` | JSON service descriptor: `{"service":"Ac adza API","docs":"/docs"}` |

The JSON response is expected for the API project. It is not the faculty console.

## A. Keep the existing backend deployment

The deployment shown at:

`https://doubt-analysis-ai-e8rm.vercel.app`

is the API origin (based on the browser screenshot). Keep its Vercel project Root Directory set to `backend`, with the FastAPI preset and its server-only environment variables.

Useful API routes:
- `https://doubt-analysis-ai-e8rm.vercel.app/` — service descriptor
- `https://doubt-analysis-ai-e8rm.vercel.app/docs` — interactive API documentation
- `https://doubt-analysis-ai-e8rm.vercel.app/api/health` — health endpoint

The health route should be checked before relying on the backend. A successful response at `/` alone does not prove that every API operation or database workflow is healthy.

## B. Deploy the faculty console separately

1. Open the Vercel dashboard and choose **Add New → Project**.
2. Import the same GitHub repository: `Nawazish2026/doubtAnalysisAi`.
3. Give this project a distinct name, e.g. `acadza-faculty-console`.
4. Set **Root Directory** to the repository root (`./` or leave the root directory as the default; do not select `backend`).
5. Choose **Other** as the Framework Preset if Vercel asks.
6. Do not enter a build command. The repository root already contains `index.html` and `vercel.json`.
7. Leave the Output Directory at its default/blank value.
8. Deploy.

The root `index.html` is the precomputed faculty-console demo. It should render the UI at the new project's root URL, not the API JSON.

If the original domain `doubt-analysis-ai.vercel.app` is still attached to a different Vercel project, first check which project owns it. Assign it to the new frontend project only after removing it from the old project; a Vercel domain can only be assigned to one project at a time. Otherwise use the new frontend project's generated `.vercel.app` domain.

## C. What URL to submit

Submit the **frontend project's root URL** as the Faculty Console URL.

Keep the API URL separate and label it as the backend/API origin if you choose to mention it. Do not submit the API root as the faculty console link.

## D. Expected result

- Visiting the frontend URL shows the Acadza Faculty Review Console, with the queue, MathML question content, report details, diff and audit drawer.
- Visiting the API URL root shows the JSON service descriptor.
- Visiting the API URL plus `/docs` shows FastAPI's Swagger documentation.

## Important boundary

The currently deployed root console is the precomputed static demo. Its audit actions are browser-local; they do not write to the Supabase-backed API. The separate `frontend/live-console.html` is a login-based starter and needs `frontend/config.js`, database seed data and faculty-role setup. Do not represent it as a fully integrated realtime console until that flow has been verified.
