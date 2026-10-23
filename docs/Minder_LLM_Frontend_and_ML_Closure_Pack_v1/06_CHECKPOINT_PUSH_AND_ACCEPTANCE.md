# Checkpoint publication and finite closure

## Authorised publication scope when Junhong sends these task prompts
A coordinates publication of the existing local A/B/C branches.
Publish the specifically named current snapshots first, then the tested committed handoffs produced
by the bounded A/B/C tasks in this pack. Do not extend this to unrelated work or branches.

Initial snapshots:
| Branch | Commit |
|---|---|
| session/a-personal-integration | 5e24f831141a417d7d7986cbffcb0cda55341d6b |
| session/b-market | 020bbcf8511aa89064b7f232723afa01cf99a427 |
| session/c-app-agents | fe78c8429374d4d9748837ee9f2c94ab573c56e9 |

This authorises normal Git pushes, not force-push, squash, amend, branch deletion, main merge,
release tagging, deployment, billing change, public data publication or paid compute.
Preserve previously approved operations; do not ask for the same Git permission each phase.

Each future handoff gives A a full SHA and named phase. A captures that SHA and pushes the snapshot.
Do not make an unbounded moving branch tip the publication scope.
B/C can continue local work during an earlier push; they do not independently race A's publication.

F (and remote D/E where already assigned) may publish tested task-scoped commits to their own
assigned feature branches so A can fetch them. They must not push the A/B/C branches or main.
Record branch ownership before publication. Local lanes may instead use A as publisher.
This clarifies the practical remote handoff; it does not grant a lane rights to another lane's work.

## Checks before push
- Verify intended remote, source commit, destination branch and clean ownership of the commit.
- Inspect new outgoing history for credentials, private data and restricted artifacts without
  printing sensitive values. Reuse previous scans for unchanged history; inspect the delta.
- Do not stage 13 preserved untracked inputs, local secret files, private database files or ignored
  generated artifacts merely because a push is due.
- Normal push only. If remote already contains the snapshot, report that verified state.
- If remote has diverged, do not rewrite it; preserve work and report the exact relationship.
- Verify the remote SHA/ancestry after publication.

Push transfers existing commit history; individual checkpoint commits do not need artificial
reconstruction or a separate push each. Preserve meaningful phase history.

## Commit discipline
One completed bounded phase -> one checkpoint, with its implementation and evidence.
One bounded correction -> a separate refinement referencing its parent phase.
No empty code changes to create a milestone. A report-only commit must record a genuine new result.
Never commit another active worktree's files/index. Isolated branches/directories remain mandatory.

## Closure record
For each handoff:
- owner, base SHA, full committed SHA, dependencies;
- actual files/capabilities changed;
- tests and environment, separating mocked/live/synthetic/real evidence;
- runtime model, policy, dataset and contract versions;
- remaining limitation and the affected feature;
- local working-tree state and preserved inputs;
- remote branch/SHA, or exact push blocker;
- deployment and paid-run status.

Do not infer model quality from test totals or convert a simulation score into a claimed percentage
accuracy for career outcomes.

## Bounded acceptance
A: credentials work in A runtime; C bridge integrated; real provider/tool/scheduled/source paths
tested; public contract and remote starting point available; versions and limitations recorded.

C: actual contracts exported; A's new types grounded correctly in representative cases; overbroad
claims rejected; existing permission and privacy controls retained; committed handoff published.

B: reproducible isolated simulations, measured baseline/Ridge/XGBoost experiments, split/label
lineage, no contamination of real evidence, honest model/data card and RunPod-ready specification.
Real forecast availability remains a separate unresolved capability if data are absent.

F: intended frontend performs real chat, source display, direct action and proposal approve/reject,
then shows persisted state after refresh. Tested actual backend SHA and evidence are recorded.

Whole product: D/E non-LLM work, integrated preferred UI, deployed storage/auth/scheduler, and
submission artifacts remain separate release work. Closing an A/B/C local scope does not silently
declare these complete.

## Decision discipline
Continue routine work and fixes within scope without repeated confirmation.
Only pause the action that actually depends on a missing product/data/spend/publication decision.
Name the exact missing item and continue independent work.
A failed source search is not fixed by generating fictitious official observations.
A missing API key binding is not a reason to redo model training.
