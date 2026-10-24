# G2-P — implement Groq chat safely alongside catalogue repair

Copy this entire prompt into a new Codex session. It first establishes a separate
working directory and then implements the LLM layer. This parallel variant
supersedes the original G2 prompt's generic overlay-merging instructions.

```text
GATE G2-P — PARALLEL GROQ CHAT IMPLEMENTATION

Implement the LLM chat layer in the existing Minder project while another Codex
session repairs the ML catalogue. Do not wait for G1A-R, G1B, independent labels
or trained learners. The existing typed result, including unscored results, is
the integration boundary. Finish implementation and relevant checks; report
actual live/API/UI evidence separately.

FIRST: ISOLATE WORK AND INSPECT
Read applicable AGENTS.md, repository status, current recommendation contracts,
backend/frontend layout and these policy files:
- ml/docs/MINDER_POLICY_REVIEW_v1.md
- ml/docs/MINDER_APPROVAL_SUMMARY_v1.md
Read the existing G1A report if available. Do not duplicate policy documents,
merge another overlay, edit approval records or reimplement scoring.

Use a separate Git worktree/branch or an explicitly isolated copy of the current
project. If launched in the ML session's directory, perform read-only inspection
there, prepare the separate working directory, and direct all implementation
writes/commands to it. Do not switch/reset/stash the other session's work.

A new worktree from HEAD will not contain uncommitted G1A changes or untracked
policy files. Inspect that difference. Establish the agreed current source and
contract snapshot in the isolated workspace using a recorded nonsecret patch/
copy when necessary; do not silently commit another person's changes. Preserve
file hashes and identify inherited changes versus this gate's edits. Exclude
credentials, environment directories, bulky generated artifacts and dependency
trees from any snapshot copy. Use an isolated environment and nonconflicting
local port. Read original project files only when needed; never write there.

OWNERSHIP
Own the Groq adapter, chat service/context/reply types, chat endpoint and the
necessary existing frontend chat hookup. Add required backend dependencies only
in this isolated change and document shared lockfile changes for integration.
Keep ml/src/minder_ml/intelligence/, catalogue data, annotation files, scoring
configuration, policy documents, AGENTS.md and existing recommendation schemas
read-only. Use chat-local adapters/types for compatibility. No new auth system,
second backend, agent loop, model training, root architecture rewrite, merge into
the actively edited workspace, commit, push, publishing or unapproved spending.

IMPLEMENT
1. Reuse backend settings, session/ownership checks, saved result retrieval and
   the existing frontend API client. Add the thinnest persistence/service adapter
   only when a real required boundary is absent. Freeze the currently consumed
   recommendation shape and record its version/hash.
2. Add one shared async Groq adapter, configured initially with
   model=openai/gpt-oss-20b, base_url=https://api.groq.com/openai/v1 and server-side
   GROQ_API_KEY. Reuse a suitable installed SDK. Verify current official provider
   model/API support. Respect the supplied total deadline, retry, token and
   concurrency budgets. Never print credentials or put them in browser code.
3. Build bounded authorized context from saved recommendation state, synthetic
   profile, actual role/milestone facts, known gaps/unknowns and allowlisted
   evidence IDs. Scores/source URLs remain canonical backend data. Reject client
   attempts to substitute numerical results, ownership or policy instructions.
4. Support BOTH scored and insufficient-information results from day one.
   When all roles are unscored, explain the available facts and score limitations;
   do not invent a ranking or numerical fit. Distinguish missing user answers
   from missing internal catalogue evidence: ask a focused user question only
   when the answer is genuinely something the user can supply. Backend catalogue
   gaps are not a request for the user to author occupational requirements.
5. Reconcile the structured reply contract in the chat layer. Start with a
   server-assembled context and a structured final response without tool calls.
   Validate schema, IDs, evidence scope, ownership, freshness and permitted
   proposed actions. Use bounded repair or explicit failure. Do not permit
   authoritative score changes, invented courses/roles/stats, mastery claims
   from unchecked tasks or silent profile/plan mutations.
6. Wire the existing chat UI to the actual endpoint if present. Render canonical
   scores/evidence separately from generated explanation, provider/model and
   useful missing-information states. An existing recommendation remains usable
   when the provider fails. Avoid unrelated frontend changes.

CHECKS AND COMPLETION
- Exercise the actual HTTP endpoint with an insufficient-information result
  from the present ML interface; test a scored response separately with a clearly
  synthetic fixture if no eligible real-role result is available yet.
- Check invalid citation/action IDs, stale versions, ownership, provider failures,
  deadline/retry behavior and unchanged authoritative numerical state.
- Exercise the existing frontend hookup where available. A fixture is not proof
  of real scored-recommendation integration. Report that final dependency.
- Make one bounded live synthetic provider call if a key is already configured
  for this isolated session. Otherwise finish code/checks and return the exact
  GROQ_API_KEY setup location and runnable live-smoke command. Ask for no key
  in chat. Record live_not_exercised when no live request happened.
- Write G2_P_report.md and G2_P_evidence.json following existing gate conventions.
  Include worktree/base snapshot, owned files, inherited versus new changes,
  dependency/contract impacts, actual commands, API/UI/live statuses, and a short
  integration checklist for after the parallel catalogue repair completes.

STOP AFTER THIS GATE
Return working chat implementation and evidence in the isolated workspace.
Do not alter ML calculations to make chat work or claim that partial catalogue
readiness blocks all LLM engineering. Do not claim grounded numeric ranking is
fully demonstrated until a valid real-role result passes the integration check.
```
