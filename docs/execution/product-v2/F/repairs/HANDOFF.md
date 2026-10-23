# F targeted Minder/Mindbot repair — final handoff

Requested repair complete for supported local behavior. Final tested code:
aeb3e08b6088cf06e6dc917d47a3e2097b5f1dd8 on session/f-product-frontend.
The commit containing this report adds documentation only. Current UI:
http://127.0.0.1:9106/#minder and http://127.0.0.1:9106/#mindbots;
API same-origin /api (also private8106). Normal verified qwen/qwen3.8-27b runtime
restored and running, F worktree only; no scheduler or deployment.

## Root causes and repaired behavior

CHAT-01: exact browser reproduction on F29281ec returned200/provider available and
native arguments validated, but only proposal disclaimer +3limitations/0sources.
A traced the closed statement vocabulary: it contained no verified app capabilities
or onboarding answer, and always appended generic limitations. F also refused unsaved
profiles locally and placed 'Language-assisted answer' ahead of actual content.
A now routes verified app guidance separately, preserves sourced evidence checks and
reports provider-required/skipped/fallback modes. F accepts unsaved null version,
never implicitly saves a profile, renders actual answer first, keeps relevant sources
and supports owner-scoped follow-up IDs only in active memory. No canned UI answer.
Natural plural role wording failed an initial real test; A12e7496 repaired its router,
then the identical phrase passed pinned source/US scope checks in final acceptance.

BOT-01: baseline navigation during chat showed GET profile blocked16519ms while
subsequent saved reads took4-10ms. Ordinary navigation took99/111ms. A confirmed serial
WSGI head-of-line blocking, repaired with bounded concurrent workers. F additionally
awaited profile and all4 reads before drawing the page, with no request deadlines.
F now draws the approved frame immediately, reads sections independently, keeps
successful saved state when optional reads fail, and offers manual bounded recovery.
Opening workspace performs no model/job/write. Authorization failures mask all saved
content; obsolete route results cannot overwrite a later page. Exact action versions,
preview hashes and idempotency remain authoritative.

PANEL/STATUS/NAV: Context has explicit Close, aria-expanded toggle, Escape/focus return,
mobile dialog/inert/focus handling and desktop nonmodal behavior. Closing retains
messages/draft/scroll and releases width, without provider calls or automatic reopening.
Working… terminates on success/error/cancel/deadline. Stop waiting warns server work
may finish, with no claim of undo. Retry is explicit review/resend. Compact72px icon
rail keeps all routes/account/new chat and actual proposal badge; hover/focus labels
never expand it, phone/coarse-touch uses labeled menu. Overview/Explore/Profile bodies
are byte-unchanged from F29281ec; no user-led content redesign was performed.

## Checkpoints and exact dependencies

| Phase | Status | SHA |
| --- | --- | --- |
| Baseline F-R3 | reproduced with real Qwen, sanitized exact payload/waterfall | 0a876d2748ed33c05dbabe9f0a11c7d20b52e739 |
| F-R1 | targeted Context/lifecycle fixtures passed | 8943ba2bdc6e85d51db2fe30182902140428025d |
| F-R2 | real rail/routes/mouse/focus/phone/touch checks passed | 7866e50749f094cb41e6f7fbe8a4d234d758d152 |
| F-R3 client | independent sections/deadlines/auth/route-fault checks passed | 4dc5b4ed3f0170e29b862ad014bcaca69c082215 |
| A-R1 contract | reviewed additive modes/answer/follow-up/ownership | 6a77d22eeff3aa81b963fdb4506b9ec5cf321479 |
| A-R2 | verified guidance + preserved empirical grounder | fddeb24fae8dd6b125705fc45e6d7178935ecda9 |
| A-R3 | bounded concurrent request workers | 19b19e0fc026c96c752b61b0f48e5e46b82aadad |
| A-R2-R01 | grounded preparation/comparison intent | 704f71658d84a1633c6c346baea1d2336d1b0b32 |
| A-R2-R02 | plural/catalogue role reference fix | 12e7496db73f4f3a1a19c0c3a7b16decaa22d226 |
| F-R3-R01/F-R1-R01 | final real integrated/provider-absent/source/retry acceptance passed | aeb3e08b6088cf06e6dc917d47a3e2097b5f1dd8 |

A changes consumed only by complete commits/merges; F authored no backend/provider/
grounder/policy/migration/scorer changes. Preserve ancestry on integration, no duplicate
cherry-pick history. tested-source-sha256.json fingerprints the actual rendered files.

## Measurements and real versus simulated evidence

Local Mac/F8106/9106, fictional owners/inputs only. These small navigation samples
are not process-cold tests or a production latency guarantee. Request intents/provider
work differ between baseline and repaired scenarios; no generalized speedup ratio.

