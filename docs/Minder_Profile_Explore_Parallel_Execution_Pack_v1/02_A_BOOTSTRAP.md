# A — bounded bootstrap for product lanes

Incorporate this after the current bounded operation; do not cancel an in-progress merge, reset the branch, or restart completed closure phases. Give the new lanes a usable base early while continuing your existing integration responsibilities.

## P0.1 — inspect current implementation and reconcile scope

Read canonical context, existing AGENTS instructions, current ownership, this pack and latest committed handoffs. Start from the actual current integration tip. Reported historical reference is A I4.7 `5e24f831141a417d7d7986cbffcb0cda55341d6b`, already including B `020bbcf8511aa89064b7f232723afa01cf99a427` and C `fe78c8429374d4d9748837ee9f2c94ab573c56e9`; newer work may exist. Inspect ancestry rather than reverting or integrating those again.

Inventory real stack, entry points, UI roots, auth/session behavior, domain services, schemas, migrations, scheduler/provider settings, dependencies and generated artifacts. Map each product requirement to an existing implementation, a partial implementation or a missing capability. C already built profile/persistence/plans/actions; reuse them.

Record whether product UI is separate from the acceptance UI. Locate actual design assets without pretending screenshots are source code. Preserve the existing LLM/ML work. Commit the meaningful inventory/scope binding as P0.1.

## P0.2 — bind contracts and ownership

Publish under `docs/execution/product-v2/`:
- `CAPABILITIES.md`: actual code/operation for every required capability, with owner and status.
- `CONTRACTS.md` plus machine-readable schemas/validated examples using the existing stack. Bind `07_DATA_AND_API_CONTRACT.md` to real paths and names. Existing operations are exported; missing additive operations are designed to existing conventions before consumers implement them.
- `OWNERSHIP.json`: exact allowed/forbidden paths and sole writers of shared files. No unresolved placeholders for a lane being launched.
- `DECISIONS.md`: reversible defaults, true unresolved decisions and affected scope.

Reserve central backend registration and public-contract coordination to A unless explicitly transferred. D becomes sole author for new product migrations and assigned persistent state changes only after recording a handoff from C/current owner. C retains provider/grounder/action orchestration and uses the same state service. If one physical file overlaps, serialize its ownership.

E owns separate product read/adapter files, not B acquisition/scoring files or D schema. F owns the frontend shell/client/routes/shared styles. Package manifests/lockfiles have one writer per package; assign the actual package owner. G remains inactive initially.

For new additive contracts, E/D may author schemas within owned modules; A reviews/publishes the shared contract, avoiding multiple independent contract authorities. Do not freeze every implementation detail or postpone all work until every field is perfect. Stabilize the first vertical slice, then make compatible additions with dependency notes.

Commit P0.2. If separate-file ownership cannot be achieved cheaply, record serialized backend mode and give D both D/E scope; do not create a second backend.

## P0.3 — create verified launch state

Create or verify D/E/F worktrees from the committed product base. Suggested branch names, subject to existing branches:
- `session/d-profile-state`
- `session/e-explore-resources`
- `session/f-product-frontend`

Suggested sibling directories are session-d, session-e and session-f under the existing worktree parent. Never overwrite an existing directory/branch. Remote teammates use separate clones and assigned branches. Record actual paths rather than asking Junhong to infer them.

Inspect existing A/B/C ports and reserve distinct ports, database files/schemas, logs, worker state, uploads and generated outputs. No copy of another lane's complete environment file or real-user DB. Provider secrets remain backend-only; reuse authorized credential access only where actually needed.

Publish `LAUNCH.md` containing exact absolute directories, branch/base SHA, prompt paths, contracts, ownership, assigned runtime resources and actual start/test commands. Publish `TEAM_START.md` for remote clone/setup with placeholder config names.

Make code and required documentation available through the authorized normal feature-branch push. Verify the remote contains the starting SHA. Account for untracked source inputs and ignored model artifacts: use permitted reproducible downloads/checksums or explicitly isolated development fixtures. A Git clone alone will not contain untracked inputs or make Mac localhost reachable.

Check a fresh/disposable setup can follow the documented path. Do not provision paid infrastructure or deploy merely to launch the lanes. Commit P0.3, then bring the completed bootstrap/documentation commit into each still-clean D/E/F branch before releasing it for application edits. Use a normal fast-forward where ancestry permits; preserve any pre-existing work and coordinate if a branch is not clean. Verify the pack, LAUNCH.md, contracts and ownership are readable from every session directory. Report each final starting SHA in the bootstrap response; do not try to embed a commit's own hash inside that same commit. Publish the launch-ready table and let D/E/F proceed immediately.

## Continuing integration

Follow `09_INTEGRATION_ACCEPTANCE.md`. Publish contract updates and small usable backend slices as they arrive. C's missing design clarification can be one short follow-up; it is not an instruction to stop C's backend work.

Do not absorb all feature implementation into A. Request scoped fixes from the owning lane and integrate their committed results. Preserve the ongoing B forecast/evaluation limits separately from product feature acceptance.
