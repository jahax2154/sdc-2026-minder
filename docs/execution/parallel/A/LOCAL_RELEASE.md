# Session A — typed current-evidence integration

Current handover: closure AC4.0/AC2, continuing I4.7. Historical phase reports and
original policy proposals remain unchanged. The provisional baseline works and A
real Groq/tool/wall-clock/privacy checks passed. Market coverage remains partial;
C's additional typed-source bridge is not yet integrated.

## Revision and operation

Closure AC1 published the named starting snapshots: A5e24f831141a417d7d7986cbffcb0cda55341d6b,
B020bbcf8511aa89064b7f232723afa01cf99a427, Cfe78c8429374d4d9748837ee9f2c94ab573c56e9.
Tested A followups through2fe9060029b5bb22f120f7557d5f4a8de4b6fe6b and B through
f62770b67eb3bd241e0a3947578064be72f609d7 were published under closure file06.
[AC1](AC1.json), [AC2](AC2.json), [AC3.1](AC3.1.json), [AC3.2](AC3.2.json) and
[working base](BACKEND_WORKING_BASE.md) record scope/evidence; later phase reports
supply the current exact remote snapshot. No main change, force, tag, PR, public
raw-data publication, application build or deployment.

B's original current-evidence handoff020bbcf is preserved; later synthetic-lab
commits are isolated from normal serving. Cfe78c84 grounder/privacy is integrated;
C's new CL1-CL3 contract/bridge remains an external committed handoff dependency.

Run from A: source .env.local, then use MINDER_PYTHON with
PYTHONPATH=ml/src:apps/backend-api and module
minder_ml.intelligence.integration_cli serve-web.

