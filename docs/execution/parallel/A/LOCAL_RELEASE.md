# Session A — verified local closure and frontend handoff

Current handover: AC4.2. Tested runtime source:
23f3f057132889b2f62e72657a9f4678042bc0e0.
The final documentation checkpoint follows that runtime without changing it.
Branch: session/a-personal-integration on the verified Minder GitHub origin.

A's local scope is implemented and verified: C's four-family bridge and final
contract are integrated; A's authorised Groq binding, source selection, direct
actions/proposals, actual scheduled event and privacy/source browser passed.
Market coverage and empirical model validity remain limited. This does not
declare the intended product frontend or deployed application complete.

## Start and connect

The handoff service is running on this Mac, loopback only:
http://127.0.0.1:9101/ with same-origin /api/.
Separate API listener: http://127.0.0.1:8101/api/.
Health /api/health reports local_source_services. Isolated persistent handoff DB:
ml/artifacts/session-a/closure-runtime/dev.sqlite3. No unattended worker is started.

A uses the existing interpreter and owner-only ignored .env.groq.local. Under the
latest explicit instruction, only the existing authorised C provider variables
were securely bound into A; C ports/database/runtime config were not copied.
A subsequently selected the actually accessible qwen/qwen3.8-27b after real
four-family/native/source verification. The same key, daily-call/context budget,
1024-token cap, native validation and action authority remain in force.
No secret is in Git or the frontend. C's private configuration remains unchanged.

    source .env.local
    export MINDER_DB_PATH="$PWD/ml/artifacts/session-a/closure-runtime/dev.sqlite3"
    export MINDER_ARTIFACT_DIR="$PWD/ml/artifacts/session-a"
    PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli serve-web

For another machine, use [working-base setup](BACKEND_WORKING_BASE.md) and the
actual [C frontend contract](../../product/llm/FRONTEND_CONTRACT.md). F uses relative
same-origin /api routing/proxy and the existing bearer/version/idempotency
bindings. This Mac's loopback address is not a hosted remote-team API.
No streaming or server conversation-history API is promised by the current
contract. Intended HTML/Replit frontend acceptance remains F-owned.

The 13 pinned source inputs are not in a Git clone. The committed standard-library
provision_dev_inputs.py verifies an authorised local pack and all existing
destinations before copying only missing matching files read-only. It never
overwrites, downloads, publishes or stages inputs; no new redistribution rights
are granted. A's own bootstrap was reused, not repeated.

## Active policies and coverage

Personal: personal-role-fit-v3-provisional; references role-reference-v3.2.
Market: personal-current-evidence-v2.1.
Grounding: minder-grounding-privacy-v1 with minder-evidence-passage-v1.
LLM runtime selection: A-typed-selection-v2, qwen/qwen3.8-27b.
The deterministic personal baseline serves; existing Ridge/XGBoost work is
preserved. No scoring configuration, reference mapping or original N01 changed.
Original N01 is historically unapproved/inactive; it was not silently approved.

Three compatible anchored skill observations and 30% assessed role criteria form
the practical minimum. Optional preferences stay optional; other industries are
considered, not excluded by current field/interests. Reset removes only prior
preference effect; repeated feedback is idempotent. Preparation time/resources
remain pathway feasibility. See RECOMMENDATION_POLICY_V3.md.

Current activity ordering remains .85F+.15M within compatible independent groups,
plus the existing bounded at-most +1 related shortage-group context. Sector
context has zero rank weight; unavailable forecasts do not gate current evidence.
See MARKET_EVIDENCE_POLICY_V2_1.md for normalization, mapping and missingness.

Same anchored synthetic example, measured again at final closure:

| Coverage | Count |
| --- | ---: |
| Catalogue references / supported / partial-explorable | 1,016 / 910 / 106 |
| Personally assessed eligible roles | 910 |
| Current activity comparisons: category proxies / employer primary | 5: 3 / 2 |
| Native employer observations available | 4 |
| Related shortage-group context / exact whole-role designation | 7 / 0 |
| Related sector context | 907 |
| Personal-only ranks without contextual adjustment | 900 |
| Selected normal forecast models | 0 |

Counts overlap. Two shortage-linked roles already have activity comparisons;
five others receive contextual exploration treatment. Sector counts are not
narrow-role demand, shortage context is not proof this role/every child is critical,
and category offerings are not employer ad counts. Overall ranking remains partial
with no comparable global rank. Independent personal-fit labels remain zero.

B's final d9ffd4f3cc7625c736ea081c52da3c1122b21c08 supplies isolated simulation
code/results/card and source-pinned RunPod preparation. No synthetic observations,
predictions or models enter normal recommendations/coverage/default forecasts.
B measured 36 fictional experiment fits across three local runs; these establish
simulation behavior, not independent Malaysian-demand accuracy. No paid job was
launched. Compatible real forecast history remains absent.

## Executed checks and limits

AC2-R01: all13 real A provider/application/actual-clock checks passed. Actual chat
and the upcoming-minute owner-scoped notice retained all four evidence families
with source/period/unit/mapping reconciliation and unavailable forecasts.

AC4.1: C's exact typed TCP HTTP operations passed on A, including native selection
and source meaning for each family, explicit persisted action/idempotency,
cross-user/stale controls, proactive preview/rejection/approval and worker facts.
The real Chromium privacy/source case passed with no page errors. Typed prototype
cards show edition labels for null date windows and omit absent population text.

Software: 204 ML and47 backend checks passed; seven targeted mocked transport
checks verified the existing cap/smaller budgets after C's refinement; three
namespace guards, four A source/API and two provisioning checks passed.
Mocked export selection and rendering-fixture checks are explicitly separate from
real provider/HTTP/Chromium/actual-clock evidence. Six final export passages were
recomputed by A against pinned sources.

Earlier failed native-tool cases and C's limited original-model CL3 HTTP result
are retained honestly. A's verified selection resolved its finite accepted cases;
this is not a guarantee of all provider outputs. Invalid/unavailable responses
still fail safely. Backend calculations determine ranks; the LLM selects
verified canonical passages/IDs, not arbitrary facts or execution authority.

Stop only the A handoff serve-web process before bounded acceptance reruns because
they reserve the same A ports; restart it afterward. Use new output directories:

    PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli verify-live --require-typed-evidence --output ml/artifacts/session-a/<new-live-run>
    PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli verify-evidence-http --output ml/artifacts/session-a/<new-http-run>
    PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_ml.intelligence.integration_cli verify-web --privacy-only --output ml/artifacts/session-a/<new-browser-run> --playwright-module /private/tmp/minder-c-ui-check/node_modules/playwright --browsers-path /private/tmp/minder-c-browser

## Publication, exclusions and next work

AC1 published the named starting A/B/C snapshots first. Subsequent tested scoped
handoffs retain meaningful normal-merge/checkpoint/refinement history under closure
file06. AC4.2 records exact phase/merge SHA lineage and final publication evidence.
No main update, force, squash, amend, tag, PR, deployment or application build.

All13 original untracked inputs still match hashes/read-only modes in the existing
G0 shared snapshot. No new external input backup. Private config, source downloads,
model-selection metadata, model weights, generated rows, logs, screenshots and
synthetic SQLite/WAL files stay ignored/local and are not newly backed up.
No real CV/profile or sibling working directory was modified or published.

Next: F binds and accepts its intended product frontend against this exact backend.
Real forecast history/independent personal labels, deployed identity/storage/
continuous scheduler and submission release remain separate work. B's paid runner
requires separate access/budget/launch authority; none is queued or inferred here.
