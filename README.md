# Minder — SDC Hackathon 2026

AI-powered career pathway decision-support system. Minder is the provisional product name.

Status: Initial engineering setup. **PROPOSED** architecture; team approval **PENDING**. This repository contains scaffolding and documentation only. No runtime stack is approved.

## Repository

- `apps/web`: Proposed frontend with five product feature boundaries.
- `apps/api`: Proposed backend API with logical domain modules.
- `packages/career-engine`: Proposed shared career matching, decision and scenario computation boundary.
- `ml`: Offline data preparation, training experiments and evaluation; inference integration remains pending.
- `contracts`: Shared API and integration contracts, pending agreement.
- `docs`: Product and engineering documentation.
- `tests`: Cross-boundary integration, contract and end-to-end test placeholders.
- `scripts`: Future development utilities.
- `.github`: Collaboration templates; no CI jobs configured.

Start with [feature scope](docs/FEATURE_SCOPE.md), [architecture proposal](docs/ARCHITECTURE_PROPOSAL.md), and [pending technology decisions](docs/TECH_STACK_DECISIONS.md). Agents should read [AGENTS.md](AGENTS.md). See [development workflow](docs/DEVELOPMENT_WORKFLOW.md) for proposed contribution conventions and [decision log](docs/DECISION_LOG.md) for approval status.
