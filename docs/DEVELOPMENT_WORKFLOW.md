# Development workflow

**APPROVED workflow update: R0, 22 October 2026.** This replaces the active historical no-commit execution rule; it does not retrospectively authorize old actions or approve proposed product/ML decisions.

1. Inspect the current task, AGENTS, Git state, worktrees and existing evidence. Preserve other sessions' work. Use a coherent task branch; do not rewrite shared history.
2. Before staging in the same checkout, coordinate a brief writer pause. If no coordination channel exists, compare source/index/HEAD hashes across a bounded snapshot; retry at most three times and request a pause only if changes persist. Isolated worktrees may continue.
3. Review source and untracked paths, scan for sensitive content and explicitly stage intended files. Preserve original index/diffs and safe uncommitted source privately when recovering mixed work. Keep secrets, real personal data, dependencies and bulky artifacts out; report excluded state honestly.
4. Run relevant available checks. Do not invent application/CI checks. A clearly labeled WIP recovery commit is permitted despite unavailable or failing unrelated checks; report limitations and do not infer gate acceptance.
5. Commit coherent authorized changes using the existing Git identity and actual current time. Report the SHA, scope, checks, outstanding dirty state and inherited attribution. Never fabricate historical gate commits or backdate checkpoint authorship.
6. Push only under applicable user authorization to the verified intended remote/branch. R0 authorizes its recovery backup; it does not authorize arbitrary future pushes, force-pushes, visibility changes or deployment. Report observed remote refs rather than assuming a backup succeeded.
7. Seek review before integration. Integration method remains a team decision. Retain historical numerical policy, source/provenance distinctions, reports and human-review records.

Historical Task 001 scope and individual execution prompts remain history. Their blanket no-commit/no-push wording is retired only where the current R0/user authorization supersedes it. Replit/RunPod rules and actual credit/spending checks remain unchanged.
