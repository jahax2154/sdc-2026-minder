# Final frontend repair handoff — F-UX0–F-UX6

Code complete and pushed only to `session/f-product-frontend`. Final tested frontend code: **f3ea83ba490f57d96de91418a35e13319a5b55e7**; remote verified equal. Preserves3c7d105d34e32c291bc7440764390f55a8fb515f and8446ca801de8d8a0163c390f76d2aa609a5fec16 by normal descendant commits/merges. No deployment.

## Exact phase checkpoints

| Phase | Published full SHA | Outcome |
|---|---|---|
| F-UX0 | d8756b12dd1134973aab672c5688abdf138573c6 | Actual source/runtime inventory, clipping reproduced, immediate A/D contract requests |
| F-UX1 | a253ee118363ae90cbc859a8783e586c7cfb0fd1 | Bounded page scroll, stable72px rail/flyout, global New Minder, +2px body/composer |
| F-UX2 | 12a159cad34d8b2a46998194a6d62225d26686f7 | Stable main/header/tabs; sibling panel updates and identity-cleared filter cache |
| F-UX3 | c7ff863bcfae8f5c8f45a4e4ea4bf1c24ec87550 | Owned searchable/paginated collapsible Minder sidebar |
| F-UX4 | 140d8affc755c26909a7792f345e16135479cad5 | Persisted name/allowlisted avatar; preview/cancel/version conflict recovery |
| F-UX5 | efeb6d7624175dfa8ce699094f88fe5ad0f77622 | Approved Home body wired to real independent reads/canonical progress |
| F-UX6 refinement | ad914a4b80f8c9a88e9594219db2f2d470bcf862 | Fresh saved profile versions, exact uncertain-turn receipt recovery |
| F-UX6 final | f3ea83ba490f57d96de91418a35e13319a5b55e7 | Retained refresh content/focus/caret, older history pages/reading position, real browser acceptance |

## Integration dependencies and runtime

A assets/public schema:29a6b9303a13b617a0698ea9c3a2c6fd4ebf796f. D implementation:d734d95cf68cb4945562bd9166714798edc2fb23. Normal integration merges preserve all ancestry; merge the F branch, do not cherry-pick only the frontend files. New contracts are exactly GET/PUT `/api/product/bot-preferences` and POST `/api/product/conversations-search`; D existing storage/schema7, no new migration/config/dependency. Default My Bot/nimo-blue,25approved IDs; no custom image upload/persona/provider changes. A existing registrations and E canonical GET `/api/product/views/overview` plus existing plan-designs supply Home. No extra Home aggregate or model-on-render.

Actual UI **http://127.0.0.1:9106/#home**; same-origin API on9106, assigned backend listener8106. Normal F process restored after provider-absent disposable fixture, session31516 at code SHA f3ea83ba490f57d96de91418a35e13319a5b55e7; health verified. Existing verified `qwen/qwen3.8-27b`; local loopback only; no F worker/autostart/deployment. A should restart its own assigned runtime after merging, never use F database or start a duplicate worker.

## Defect matrix

| Defect/cause | Main changed files under apps/frontend-product | Verified result |
|---|---|---|
| Profile/Explore root class dropped flex/overflow inside locked document | product.css | All required layouts, real wheel + keyboard, complete Profile creation at actual200% zoom |
| Explore inserted rail rows; global plus hidden outside chat | app.js,index.html,product.css | Fixed72px border-box/row coordinates; anchored flyout; hover/focus labels; plus in all modules |
| Every route/tab replaced main/loading shell | app.js,pages/careers.js,pages/my-path.js,panel-refresh.js | Stable object identity, slow/rapid tab trace, content/focus/caret/filter retained, local failure retry |
| Horizontal toolbar and unsearchable history | conversation-sidebar.js,conversations.js,pages/minder.js |25real histories,20+5pages retained on older open, title+actual provider-message search, confirmed delete, mobile backdrop/Escape/focus |
| Hardcoded Nimo/disabled Customize | bot-identity.js,bot-avatars.js,bot-customization.js,pages/mindbots.js | Real save/cancel/refresh/two-owner isolation,409/uncertain save reconcile, identity across sidebar/page/panel/Home; singleton unchanged |
| Overview lacked approved Home composition | pages/home.js,assets/approved-home.css,tools/import_approved_styles.py | Before/profile-only/chosen-no-plan/active/bot-only, responsive Tasks/Skills/Progress, canonical next task/progress; zero model calls |
| Retry/status and reading-position edges | pages/minder.js,pages/mindbot-chat.js,pages/mindbots.js | Working terminal cleanup, exact receipts/no replay, Context close, long transcript position and actual panel opener focus |

## Acceptance and evidence

[Sanitized machine-readable evidence](F_UX6_EVIDENCE.json) includes exact sanitized requests, response modes, provider timings, actual browser zoom, partial-update trace assertions, recovery/provider-absent reports and screenshot/trace paths+hashes. [Implementation log](FINAL_UX_GATE.md). [Runnable acceptance instructions](../../../../apps/frontend-product/tests/FINAL_UX_ACCEPTANCE.md).

Three real new Qwen calls only: original Minder969ms, unseen follow-up1710ms, same-channel Mindbot task completion1300ms; all available/generated_guidance. Two additional HTTP exact receipts reused saved outcomes with unchanged canonical version and one action-history row. Mindbot independent frame6ms/ready29ms. Subsequent CSS/focus refinements used no additional paid calls. Existing Profile/CV/PDF review, typed proposals/task editing, auth expiry/two local owners and escaped model/source content regressions passed. Provider-absent actual app returns truthful unavailable response, clears Working and loads Mindbot without model calls.

Review these actual local screenshots: `/private/tmp/minder-f-ux/final/ux6-restored-home-desktop.png`, `ux5-home-390.png`, `ux4-customize-mobile.png`, `ux1-minder.png`, `ux6-real-200pct-profile.png`; provider flow screenshots under `/private/tmp/minder-f-ux/regression/ux6-minder-real-followup.png` and `ux6-mindbot-real-action.png`. Trace `/private/tmp/minder-f-ux/final/ux2-partial-trace.zip` proves retained DOM/partial updates rather than screenshots alone.

## Remaining release gaps and excluded state

No remaining requested F local UI capability is disabled or deferred. Actual hosted/managed Clerk two-account acceptance and Railway provisioning remain A/E release gaps; B GPU work remains separately owned. Controlled local credential expiry/two-owner tests do not claim live Clerk acceptance. No release/deployment approval inferred.

Untracked ML raw/derived inputs untouched and not backed up; local environment/credentials, F SQLite/uploads, browser profiles, synthetic PDF fixtures, screenshots/traces excluded. Temporary screenshot/trace binaries are available locally to A with hashes, not remotely backed up. No ignore rules added; only explicit reviewed F paths staged.
