# B synthetic experiment handoff to A

A coordinates publication under `06_CHECKPOINT_PUSH_AND_ACCEPTANCE.md` of the closure pack supplied in the main checkout. B does not independently push A/B/C branches. Initial B snapshot was `020bbcf8511aa89064b7f232723afa01cf99a427`. Publish tested task snapshots by full SHA, retaining meaningful history; do not force-push, deploy or infer paid permission.

| Phase | Status | Full local SHA | Output |
| --- | --- | --- | --- |
| SY1 | passed | `3dcc8e08fcfafc0c358aaf140063e929c2a752f7` | Existing-test audit, fictional generator/spec, examples, isolation checks |
| SY2 | passed | `e2561ff2430eb317ae8cbe547c6c913246c0cd32` | Actual baseline/Ridge/XGBoost measurements, log, model lineage |
| SY2-R01 | passed | `f62770b67eb3bd241e0a3947578064be72f609d7` | Clean worker runs without uploading the 13 real raw inputs |
| SY3 | passed for preparation; paid run blocked_external | Commit containing `SY3.json` and this handoff; capture its full SHA with `git rev-parse HEAD` | Exact replay, tested bounded worker launcher, model/data card and job specification |

**55 relevant tests pass**; unchanged observed-source/registry hashes and read-only 13-input preservation checks pass. Two additional fixed local replays reproduce the original experiment; no search/tuning was repeated. The clean clone under `/private/tmp` is a disposable reproduction environment, not another session's checkout. It has no raw inputs or credentials and is not an external backup.

Read `SYNTHETIC_DATA_MODEL_CARD.v1.md` and `synthetic-results.v1.json` for measured outcomes and limitations. The same test examples compare all methods: role/skill MAE is 1.4706/1.5294 last-value, 2.1765/1.8824 seasonal, 10.4692/5.7879 Ridge, 29.0250/15.7132 XGBoost. Seasonal won validation; it was not replaced based on test results. No independent real accuracy is established.

For reproducibility, use the pinned job specification and dependencies in an isolated environment; source `PYTHONPATH=ml/src`, then run:

```sh
python3 docs/execution/parallel/B/checks/run_synthetic_job.py --preflight-only
python3 docs/execution/parallel/B/checks/run_synthetic_job.py
```

The launcher verifies its code/input hashes, dependencies, CPython 3.9 and code ancestry before invoking the same generator/runner. It enforces the synthetic output namespace and process deadline, captures stdout/failures/hashes and compares metrics with the frozen reference. Job resources, Linux `timeout` outer command, one-worker/12-fit limits, maximum USD2 proposal, external resource-termination requirement and output collection are in `synthetic-runpod-job.v1.json`. It never creates a RunPod resource or measures billing itself. Linux image/digest, rate/balance/prior jobs and paid authority remain unverified; no paid execution occurred. USD25 is a reported total allowance, not verified remaining credit; existing A-002 requested no paid job and capped it at USD0.

No shared integration change is requested. A may use the labelled card/results for the submission and retain current observed context from `HANDOFF.v3.md`. Do not feed scenario rows/predictions/artifacts into recommendation evidence, normal forecasts, coverage counts or LLM market claims. Dataset IDs, geography, paths and all exported metadata visibly distinguish simulation. Normal runtime selected forecast models remain zero; A's personal policy and shared contracts are untouched. Broader source acquisition was not restarted.

Working-tree exclusions: original read-only untracked raw/derived inputs; ignored datasets, examples, predictions and eight synthetic artifact exports per local run; caches and local run logs. Original source inputs retain the G0 local snapshot; new generated artifacts and the disposable clone have no external backup. Committed code/specs reproduce them, and committed results/log summaries retain the evidence. No credentials, real personal records, source corpora, environments, database files or model weights were staged.

B has not pushed or deployed. A is authorised to coordinate the named snapshot push under file 06; B has not verified remote publication. Paid execution is separately blocked, not a blocker to the completed local experiment/preparation. No further synthetic expansion is needed.
