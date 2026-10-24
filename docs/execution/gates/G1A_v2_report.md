# G1A completion — re-execution v2

**Implementation PASS · Catalogue PARTIAL · Meaningful-baseline data gate BLOCKED · Empirical quality NOT EVALUATED.**

The current instruction was executed against the existing implementation. Earlier G1A reports, source projections, pending records and blind-review materials remain unchanged. [Evidence](G1A_v2_evidence.json), [authorization/version/hash](G1A_v2_authorization.json), [actual instruction](G1A_v2_instruction.txt), [test log](G1A_v2_checks.txt) and [service output](G1A_v2_service_demo.json) describe this execution. No G1A-R, G1B/G2, labeling, training or LLM integration was performed.

## Implementation

Reused `ml/src/minder_ml/intelligence/`, the existing shared feature mathematics, scorer, recommendation service and source manifests. The canonical policy remains `ml/docs/MINDER_POLICY_REVIEW_v1.md`; `ml/docs/MINDER_APPROVAL_SUMMARY_v1.md` remains a reading aid. The existing exact JSON projection `ml/configs/intelligence/policy.v1.json` is unchanged, including its proposed historical approval status and null reviewer fields. The prior instruction to use these existing locations remains in effect; no duplicate policy documents or replit policy were created. Root AGENTS already points to the canonical source.

The existing policy loader validates once per unchanged policy/document/authorization content and returns defensive copies. It now records the current execution authorization rather than reusing the previous execution identity. Policy ID `minder-intelligence-v1`, policy schema `1.0.0` and actual hashes are retained in the evidence and returned service metadata. This authorizes G1A execution only; it does not manufacture a historical approval or human review.

The pipeline is now **policy-feature-pipeline-g1a-v1.1**. Changes are confined to G1A boundary correctness:

- Source/criterion/task evidence references must be lists of distinct, nonempty string IDs. Truthy strings cannot masquerade as evidence or remove prerequisite effort. Missing assessment evidence remains unknown or is rejected when a numerical assessment claims it exists.
- An explicit user hard constraint with no resolved requirement check returns `needs_check` and is excluded from ranking. Its known feature components remain available. Confirmed conflicts still return `excluded`; occupation titles establish no requirements.
- Invalid milestone definitions return a targeted correction question. A bad catalogue option remains separate from valid options in the same comparison, with Q=null rather than a fabricated Q=0.
- Constraint declaration evidence is included in the returned provenance when used for a resolved check.

The envelope schema now accepts both the previous v1 and current v1.1 pipeline identifiers. Both historical and new responses validate. The strict nested recommendation-v1 schema, feature order C/I/T/R/W, baseline weights [0.40,0.20,0.20,0.10,0.10], horizon semantics and explicit scorer selection remain unchanged. No second scoring engine was added.

Existing FIT/AUTO behavior is retained: equal default criterion/tag/group weights; anchored criterion answers with explicit evidence basis; explicit interest utilities; W=0/0.5/1 with acceptable/no-preference=0.5; deduplicated prerequisite effort; version/evidence-bound completed tasks; upper-bound effort reference with T bounds; resource alternatives as OR within equally weighted required groups; compatible cost currency/period; complete Q=1 and all positive-weight features before scoring. Unknown never becomes zero or neutral. Source changes invalidate pinned acceptance and content-addressed feature keys. Unavailable selected learners return model_not_ready rather than a baseline fallback.

Source-native O*NET records are policy_accepted/source-derived, distinct from human-reviewed judgments. Source database 31.0 and file hashes are checked on their actual scope; the unspecified taxonomy edition is not mislabeled as database 31.0. Twenty-four optional crosswalk candidates remain quarantined; native occupation use proceeds without them. Structured template acceptance validates registered source/version/hash, role scope, anchors and provenance. The only currently available accepted milestone template is explicitly synthetic and cannot establish requirements for the three real roles.

The new native projection is `ml/data/review/g1a-v1.1/catalogue.policy-accepted.json`. P2-4 remains transparently versioned as `P2-4-policy-acceptance-g1a-v2`: source-native identity acceptance, bounded milestone readiness, independent labels and empirical learner quality are separate. Historical P2-4 checks are preserved.

## Actual data and service results

