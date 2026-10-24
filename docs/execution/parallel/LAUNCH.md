# G0 launch handoff

G0.1 reused recovery code `8fbff9521ef3f48d3ac1eddbdddd3ed25f67a15f` and evidence `cd252e449048f6ffbab6e09663fcd02481682e28`, then integrated the supplied pack at `de89335`. G0.2 contract checkpoint is `d26bd704ee798c0ab4c9522ae66ce2378d2680d9`. G0.3 starting SHA is the commit containing `G0.3.json`; the final verification prints its actual full SHA for all sessions. No reconstructed historical commits.

Canonical context: `docs/MINDER_AI_ML_DECISION_CONTEXT.md` revision5. Pack directory: `docs/Minder_ML_AI_Layer_Execution_Pack/` (actual supplied name). Ownership: `docs/execution/parallel/ownership.v1.json`; contracts and migration: `SHARED_INTERFACES.md`, `NUMERICAL_POLICY_MAP.md`. The pack's context file is a pointer, not another authority. Original pack hashes remain delivery history; canonical revision5 hash matches its original payload.

| Session | Exact directory | Branch | Assigned prompt relative to directory |
| --- | --- | --- | --- |
| A | `/Users/phuahjunhong/sdc-2026-minder-worktrees/session-a` | `session/a-personal-integration` | `docs/Minder_ML_AI_Layer_Execution_Pack/02_SESSION_A_PERSONAL_MATCHING.md` |
| B | `/Users/phuahjunhong/sdc-2026-minder-worktrees/session-b` | `session/b-market` | `docs/Minder_ML_AI_Layer_Execution_Pack/03_SESSION_B_MARKET_FORECASTING.md` |
| C | `/Users/phuahjunhong/sdc-2026-minder-worktrees/session-c` | `session/c-app-agents` | `docs/Minder_ML_AI_Layer_Execution_Pack/04_SESSION_C_LLM_APP_AND_AGENTS.md` |

Open each session in its printed directory. Do not run B/C inside the original checkout. Original `/Users/phuahjunhong/sdc-2026-minder` is parked on `bootstrap/g0-parallel-20261023`; Session A continues in its new worktree on the integration branch. No sessions/services were auto-launched. No optional D ownership assigned.

Each worktree has ignored local `.env.local` with only non-secret reservations. Run `source .env.local`; `$MINDER_PYTHON` points to the existing interpreter read-only and `PYTHONPATH=ml/src` selects this worktree's source. The DB/output paths are unique per lane under ignored `ml/artifacts/session-<lane>/`. Reserved ports are A 8101/9101, B 8102/9102, C 8103/9103. These are local reservations, not running listeners or a selected production database. C wires runtime configuration in its lane. Credentials remain environment-managed and must be configured privately when available; none were copied or committed.

Thirteen existing source inputs are pinned in one read-only physical snapshot (source_snapshot.v1.json). Each lane has read-only hardlinks at its own existing raw/derived paths, so the legacy repository-containment guard still works without code changes. These are intentionally untracked; do not `git add .`, chmod, replace or regenerate them. Source acquisition updates go to the owning lane's new versioned output; coordinate new immutable snapshots with A. Generated outputs/models are lane-owned and never shared mutable state. No absolute imports from another worktree's source are needed.

A owns shared DTOs/root dependencies, personal catalogue/features/learning and integration. B owns market files plus a single RunPod budget ledger and all paid launches, including immutable A jobs. Bootstrap authorises no spending. C exclusively owns app/backend router/migrations/persistence/provider/actions/UI; request shared dependency/schema changes from A. Report/request paths are per lane; do not race on the shared manifest. Integrate actual owner commits locally; no pushes.

Verification: 35 existing foundation tests passed; 12 new contract tests passed, then passed independently in all three worktrees. Existing service demonstrably loads the actual three legacy roles in each and returns honest missing-milestone results (0 scored); reference feature vector still yields 67. Data hashes match all 13 pinned inputs. Contracts validate complete/partial evidence, scoped negative preference, unavailable forecast, no-company-role-found, plan state, direct action and approval-required cases. DTO validation is not actual persisted action execution, an HTTP endpoint or live forecasting/provider success.

Single substantive pending decision: N01 in NUMERICAL_POLICY_MAP.md proposes new occupation-fit/industry arithmetic and keeps market periods separate. Its machine config is explicitly inactive. Do not reuse preparation labels or activate new numerical scores before this meaning-changing policy is settled. Catalogue, intake/feedback storage, market ingestion/forecasting and app/provider/action foundations proceed independently. Human-labelled empirical validity is separate; no labels/approvals were generated.

Live readiness: backend/frontend are placeholders, Groq is disabled, RunPod access/balance and Replit deployment capability are unverified; no HTTP/UI/live-provider or new training success is claimed. G0 is ready for lane engineering, not product launch. No source-data approval or catalogue repair is implied.

Final post-commit verification: run `python3 scripts/check_parallel_bootstrap.py --expected-commit <G0.3-SHA>` after all three tracked-clean worktrees have fast-forwarded to that SHA. Store its output in ignored `ml/artifacts/session-a/g0-launch-verification.json`. The final response includes observed starting SHAs. Tracked files must match the final launch/contract checkpoint. Lane states intentionally include 13 untracked input files and ignored non-secret runtime reservations. The original checkout's reset-v2 pack, large G3 artifact, source files and submission placeholders remain preserved/untracked; no claim of wholly clean repositories.

Push status: not pushed — awaiting explicit instruction. Stop bootstrap after the launch report; next user-issued lane prompts begin A1.1/B1.1/C1.1.
