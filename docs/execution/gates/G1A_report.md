# G1A execution report

**Implementation: PASS. Catalogue: PARTIAL. Meaningful-baseline data gate: BLOCKED. Empirical readiness: NOT EVALUATED.**

Executed locally on the existing Python CPU environment for the current G1A instruction only. [Authorization](G1A_authorization.json) records the stored instruction version/hash and current location override. This is execution authorization, not historical package approval or human review. [Structured evidence](G1A_evidence.json), [test output](G1A_checks.txt), [service demonstration](G1A_service_demo.json) and [working-tree status](G1A_git_status.txt) retain the actual results.

## Implementation and policy mapping

- `ml/docs/MINDER_POLICY_REVIEW_v1.md` remains the canonical policy. Its exact JSON block is projected to `ml/configs/intelligence/policy.v1.json`; equality is checked on load. All values, including proposed approval status and null reviewer fields, are preserved. `policy.py` caches validation by policy/document/authorization content, returns defensive copies, and records policy ID, version, hashes and G1A authorization. No separate policy pack/configuration was found in the repository; no duplicate intelligence README or replit policy was created.
- `policy_sources.py` validates existing source-manifest hashes and database release 31.0, then projects three source-native O*NET occupation identities and their skill rows. `ml/data/review/g1a-v1/catalogue.policy-accepted.json` is the versioned projection. These are **policy_accepted / source-derived**, never human-reviewed. O*NET database release is recorded separately from the unspecified taxonomy edition; the historical identifier version of 31.0 is not repeated as a taxonomy edition.
- Structured milestone templates require a versioned source registration, pinned file hash, role scope, source record, criterion anchors and rule provenance. The builder revalidates the acceptance proof against the actual source content. LLM proposals cannot acquire acceptance merely by supplying a status flag. The only registered milestone source currently is the explicitly synthetic contract fixture; it cannot establish requirements for any of the real occupations.
- `policy_features.py` implements FIT-01..12 measurements using the existing `build_features`, skill coverage, time feasibility and criterion-gap functions. Equal criterion/tag/group weights default to 1. Nondefault coefficients require an explicit separately implemented named policy; this gate adds none. Full occupational skills remain reference context, separate from initial milestone criteria.
- Criterion answers bind profile, milestone and anchor versions and cite assessment basis/evidence. Anchored self-report is visible as such, without becoming human review. I uses explicit avoid/dislike=0, neutral/open=0.5 and interested=1. W uses incompatible=0, acceptable/no preference=0.5 and compatible=1. Unanswered inputs stay null.
- Remaining effort counts each unique prerequisite task once, removes only version-matched completed tasks with evidence, retains estimate/source basis and uses the summed upper bound. Unknown task effort makes aggregate effort unknown. Known E=0 produces T=1, including unknown weekly hours; missing hours with positive E stays unknown. Lower/upper T bounds are retained.
- Resources use OR alternatives within each required group and complete equally weighted groups. Explicitly confirmed empty resource groups produce R=1; missing definitions do not. Price checks require compatible currency/period and budget evidence; affordability alone never proves access. Explicit user hard-constraint declarations and sourced requirement checks produce clear / needs_check / excluded before ranking. No requirement is inferred from an occupation title.
- `inference.recommend_profile` adds a versioned envelope around the existing `recommend` callable. Baseline weights, feature order, horizon semantics, scorer selection and the strict `minder-recommendation-v1` body remain unchanged. Rich rule/component traces, gaps, questions, evidence IDs, acceptance/version context and exceptions are sidecars under `contracts/policy-recommendation.g1a.v1.schema.json`. Invalid catalogue Q is null and excluded from numeric RoleInput, rather than misreported as Q=0. Constraint exclusions and unresolved eligibility also stay outside ranking. Explicit unavailable learners return model_not_ready without baseline fallback; catalogue compatibility now includes policy and pipeline context.
- Repeated inputs give identical values and fingerprints. Profile, answers, criterion/effort definitions, source bytes, source registry, policy and versions affect fingerprints. Changed/missing pinned source bytes invalidate eligibility. There is no persistent feature cache in this repository; downstream caches must use these content keys. No recomputation trains a model.

Historical Phase 2 adapters, six canonical entity schemas, pending role/criterion/mapping records, blind review materials and earlier reports remain unchanged. The additive G1A measurement supplement binds `profile_version` and `milestone_version`; it supplies criterion assessments, explicit interest/work-style tag answers, resource/budget facts, task completions and declared hard-constraint checks. It does not rewrite canonical UserProfile or human-review statuses.

