# F Revision3 frontend source handoff — local acceptance, external gaps open

The containing F refinement commit is the immutable source checkpoint. Branch:
session/f-product-frontend. No main/force push and no deployment. A must consume
committed F history, never copy ongoing files. Original repair8446ca8 preserved.

## Exact phase and dependency SHAs

- 8446ca8: `8446ca801de8d8a0163c390f76d2aa609a5fec16`
- 57edea4: `57edea4abc9b77645d285c6122dfb2df89e6a3a3`
- 02d5b83: `02d5b83c31c671626b514054ff7d477f70d93678`
- 397b410: `397b4105505c7255b87ab742a0ca567add1b2d7c`
- 631be6a: `631be6a5415a1c7da172941df36664df5e2f3c26`
- 45be4df: `45be4df58e1ae702cb780de317fd7effffef1380`
- 09a653d: `09a653d31268662ab76749f669d3f628439fac4a`
- 178a7a8: `178a7a8cccdd7b65a1a4fec068aa9d43570f65b1`
- e8f70d2: `e8f70d26d3589c98a90a5f252813f83b74541fb1`
- 37d9fcb: `37d9fcb0d0c0917e673eece958ea0aaebbe6c3b0`
- 53e1544: `53e154459cf53eb9c2472658d381b85b4ad3302a`
- 1669142: `1669142ade6ac1e8f9790633e3b9e125c97a7aa1`

The final source includes A37d9fcb, D53e1544 and E1669142 via A's committed integration.
No F edits to backend/provider/grounder/scoring/deployment files. Importing upstream
hosting/GPU preparation source is not executing a deployment or paid experiment.

## Actual UI and retained source layout

http://127.0.0.1:9106/#minder
http://127.0.0.1:9106/#mindbots
http://127.0.0.1:9106/#profile
http://127.0.0.1:9106/#careers/matches
http://127.0.0.1:9106/#my-path/next

