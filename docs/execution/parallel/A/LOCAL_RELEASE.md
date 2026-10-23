# Session A — current provisional recommendation prototype

Current handover: N3.1. This replaces the operational description of the earlier
I2.4 local release; historical phase reports and checkpoints remain unchanged.
The recommendation mechanism is implemented and locally verified. Data coverage
is explicitly partial; no general claim of full market/provider/forecast completion.
No push, deployment, production-data change or application build occurred.

## Run in A

Use the assigned directory and branch. Reuse the existing interpreter, pinned
read-only source inputs and available browser tooling; no setup recovery needed.

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli serve-web
```

API 8101, UI 9101, loopback only. Database stays under A's reserved
`ml/artifacts/session-a/runtime/dev.sqlite3`; C migrations/actions/persistence are
reused. No B/C runtime database is opened. No dependency install or build required.
The existing 13 untracked inputs must be restored by their G0 snapshot hashes on
a new machine; a Git clone alone does not contain those bytes.

Save a User Profile, then supply three anchored essential-skill observations and
activity/evidence descriptions. Source examples are available directly in the
form; an explicit zero differs from unanswered. Prior employment, a chosen role,
role-by-role ratings and a preparation plan are unnecessary. Industry background,
industry/role interests and work-style preferences are separate optional inputs.
Unstructured CV/chat claims remain reviewable input, never automatically scored
competence. Clear/reset removes only the specified effect. Profile history remains.

Career Match assesses every supported eligible role. Its groups have independent
ranks: current comparable Malaysian evidence, and personal-only exploration where
market comparison is unsupported. Eight cards per group are shown initially;
other roles remain searchable. Selected-role context displays separate personal
components and industry paths. Current observations have source dates/links;
next-quarter forecasts remain separately unavailable. Personal-only fallback is
never full recommendation completion. Preparation time/resources stay in pathways.

## Policy and evidence

The user delegated bounded provisional choices in N01-R1. New policy
`personal-role-fit-v3-provisional`, source projection `role-reference-v3.2`,
market combination `personal-current-cohort-v1`. Original N01 v2 remains
historically unapproved, pending and inactive. Legacy preparation F0 and its 67
reference result, labels and learner artifacts are preserved.

Minimum: three usable explicit native assessments and 30% of role criteria.
C is the equal mean of `min(person LV / occupational LV, 1)` over assessed usable
positive-LV criteria. Unknown criteria are disclosed, not invented as competence.
F is `clip(80*C + industry_path_points + role_points + style_points,0,100)`.
Optional background contributes up to 5, industry interest -5..5, role interest
-5..5, style -5..5. The strongest supported industry path contributes once;
other industries remain considered. Missing optional answers have no adjustment
and retain null raw values. These are partial essential-skill evidence-fit indices,
not independently validated qualification, hiring or career-success probabilities.

Within one compatible current MY cohort of at least two assessed roles,
`M=100*log1p(role ads)/log1p(inspected ads)` and `S=.85*F+.15*M`.
This new blend is explicit and independent of forecasts; it does not inherit
legacy 70/30. No global rank crosses incompatible/unsupported market groups.
Backend calculates; the LLM explains allowlisted backend facts.

Full choices, effects and source limits: [policy](RECOMMENDATION_POLICY_V3.md).
Reproducible evidence: [application](N1.3.json), [learners](N2.1.json),
[final coverage/status](N3.1.json). Current shared interface and numerical indexes
point to v3 while preserving original G0 text and fixtures.

## Measured coverage and actual verification

| Case | Personally assessed | Current-comparable ranked | Personal-only ranked |
| --- | ---: | ---: | ---: |
| New anchored fresh graduate | 910 | 4 | 906 |
| New anchored career switcher | 910 | 4 | 906 |
| Incomplete, one anchored skill | 0 | 0 | 0 |
| Each of five unchanged original synthetic profiles | 0 | 0 | 0 |

Catalogue: 1,016 references, 910 supported, 106 partial/explorable. Among supported
roles, 907 have sourced industry relationships and 878 have sourced positive-style
links; absent mappings remain unknown. Twelve source industry aggregates lack
native codes and were deliberately not joined. US reference context is separate
from Malaysian observations.

Actual B current evidence: all 155 inspected Bosch Malaysia native requisitions,
154 observed qualification sections, four mapped role identities. Counts are
software developers 5, other three mapped roles 0 **within this inspected feed**;
SQL 11, Excel 27, C++ 8, Python 6, Java 4. Not national demand, current hiring,
positions or quarterly inflow; old release dates remain visible. New B historical
research preserves broad/censored/frozen-corpus measurements as their actual
quantities. It supplies no compatible selected forecast model or personal labels.

Checks: full ML suite 165 passed at N1.3; backend 28 passed; real HTTP and Chromium
application/recommendation cases passed with no fetch mocks or page errors and no
mobile overflow. Latest handoff/source refinement checks: 49 passed. Negative role
feedback changed personal fit 65.8824 → 60.8824; repeated feedback was idempotent;
reset restored 65.8824 without changing skills or market evidence. Explicit
counterfactual comparable counts reversed ranking with unchanged personal evidence
and unavailable forecasts; factual snapshot was not altered. A whole-catalogue
service timing probe took 6.52s, excluding additional boundary validation; this is
local prototype evidence, not a production latency guarantee.

Ridge and CPU XGBoost actually ran: 48 fictional profile families, 569 retained
examples, 32/8/8 family split, 378/95/96 rows. Exact cross-family feature duplicates
were removed; train-only scaling and validation-only Ridge choice. Holdout teacher
MAE: Ridge .0021, XGBoost 3.6832, baseline about 2.4e-9 rounding difference.
Reload differences 0. These provisional policy-distillation labels are not
independent evaluation; baseline remains active. No paid launch; models stay ignored.

## Reproduce checks

Choose new ignored output directories; existing evidence is not overwritten.

```sh
"$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli verify-recommendations --output ml/artifacts/session-a/<new-http-run>
"$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli verify-web --output ml/artifacts/session-a/<new-browser-run> --playwright-module /private/tmp/minder-c-ui-check/node_modules/playwright --browsers-path /private/tmp/minder-c-browser
"$MINDER_PYTHON" -m minder_ml.intelligence.role_fit_experiments --output ml/artifacts/session-a/<new-control-run>
"$MINDER_PYTHON" docs/execution/parallel/A/checks/coverage_audit.py --output ml/artifacts/session-a/<new-coverage-run>
```

Temporary browser paths were available during verification; use available
equivalents on another machine. Browser verification starts/stops its own A
servers and runs C's committed HTTP/UI checks plus A's numerical UI cases. Only
ports, output paths, stale policy-report wording and worker namespace are adapted.
A's guarded `integration_cli worker-once --owner <synthetic-owner>` reuses C's
worker code without weakening C's DB guard. Manual one-shot checks are not proof
of a deployed unattended schedule.

## Remaining external and owner work

A's Groq key/model presence are both false. Secure loading and native-function
software tests are integrated, but no real-provider success is claimed. Configure
A's own owner-controlled private provider settings, verify actual access, then run
real grounding/native-tool and scheduled wall-clock checks. Never copy C secrets
or print values. Local anonymous bearer identity remains a prototype, with no
production auth/session-hardening, HTTPS or deployment claim.

Comparable next-quarter role/skill target history and independent personal-fit
labels remain absent. B's audit explains why broad tables, top-list missingness,
and surviving-corpus dates do not provide the approved forecast target. Continue
source work in B and use committed handoffs; no invented forecast or retraining
against a different quantity. Paid training remains B-only; no paid A job is queued.

C's company explorer explicitly retains its old generic pending-policy call;
company-specific competence remains unknown. The main recommendation uses v3.
A's [committed consumer handoff](requests/N01-R1-CONSUMER-HANDOFF.md) requests a
later C-owned cleanup, preserving company qualification distinctions. No C-owned
company/worker/migration module or sibling directory was rewritten by A.

Excluded local state: original 13 read-only inputs preserved in the G0 shared
snapshot; A's ignored source downloads, logs, synthetic SQLite databases, model
artifacts, screenshots and temporary browser binaries remain local and not newly
externally backed up. No credentials, real CVs/profiles, raw bulk downloads,
weights, database files or unrelated inputs are staged. Later checkpoints remain
local until a separate explicit push instruction.
