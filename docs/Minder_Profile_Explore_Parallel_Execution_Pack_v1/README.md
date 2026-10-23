# Minder — Profile and Explore parallel execution pack

Version 1 · 23 October 2026 · Asia/Kuala_Lumpur.
User-supplied submission target: 25 October 2026, 08:00 Asia/Kuala_Lumpur.

## Purpose

Complete the product features on top of the existing AI/ML backend: Profile, Career Match, Progress, Tasks, Roadmap & Skills, and News & Trends with relevant resources. Integrate the intended Minder and Mindbots frontend when its design assets arrive.

This is an execution plan, not proof of repository implementation. It was prepared from Junhong's reports and earlier execution packs, not direct inspection of the current Mac checkout. A's first phase binds the plan to actual source files, endpoints, schemas, owners and current commits. Do not replace the existing backend or assume a framework from an older proposal.

## Relationship to earlier packs

- A/B/C continue their active LLM/ML closure tasks. Do not cancel or restart them.
- This pack replaces the not-yet-started D/E/F product scope in `Minder_Product_Execution_Pack_v1` and the abbreviated D/E/F launch instructions in the closure pack.
- It supplements the closure pack's Minder/Mindbots behavior contract. C retains CL1–CL3 and F retains that frontend behavior, with the combined phase IDs in this pack.
- The latest user instructions control. Preserve the active scoring policy; this pack does not approve a new market formula, activate original N01, or convert simulations into real forecasts.
- Existing `AGENTS.md` and the canonical decision context remain the engineering references. Add links to this pack if appropriate; do not create a competing copy of repository-wide instructions.
- The working navigation interpretation is five Explore areas. See `00_PRODUCT_CONTEXT.md`; do not silently delete older Skills, Roadmap or Future Explorer capabilities.

## Start here

1. Extract this folder under `docs/Minder_Profile_Explore_Parallel_Execution_Pack_v1` in the repository.
2. Send A the bootstrap continuation from `11_LAUNCH_PROMPTS.md`. It finishes its current bounded operation, then prepares the new lanes early. Do not wait for A's whole ML/LLM work to finish.
3. D/E/F may read context and inspect available assets immediately. They edit application code only after A publishes their exact worktree/branch/ownership and initial contracts.
4. Launch D, E and F concurrently on those separate worktrees or remote clones. D handles shared persistence; E handles read views and resource adapters; F owns the frontend.
5. F works on Profile/Explore and shared UI while the Minder/Mindbots design is pending. C does not wait for HTML.
6. Add G only if A/F confirm the page-only separation described in `06_OPTIONAL_G_FRONTEND.md`. Otherwise F implements all pages.
7. Integrate small committed deliveries as they arrive. Do not wait for every lane's final phase before the first working user journey.

Copying this folder into one checkout does not automatically place it in the other worktrees. A must commit/distribute the documentation through the normal handoff process and report its availability.

## Read order

Everyone: this README, `00_PRODUCT_CONTEXT.md`, `01_HANDBOOK.md`, `10_GIT_CHECKPOINT_PUSH.md`.

| Owner | Execution file | Supporting files |
| --- | --- | --- |
| A | `02_A_BOOTSTRAP.md`, `09_INTEGRATION_ACCEPTANCE.md` | contracts, ownership, launch prompts |
| D | `03_D_STATE_BACKEND.md` | `07_DATA_AND_API_CONTRACT.md`, evidence/privacy |
| E | `04_E_EXPLORE_AND_RESOURCES.md` | contracts, evidence/privacy |
| F | `05_F_PRODUCT_FRONTEND.md` | contracts, design handoff, original LLM frontend context |
| G, optional | `06_OPTIONAL_G_FRONTEND.md` | F's committed component/client contract |

`11_LAUNCH_PROMPTS.md` contains copy-ready instructions. `12_DESIGN_HANDOFF.md` explains what Junhong supplies. `13_STATUS_AND_HANDOFF.md` defines completion reports.

## Publication authorization when these prompts are issued

Commit each bounded phase and each later refinement separately. Normal pushes of tested, task-scoped checkpoints to assigned feature branches are authorized by the launch prompts. A coordinates A/B/C publication; D/E/F/G publish only their own assigned branches. No force push, main merge, history rewrite, production deployment, new paid service or billing change is included. Preserve other explicit existing authorizations rather than asking again.

The author has not performed any repository push, migration, application test or deployment through this document.
