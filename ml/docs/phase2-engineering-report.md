# Phase 2 data engineering execution

Scope: [the approved handoff](phase2-engineering-gate.md) only. Schema/pipeline approval does not approve occupational content, mapping relations, ratings or labels. Actual commands, outputs, environment, counts and gate evidence are retained in [phase2_checks.json](../evaluation/phase2_checks.json).

## Implementation and boundaries

The existing `ml/src/minder_ml/intelligence` package now owns the Phase 2 data path:

- `data_schemas.py` validates [six versioned canonical entities](../../contracts/data-entities.v1.schema.json), enums, finite numbers, nulls, dates, review provenance and semantic constraints. Pending records remain valid without becoming approved. Weak proposals and role acceptance cannot become gold labels. `UserProfile` supports a private marker, but public review/export refuses private records.
- `data_pipeline.py` verifies the supplied source hashes, reads the real DOSM XLSX using the standard library, checks the derived CSV against source cells/labels/quarter headers, creates long-form observations and writes immutable snapshots.
- `market.py` implements comparability keys, safe observed source shares and quarterly YoY change. Cohorts remain separated by source, coverage, geography, window, taxonomy, method, unit and indicator. No scalar market-score policy is enabled.
- `data_adapters.py` connects canonical profiles/roles to the existing feature builder, gap calculation and recommendation service. The original result-v1 contract and algorithms are unchanged. Self-reported or unreviewed skill observations do not become assessed criteria. Unknown stated preferences/resources keep alignment unknown.
- `annotation_io.py` generates profile–role pairs, precomputes engineering features/gaps without invoking scoring, exports blind packets and imports explicit reviewer responses. Packet fingerprints protect against accidental context edits. Weak proposals remain separate from gold/exported evaluation rows. Conflicting independent grades are recorded as disagreements, not averaged into invented labels.
- `data_cli.py` supplies the requested `minder-data` equivalents as Python module commands, with no extra service or package bootstrap.

The existing pending worksheet is preserved. Its canonical adapters are in `ml/data/review/phase2/`: three pending roles, 24 pending role crosswalks, an empty skill-crosswalk list, and a generation template. Importance values are not inferred from source scales. No crosswalk was silently approved or applied to narrow-role demand. The empty skill crosswalk means no supplied mapping records, not zero skill demand.

One deterministic [synthetic profile](../tests/fixtures/phase2_profile.synthetic.json) is included for software smoke tests only. It is not a reviewed person or labelled training example. The calibration plan remains five independent families × three roles, followed by possible expansion to 25 × eight when reviewer capacity exists; these are planning targets, not generated gold examples.

## Actual source results

The supplied DOSM release covers 2019-Q3 through 2026-Q2. Its publication/availability date is 2026-08-18, with source retrieval recorded as 2026-10-20 in the original manifest. Availability is preserved at its supplied date precision; historical columns are a revised release vintage, not historical as-of snapshots.

- 952 source rows/cells validated; 921 numeric observations and 31 missing values; zero rejected rows.
- All source observations retain workbook sheet/cell, raw value/status, source version, unit, dates, scope and quality flags. Missing source values remain null, and no missing quarter or annual observation is converted into fabricated quarters.
- The role market view contains 308 records at the published occupation-major-group level. It does not establish demand for the three narrow career-role cards.
- Skill and employer views explicitly return `not_supported_by_sources` with empty record arrays, not numerical zeros. No skill-tagged or employer-level posting source has been acquired.
- Economic-activity and occupation tables remain separate marginals. No industry × occupation or country × skill × employer tensor is synthesized.
- The economic-activity unclassified count moves from 49,549/626,861 in 2026-Q1 to 273,024/555,509 in Q2. This is a classification-coverage diagnostic, not an explanation of the change. The 23 economic-activity rows in Q2 carry a review flag; their YoY comparisons are withheld pending continuity review.

The source XLSX SHA-256 is `965f2f20bcb33425eb43eac7f9edfcff186e7fa92048b8b26f8ee8bbe5d25764`; the supplied derived CSV SHA-256 is `0c82e184e67090b941a8921d9c3604fd291e6cc9c51ea48827c57dc9891ef41b`. Both remain unchanged. The original manifest retains attribution and the unverified attachment-specific reuse terms; code/schema approval does not approve those terms.

Actual permitted comparison: published Managers observations for 2026-Q2 (87,950) versus 2025-Q2 (48,864), from the same source vintage, geography, window type, metric and coverage. The report records the calculated YoY and the observed share using the published 2026-Q2 total of 555,509. Annual/quarter mismatch, an explicitly hypothetical incompatible-country/provider fixture, and actual separate industry/occupation marginals are rejected. The hypothetical rejection fixture is not an observation about another country's market.

## Exact commands and frozen outputs

Run from repository root in the existing `ml/.venv` environment:

