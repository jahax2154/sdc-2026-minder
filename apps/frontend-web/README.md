# Minder browser UI

Existing placeholder paths now host a small dependency-free ES-module UI. Start `minder_app.dev` from the backend README to serve UI 9103 and API 8103 against C's isolated SQLite file. Same-origin API calls, no cross-origin proxy or browser secrets. Exact navigation: Homepage/Overview, User Profile, Minder, Mindbots, Explore → Progress / Tasks / Future Explorer / Career Match / Roadmap. Company Explorer stays within Career Match.

Profile/self-report intake, TXT CV draft, bounded selected-role context, grounded chat availability, scoped role preferences/reset, separate company data, pathway preview/create, tasks/completion/progress, exact proposal approval/reject, action audit/undo and daily-check configuration call the real API. Whole-job automation and external actions are absent. Text is escaped; provider cannot write markup/actions. Root scripts/styles are served with CSP. Static assets plus API HTTP checks are separate from actual browser interaction evidence.

No model scores are computed in JavaScript. N01 pending and forecast-unavailable states remain visible. UI stores only anonymous local session capability and selected exploration role in sessionStorage; production auth/recovery is not provided. End-of-tab session loss does not delete the SQLite state.

Actual browser acceptance (Playwright library may be supplied from a temporary test installation; no root dependency changes):

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api MINDER_PLAYWRIGHT_MODULE=<absolute-module-path> PLAYWRIGHT_BROWSERS_PATH=<browser-directory> node apps/frontend-web/tests/browser_acceptance.cjs
```

This runs headless Chromium against the real localhost API, creates a labelled synthetic user, exercises navigation/intake/preferences/roadmap/progress/grounded-chat availability and a real worker proposal approved through UI, and writes sanitized evidence plus a synthetic screenshot under `ml/artifacts/session-c/`. It does not mock fetch, A/B services or the provider. Missing provider access remains explicit. The initial run used a temporary Playwright installation and browser under `/private/tmp`, without a tracked package/lockfile.

After provider confirmation/activation and restart, set `MINDER_REQUIRE_LIVE_PROVIDER=1` for browser acceptance to require successful native grounded selection. Browser evidence reports request-success booleans, never provider text/configuration. Worker diagnostics are scoped to the synthetic browser user's account. New optional official learning choices persist only when explicitly selected during roadmap creation; required/preferred/mandatory-status-unknown employer qualifications remain distinct.
