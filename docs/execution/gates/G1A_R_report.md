# G1A-R — catalogue readiness repair

**Implementation PASS · Catalogue PARTIAL · Usable actual score coverage 0/18 · Independent evaluation NOT_EVALUATED.**

Executed the task found at `ml/docs/G1A_R_CATALOGUE_READINESS_REPAIR.md`; the requested `ml/data/docs` directory is absent. [Authorization](G1A_R_authorization.json) records the actual task path and SHA-256. [Evidence](G1A_R_evidence.json), [test output](G1A_R_checks.txt) and [before/after service output](G1A_R_service_demo.json) retain actual execution results. This repair adds compatible ML adapters and data; it does not change the shared recommendation contract, G1A engine, Groq/chat, frontend, policy or dependency locks.

## Reproduced failures and upstream causes

The count is **six profiles in six families × three roles = 18 pairs**, not five profiles/15 pairs. `software-smoke-profile-001` / `software-smoke-family-001` is the initial smoke case; `calibration-profile-01` through `05` belong to the corresponding five calibration families. All original profiles and versions are preserved. None had a valid bounded milestone before or after this repair. They remain unscored because of catalogue definitions, not independent-label availability or an inferred lack of user skill.

| Role/milestone | Unique missing upstream fields | Affected pairs | Provenance / source availability | Repair / current state |
| --- | --- | --- | --- | --- |
| Software Developers 15-1252.00 / no accepted milestone | sw-requirements and sw-debugging anchors/inclusion; task effort; accepted tags/resources/constraints and artifact | 6 | Draft tasks are generated proposals. Pinned occupation/skill rows and primary background references exist, but no accepted bounded task template or effort estimate does. | Proposed two-task written brief/debug worksheet, concrete synthetic examples and anchors; inactive pending batch decision and supported effort ranges. |
| Data Scientists 15-2051.00 / no accepted milestone | ds-statistics and ds-evaluation anchors/inclusion; task effort; accepted tags/resources/constraints and artifact | 6 | Same source distinction; O*NET ratings do not determine user proficiency, worksheet scope or learning hours. | Proposed table-summary/leakage worksheet with concrete examples, definitions and anchors; inactive for the same dependencies. |
| Information Security Analysts 15-1212.00 / no accepted milestone | sec-policy and sec-risk anchors/inclusion; task effort; accepted tags/resources/constraints and artifact | 6 | Occupation/skill context and public security guidance exist; neither approves the generated assessment or hours. | Proposed fictional access-policy/risk worksheet with concrete examples, definitions and anchors; inactive for the same dependencies. |
| All six existing profiles / downstream evidence | Version-bound anchored criterion answers, explicit interest/work-style utilities, confirmed access and hard-constraint checks | 18 overlapping, **not additional** | Existing narrative self-reports and constraints are retained; their normalized assessments are unknown. | No imputation. New explicit synthetic cases are appropriate only after actual valid milestones exist. |
| Optional ESCO crosswalk | Relation/target applicability and reuse terms | 0 baseline pairs; 24 candidates | Native taxonomy relationship is now verified; the remainder is not established merely by matching IDs. | Continue native identity use; no candidate adopted. |
| Independent labels | Zero independent annotation rows | 0 baseline pairs | Labels assess empirical agreement; they are not missing feature inputs. | Evaluation remains not_evaluated. No grades, label collection or training performed. |

The first three rows partition all 18 primary failures. Downstream and optional dependencies overlap or affect separate outputs. No remaining scorer/schema defect was observed causing these 18 failures; the original exception was `milestone_definition_missing`, with Q=null. The detailed pair inventory and field-level reasons are in the evidence/demo.

## Deterministic repairs applied once

`ml/src/minder_ml/intelligence/catalogue_repair.py` adds a local compatible adapter around the existing source loader, builder and inference service. Its default `load_catalogue()` returns repaired native reference records with no fabricated milestone.