## Actual service results

The initial smoke profile (`ml/tests/fixtures/phase2_profile.synthetic.json`) and all five calibration families (`ml/data/review/phase2/calibration-v1/profiles.synthetic.json`) ran against all three source-native role projections: **18 pairs, zero eligible scores**. Weekly hours and the 12-week horizons are retained as known inputs. No free-text skill, interest or resource statement was converted into an invented assessment.

All six proposed criteria remain pending:

| Role | Criteria |
| --- | --- |
| 15-1252.00 Software Developers | sw-requirements; sw-debugging |
| 15-2051.00 Data Scientists | ds-statistics; ds-evaluation |
| 15-1212.00 Information Security Analysts | sec-policy; sec-risk |

Each needs source/template-backed milestone inclusion, explicit 0/0.5/1 content anchors and anchor versions. Each role also lacks a bounded target artifact, task/prerequisite definitions and effort basis, explicit interest/work-style tags, resource alternatives and hard-requirement definitions or confirmed empty lists. Existing profiles then need explicit version-bound answers for those definitions. Complete per-pair missing-evidence records and targeted questions are in the service demonstration. Q remains null for invalid catalogues; no user deficit or fabricated score is assigned.

The **contract-only synthetic fixture** (`ml/tests/fixtures/g1a_contract.synthetic.json`) exercises the same acceptance, builder and service path: C=0, I=1, T=0.5, R=1, W=0.5, Q=1, F0=45. Its fictional requirements/estimates are test inputs, not real occupational facts or independent labels. Separately, the inherited foundation vector [0.6,0.8,0.5,1,0.7] still produces **67**.

P2-4 is transparently superseded for this path by `P2-4-policy-acceptance-g1a-v2`: valid source-native identities and bounded policy-accepted milestone definitions can pass catalogue validation without blanket human review. Three identities pass; zero real-role milestones pass. Independent-label readiness remains a separate gate. The historical P2-4 report is preserved.

## Verification and preservation

- Full discovery: **73 tests passed in 89.889 seconds** at that revision, including all 59 existing foundation/Phase 2/review tests. After final G1A source-dependency, authorization-context and boundary changes, **16 focused tests passed**. The full suite was not rerun after those final isolated changes.
- Seven actual/synthetic service envelopes validate with Draft 2020-12 JSON Schema, including the unchanged nested recommendation-v1 contract. Golden score, zero versus unknown, partial Q, invalid catalogue, effort/constraint/resource boundaries, source integrity, deterministic fingerprints and learner no-fallback behavior pass.
- `git diff --check` still reports **preexisting trailing whitespace at training.py:17**. That unrelated file is unchanged by G1A. Task-file whitespace checks pass.
- Before/after hashes confirm only existing `AGENTS.md` and `ml/src/minder_ml/intelligence/inference.py` were changed by G1A; no existing files were removed. All other preexisting work, source data, contracts and pending reviews were preserved. Added code/configuration/fixture/projection/contract and execution evidence paths are enumerated in the evidence JSON.
- New-file binary/NUL and credential-pattern checks found no binaries or credential matches. No packages were installed; no models fitted, labels generated, remote compute/spend, commits, pushes or publishing occurred.

## Remaining dependencies and next interface

One deduplicated exception list lives in `G1A_evidence.json` (with affected pairs in the demo): missing bounded milestone/measurement evidence; 24 optional crosswalk candidates with unresolved taxonomy/scope/reuse terms; and zero independent labels. The optional bridge does not block native identity use, but cannot establish ESCO or Malaysian narrow-role demand. The source pack's U.S. scope remains explicit.

Python callable integration was exercised. `apps/backend-api` and `apps/frontend-web` contain scaffolding only: **no HTTP endpoint or frontend flow was exercised**. No live-service readiness is claimed. Empirical baseline quality and Ridge/XGBoost comparison remain unevaluated with zero gold rows; this gate does not begin training or labeling.

Usable next interfaces for a separately requested G1B/G2 task:

```python
from minder_ml.intelligence.policy_features import derive_features
from minder_ml.intelligence.inference import recommend_profile
# Accepted, pinned bounded template + explicit version-bound answers:
measurement = derive_features(profile, role, answers)
response = recommend_profile(profile, roles, answers_by_role=answers_by_role,
                             scorer_kind="baseline")
```

Reproduce the offline demonstration:

```sh
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.g1a_cli
```

G1A stops here. No empirical training or subsequent gate implementation was started.
