# Functional repair — current integration status

This supersedes baseline failure statuses in A_FUNCTIONAL_GATE_AUDIT.md without
erasing the original observations. It is a local product gate, not hosted proof.

## Completed implementation and measured evidence

- A-FG1 **0a39b392b1f2b594abb8b23a4f0a8f73a4bec0c4**: sourced role display,
  scoped saved-career fallback, independent typed forecast read. Official A
  remote push verified. Full backend168pass. `role-display-v1` preserves19source
  records as10skill groups, no manufactured labels/competence or scoring change.
- A-FG2 **cd6cea3f8aea8f6e6db8cdffcdcccf5359e2ee0d**, linked R01
  **ca8eb2c0c9c57e16b83742bea76839d5ec363486**: committed visible-action/API/state
  audit and genuine fresh UI journey. Both normally pushed. Baseline Compare/
  Skills failures retained; CV wrong-route test error explicitly distinguished.
- A-FG3 **cdd76c20fc77768509b6704e740f4a9d3dd8b6f4** integrates exact F
  **c76fe768603850a7ba647420242420db10914d52**, preserving all prior checkpoints.
  Actual A9111 browser suites functional_connections, functional_action_recovery
  and check_ux_visibility all pass,0modelcalls. Real API reads/concurrent writes;
  only the legacy undated-notice agents read is a controlled fixture. Compare
  labels/distinct measures/outside-first50selection/single-result search/Outlook/
  four no-plan views,409local reload/explicit undo and both old UX failures pass.
  Served Careers/My Path/helper bytes matched this integrated frontend exactly.
- A-FG4 bounded backend explanation repair: `career-explanations-v1` replaces
  raw role IDs, runtime-mode names and comparison-group hashes in human-readable
  context statements with actual catalogue labels and understandable scope.
  Machine IDs/metadata, dates, source verification, unknowns and numerical
  assessments remain. Existing N01-R1 integration ownership covers app_context;
  C grounder/provider and F files are not edited.169backend tests pass7.840s;
  46context/contracts/personal-fit/current-evidence regressions pass3.668s. The new
  regression asserts explanation rendering does not mutate recommendation or
  market calculations. This source change needs restart/current browser proof.

Fresh initial A UI evidence: zero assessed skills gave0/910personal assessments
and3focused questions. Three source-anchored self-reports entered through UI gave
910assessments,5comparable current-market ranks (2employer/3published),900strictly
personal-only;7shortage contexts/0exact-role shortage and907sector contexts.
Real qwen/qwen3.8-27b generated3stages/3tasks, provider1686.540ms;
generation/save/separate activation2127ms. Task completion0/3→1/3 persisted with
the same plan/task definitions and no regeneration. F's independently reported
fresh journey2561ms is separate evidence, not substituted for A's final gate.

## Still being completed — do not claim full integration

F follow-up restores unreachable Interested/Not interested/Reset in active
Careers, Home skill labels, schedule/saved-plan career labels and relevant exact
receipt recovery. Await its exact tested commit, integrate only missing history,
then run A's expanded combined fresh-onboarding journey. It includes actual CV
upload/extract/review/download/delete plus controlled lost-review response,
actual Qwen guidance/unseen follow-up/navigation, Mindbot own-channel action,
daily schedule create/pause/resume/cancel, all four tabs and progress. Evidence
types and any test-selector corrections must stay explicit. F alone edits UI.

Browser credentials were not exported: automatic approval review rejected a
proposed copy of a synthetic browser session to a file. That command did not run;
the safer final journey uses normal browser state without credential extraction.
No test result or application work is discarded. Earlier evidence remains.

## E/runtime/release handoff

Current running backend is0a39b39 at http://127.0.0.1:9111 (API8111), with the
integrated F c76fe76 frontend served from A. The existing private provider is
qwen/qwen3.8-27b, unchanged. No new key/setup/model/build required. A will restart
only its own isolated process after committed integration and record final
backend/frontend revisions. Localhost is not a remote team's backend.

**No approved hosted candidate yet.** E may prepare existing-resource packaging,
but actual Clerk realm/domain/DNS, Railway project/volume access, two real managed
accounts and hosted history/CV/restart/daily checks remain required. Never call
local capability sessions live Clerk or a development realm production. No main
merge, deployment, upgrade, tag, branch rewrite or credential publication occurs
in these repair checkpoints. Draft release PR1 remains the existing candidate PR.

Private local evidence hashes:

| Evidence | SHA256 |
| --- | --- |
| functional-backend-fg4.log |7d31ab0e16f2069d1266aebdd43f64896fddbd5d40121e597ad704be252d705f|
| functional-policy-fg4.log |e125e26f0c866bdb88e62e998f2a4b15226457508c05065281d72e82250c7f16|
| functional-fresh/initial.json |2b240788ea2d8b4c4c5ff068c0378a4fcaa11e4188bc9c814f56b6aa61803c25|
| functional-fg3/functional_connections/functional-connections.json |55d591e1a1b4a8faf2087fd601c2eb801fefba865b92f660c6d993784c40b32f|
| functional-fg3/functional_action_recovery/functional-action-recovery.json |35eac89d485c9c2aacb5aeef5046f502fadd6f1014efffe3c90bd62ca3c8c50d|
| functional-fg3/check_ux_visibility/visibility.json |c3625c4c053af1aafc742435d7c2cc5eb53d1be0c107dbe7c6b3d1fac2a63d5d|

All paths under `ml/artifacts/session-a/product/morning/`, excluded from Git.
Preserved raw/derived inputs, environments, real/private profiles, CVs, DB/uploads,
browser profiles/traces/screenshots and weights are not staged or backed up by
these commits. No historical failed check is rewritten as passing.