```sh
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.data_cli inspect
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.data_cli prepare
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.data_cli validate --snapshot ml/data/snapshots/b98b3798cd3034e4c5f41637
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.data_cli market-build --snapshot ml/data/snapshots/b98b3798cd3034e4c5f41637
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.data_cli annotation-export --output ml/artifacts/phase2/review-v1
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.data_cli annotation-import --packet ml/artifacts/phase2/review-v1 --responses ml/artifacts/phase2/review-v1/responses.template.json --output ml/artifacts/phase2/review-import-v1
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence.data_cli report --snapshot ml/data/snapshots/b98b3798cd3034e4c5f41637 --review-results ml/artifacts/phase2/review-import-v1/readiness.json
PYTHONPATH=ml/src ml/.venv/bin/python -m minder_ml.intelligence checks
```

Snapshots are ignored generated outputs under `ml/data/snapshots/<content-id>/`; review runs are under the already ignored `ml/artifacts/phase2/`. Repeating identical inputs/configuration reuses the identical snapshot ID and output hashes. A changed source manifest, bytes, schema or declared pipeline version produces a new snapshot identity. Existing frozen files are checked, never overwritten. Use `--pack` to select another acquired source pack using the same documented DOSM structure/manifest; no refresh performs model training, international scraping or schema invention for unsupported source dimensions.

The snapshot contains the canonical `observations.jsonl`, source/checksum manifest, quality report, derived views and output hash manifest. Export produces `packet.json`, a blank response template, an explicit review manifest, and separate engineering inputs/features. Give initial graders only `packet.json` and a **copy** of the response template. Do not expose engineering feature files, baseline outputs, weights or rankings. Initial reviewers fill actual IDs, rationale, time, independence and grades only when the underlying requirements/profile evidence are ready. Give each independent judgment a unique annotation ID; retain original votes and separate adjudication of disagreements.

Import preserves pending grades as null, logs weak proposals/disagreements/unresolved cases, and writes only eligible independent human judgments with complete approved requirements/features to `foundation_annotations.csv`. That file uses `profile_family_id` as the existing `profile_group_id`, preserving family isolation for the established grouped evaluation workflow. No automatic role acceptance, script assertion or LLM output is a human review. Local file hashes detect accidental edits, not maliciously rewritten provenance.

## Gates and next dependencies

| Gate | Result | Actual evidence / remaining dependency |
| --- | --- | --- |
| P2-0 Contract | PASS | Six entity schemas, canonical enums/null rules and semantic validation exercised by focused tests. |
| P2-1 Source ingestion | PASS | 952 workbook-cell round trips, source checksums/provenance, missingness and methodological exceptions recorded. |
| P2-2 Comparability | PASS | Permitted within-series YoY/share; incompatible annual, coverage/geography and separate-marginal comparisons rejected. |
| P2-3 Review readiness | PASS | Blind export/import works for three pending roles and one synthetic draft family; 0 approved roles, 0 approved families, 0 gold labels, 3 unresolved pairs. This is engineering readiness, not completed content review. |
| P2-4 Meaningful baseline inference | BLOCKED | No approved role cards. The smoke profile produces explicit pending-role reasons, null unestablished features/coverage and per-criterion gap/source records. No meaningful role ranking is reported. |
| P2-5 Repeatability/integration | PASS | Same snapshot/output hashes on rerun, frozen tampering rejected, old sources/evidence preserved, scoring JSON schema remains compatible. Python interfaces tested; HTTP/frontend not exercised. |

The evidence JSON owns the final exact test count and command outputs. Tests with fictional approval/reviewer flags run only in temporary software fixtures; they are not real labels or review evidence. No existing trained model or frozen empirical holdout was present; the repeatability test additionally checks an unchanged holdout sentinel. Existing annotation templates and earlier evidence remain unchanged.

Repository-wide `git diff --check` reports a pre-existing trailing space at `ml/src/minder_ml/intelligence/training.py:17`. That file's checksum matches the Phase 2 starting snapshot. It is left unchanged under the task-only constraint; Phase 2 new/modified files pass their separate whitespace check. This hygiene exception is recorded separately from the engineering gates.

Next dependencies within the handoff are substantive human review of milestones/criteria/mappings/effort/rubrics, then independent calibration grading and ambiguity resolution. Skill/employer views need appropriate authorized, attributed posting sources before they can become supported. RunPod learner machinery and reviewed-label evaluation remain pending from the previous phase; neither is attempted or claimed by this data-only task. No new provider, training, model fitting, forecast, scalar market policy, commit or push is performed.

Retained source notes: [DOSM Q2 2026 JMI](https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-q22026), [OECD posting comparability research](https://www.oecd.org/en/publications/how-well-do-online-job-postings-match-national-sources-in-large-english-speaking-countries_c17cae09-en.html), and [ESCO downloads](https://esco.ec.europa.eu/en/use-esco/download). These references are retained from the handoff; this task uses the supplied immutable source pack rather than claiming a new acquisition or review of external material.
