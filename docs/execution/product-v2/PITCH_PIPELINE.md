# Actual prototype intelligence pipeline — Revision 3

Profile/user evidence → provisional backend role-fit → eligible typed Malaysian
current evidence → separate rank scopes → retrieved factual statements / model
practice guidance → validated scoped actions → canonical persisted state.
LLM explanations and roadmap/task drafts never calculate or replace rankings.

Active policies: personal-role-fit-v3-provisional and personal-current-evidence-v2.1.
Original N01 proposal history remains unapproved; N01-R1 is delegated provisional
implementation, not independently validated suitability labels. Baseline is active.
Preserved Ridge/XGBoost/synthetic experiments are not active independently evaluated
outcome predictors; unavailable real future forecasts remain separate.

Practical personal assessment minimum:3 valid anchored essential skills and30%
coverage. Missing inputs cannot invent skill, and interests/title/occupation importance
are not competence. Capability contributes up to80 points; transferable background,
role interests, industry interests and work-style each up to5. Optional unknown adds
no effect and is not dislike. Explicit preference/reset remains idempotent; interests
alone do not exclude other industries. Preparation constraints govern feasibility.

Comparable activity score = .85 × personal + .15 × source-specific normalized
activity + bounded shortage adjustment, capped100. Published category index uses
100*log1p(count)/log1p(max category count in same latest source period); inspected
employer counts use the inspected sample denominator. Different measurement/cohort/
source scopes are not pooled. Require at least2 personally assessed roles per group.
Related-group shortage adds at most1; exact independently supported role designation
at most2. Sector-context and future forecast ranking weights are zero. Missing market
is neither zero demand nor proved opportunity. Exploration has its own ranks, with
no cross-group overall ordering claim. Full active configs and checksums in trace.

Actual synthetic adequate-profile run (fresh current code, same pinned inputs):

| Scope | Count |
| --- | ---: |
| Catalogue | 1016 |
| Supported eligible / personally assessed | 910 / 910 |
| Comparable activity ranked | 5 (3 published category proxy,2 employer sample) |
| Published activity evidence supported | 7 |
| Related shortage context / exact whole-role shortage | 7 / 0 |
| Sector context | 907 |
| Personal-only ranks without shortage adjustment | 900 |

Counts overlap; current_available4 is the legacy employer-result availability count,
not the number of comparable activity ranks. Published evidence7 doesn't imply7
comparable ranks: scope/group eligibility and source precedence determine5 comparisons.
Historical industry offering index throughQ12026 is separate from active detailed
role ranking; broad occupation-group indexes and source-specific skill counts are
not an equally covered national skill-demand leaderboard. No market forecast accuracy
or learned career success claim follows these counts.

[PITCH_PIPELINE_TRACE.json](PITCH_PIPELINE_TRACE.json) is a synthetic internal example,
not ordinary user score UI. Software Developers: personal79.21822451; published
category activity93.27156204355506; related shortage+1. Exact result:
.85*79.21822451 + .15*93.27156204355506 + 1 =82.32622514003326, within its published
comparison group. Trace includes exact evidence IDs, mapping scopes, source periods,
normalization denominator40640, policy hashes and missingness. Backend trace determines
this number; model prose cannot change it.

```sh
source .env.local
PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" docs/execution/product-v2/checks/export_pitch_trace.py
```

Reads pinned sources and creates a disposable A-only DB; output stays under A ignored
artifacts. No training, paid job or production writes. Use a complete synthetic profile
for assessed coverage; an incomplete Profile is not claimed to rank910 roles.

## Measured engineering refinement

Full assessment timing was dominated by repeated schema traversal and quadratic
JSON Schema uniqueItems on large arrays of objects. Instrumented same rich-profile
context:281.7million calls/42.371s before;169.8million/27.716s after linear JSON
uniqueness and reused validator construction. cProfile overhead means these are NOT
HTTP latency claims. JSON equality retains bool-vs-number distinction,1==1.0 and
object key-order equivalence;1256 parity cases plus all cross-field checks remain.
A trial extra content-validation cache yielded28.597s, so was removed before commit.
No data/scoring arithmetic/coverage/approval validation was relaxed. Global assessment
may still take seconds on first load; generated advice avoids it entirely.
