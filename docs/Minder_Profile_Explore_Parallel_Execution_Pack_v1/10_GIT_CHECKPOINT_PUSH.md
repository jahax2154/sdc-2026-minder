# Checkpoints, publication and remote teamwork

## 1. What a checkpoint affects

A normal commit records the staged changes in that worktree and advances its checked-out branch. Linked worktrees have separate working files, indexes and HEADs, while repository objects/references and some configuration are shared. A normal D commit does not stage or commit E's working files. See the official Git reference: https://git-scm.com/docs/git-worktree.

This isolation is not a guarantee against integration conflicts. Two branches can edit the same file or disagree about a schema. Hence one writer per shared file, explicit contracts and A's controlled integration are still required.

Use one active coding session per worktree/branch. Do not point several sessions at the main directory. Do not change another lane's branch, index, runtime database or shared Git configuration.

## 2. Phase loop

For every bounded phase:
1. Verify actual directory, branch, ownership and dependency revision.
2. Inspect existing implementation; reuse work already completed.
3. Implement the phase within owned paths.
4. Run meaningful checks for changed behavior, including the necessary real interface where applicable.
5. Review the diff, secret/private-data exposure and unrelated files. Stage explicit owned paths; preserved untracked inputs are not automatically included.
6. Commit a concrete checkpoint with phase ID and purpose.
7. Record evidence, dependency SHAs, remaining gaps and the exact handoff.
8. Normally push the tested task-scoped checkpoint under the branch rules below, and verify the remote.

Examples: `D1.2: persist partial profiles with evidence attribution`; `E2.1: serve source-linked resource feed`; `F2.2-R01: refresh tasks after approved bot changes`.

Repairs get separate commits and reference the original phase. Do not amend/squash earlier checkpoints or create empty commits just to fill a phase table. A report-only commit is appropriate when it records a meaningful investigation or handoff.

## 3. Branch publication authority

When Junhong issues these execution prompts, tested task-scoped checkpoint commits and normal pushes to the assigned feature branches are authorized.

| Branch group | Publisher |
| --- | --- |
| A/B/C existing branches | A coordinates captured committed handoffs, preserving the prior authorization |
| D | D pushes only its assigned D branch |
| E | E pushes only its assigned E branch |
| F | F pushes only its assigned F branch |
| Optional G | G pushes only its assigned G branch |

A does not simultaneously publish D/E/F/G tips unless ownership of that specific push is handed over. A can merge their committed deliveries into A's designated integration branch and publish that integrated result.

Before a first branch publication, verify the intended remote and any known branch-triggered deployment workflow. Routine CI is expected; production deployment is outside this authorization. If a push would trigger known unauthorized production deployment, resolve the branch target/workflow with the owner or stop only that publication action. Do not silently deploy.

Inspect new outgoing content for credentials/private/restricted files; reuse prior inspection for identical objects. Push the intended committed snapshot. Verify remote containment/SHA. If a remote already contains the checkpoint or a valid descendant, report it rather than rewinding. On divergence inspect and coordinate; no force push.

No main merge, history rewrite, forced update, unrelated branch push, tag, production deployment, billing change or paid job is authorized by these instructions. Previously granted separate specific authority remains valid. Do not ask repeatedly for a push already within this scope.

## 4. Integration while work continues

Producers hand A an immutable full SHA plus dependencies. A inspects ancestry/content and integrates only missing committed work. Do not copy an active worktree's files or broadly merge an unspecified latest tip.

A can integrate a completed phase while its producer works on the next independent phase. If a change needs a shared contract or same-file repair, coordinate at the next bounded handoff. Do not reset, stash or clean another lane to resolve a conflict. Do not delete Git lock files without establishing why they exist and that no active operation owns them.

Default handoff direction: D/E/C/B to A for integration; G pages to F; F's assembled frontend to A. A normally integrates F's commits without editing frontend-owned files. A frontend conflict or correction goes to F, or requires an explicit temporary ownership transfer; integration ownership is not concurrent frontend-writing authority. If a specific shared dependency must reach E/F earlier, A records the exact compatible SHA and adoption method. Avoid repeated indiscriminate pulls/rebases of every branch.

## 5. Remote teammates

They need repository access, an actually pushed base, their assigned branch, actual setup commands, contract examples and permitted data/artifact provisioning. A supplied branch name is not enough if its objects exist only on Junhong's Mac.

Use separate clones and local DBs. Do not share private database dumps or keys through Git/chat. A remote browser or Replit runtime cannot reach Junhong's localhost by using the same 127.0.0.1 address. Run an allowed local backend alongside the frontend or use a deliberately authorized reachable environment.

Commits, pushes, integration and deployment are separate status fields. A locally committed phase is not yet on GitHub; a pushed branch is not automatically merged into the shared application.
