# Vercel Deployment

This is a static site. It requires no environment variables, build command, server, or database.

## Project settings

- Framework preset: `Other`
- Build command: leave blank
- Output directory: leave blank
- Install command: leave blank
- Root directory: repository root

Vercel will serve the root `index.html`. The deployment configuration adds basic browser-security headers and prevents local source files, raw fixtures, and development scripts from being included in the public artifact.

## Deploy

Import the repository in Vercel, keep the project settings above, and deploy. Alternatively, run:

```bash
npx vercel --prod
```

## Data note

The console intentionally embeds the demo queue, reports, and triage outcomes in `index.html` so it works without a backend. Do not deploy real student reports or personally identifiable data with this static architecture. A production rollout needs authenticated access and a server-side data/API layer.
