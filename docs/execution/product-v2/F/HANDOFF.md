# F3.1 — final frontend assembly and handoff

Owner F, branch session/f-product-frontend. Supported local product journey is
implemented and verified; upstream unavailable capabilities remain explicit.
Final tested code: c25173176489b42019b75abb8b0f00dc50943911. This culminating
report adds no product code; the commit containing it is the final F handoff.

| Phase | Status | Actual delivered / verified | Checkpoint |
| --- | --- | --- | --- |
| F0.1 | passed | Actual HTML/CSS/JS/assets/contracts inspected; no DESIGN_CONTEXT wait | bef10ca |
| F0.2 | passed | Approved shell, routes, source tokens, session/client, errors, sources/diffs; early A handoff | e9c3ff25257cda9f68a2f95c53b7407f3441a9d1 |
| F2.1 | passed for exported contract | Real Qwen, validated statements/sources, temporary history, safe explicit retries | 83701a58e255219517a48105f11767dba0d52443; refined c251731 |
| F2.2 | passed for exported contract | Exact approval/rejection/stale/duplicate controls, settings/activity/audit, no false always-on state | 470593946f63709ef256643c1a1477291a677c46 |
| F1.1 | passed for supported operations | Partial profile, evidence/zero-vs-unknown, reviewed TXT, source-backed career exploration/preferences/direction | 1354356908a4557b9b4cd0a4d6e25fce473a3d3e |
| F1.2 | passed for supported operations | Real shared plans/tasks/canonical progress, undo/refetch, source-resource persistence, explicit missing news/forecast | dc45f0e1ee7ee11b9ab74f9534cb9e2885aee5b3 |
| F1.1-R01/R02 | passed locally; hosted storage limited | PDF/TXT list/upload/attachment/delete, explicit TXT review/apply; default-disabled storage honest | 6f3fa4035cc0724a1e49e9351a59a95560fcfdae; c251731 |
| F0.2-R01/F2.1-R01/F1.2-R01 | passed | Transport/retry/validation/feedback refinements and configurable acceptance scripts | c25173176489b42019b75abb8b0f00dc50943911 |
| F3.1 | passed for local frontend acceptance | Desktop/phone/keyboard/assets/console/session and actual integrated journeys; no deployment | this report; F3.1-evidence.json |

IDs preserved despite executing F2 before F1. G remained inactive: F handled the
separate page modules and retained shell/router/client/global styles/final assembly.
A received the first working F0.2 checkpoint early and integrated F2/F1 incrementally.

## Inputs and exact integration boundaries

- Bootstrap fbddeb80763442a8f1a4c8f8c2c80e4d6c4697a7, C exported
  docs/execution/product/llm/FRONTEND_CONTRACT.md and frontend-envelope.schema.json,
  canonical contracts/parallel-services.v1.schema.json and product-v2 schema.
- D final 9f1f2eeabb8d5d8247fcc1b0353a8777d690d71e (includes A3561e93 document
  routing and D989480f owner repair); E c2628eceaf4700cd124a407ec4dfe43a6cdbd4ff.
  Integrated committed history; no active producer files copied or edited by F.
- Visual authority docs/minder-ui-html-previews/{minder-chat.html,mindbot.html,
  assets/minder.css,assets/minder.js,assets/*,screenshots/*}. Both embedded CSS
  blocks exactly equal the imported shared CSS; hero PNG bytes also match.
  Supplementary product.css handles real capability/error/forms. No redesign,
  alternate framework, root package/lockfile change or provider-client duplication.

## Actual final checks

82 backend unittests passed after final D/E source integration. Browser scripts use
real F8106/9106, same-origin JSON/private bearer and fictional owners:

- chat_actions.cjs: real qwen/qwen3.8-27b,10 public validated statements/5 source
  entries, native arguments validated; employer/offerings/shortage/sector families;
  no profile mutation; temporary history; exact reject/approve/repeat/stale/settings.
- workspace.cjs: profile/intake/evidence/career/preferences/direction/plan/tasks/
  canonical progress/undo/resources/source detail/refresh/conflicts/settings; all9
  phone routes no overflow; session isolation; zero page errors. Final rerun after
  document UI/client refinements passed. No provider call or fetch mock.
- documents.cjs: enabled development-local synthetic TXT/PDF lifecycle, exact
  attachment bytes, explicit reviewed apply/no mastery, delete retaining applied
  profile, limit/refresh/mobile; separately actual default-disabled upload state.
- smoke.cjs:20 desktop/phone route-width combinations, keyboard entry/navigation,
  zero unexpected console errors and zero failed static assets.
- error_states.cjs: explicitly intercepted error/validation/security fixtures only,
  zero provider calls; pending duplicate prevention/malformed answer/escaping/unsafe
  links pass. Fixtures are separate from real-provider and real-source evidence.
- Node syntax checks for every owned source/test script; Git diff --check passed.

Sanitized machine evidence is F3.1-evidence.json; phase records retain prior runs
and the resolved stale bootstrap-test expectation. Private synthetic screenshots,
download and raw check JSON stay outside Git. No empirical fit/forecast validation
or independent human-label approval is inferred from engineering checks.

## Start and consumer action

Single entry apps/frontend-product/index.html, ES modules app.js/client.js/ui.js,
pages/{minder,mindbots,profile,career,explore,documents}.js and source CSS/assets.
No build step. In F's existing worktree:

```sh
source .env.local
"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane F
```

UI http://127.0.0.1:9106; API same origin /api and private8106. F runtime is left
running with default document storage disabled, no scheduler auto-start. For local
fictional document work only, stop that owned process normally and prefix the same
command with MINDER_DOCUMENT_STORAGE=local-development. Files stay under F uploads.
No server config/token/DB/key should be copied to another lane or frontend.

A: integrate the final full F handoff SHA preserving D/E ancestry. Use --lane A
and A's own8111/9111, not F's DB. Browser scripts accept MINDER_PRODUCT_BASE_URL
(e.g. http://127.0.0.1:9111), MINDER_BROWSER_OUTPUT_DIR (own ignored output folder),
MINDER_PLAYWRIGHT_MODULE and PLAYWRIGHT_BROWSERS_PATH. chat_actions makes one real
provider call unless MINDER_SKIP_CHAT=1. Preserve the verified Qwen server profile.
No requested local implementation remains pending in F.

## True limits and excluded state

No server transcript/history CRUD or streaming; temporary conversation is labeled.
No verified continuous scheduler, custom bot persona/calls/Slack/computer integration.
No PDF/DOCX/OCR extraction, automatic competence inference or hosted durable storage.
News/video feed coverage remains unavailable; two sourced learning records are real.
Future forecasts retain backend unavailable results. Tasks are activity, not readiness.
Profile deletion/account erasure, secure physical WAL/backup erasure and hosting are
not claimed or invented. These are upstream capabilities, not silent UI fallback.

Only explicit owned paths were staged. Initial untracked ml/minder_ml_starter/raw/
and derived/ remain untouched/excluded and are NOT backed up by F. .env.local,
private provider config, lane DB/runtime artifacts/uploads, browser binaries/caches,
synthetic screenshots/download/check JSON stay excluded and are not newly backed
up. Safe owned frontend/report source was privately copied under
/private/tmp/minder-f-pre-f1-checkpoint; final owned snapshot under
/private/tmp/minder-f-final-source. Neither is a backup of private runtime/data.

Only normal pushes to verified origin https://github.com/jahax2154/sdc-2026-minder.git
branch session/f-product-frontend are authorized/performed. No main/force/tag/PR,
paid training, scheduler activation, public tunnel, app publishing or deployment.
