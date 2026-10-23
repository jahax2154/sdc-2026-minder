# G0 shared interfaces — minder-parallel-v1

## Current N01-R1 implementation additions

The following additive v1 schema extensions are implemented and validated in A;
the original G0 description and fixtures below retain their historical meaning.
Current policy `personal-role-fit-v3-provisional` and market policy
`personal-current-cohort-v1` supersede the original wait for bounded delegated
choices. See `A/RECOMMENDATION_POLICY_V3.md`; original v2 remains pending/inactive.

Evidence may include structured `assessment` (kind, statement, rubric version).
Only matching explicit native anchored skill evidence satisfies the practical
minimum. Public intake cannot certify a human review. Personal v3 assessments
are explicitly provisional and may have unknown optional components with zero
adjustment; `contribution_points` is authoritative, not an inferred weighted
mean of nullable values. Coverage, evidence kinds, industry paths, unknowns and
focused questions remain available separately. Old pending DTOs still cannot score.

Public recommendation additions: independent `ranking_groups`, per-group `rank`
and `ranking_basis`, `evidence_coverage`, counts in `coverage`,
`ordering_scope=within_groups_only`, `overall_ranking_complete`, targeted input.
Personal-only comparison is partial. Internal market comparison calculations and
matrices remain excluded by `public_recommendation`; selected-role public context
contains only the user's personal assessment detail plus allowlisted market facts.
Current observations and forecasts remain separately typed and dated.

Default constructor `PersonalMatchingService(market)` uses v3. Explicit old policy
requests route only to the preserved pending API. New current application wiring
is committed in N1.3. No migrations, dependency installs, paid jobs or deployment
are implied by these additive contracts.

## Preserved G0 interface description


Additive executable schema: `contracts/parallel-services.v1.schema.json`. Existing `recommendation-result.v1.schema.json`, `policy-recommendation.g1a.v1.schema.json` and `data-entities.v1.schema.json` remain unchanged. New DTOs adapt new product meaning explicitly rather than changing old target semantics. IDs are opaque source-namespaced strings; preserve taxonomy ID/edition, database release and entity version separately. Source hashes are SHA-256 of identified bytes, not a claim of approval.

Python boundary: `minder_ml.intelligence.service_contracts`. `validate(kind, payload)` validates individual DTOs and cross-field invariants. `PersonalService.assess(profile, roles, *, scorer_kind, policy_version, market_period_policy_key)` is A's implementation boundary; returns Recommendation. `MarketService.current(entity_type, entity_id, *, as_of)` and `.forecast(..., issued_at)` return MarketResult. `ApplicationAdapter.career_context(profile_id, *, expected_profile_version)` composes saved context; `.execute(action, *, expected_state_version)` is C's persisted action boundary. These are Protocols, not implemented new services. C may call Python in-process or bridge through its actual backend transport, validating JSON; no HTTP endpoint or framework is chosen by this contract. No absolute imports from sibling worktrees.

`legacy_preparation_recommendation` delegates to existing `inference.recommend_profile`, preserving its G1A envelope. Never pass new Profile/Role DTOs directly into it: existing entity formats and target remain legacy. C must label that output legacy_preparation_fit; new role-fit implementation uses the new DTO and pending policy state until authorised. Legacy F0 fixture remains 67.

| Family | Stable fields and semantics |
| --- | --- |
| Profile | Version/group ID, explicit evidence state/value/unit/method/provenance; source-derived claims != verified competence; typed scoped preference state; current fields including no employment/unknown/want to leave; explicit hard constraints. Evidence unknown=null, known zero=0. |
| Role | Native taxonomy ID/version and database version; source hashes; source/policy accepted vs pending many-to-many skill/industry mappings; occupational requirements distinct from later milestone. |
| Personal | Status, nullable index 0–100, measurement/policy/model, explicit scorer; components 0–1 and weights, industry trace, criterion gaps, prerequisites/unknowns/questions/evidence/rules. Pending policy never numeric-scored. |
| Market | Current vs forecast; MY; named source universe/cohort; measured quantity, units and denominator; observed/published/available/ingested/issue/target dates; target next full calendar quarter; value, internal index, interval method/limits, versions/sources/missing reasons. Unavailable is null, never 0. Source counts != all vacancies/hires. |
| Recommendation | Internal personal/current/forecast results separated from strict public DTO; candidate IDs, profile/policy/model versions and explicit market_period_policy_key. Pending blend has no combined scores. `public_recommendation` returns allowlisted public data, excluding internal market matrices. |
| Company | Employer/location/role plus actual checked scope and time, official sources, matching/unknown requirements and separately authored suggestions. No-role-found means only checked sources, never universal absence. |
| Plan/progress/actions | Versioned task graph, activity vs mastery, locks/prerequisites/constraints and past state. Mutations carry expected version, idempotency key, exact diff and authorising request or matching approved proposal. Direct-specific requests avoid redundant approval; proactive pending proposals cannot be applied. C enforces atomic execution, stale-state checks, retry/undo and persistence; G0 validates DTOs only. |

Synthetic fixtures under `contracts/fixtures/parallel-v1/` cover complete/partial evidence, pending numeric policy, role-not-interested state, unavailable forecast, no-company-role-found, plan state, direct request and approval-required proposal. No fixture is a live source observation, empirical label, human approval or working database mutation. Complete evidence can coexist with pending numerical policy; no fabricated score closes that dependency.

Validation: `PYTHONPATH=ml/src <python-with-requirements-foundation> -m unittest discover -s ml/tests -p test_service_contracts.py`. Existing source contract tests use `test_foundation.py`. Dependencies are already present in the original checkout ml/.venv; no dependency installation or framework bootstrap occurred.
