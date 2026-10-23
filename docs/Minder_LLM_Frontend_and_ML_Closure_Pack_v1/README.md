# Minder — LLM frontend and ML closure continuation
Version 1. Prepared 23 October 2026, Asia/Kuala_Lumpur.
Deadline supplied by Junhong: 25 October 2026, 08:00 Asia/Kuala_Lumpur.

## Purpose and authority
Continue the existing work. This pack narrows the immediate work to:
- pushing meaningful committed checkpoints;
- binding the working Groq credential into A's isolated runtime;
- enabling C's grounder to consume A's new evidence types;
- exporting the actual API contract for Minder/Mindbots;
- building those product frontends;
- adding a bounded, explicitly synthetic ML experiment without inventing market evidence.

It supplements Minder_Product_Execution_Pack_v1. Existing D/E ownership and shared-backend rules
remain applicable. It does not relaunch their work or reopen scoring decisions.
The author used Junhong's latest reports, not an inspection of the live Mac repository.
Exact public API paths and payload fields must be exported from code by C and accepted by A.

## Latest reported state
Remote checkpoints verified by A:
- A session/a-personal-integration: a0349bcccf5923c65919727279c3a137dcda519f
- B session/b-market: 90ebdf1b0d3144cfd2467abe4b3f66693d7e2bc7
- C session/c-app-agents: 144a10d54f5b632388c7a64a78e9faa08c4d70e5

Later committed local checkpoints to publish:
- A: 5e24f831141a417d7d7986cbffcb0cda55341d6b
  Includes I4.6 3b62a9a705d3a0a46cbc7d7b340702a312ee1a99 and
  I4.4-R01 42a996e17144e48a0fcb47679fa56b1da63d5ea6.
- B: 020bbcf8511aa89064b7f232723afa01cf99a427
- C: fe78c8429374d4d9748837ee9f2c94ab573c56e9
A reports these B/C deliveries already integrated. Inspect ancestry before further integration.

The same anchored synthetic example profile yielded:
910 personally assessed; 5 activity comparisons; 7 related shortage-group contexts;
0 exact whole-role shortage designations; 907 sector contexts; 900 personal-only ranks.
Counts overlap. Three activity comparisons use category proxies; two use employer observations.
These counts are neither an independent evaluation nor universal coverage for every user.

200 ML, 42 backend and 3 runtime-isolation checks were reported passed.
A's real Groq/native-tool/scheduled/privacy-browser checks remain unrun because its key is absent.
C's existing grounder supports Bosch derivations; the new passage types need a focused bridge.
Forecasts remain unavailable; independent forecast fits/evaluation and RunPod usage remain unproven.

## Launch sequence
1. Put this folder under docs/Minder_LLM_Frontend_and_ML_Closure_Pack_v1.
2. Send A its prompt from 07_LAUNCH_PROMPTS.md. It pushes the named checkpoints immediately,
   then resolves its credential binding and coordinates the current closure.
3. Send C its prompt. Its first useful delivery is the API contract export; its focused code work is
   the new evidence-type grounding bridge. This is additional work identified by A, not a repeat of C4.1-R04.
4. Send B its prompt. Reuse the existing synthetic harness and add only identified missing scenarios.
5. Send the frontend owner F its prompt. Source/design work can proceed while C exports contracts.
   Real API wiring waits only for the specific bound contracts, not for historical forecast data.
6. D/E can continue other feature work in separately assigned files from the original product pack.
   No second agent edits F's shell/client/styles or the same backend models/migrations.

## Read order
- All: README, 05_SYNTHETIC_DATA_POLICY.md, 06_CHECKPOINT_PUSH_AND_ACCEPTANCE.md.
- A: 02_SESSION_A_CLOSE_AND_PUSH.md.
- C: 03_SESSION_C_EVIDENCE_AND_CONTRACT.md plus frontend context.
- B: 04_SESSION_B_SYNTHETIC_EXPERIMENT.md.
- F: 01_MINDER_MINDBOT_FRONTEND_CONTEXT.md.
- Starters: 07_LAUNCH_PROMPTS.md.

When pasted as instructions by Junhong, the push instructions authorize the specifically named
checkpoint publication and subsequent task-scoped tested handoffs, as defined in file 06.
They do not authorize deployment, billing changes, public data release, paid training or unrelated pushes.
