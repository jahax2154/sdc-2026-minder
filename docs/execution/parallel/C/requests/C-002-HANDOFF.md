# Session C — culminating handoff to Session A

Branch: `session/c-app-agents`. Required directory and bootstrap ancestry verified at start; HEAD was exactly `70dc99e96c51e2da3cacc0b84cdc729b2be33fd9`. No recovery/setup repeated. This handoff's checkpoint is the commit containing this record; the final report supplies its actual SHA. Code/runtime checkpoint: `0966d5cefd1be775a6d461d7cf0efd4af7c90fea`.

C is ready for coordinated local integration, with explicit limited phases below. No successful live Groq, numerical role ranking, empirical forecasting or deployment is claimed. N01 is still pending; no LLM chooses scoring weights. No pushes, deployment, paid RunPod jobs, production changes, history rewriting or writes into other sessions' directories.

| Phase | Final status | Actual behavior / coverage | Original checkpoint SHA |
| --- | --- | --- | --- |
| C1.1 | limited | Groq transport/mock errors verified; real access unavailable | `a9329d61404e6d0630f114ec565ba695a0c78a0b` |
| C1.2 | passed | Persisted intake/profile/version/identity; actual A/B adapter integration verified locally | `5c78d50a2cfb8843209dfdfa9ba5698bd1388614` |
| C1.3 | limited | Grounded facts and real A/B round trip; successful Groq grounding blocked | `b7585632b5801a64d3b920cb2d43bf4f4343382e` |
| C2.1 | limited | Persisted source-gap pathways/tasks/progress; effort/resources unknown | `f49141c738f6df32460a1765f89c717788a084ca` |
| C2.2 | limited | Dated Bosch company summaries; full required/preferred criteria unavailable | `3c7a0c001aba5ff2159373a832b35e6075936ab3` |
| C2.3 | passed | Scoped direct authority, exact proposal approval, rejection, stale checks, retries/undo | `db652c0c1c3ed0f594a98ce05c3c81e9f63124e5` |
| C3.1 | limited | Persisted triggers/daily local worker; deployed unattended scheduling unverified | `184450def8f1c843c4218202c4c8393d7667d3ec` |
| C4.1 | limited | Actual A/B HTTP + Chromium UI flows; provider/deployment limitations explicit | `0966d5cefd1be775a6d461d7cf0efd4af7c90fea` |

Statuses are local C acceptance statuses, not full launch approval. C2.3 passes implemented bounded action tools; arbitrary task-graph replacement/general planning optimizer is not supplied. Original records retain contemporaneous status/check counts; later integration/refinement does not rewrite earlier evidence. C4.1.json records final results. Initial test counts included inherited repetitions; final backend count is 20 distinct tests.

| Refinement | Checkpoint SHA | Focus |
| --- | --- | --- |
| C1.1-R01 | `e2a69d5ee25aaa7b1c0a3e283c5ae5ee8851416b` | Persisted per-user provider budgets shared by chat/worker |
| C1.2-R01 | `badae3681ceaf63b0b0f7e399bc922f28eeeb3c0` | Close SQLite read connections |
| C1.3-R01 | `f7d4536e4aaa75fad51d52d7bc8e2c0fc93d842a` | Bound explicit selected-role chat view and typed skill queries |
| C2.1-R01 | `c7983aac23bcff056c7f731513cbb609b470a7b4` | Source-criterion pathway previews/design annotations |
| C2.1-R02 | `ee9ec7b522ba4ccd7ffb328d1805b4f1c594492e` | Prevent schedule conflicts across saved plans |
| C2.2-R01 | `8cb2acbcce2714b2c0c40b095d967e8420926148` | Official entry link and committed Bosch snapshot reuse |

A/B handoff consumption: local merges `3fc9cbd` (A through A2.1 `745f6af`, including shared schema/ownership and service constructors) and `d2b8dd8` (B1.2 `0b61ede1cb596cff6a0110d80c2a8769e385bd7e`). Owner histories preserved. C did not modify A/B internals or shared dependencies/schemas. Runtime imports committed current-worktree modules only. C-001 is resolved for constructors/catalogue/B market wiring. A's A-001 request for bounded chat/typed skill handling is resolved by C1.3-R01.

Actual verification:

- Backend: 20 distinct unittest cases passed, covering owner isolation, version conflicts, ambiguous intake, prompt injection/hallucination rejection, pending/reject/approve/undo, concurrent idempotent retries, completed/locked work, DAG/overcapacity/overlap, combined-plan conflicts, worker relevance/timezone/dedup/retries, provider budgets.
- Shared contracts 12 passed; mocked Groq transport 5 passed; app-context bounds 1 passed. Integrated A personal tests 11 and B market tests 10 passed. Provider mocks are not real-provider checks.
- Actual HTTP on C ports 8103/9103: persisted synthetic profile → A's pinned catalogue/personal service → B current role AND skill observations → grounded chat availability; explicit unavailable next-quarter role/skill forecasts; source links/date/uncertainty separation; no public internal market matrices; 1,016 references, 910 unranked supported candidates, zero numerical personal scores.
- Real HTTP pathway preview/create/restart-readable SQLite/activity completion and retries, real worker subprocess pending proposal/reject/approve/undo, cross-user rejection. No success notice before committed write.
- Actual Chromium 156.0.8078.4 with real network/API (no route/fetch mocks): profile, CV TXT draft, catalogue selection/preferences/reset, pathway/task/progress, current/future view, chat provider-unavailable, worker proposal approved via UI; zero page errors; 390px mobile layout no horizontal overflow. Screenshot visually inspected. Fixed early UI handler-loss during implementation before C4 checkpoint; final UI preserves listeners when appending cards.
- Final real provider probe returns `provider_credentials_missing`; chat returns `provider_model_not_configured`. Both GROQ_API_KEY and GROQ_MODEL are absent. No credential lookup in other files/accounts, no live call or entitlement/rate-limit verification. Never copy keys into handoff. Official transport docs are linked in C1.1.md.

