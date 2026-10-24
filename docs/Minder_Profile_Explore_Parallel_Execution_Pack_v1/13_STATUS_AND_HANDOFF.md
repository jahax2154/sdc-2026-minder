# Phase status and handoff template

Each owner reports a concise, evidence-based status after meaningful checkpoints. Avoid repeated 'all tests passed' updates with no capability or dependency information.

## Required fields

```text
Lane / branch / worktree:
Phase ID and purpose:
Refines phase, if applicable:
Actual base and dependency SHAs:
Implemented behavior:
Files owned/changed:
Contracts/migrations changed:
Verification performed and actual result:
Fixture vs real API/provider/source checks:
Capability status: passed / limited / blocked
Exact remaining blocker and affected operations:
Next independent work that can continue:
Local full commit SHA:
Push status and verified remote SHA:
Integration status and consuming owner:
Deployment status:
```

For real missing decisions, state the question narrowly, consequences of each option and safe current behavior. Do not treat routine code organization as a product decision or repeat an authorization already granted.

## Handoff content

- Immutable full SHA(s), not just 'latest branch'.
- Contract and schema revision, setup/start/test commands, any migration order.
- Actual supported capabilities and limitations.
- Required configuration variable names with placeholders only.
- Reproducible permitted input/artifact provisioning; no hidden dependency on untracked Mac files.
- Source/data provenance and any reuse restrictions.
- Specific integration steps or ownership requests.

## Final combined status matrix

Use one row per capability, for example Profile persistence, Career Match view, Tasks/Progress, Roadmap & Skills, resource feed, Minder chat, Mindbots actions, background operation, future forecast and intended frontend.

Columns: implemented; meaningful checks; committed SHA; pushed SHA; integrated SHA; user-visible limitation; remaining dependency.

Do not give a precise overall completion percentage without an agreed weighted scope. Report implemented product journeys separately from data coverage, empirical model validity and public deployment.
