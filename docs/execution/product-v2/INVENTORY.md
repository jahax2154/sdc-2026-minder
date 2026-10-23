# P0.1 — actual implementation binding

Inspected integration base07f60a8e0b3097685f99d0bc68d05edd29021391, a descendant
of the verified A/B/C handoffs. Closure is reused, not rerun. Git porcelain lists
only original checkout plus A/B/C; no product launch/ownership records or D/E/F
worktrees/branches were present locally/remotely at inspection.

Actual runtime is Python3.9 stdlib WSGI/SQLite with jsonschema, not FastAPI.
C's Application/api.py owns the existing transport, auth/error boundary. Profile,
plan, history and task state live in the same Store; ActionExecutor and Worker
share them. Migrations1(Store),2(actions),3(agents),4(provider_calls) are idempotent,
with4 currently lazy; plan_creations is another existing lazy table. No DB/framework
replacement is warranted. No package.json/lockfile or React/Vite source exists in
this checkout. The preview README's reference to React is not implementation proof.

Actual frontend roots:
- apps/frontend-web: working acceptance/prototype HTML/ES-module UI, not intended UI.
- docs/minder-ui-html-previews: approved standalone Minder/Mindbot design source
  imported from the original checkout, with41approved source/asset/reference files(about2.93MB).
- apps/frontend-product: reserved for F's single intended frontend. ES modules,
  existing tooling and same-origin API are the reversible three-hour default.
  No framework migration/build tool install is required by bootstrap.

Approved source hashes/attribution are retained. Only two blank HTML lines were
whitespace-normalized for Git checks. Eleven supplied fictional screenshots are
included as approved visual references; newly generated A browser evidence remains
ignored and is not imported as design source. Both HTMLs were opened offline in existing
Chromium at desktop/390px phone widths: zero script errors and no horizontal
overflow. Actual desktop/mobile reference screenshots were visually reviewed.
Mock names/replies/schedules/role scores are fictional placeholders; local storage
is demo-only, never a production state adapter. No external URL/fetch dependency
was found. Assets/pack are ready; DESIGN_CONTEXT.md is supplementary, not a gate.

## Existing capability/gap map

| Capability | Actual reusable code/API | State / remaining owner work |
| --- | --- | --- |
| Session/auth | POST /api/session; Store.authenticate; bearer owner | Implemented local capability identity; hosted auth not established |
| Partial profile | GET/PUT /api/profile; profiles.save_profile | Implemented nine-field Profile, history/version conflicts; D adds context/lifecycle only where missing |
| Skills/preferences | Profile.evidence/preferences; reference/requirements APIs, direct-action | Anchored/self-report/reset semantics implemented; no new scorer |
| CV/chat intake | POST /api/intake, profiles.intake_draft | UTF8TXT<=64KiB; stored draft, no correction/status API or PDF/OCR |
| Recommendation | GET/POST /api/career-context, role_fit/market_evidence | Implemented provisional/partial, source-qualified groups; E presents only |
| Role browse/detail | POST /api/roles,/role-requirements,/role-evidence | Implemented, canonical IDs and trace version guard |
| Direction | PlanProgress.selected_role_id | No explicit persistent active direction/plan selector; D |
| Plan/roadmap | GET/POST /api/plans,/pathway-preview,/plan-designs; plans.py | Existing plan/history/gaps; D manual lifecycle, E read projection |
| Task writes | Existing plans, direct-action/undo | Completion/reschedule/undo supported; full manual create/edit endpoints/titles absent; D |
| Progress | Stored activity_completion; prototype counts | No canonical selected-plan progress endpoint; D definition/service, E projection |
| Sources/market | role-evidence/native context APIs, B registry | Four real typed families; source scope retained, forecasts unavailable |
| Learning | resources.learning_options; GET/POST /api/learning-resources | Existing reviewed options; E bounded feed metadata, not new crawler |
| News | B news.py/credible event registry | Existing source machinery, no product feed/read adapter; E |
| Saved/dismissed content | None in product API | D per-user interaction state; E content/read views |
| Add resource to plan | Existing explicit resource choice/plan data | D adapter, no automatic completion/mastery |
| Minder | POST /api/chat; canonical ledger/typed grounder | Implemented, actual exported contract. No server transcript/history/streaming |
| Mindbots | agents/settings/proposals/decisions/action-history | Implemented scoped proposals/actions; no generic pause/delete or24/7 proof |
| Product shell/Profile/Explore pages | Not present | F, with optional G only after foundation/file transfer |

Authoritative API export is docs/execution/product/llm/FRONTEND_CONTRACT.md and its
schema-valid fictional examples, checked at C37d48be and accepted by A. Do not
re-export an imagined framework. API responses use current200/401/404/409/413/415/
422/500 error semantics, expected versions and immutable preview hashes.

A actual provider config is owner-only and selected model qwen/qwen3.8-27b.
AC2-R01/AC4.1 report13 real application/clock checks and real HTTP/browser evidence.
Only presence/model ID were re-inspected, no new closure or provider calls needed.
Provider secrets, DBs/WAL, weights, logs/screenshots and13readonly source inputs
stay excluded. New lanes need isolated namespace adapters; existing A/C launchers
hard-code their own artifact roots/ports and cannot simply be reused with D/E vars.

Numerical files/mappings remain unchanged: personal-role-fit-v3-provisional,
market personal-current-evidence-v2.1; original N01 historically unapproved/inactive.
One anchored example:910assessed,5activity comparisons(3category proxies/2employer),
7related shortage contexts/0exact whole-role designation,907sector context,
900personal-only. These overlap; neither coverage nor204ML/47backend tests imply
independent career/forecast accuracy. B simulations/zero RunPod jobs are separate.

No broad B0 research is relaunched. Existing acquired-real-series eligibility is
B HANDOFF.v3/B2.2-R01/HISTORICAL_SOURCE_AUDIT: zero approved-target examples. A bounded
optional B reconciliation may identify whether that exactly satisfies revised B0;
that uncertainty does not gate product lanes or justify another broad search.
