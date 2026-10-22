# Personal service — early A1 handoff

Common contract: `minder-parallel-v1`. This checkpoint adds optional qualitative
trace fields without changing existing required DTOs. N01 stays inactive.
This resolves the constructor/catalogue portion of C-001; market wiring awaits B.

```python
from minder_ml.intelligence.catalogue_service import OccupationalCatalogue
from minder_ml.intelligence.personal_service import PersonalMatchingService
from minder_ml.intelligence.service_contracts import public_recommendation

catalogue = OccupationalCatalogue()  # verifies pinned local source bytes
roles = catalogue.roles()           # 1,016 references; 910 supported, 106 partial
service = PersonalMatchingService()
result = service.assess(saved_profile_dto, roles)  # 910 unranked candidates
public = public_recommendation(result)
requirements = catalogue.role('onet:15-1252.00')['requirements']
reference = catalogue.reference('onet:15-1252.00')
```

Use the actual C-saved Profile DTO. No private profile is included here. For a
named synthetic smoke call use `personal_cli.synthetic_profile()`. The existing
G1A `recommend_profile` remains legacy preparation; do not use it for role fit.
Load with current-worktree `PYTHONPATH=ml/src`; no sibling-source imports. Source
IDs/versions/hashes/URIs are in `catalogue.coverage['sources']`, role sources and
reference records. Source access errors fail explicitly, without a fixture fallback.

Initial matching has no milestone, learning-hours or roadmap dependency. Partial
references remain browseable but do not enter supported assessment candidates.
No numeric score, rank, industry contribution or weight is issued before N01.
Known profile evidence and explicit field/industry history are preserved; source
ratings have units `onet:IM`/`onet:LV` and method
`onet-occupational-rating-not-user-rubric-v1`. They do not establish a personal
competence threshold. Gaps are unknown until a compatible rubric exists.

`industry_contributions` preserves background fields, explicit preferences and
mapping support independently. Missing mappings are unknown, never inferred
from titles. `profile_fields`, `role_preference` and `unresolved_constraints`
preserve context in the internal assessment. Hard constraints are disclosed as
unevaluated while their source-backed comparisons are unavailable; do not
describe these candidates as confirmed feasible or qualified to apply today.

B may be injected with `PersonalMatchingService(market_service,
as_of='2026-10-23T00:00:00Z')`. Its `current(..., as_of=...)` and
`forecast(..., issued_at=...)` must return validated MarketResult for the exact
requested role ID. Current/forecast arrays stay distinct, public projection
excludes internal indexes, and combined scores remain empty. Errors propagate
to C's boundary; there is no silent score/fake forecast substitution.

Reproduce coverage: `source .env.local` then
`"$MINDER_PYTHON" -m minder_ml.intelligence.personal_cli --output
ml/artifacts/session-a/<new-evidence-directory>`. The five original synthetic
profiles each produce 0 legacy scores and 910 new unranked candidates with 0
numeric scores. Five D02 synthetic audience demonstrations have the same
candidate/score counts. These runs demonstrate software/coverage, not validity.

A1.3 adds `update_preference(profile, entity_type=..., entity_id=...,
state=..., authorizing_request_id=..., expected_profile_version=...)`.
It returns a validated Profile for C to persist under its own atomic version
check. It performs no database write. `unknown` resets only that scoped state;
repeated same-state requests preserve the existing version. No numeric penalty
is active. C must persist the returned version and preserve evidence/history.

`filter_roles(roles, view_filter=None)` returns `roles`, `applied_filter`,
`excluded_role_ids`, `unresolved_industry_role_ids`, and `unmatched_role_ids`.
The new SearchFilter DTO requires nullable `role_ids`, `industry_ids`, `query`,
and an explicit `authorizing_request_id`. Null ID lists impose no restriction;
empty ID lists match nothing. Clear with `None` to restore all supplied roles.
Industry filters require source/policy-accepted links; missing links are
disclosed, not guessed. Show `applied_filter` and a clear control in the UI.
Preferences alone never invoke a view filter or remove catalogue records.
