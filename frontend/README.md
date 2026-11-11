# Frontend live-backend integration

The current root index.html is intentionally retained as the working static demo. It embeds CONSOLE_DATA and persists decisions in browser localStorage; it does not call the API. The files in frontend/js/ are the new integration layer to use when migrating the page to live mode.

## 1. Configure the browser

Create frontend/config.js from config.example.js and provide:
- apiBaseUrl: deployed FastAPI origin, e.g. https://your-api.example.com
- supabaseUrl: Supabase project URL
- supabasePublishableKey: Supabase publishable/anon key (safe to expose in the browser)

Never put a database password, Supabase service_role key, or JWT signing secret in frontend files.

## 2. Load the modules

Serve the repository over HTTP(S), not file://. Add this before </body> in the console page after configuring window.ACADZA_CONFIG:

    <script src="/frontend/config.js"></script>
    <script type="module" src="/frontend/js/console-live.js"></script>

The first iteration should run beside the existing demo. Do not remove the static renderer until the live queue has been tested.

## 3. Sign in and load queue

The integration module exposes window.ACADZA_LIVE:
- signIn(email, password)
- signOut()
- loadQueue()
- submitProposal(reportId, proposal)
- approve(reportId, proposalId, expectedQuestionVersion, reason)
- reject(reportId, proposalId, reason)
- subscribe(onRefresh)

Render returned API objects with the existing visual components. When a change event arrives, call loadQueue() again. Events are notifications; the API/database remains the source of truth.

## 4. Replace the old local-only decision path

The old recordDecision() function in root index.html calls saveAudit(), which writes only to localStorage. It also tells the user that no question data changed. Do not call this for a live review.

In live mode:
1. Create a proposal using submitProposal.
2. Use the returned proposal ID and question version.
3. Call approve or reject.
4. Show success only after the API response succeeds.
5. On HTTP 409, reload the case and ask faculty to review the latest version.

Keep the demo mode available until this migration is complete.