The initial supplied smoke profile plus five existing calibration families ran through `inference.recommend_profile` against all three occupations: **6 profiles × 3 roles = 18 pairs; 0 scored**. No supplied profile answers were filled or inferred from free text. The service demo ran in **0.068872 seconds locally**, and a repeated unchanged run produced exactly equal values, versions and fingerprints. Seven current envelopes and seven historical envelopes validate against the compatible envelope and nested result contracts.

| Real role | Pending criterion IDs | Actual affected pairs |
| --- | --- | --- |
| Software Developers, 15-1252.00 | sw-requirements; sw-debugging | 6 |
| Data Scientists, 15-2051.00 | ds-statistics; ds-evaluation | 6 |
| Information Security Analysts, 15-1212.00 | sec-policy; sec-risk | 6 |

For all three roles, the missing bounded milestone evidence is: target artifact; criterion inclusion backed by a compatible source/template; explicit 0/0.5/1 content anchors and anchor versions; task/prerequisite graph; sourced or accepted-estimate effort hours; explicit interest/work-style tags; resource alternative groups; and explicit hard-requirement definitions or confirmed empty sets. The six existing criterion descriptions are proposals, not source-native task facts. No learning hours or empty requirements were invented. Once definitions exist, profiles need matching anchored criterion answers and explicit utility/access/constraint measurements. The demo contains exact per-role missing fields, known hours/horizon, reasons and follow-up questions. Invalid catalogue Q remains null.

The separate **synthetic contract-only** fixture exercises the same pinned-template acceptance, feature builder and service: C=0, I=1, T=0.5, R=1, W=0.5, Q=1, baseline=**45**. These fictional task estimates and requirements are test inputs, not real-role readiness or independent labels. The inherited foundation vector [0.6,0.8,0.5,1,0.7] still produces **67**.

One deduplicated exception list is in the evidence JSON: missing milestone/measurement definitions; unresolved optional crosswalk scope/reuse; and absent independent labels. Labels are not a prerequisite for baseline inference; they prevent empirical agreement evaluation and learner comparison. No grades were generated or promoted to gold.

## Verification and preservation

- **79 tests PASS**, full unittest discovery, exit 0, **86.863 seconds** in the existing local `ml/.venv` environment. This includes all existing tests and 20 G1A checks covering the new boundaries, golden score, zero/unknown, partial Q, invalid catalogue isolation, effort/resource/constraint boundaries, source integrity, contract validation, determinism and cache-key invalidation.
- Current and historical response schemas validate; the unchanged actual service demonstration reproduces exactly.
- Task-file syntax, trailing-whitespace, credential-pattern and binary/NUL checks pass. These are scoped checks, not a guarantee of comprehensive secret detection.
- Repository-wide `git diff --check` still fails only on the preexisting `training.py:17` trailing space. That file is unchanged by this execution.
- Before/after hashes identify four existing files changed: `policy.py`, `policy_features.py`, `test_g1a.py` and the compatible envelope schema. No existing files were removed. Historical reports, canonical policy/configuration, original pending records, labels, strict recommendation contract and unrelated work were preserved. No dependencies were installed, models fitted, commits/pushes/publishing or spending performed.

## Readiness and next usable interface

Python service: **exercised**. HTTP endpoint and frontend: **not implemented/exercised**; the actual `apps/backend-api` and `apps/frontend-web` directories remain scaffolding. No live-service pass is claimed. Catalogue is **partial**: three pinned identities accepted, zero real-role milestones ready. Empirical status is **not_evaluated**, with zero rows in the independent annotation CSV.

The remaining data dependency is a compatible, traceable bounded milestone/template for each real role, then explicit version-bound profile measurements. These remain pending; this gate does not approve new role requirements or collect labels.

Next interface for a separately authorized G1B/G2 task:

```python
from minder_ml.intelligence.policy_features import derive_features
from minder_ml.intelligence.inference import recommend_profile
measurement = derive_features(profile, role, answers)
response = recommend_profile(profile, roles, answers_by_role=answers_by_role,
                             scorer_kind="baseline")
```

Use current v1.1 pipeline metadata and `contracts/policy-recommendation.g1a.v1.schema.json`; the nested recommendation remains v1. Explicit supplements bind profile and milestone versions. There is no persistent feature cache; downstream caches must use returned content fingerprints. Reproduce the synthetic/offline demonstration with `PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.g1a_cli`.

Stopped after G1A completion. No empirical training was started.