A API 8101/UI 9101 on loopback; same-origin /api/*. Entry /#profile,
Career Match at /#explore, Minder chat at /#minder, agents at /#mindbots.
C migrations/actions/persistence are reused with A's isolated
ml/artifacts/session-a/closure-runtime/dev.sqlite3 is the currently started local
frontend-handoff database. AC2 acceptance used separate disposable A databases.
No sibling database is used; only explicitly authorised provider variables were
securely transferred into A's private configuration.
A clone alone lacks the 13 pinned read-only inputs; reuse the existing G0 snapshot.
Reuse the existing interpreter/tooling; no install or build is required.

Supply three explicit anchored skill observations with activity descriptions.
Industry background/interests, role interests and work-style inputs are separate
optional evidence. No prior job or role-by-role ratings are needed. CV/chat claims
remain reviewable; no automatic mastery inference. Incomplete profiles receive
focused questions and no invented personal assessment.

## Policies and measurement treatment

Personal policy personal-role-fit-v3-provisional, references role-reference-v3.2
and baseline remain active. Minimum: three compatible native observations and
30% assessed role criteria. C is the mean of min(person LV / role LV,1) over usable
assessed positive-LV criteria. F is clipped 80*C + industry path + role interest +
work-style alignment; unknown optional values have no adjustment and retain null
raw values. Background/industry interest use the strongest supported path once.
Preparation time/resources stay in pathways.
See [personal policy](RECOMMENDATION_POLICY_V3.md). Original N01 remains historically
unapproved/inactive. Legacy F0/67 and learner artifacts are preserved.

Current market policy personal-current-evidence-v2.1 retains separate employer
observations, published occupation-category offering activity, related shortage-
group context and sector context. Comparable activity uses .85*F+.15*M within valid
independent source groups; employer M normalises log count against 155 inspected
ads, published M against the observed maximum for that same source period.
No pooled denominators or global rank across unlike groups. A related shortage-
group prior contributes at most +1 once without changing F. Sector totals have
zero rank weight. Missing evidence is unknown. Forecasts contribute zero and
remain separately unavailable. See [v2.1 policy and scope](MARKET_EVIDENCE_POLICY_V2_1.md).

Seven code-backed related-group links preserve pinned crosswalk rows and MyCOL
native scope. They do not certify whole-role equivalence or that every child is
critical. MyCOL publication/continuous fieldwork dates remain null; edition and
actual availability remain explicit. All 96 B native facts are queryable without
inventing canonical links or mutating profile/preferences. Galaxy bulk data
remains undistributed under B's reuse hold.

## Actual coverage and interfaces

| Same anchored synthetic profile | Original v1 | Current v2.1 |
| --- | ---: | ---: |
| Personally assessed eligible roles | 910 | 910 |
| Comparable activity ranking, including category proxies | 4 | 5 |
| Exact native employer observations available | 4 | 4 |
| Published-category primary / employer primary | 0 / 4 | 3 / 2 |
| Related shortage-group context | 0 | 7 |
| Exact whole-role shortage designation | 0 | 0 |
| Related sector context integrated | 0 | 907 |
| Personal-only ranks without contextual adjustment | 906 | 900 |

Counts overlap: two shortage-linked roles have activity comparisons; five others
receive contextual exploration treatment. No sum implies 907 narrow role-demand
series or a catalogue-wide comparable rank. Catalogue: 1,016 references, 910
supported, 106 partial/explorable. The five unchanged original calibration profiles
and one-observation incomplete profile lack the new assessment minimum.
Independent personal-fit labels: zero.

POST /api/role-evidence returns typed source records and canonical verifiable
passages. Optional trace retrieval requires owner/current profile-version-bound
trace identity; normalized market values and final internal scores are excluded.
GET /api/source-market-catalogue and POST /api/source-market-context expose bounded
native facts. Unlisted children stay unknown. Source cards show quantity/type/
unit/source/scope/date. Ordinary numeric ranks/scores/points remain hidden in C's
presentation while backend ordering is preserved.

[EvidencePassage v1](requests/I4-VERIFIED-PASSAGE-CONTRACT.md) verifies actual source
artifact/row integrity and recomputes the complete record/passage/references.
Wrong values/scope/dates/citations/role/future issue time fail even with a
valid-looking ID/hash. This is closed structured-source verification, not source
truth, mapping validity or general natural-language entailment.

C's integrated minder-grounding-privacy-v1 uses owner-scoped support ledgers,
closed claim selection, exact Bosch count reconciliation, minimized prompts and
0600 DB files. It does not yet consume the new typed passage adapter. Published,
shortage and sector facts work in backend/UI; their new LLM claims remain
unsupported until C returns a focused committed consumer handoff. No broad C
grounding rewrite or source-ID-only citation fallback was made by A.

## Checks, models and access

Historical full-suite checks are consolidated in [I4.7](I4.7.json); source/contract/API
evidence is in [I4.6](I4.6.json). [AC2](AC2.json) records actual A provider/tool,
11 application/scheduled checks and five real privacy-browser checks. [AC3.2](AC3.2.json)
records43 market/forecast tests and synthetic isolation; [AC4.0](AC4.0.json) records
permitted input provisioning without repeating A bootstrap. Real HTTP/Chromium uses
synthetic profiles with actual local services/sources, no fetch/provider mocks.
Scenarios distinguish incomplete intake, fresh graduate, career switcher,
not-interested/idempotent retry/reset, source queries, persisted actions/approval
and unavailable forecasts. Controlled counterfactual counts test ranking
sensitivity without altering factual snapshots. Mocked transport unit checks
are separate from real provider success.

Baseline serves. Existing Ridge/XGBoost policy-distillation runs are preserved:
48 fictional families, 569 rows, 32/8/8 family split; holdout teacher MAE Ridge
.0021, XGBoost 3.6832. Independent evaluation labels remain zero; neither learner
was promoted. B's actual approved-target forecast eligibility run found zero
compatible examples. Baseline/Ridge/XGBoost machinery exists, but no real market
fit/evaluation/selected forecast model is claimed. No new training target/spend.

A's ignored owner-only .env.groq.local is now securely configured under the latest
explicit user instruction. Only the existing authorised C key/model were copied;
no C ports/database/runtime/model-selection file was copied. No secret values were
printed or committed. A itself verified discovery, model access, chat/native tool,
direct action, proactive preview/rejection/approval, persisted state and an actual
upcoming-minute owner-scoped scheduled event. Its real Chromium privacy/source
case passed. These close the earlier I4.2 access blocker; original reports remain
historical. The existing sibling-path runtime guards remain intact.

Bounded reruns use the existing interpreter/PYTHONPATH and integration_cli verify-live
--output ml/artifacts/session-a/<new-live-run>. For the scoped unchanged privacy
browser use verify-web --privacy-only --output ml/artifacts/session-a/<new-run>
--playwright-module /private/tmp/minder-c-ui-check/node_modules/playwright
--browsers-path /private/tmp/minder-c-browser. --privacy-only requires real provider
success. Do not repeat unchanged full checks merely to inflate totals.

The local handoff server is loopback-only8101/9101, with health at
http://127.0.0.1:9101/api/health. It starts no unattended worker. Remote teammates
use the published Git base and permitted inputs; this Mac's loopback is not their
hosted API. Local wall-clock success does not establish hosted24/7 scheduling.
Intended product/Replit frontend remains F-owned and unverified here.

## Exclusions and next work

Original 13 read-only untracked inputs remain in the G0 shared snapshot; no new
external backup. A ignored logs, synthetic DBs/screenshots, downloaded sources,
model artifacts and browser tooling remain local. Configured provider file remains owner-only and
ignored; no credentials/private CVs/profiles/databases/weights/raw bulk inputs are
staged. No B/C working directory or production data was changed.

Next runnable work: C consumes the versioned passage contract through a committed
handoff; A integrates and verifies it against the already working A provider.
New non-Bosch typed-source chat/scheduled acceptance remains pending that bridge. B may expand supported mappings and
compatible role/skill forecast history through committed handoffs. No paid job
is queued. Tested task-scoped closure handoffs are authorised for normal push
under file06; unrelated pushes/deployment remain unauthorised.
