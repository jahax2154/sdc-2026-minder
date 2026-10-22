# Three-role review worksheet

Status: **PENDING**. These are proposed source-linked review materials, not a reviewed catalogue, a supplied raw profile or human-reviewed labels. No numerical annotation grade has been generated.

## Concrete materials

- `three_roles.pending.json`: Software Developers (15-1252.00), Data Scientists (15-2051.00), and Information Security Analysts (15-1212.00). Six Codex-assisted milestone criteria are proposals. Approved weights, effort bounds/selected estimate, role-specific I/R/W rubrics and reviewer provenance are blank/pending.
- `role_requirements_worksheet.csv`: six editable criterion rows. The proposed equal criterion weights are independent of the baseline's feature weights and must be approved or replaced by a reviewer.
- `source_mappings.pending.json`: 24 mapping candidates extracted from the supplied ESCO–O*NET crosswalk. Relation types, taxonomy vintage and individual source row numbers are preserved. None is adopted automatically.
- `source_references.json`: source URLs, attribution/licence notices and original file hashes. Criterion descriptions are new proposed adaptations, not quoted O*NET task requirements.
- `profile_intake.pending.json`: blank raw-profile intake. The existing single-role feature-vector fixture does not establish a user's criterion evidence, interests, resources, preferences or weekly hours for these roles. Do not reverse-engineer those facts from its normalized values.
- `blind_grading_packet.pending.json`: three pending role cards without model outputs or derived feature values. It cannot yet be graded because profile and catalogue prerequisites are missing.
- `annotation_intake.pending.csv`: three pending role rows with blank grades/reviewer fields/features. These are intake slots, not three labelled user-role examples. The empirical training template remains untouched and empty.

The source pack describes U.S. occupations, not observed Malaysian role demand. Crosswalk versions are O*NET-SOC 2019 / ESCO v1.1.0, whereas the role source is O*NET 31.0. Review the mapping/version alignment and specific crosswalk reuse terms before adoption. IM and LV values remain source context; neither is divided into an invented user-proficiency ratio. No D or S is computed.

## Required review actions

1. Confirm the three role choices and intended geography. Inspect each source row/mapping relation; document acceptance/rejection rather than assuming exact, broad, close and narrow relations are interchangeable.
2. For each role, approve or replace the proposed initial milestone criteria. Specify observable content that earns demonstrated fractions; approve nonnegative criterion weights with positive total weight. Record reviewer ID, reason and actual review date. A whole-career O*NET description does not establish a twelve-week milestone.
3. Review the remaining effort estimate and its uncertainty range under that milestone. Record the E used and the basis. Unknown effort stays null. Review concrete role-specific interests, resource checklist and work-style rubric; unknown alignment is not neutral alignment.
4. Supply a fictional/raw profile with profile/group/version IDs, explicit interests/preferences/resources, weekly hours and horizon. Preserve related variants in the same group. Record criterion evidence with demonstrated fractions and review provenance; absent evidence stays unknown.
5. Only actual reviewers may change `review_status` to `reviewed`. `mapping_reviewed` requires the role reviewer to approve the chosen mapping. Each role, criterion, feature rubric and effort estimate requires nonempty reviewer ID, reason and actual `reviewed_at` before this adapter builds features. This structural attestation does not independently establish review quality.
6. Store criterion assessments in `criterion_assessments` as `{role_id, criterion_id, demonstrated_fraction, evidence_ids, review_status, reviewer_id, review_reason, reviewed_at}`. Store the role's reviewed I/R/W in `role_assessments` with role_id, the three named values, evidence IDs and the same review provenance. Raw facts and source links must justify these judgments; an LLM suggestion alone is not independent review.

## Blinded annotation sequence

Keep the initial grading session separate from engineering score output. Use [GRADER_INSTRUCTIONS.md](GRADER_INSTRUCTIONS.md) and the pending packet only after real input/role review is complete. Do not hand graders the baseline result, weights, ordering, learner output or the normalized feature vector. Collect independently reasoned grades before revealing predictions. Do not publish private reviewer identities if pseudonymous, traceable reviewer IDs suffice.

After grading, separately prepare reviewed feature snapshots through the shared builder and join on immutable profile/group/role/version/horizon IDs. Preserve the original blind judgments; do not overwrite them to agree with the baseline. An independent reviewer must explicitly attest the label's provenance. Transfer only complete eligible independently reviewed rows into `ml/data/annotations/personal_fit_annotations.csv`. Keep unresolved rows pending. Blank grading slots must not be promoted merely to unblock fitting.

## Engineering execution after prerequisites exist

Use `prepare-profile` with the completed files to derive features and per-criterion gaps through `build_features` and the existing `recommend` service. The original recommendation-v1 structure is unchanged; derivation/gaps are a separate `profile-feature-review-v1` report. Unknown criterion content has null gaps. A pending/invalid catalogue is a validation/review issue, never Q=0 implying user inability. Actual scoring requires Q=1 and all features known. The CLI writes JSON to stdout; save it to an engineering-only location, away from initial graders.

```sh
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence prepare-profile --profile ml/data/review/profile_intake.pending.json --catalogue ml/data/review/three_roles.pending.json
```

The command currently fails explicitly for missing profile_id; no raw profile or approvals are invented. Do not interpret this as a demonstration across reviewed roles.

```sh
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence validate --data ml/data/review/annotation_intake.pending.csv
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence baseline-evaluate --data ml/data/annotations/personal_fit_annotations.csv --run-id baseline-review-001
```

The baseline command needs no RunPod runner or model fitting. With reviewed rows, it freezes profile-group splits, saves dataset/snapshot/split hashes, and evaluates development only. Holdout labels never enter its metrics. With the current empty template it returns `not_evaluated` and creates no split. For learner comparison on a verified, budget-funded RunPod CPU runner, reuse the frozen split with the existing `compare --split ml/artifacts/intelligence/baseline-review-001/split.json ...`; final holdout remains reserved for the development-selected candidate and baseline reference. A tiny reviewed pilot measures rubric agreement, not career outcomes.