Sanitized HTTP/browser evidence and artifact hashes are committed inside `C4.1.json`. Original JSON and synthetic screenshot are ignored at `ml/artifacts/session-c/c4.1-*`; no private tokens/profiles in committed evidence. Temporary Playwright/browser under `/private/tmp` provided actual UI checks without root manifests/dependencies. Tests can be reproduced with the committed scripts and an available Playwright library/browser; A may coordinate a dev-test dependency separately if useful.

Integration/runtime instructions:

1. Integrate C's meaningful commits locally preserving owner history; C does not request a push. The backend and UI READMEs give exact commands and API examples. `minder_app.runtime.application()` is the real A/B binding. For A's deployment runtime, coordinate its own namespace instead of weakening C's DB reservation guard or pointing at C's live DB.
2. Migrations are additive: 1 sessions/documents/history/drafts, 2 authorities/proposals/executions/audit, 3 events/notices, 4 provider_calls on first budgeted call. Plan-creation idempotency table is created on first create. No production migration executed. Use one durable database owned by the integrated runtime after deployment coordination.
3. Start C development locally: `source .env.local` then `PYTHONPATH=ml/src:apps/backend-api "$MINDER_PYTHON" -m minder_app.dev`. API 8103, UI 9103; both loopback only. The dev server remains running at handoff. No unattended daemon was launched; worker tests used real bounded subprocess `-m minder_app.worker --once`. Continuous worker command is `-m minder_app.worker`; supervise/deploy and observe actual scheduled runs before claiming unattended operation.
4. Runtime environment NAMES only: MINDER_DB_PATH, MINDER_API_PORT, MINDER_UI_PORT, MINDER_PYTHON, PYTHONPATH; provider GROQ_API_KEY, GROQ_MODEL, optional MINDER_LLM_DAILY_LIMIT; browser test MINDER_PLAYWRIGHT_MODULE, PLAYWRIGHT_BROWSERS_PATH. Daily enable/check_time is versioned user state; timezone is the profile's IANA timezone.
5. Plain chat does not execute actions or accept a bare 'yes'. Direct structured UI/API commands mint a trusted exact server-side authority; inferred/event proposals need exact stored preview hash and relevant expected state version. Workers can only propose; approval/execution/audit/idempotency share one transaction. Completed activity cannot certify mastery. No email/calendar/application tools.

Remaining dependencies/changes, not hidden passes:

- Configure Groq privately, run discovery/select entitled model, then real grounded and agent selection calls. Missing access is the only provider blocker; no invented default model or credentials. Mock/local deterministic reasoning is labelled separately.
- A owns N01 numerical policy; no ranking/weight/model activation until its explicit approved implementation. Current source-grounded assessment and full catalogue remain usable without scores.
- B has a bounded dated Bosch Malaysia active-ad snapshot; no comparable quarterly role/skill history or trained forecast is supplied here. Preserve unavailable states and source scope. C does not substitute zero or national employment claims.
- Company descriptions have official URLs/dates/hashes; company-specific required/preferred criteria and mappings not preserved in B summary. Show generic occupational assessment as generic. Intel entry linkage checked; full role content unavailable. Expand employer coverage through verified official/ATS records, not snippets.
- Pathways currently design up to six evidence-review/practice activities from actual unknown/gap criteria. No verified resource catalogue, effort evidence or competence rubric supplied; no invented mastery/feasibility. Broad optimization and arbitrary plan graph replacement remain explicit limitations.
- Deployment auth/session expiry/recovery, HTTPS/durable storage and actual scheduler supervision/wake/sleep checks are A integration/release work. Local anonymous capabilities are not production identity. No deployment authorised by this task.

Excluded local state: original 13 untracked read-only raw/derived source inputs left untouched and outside commits (already pinned in G0's shared snapshot; no new backup made); ignored `.env.local` reservations unchanged; ignored C SQLite/WAL/runtime evidence/screenshots/caches not backed up or committed; temporary npm/browser binaries under `/private/tmp` not backed up/committed. No new ignore rules conceal source. No intended tracked changes remain after this handoff checkpoint; only preserved input directories should remain untracked.

Next A actions: merge/review C checkpoint, run integration smoke on A's assigned namespace, configure provider if available, then coordinated I2 auth/storage/scheduler/live-grounding acceptance. Do not classify missing provider/forecasts as successful live services.

Push status: not pushed — awaiting explicit instruction.