| Scenario | n / conditions | Observed |
| --- | --- | --- |
| Baseline exact capability question, saved empty evidence | 2, real Qwen included |15969/16561ms, boilerplate |
| Baseline ordinary Mindbot navigation | 2, initial/repeated navigation |99/111ms |
| Baseline Mindbot during capability chat | 1, real pending chat |16595ms usable; profile GET16519ms |
| Repaired exact capability question, unsaved | 1 final, application guidance/provider skipped |32ms, useful answer + question |
| Repaired paraphrase/onboarding/follow-up/partial capabilities | 4 final, provider skipped |12/10/10/14ms |
| Repaired plural role quote | 1 final, verified source/provider skipped |19ms; US scope retained |
| Repaired personal evidence question | 1 final, Qwen available |1278ms |
| Repaired saved Mindbot during real forecast chat | 1 final, Qwen available/pending |100ms saved ready before chat finished; chat802ms/provider635ms |
| Earlier compatible repaired pending chat | 1, Qwen available |127ms saved ready; chat788ms/provider619ms |
| Provider configured absent, actual HTTP/disposable F DB | 3 initial/repeated navigation |frame1ms; saved31/74/23ms; zero new chat calls |
| Client transport fault fixtures | explicit intercepts, no provider |frame69ms with optional rejection; saved49ms during held chat; not real provider performance |

integrated-real.json retains exact synthetic requests/answers, response modes, request
correlation IDs, provider invocation/status and backend stage timings. guidance-real.json
is earlier real A-R2 guidance acceptance. provider-off-real.json is actual application/
HTTP with explicitly absent provider key, not an alleged live Groq incident or browser
mock. Guidance/reference modes truthfully skip unnecessary provider; real empirical
calls returned provider available/native verified evidence. Configured-unavailable
calls returned limited_fallback/provider_credentials_missing,0 provider invocations,
10 verified statements, manual recovery. Real forecasts remain unavailable.

## Checks and commands

- 90 combined backend unittests passed7.284s at integrated A-R2/A-R3. First3 concurrency
  socket errors were sandbox permissions; permitted rerun passed, no code bypass.
- After A's final routing refinements,8 focused conversation/concurrency tests passed
  3.122s. These include controlled HTTP concurrency/duplicate write checks, not Groq.
- Real final repair_integrated.cjs passed unsaved/partial/paraphrase/follow-up, foreign
  follow-up404, role source/US scope, focused clarification, real pending Qwen saved
  reads, forecast-unavailable, direct request, approve/reject/repeat/stale protections.
- repair_ui.cjs/repair_workspace.cjs explicitly inject transport failure/held request/
  compressed deadlines: Context/width/draft/scroll/focus, Working success/failure/
  cancellation/timeout, duplicate prevention, independent sections, auth masking,
  startup retry. No provider calls in these fixture checks. Deadline tests compress
  final45s chat to80ms and8s read to100ms only in test browser.
- repair_navigation.cjs uses real shell/API and verifies72px rail, hover/focus labels,
  route/active state, phone and coarse-touch labeled menu. No provider calls.
- smoke.cjs final20 desktop/phone route-width combinations, keyboard navigation,
  zero unexpected console errors/failed assets. All owned JS/CJS syntax checks and
  Git diff checks passed. Real repaired-state screenshot capture also passed.

```sh
source .env.local
"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane F
# Existing Playwright tooling, no root dependency installation:
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/minder-c-browser node apps/frontend-product/tests/repair_integrated.cjs
# Configurable MINDER_PRODUCT_BASE_URL (A uses9111); MINDER_PLAYWRIGHT_MODULE if needed.
# To verify explicitly absent provider: stop only F's owned server, then
"$MINDER_PYTHON" apps/frontend-product/tests/serve_provider_unavailable.py
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/minder-c-browser node apps/frontend-product/tests/repair_provider_off.cjs
# Stop normally and restore standard --lane F runtime afterward.
```

Client bounds read8s/write12s/chat45s include JSON body reads and have no automatic
write/chat retry. Browser cancellation stops waiting, not proof of server rollback.

## Screenshots and A consumer action

All screenshot files are fictional/sanitized local artifacts; exact hashes and byte
sizes are screenshots.json. Key paths:

- /private/tmp/minder-f-repair-before-chat.png — actual original boilerplate.
- /private/tmp/minder-f-repair-after-onboarding.png and after-onboarding-context.png.
- /private/tmp/minder-f-repair-rail-desktop.png and menu-mobile.png.
- /private/tmp/minder-f-repair-final-context-mobile.png and final-mobile.png.
- /private/tmp/minder-f-repair-final-role-source.png and final-working.png.
- /private/tmp/minder-f-repair-after-mindbot.png — normal real saved reads.
- /private/tmp/minder-f-repair-provider-off-fallback.png and provider-off-mindbot.png.

A: integrate final F handoff SHA, whose product code is aeb3e08, preserving all A
backend ancestry above. Use A's own runtime/database/ports8111/9111. Exact F URL is
http://127.0.0.1:9106/#minder. Do not copy F private config/session/database. No pending
requested local F repair remains; A's own combined snapshot publication is separate.

## Limits / excluded state

Conversations remain temporary across refresh. Saved tasks are activity, not assessed
mastery. Real forecast/news/video coverage and hosted durability remain unavailable
where documented; document storage defaults disabled, PDF extraction unavailable.
No deployment, scheduler activation, model/scoring change or production-readiness
claim. The prior separate F-DOC-REVIEW-R01 uncertain document-editor retry request
remains outside this targeted chat/Mindbot repair; no new library work was done.

Unrelated initial raw/derived directories remain untouched/untracked/excluded and
not newly backed up. Private config, real profile/CV inputs, DB/runtime/uploads,
browser caches and screenshot artifacts remain excluded from Git; no new runtime
backup is claimed. Only safe owned source/reports privately copied under
/private/tmp/minder-f-repair-final-source; screenshots remain local with hashes.
Only tested normal pushes to session/f-product-frontend; no main/force/deployment.
