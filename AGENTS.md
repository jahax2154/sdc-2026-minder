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