F API8106, private lane Store. Normal runtime restored after isolated tests; worker
not auto-started in F (A's official supervised local worker is A-only). Existing
Qwen qwen/qwen3.8-27b config remains server-only. No frontend provider call.

Approved Profile/Explore assets are scoped into existing72px shell. Careers has
Matches/Compare/Outlook. My Path follows supplied Next steps/Roadmap/Skills/Progress
order. Profile has adaptive three-question setup, optional review, five returning
tabs, focused edits/dirty guard and CV/resume-only library. Context Close/Escape,
Working terminal cleanup, rail labels and independent Mindbot reads retained.
Overview body was not redesigned by F.

Minder creates/lists/opens/deletes/continues server conversations. Mindbot has one
continuous singleton, inline replies/draft review/proposals/actions/task controls,
no New/list/branch/switch and no send-to-Minder redirect. Scheduled notices append
there. Private history/plans never use localStorage. Owner changes clear private
UI/caches; late replies cannot restore an older identity. Server owner reference
in sessionStorage scopes nonauthoritative UI preferences only, never history.

Generated roadmap saves require exact server draft/Profile versions and explicit
acceptance; activation is another explicit step. Refresh reads persisted records.
All displayed progress comes from canonical task state. No prototype scores/tasks/
forecasts, readiness claims or hidden implicit plan creation. Actual source scopes
and O*NET31 CC BY4.0 changes attribution remain available.

## Final bounded refinements and actual checks

- Real-provider capability reply:966ms, generated_guidance, invoked/available Qwen;
  useful complete English answer, no repeated policy/rubric block. Mindbot student
  nextstep1279ms. Histories/refresh/delete/singleton/logout pass.
- Real generated draft2055ms → explicit save → deliberate lost acceptance response
  → exact same-key retry: one canonical plan/version → explicit activation. Actual
  generated phases refresh without regeneration. Same-Mindbot contextual one-hour
  follow-up leaves the saved plan unchanged. Prior detailed MF2 report retained.
- Real task completion response loss/exact retry: one action/version, no replay.
  Stop waiting with a held real-provider response clears Working; original text
  locks until exact saved receipt. Reading matching old text cannot confirm receipt.
- Actual immutable structured task/scope proposals: complete escaped values, no
  effects before decision, reject preserves state, approve applies once. Unsupported
  generic Undo hidden; canonical edit/schedule/cancel stays inside Mindbot.
- Actual approval response loss reconciles saved applied state with one decision;
  independent welcome/history load cannot hide or intercept action controls.
- Actual Profile/CV/PDF flow, metadata merge, dirty Stay, refresh, self-report separation,
  TXT corrected review, text-PDF draft and scanned reason passed. CV library network
  fault has a working retry. Lost reviewed-save response retries same body/version
  once; editor cannot silently change intent. PDF request deadline18s covers D's
  bounded12s parser; no OCR or automatic profile application.
- Actual server409 refreshes context without automatic resend. A new explicit retry
  uses current Profile version. Actual server401 clears private content/credential.
  Two actual local owners with controlled credentials and delayed old response pass;
  this is not live Clerk evidence. Logout cancels a held bootstrap rather than
  reopening an anonymous workspace. SDK initialization is bounded and UI unmounted. Missing fresh credentials also mask the workspace without fallback; queued identity changes cannot be lost during bootstrap.
- Actual configured-absent provider: Mindbot frame1–8ms / saved reads3–33ms, no model
  requests from reads. Actual managed-unconfigured mode refuses anonymous fallback.
- Actual Worker/HTTP/browser in isolated F Store, explicit synthetic due clock and
  absent provider: browser closed during tick, reopened from server, one SAME-history
  message matching last_result, provider fallback visible, proposal only/no task
  mutation, repeated tick adds zero messages. Not a continuous/hosted worker claim.
- Malicious-content software fixture: no executable DOM nodes/unsafe links; content
  remains inert text. Source/user/model HTML is never trusted. All JS syntax/diff
  checks passed; no required framework build exists for vanilla ES modules.

Scripts: apps/frontend-product/tests/morning_*.cjs. Actual/controlled boundaries are
stated in each source and adjacent JSON. Successful backend/provider responses were
not fabricated. The response-loss, held-network, controlled credential and synthetic
clock injections are explicitly labeled. Reuse existing Playwright install:
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/minder-c-browser; module path in scripts.
Set MINDER_BROWSER_OUTPUT_DIR to a private F temp directory. Worker fixture uses
F-only /private/tmp/minder-f-worker-control; no product control endpoint was added.
F PDF dependency is ignored ml/artifacts/session-f/product/python-deps; shared Python
unchanged. Hosted Clerk requires the A/E Python3.12 dependencies and provisioned keys.

## Screenshots (local, not bulk-committed)

- /private/tmp/minder-f-morning-conversations/minder-real-answer.png
- /private/tmp/minder-f-morning-conversations/mindbot-real-answer.png
- /private/tmp/minder-f-morning-profile/profile-overview.png
- /private/tmp/minder-f-morning-profile/profile-mobile.png
- /private/tmp/minder-f-morning-profile/profile-cv-record.png
- /private/tmp/minder-f-morning-explore/careers-outlook.png
- /private/tmp/minder-f-morning-generation/generated-roadmap.png
- /private/tmp/minder-f-morning-generation/mindbot-followup.png
- /private/tmp/minder-f-morning-scheduled/scheduled-same-history.png
- /private/tmp/minder-f-morning-structured/typed-task-review-mobile.png

## Open acceptance boundaries — do not mark release complete

Live managed Clerk application/two accounts, hosted volume/restart and deployment
remain unprovisioned/unverified with A/E. F wired actual routes/maintained SDK, fresh
Bearer, logout and identity invalidation; it does not claim live login/expiry proof.
No validated future forecast is returned by current source contract; Outlook shows
actual scoped observations and truthful unavailable forecast status.

Actual cold global matching on a saved sparse Profile (onboarding studying/fit,
context fictional computing student, no anchored evidence) exceeded12s:12600ms
request_timeout. A received exact repro/evidence. Matching uses approved explicit
Find my matches, catalogue stays usable, errors/retry are visible, and refresh never
starts unrequested ranking. F did not change scoring or invent ranked results.
This backend finding remains open until A supplies a tested correction.

Unrelated ml/minder_ml_starter/raw and derived remain untracked/excluded, untouched
and not backed up by F. Existing .env/private runtime config, DBs/uploads, caches,
PDF dependency tree and bulky screenshots stay excluded; synthetic local test state
is not a backup of real user data. No new ignore rules hide legitimate source.