- The official [O*NET API reference](https://services.onetcenter.org/v1.9/reference/) explicitly distinguishes database 31.0 from O*NET-SOC 2019. The new projection records taxonomy edition **2019** separately from database **31.0**, checks applicability to the pinned database, and records source capture/version/hash/rule provenance. The historical projection with unknown edition is preserved.
- Six criterion-weight defaults are explicitly projected as **policy_accepted / policy-derived**, weight 1 under FIT-04. This accepts the default coefficient only, not criterion inclusion or a role-specific rubric. Native source records remain **source-derived**; no human-reviewed status is invented.
- Source-side taxonomy alignment no longer needs a human assumption. Crosswalk target/relation/geography/reuse remain quarantined; no optional mapping was adopted solely because identifiers exist.
- New source capture metadata, repaired reference versions and source hashes are in `ml/data/review/g1a-r-v1/source_facts.json` and `catalogue.reference-repaired.json`. Capture hashes cover saved excerpt/summary text, explicitly **not raw upstream HTML**. Existing source-pack bytes and pending records remain unchanged.

Targeted primary references were inspected for requirements, debugging, data analysis/leakage and authorization/risk concepts. Their URLs, exposed versions and limitations are retained. The inspected Microsoft overview renderings did not expose usable numeric durations. Unknown source revisions and task hours remain null. Background references do not independently approve our role-specific anchors or establish preparation/mastery time. The initial O*NET database-page fetch timed out; its official API reference supplied the documented version relationship instead.

## One concrete inactive batch and loader

[Human-readable batch](../../../ml/data/review/g1a-r-v1/BATCH_REVIEW.md), [structured proposal](../../../ml/data/review/g1a-r-v1/milestone_batch.proposed.json) and [single pending decision](../../../ml/data/review/g1a-r-v1/batch_decision.pending.json) are ready for review. There are no per-pair or per-mapping signature worksheets.

The batch supplies three narrow written artifacts, all six existing draft criteria, explicit 0/0.5/1 content anchors, six fixed fictional assessment examples and expected evidence, independent task graphs, proposed interest/work-style tags, and a nonempty proposed resource group. No essential draft criterion was removed to obtain a score. Template selection, specific anchors, task mappings/resources and the absence of additional eligibility requirements for these local exercises are **proposals**, not source-native occupational facts. All remain inactive/llm-proposed until a real batch decision exists. The synthetic answer keys are not user assessments or relevance labels.

Six task-effort ranges remain **unknown**. Their proposed estimation method itemizes setup, reference reading, artifact work and checking, using a named accepted work-breakdown estimate informed by defensible evidence. Course duration is not assumed to be mastery time; coverage does not imply proportional effort. No hours, zero-effort tasks, completed assessments, default access or active empty resource requirements were invented.

The implementation is complete for this dependency:

- `load_batch()` validates the pending batch, source/draft hashes, complete criterion/task coverage and synthetic assessment examples without activating it.
- `activation_plan(..., decision_path=...)` is read-only and rejects a pending decision, wrong batch hash, missing actual decision provenance, incomplete assessment selection, missing/inverted/zero task estimates, unsupported estimate bases and unrelated evidence. This loader accepts explicitly reviewed prototype work estimates; it does not ingest raw pilot timing evidence automatically.
- `activate_batch(...)` is an explicit future operation after a real complete decision. It materializes an immutable content-addressed source and registers it only after validation. It detects registry changes before replacement. It was **not executed on the actual repository**.
- `load_catalogue(source_id=...)` subsequently selects that exact registered approved release and reuses the existing `accept_milestone` checks. Default loading never adopts a pending proposal or selects a template to maximize a score.

A synthetic future approval/activation round trip was tested **only in temporary directories**, including idempotence and service scoring across three role IDs. Those test estimates, approvals and scores are not real catalogue acceptance, human review, actual coverage or independent evaluation. No temporary test decision was installed in the repository.

## Actual before/after verification

- **89 tests passed**; unittest time **120.625 seconds**, process wall time **120.731 seconds**, existing local CPU `ml/.venv`. Ten new repair tests cover pending isolation, exact decision hashes, effort/assessment requirements, essential-criterion preservation, source changes, activation planning and temporary activation/load/service round trips.
- The inherited foundation vector [0.6,0.8,0.5,1,0.7] still produces **67**. Existing golden, completeness, constraints, resource alternatives, source integrity and typed-contract tests pass.
- Before **0/18 scored**, after **0/18 scored**. Native identities remain 3; accepted actual-role milestones remain 0. The change is verified reference metadata and a reviewable, loadable pending batch, not fabricated score coverage.
- Twelve before/after service envelopes validate against the unchanged shared envelope/nested recommendation contracts. Repeated diagnostic outputs are equal after excluding measured execution duration. Actual new complete synthetic profiles created: **0**, because the required valid actual-role milestones do not yet exist. Original unknown inputs remain unknown.
- Source/draft/profile/configuration hashes and before/after catalogue fingerprints are recorded in the evidence. All preexisting files, shared contracts, labels, policy, root dependency locks, G1A code/reports and parallel chat/frontend work were preserved. No dependencies were installed, models fitted, commits/pushes/publishing or spending performed.
- Task-file syntax, whitespace, binary/NUL and credential-pattern checks pass. Repository-wide `git diff --check` still reports only the **preexisting training.py:17 trailing space**; this repair did not edit it. Pattern scanning is not a complete secret-detection guarantee.

Python callable service was exercised locally. HTTP/frontend/Groq were not exercised or modified by this gate. Independent quality remains `not_evaluated` with zero gold rows. No meaningful-baseline data pass or empirical accuracy is claimed.

## Remaining batch dependency and usable interface

The single remaining template decision is to approve/revise/reject the proposed three-milestone batch **and provide six defensible effort ranges with an accepted method/basis**. Then supply version-bound profile measurements; approving a catalogue never supplies a user's answers. The batch documents the expected effect and limitations in one place. No approval is asserted by this completion report.

Current usable source-only interface:

```python
from minder_ml.intelligence.catalogue_repair import load_catalogue, load_batch
from minder_ml.intelligence.inference import recommend_profile
batch = load_batch()                  # validates pending content; no activation
roles = load_catalogue()              # three repaired native references; milestone=None
result = recommend_profile(profile, roles, scorer_kind="baseline")
# Actual existing profiles return explicit missing-information results.
```

Reproduce: `PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.catalogue_repair_cli`.

G1B may consume `g1ar-reference-v1` reference projections and the existing canonical missing-information result now. It must not represent `g1ar-proposal-v1` as an accepted milestone. A future accepted source gets an exact content-hash version and must be selected explicitly. Stop after G1A-R; the parallel Groq task is unaffected.
