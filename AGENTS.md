# Agent entry point

Minder is the provisional SDC Hackathon 2026 career decision-support prototype. Execute only the user's current task; preserve unrelated work and inspect Git status, branch and applicable instructions first.

Read [scope](docs/FEATURE_SCOPE.md), [architecture](docs/ARCHITECTURE.md), [technology decisions](docs/TECH_STACK_DECISIONS.md), [decision log](docs/DECISION_LOG.md) and [workflow](docs/DEVELOPMENT_WORKFLOW.md) as relevant. The canonical [intelligence policy](ml/docs/MINDER_POLICY_REVIEW_v1.md) and its [approval summary](ml/docs/MINDER_APPROVAL_SUMMARY_v1.md) retain their numerical definitions and approval distinctions. Gate reports are execution evidence, not automatic product or human-label approval.

## Active workflow — APPROVED by R0, 22 October 2026

- R0 explicitly authorizes present-time local recovery/checkpoint commits and a backup push on a recovery/feature branch to the verified existing official team remote. It supersedes historical blanket no-commit/no-push execution restrictions for these actions.
- Future authorized engineering tasks should commit coherent, reviewed task changes and report the actual SHA. Label incomplete work honestly as WIP. Do not invent historical gate commits, authors, dates or passing results. Follow any newer explicit user restriction.
- R0's push authorization is for this recovery backup. Other pushes require applicable user authorization; commits do not imply authorization to deploy or publish.
- Before staging in a shared checkout, coordinate writers or verify a stable bounded snapshot. Preserve the index, diffs and safe untracked source privately. Do not kill processes or discard another session's files.
- Explicitly stage reviewed paths. Keep credentials, real personal profiles/CVs, environments, caches, databases, model weights and bulky artifacts out of commits/exports. Itemize excluded local state and whether it is actually backed up. Do not conceal legitimate source with new ignore rules.
- Preserve attribution and historical reports. Separate contemporaneous logs from present-time summaries. Passing tests are not a prerequisite for an honestly labeled recovery checkpoint; report checks actually run.
- No history rewriting, force-push, repository visibility changes, unapproved spend or app publishing/deployment. Do not change scoring, train models or repair unrelated defects during R0.

The initial Task 001 scaffolding-only limits and old gate no-commit prompts describe those historical executions; they are not the active commit workflow. Other numerical, data-provenance, label-independence, runtime-budget and scope policies remain in force. Do not treat generated judgments as independently reviewed labels.

## Active parallel execution — G0, 23 October 2026

Read [canonical D01–D09 revision 5](docs/MINDER_AI_ML_DECISION_CONTEXT.md), [execution handbook](docs/Minder_ML_AI_Layer_Execution_Pack/00_EXECUTION_HANDBOOK.md), and [phase checkpoints](docs/Minder_ML_AI_Layer_Execution_Pack/07_PHASE_CHECKPOINT_RULES.md). These supersede conflicting product meaning and old push authorizations; retain compatible technical policies and historical reports. Local coherent phase commits are mandatory. **Do not push to any remote without a later explicit instruction.**

G0 ownership/contracts and lane launch records live under `docs/execution/parallel/`. Follow its path ownership before editing shared files. Initial role fit is distinct from legacy milestone preparation; pending numerical replacements are not approved policy. Session A owns integration/shared schemas and dependencies, B market internals and paid RunPod execution, C backend/UI/provider/persistence. No duplicate paid jobs or shared live database writes.

## Active product lanes — P0, 23 October 2026

Current product ownership/commands are docs/execution/product-v2/OWNERSHIP.json
and LAUNCH.md, supplementing compatible A/B/C historical records. A owns central
registration/public contracts; D alone owns new product migrations and transferred
profile/plan state files; E owns separate read/content adapters; F owns
apps/frontend-product (not the acceptance UI). G remains inactive until a committed
F foundation and exact page transfer. Preserve the verified Qwen provider profile.
Use only assigned lane DB/ports/outputs. Integrate committed handoffs continuously;
reserve the final50minutes for acceptance/repairs/handoff. Current user authorises
normal tested task-scoped commits/pushes to assigned branches, never main/force/
deployment. D/E/F publish their own branches; A publishes integrated A snapshots.

## Targeted chat/Mindbots repair — 24 October 2026

The current user assigns A-R1/A-R2/A-R3 backend chat routing, verified conversation
policy, public contract and product HTTP concurrency to A. See product-v2/OWNERSHIP.json
and CHAT_REPAIR_CONTRACT.md. The legacy C chat.py entry is transferred to A for
this bounded repair; C retains factual grounder/provider adapter/actions/worker,
D migrations and F every frontend file. Integrate only committed F handoffs.
Keep qwen/qwen3.8-27b, source/scoring/action/privacy boundaries, isolated databases
and read-only inputs; no main merge, history rewrite, deployment or paid job.
