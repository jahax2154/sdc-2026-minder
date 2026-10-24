# F-R3 — client/nonblocking workspace and contract consumer

Status: passed browser client/fault checks; real integrated backend acceptance pending
A's implementation checkpoint. Dependency A6a77d22eeff3aa81b963fdb4506b9ec5cf321479
publishes conversation-routing-v1 contract and measured server bottleneck ownership.
F has not changed backend/provider/grounder/policy/schema. Overview/Explore bodies
remain unchanged. Frontend currently consumes old or reviewed additive envelopes.

Mindbot frame is drawn before profile and ordinary saved-state reads. Proposals,
activity/history/settings load independently, each with explicit empty/error/manual
retry; successful sections survive an optional failure. Opening workspace sends no
chat/job/write. Pending-proposal badge uses actual successful read only. Stale
approve/reject/undo still use exact hash/version/idempotency; success refetches saved
sections. No automatic write retries. Auth failures mask all saved content and clear
transient conversation/notification data. Obsolete route reads are aborted and late
results cannot replace another view. Startup failure has explicit retry.

Read8s/write12s/chat45s deadlines now follow A's committed provider25s maximum bound;
include response body parsing. Prior F-R1 conservative12/30/90 values are historical.
Application guidance renders answer first and is not mislabeled provider outage.
Grounded claims retain their statements/sources; limited fallback is labeled distinctly.
Unsaved Profile sends expected_profile_version:null, no implicit save; follow-up sends
only previous_context_id from the last own response, in active memory, reset New chat.
No browser-authored canned answer or factual grounding relaxation.

repair_workspace.cjs: explicit transport fixtures over real ordinary saved reads,
zero provider calls, passed immediate frame despite rejected optional read69ms;
other sections ready; manual section retry; saved reads during held chat49ms;
no late chat overwrite; unauthorized mask/no badge; read deadline8s compressed100ms
in test only; backend-down startup retry. These are client fixture timings, not real
provider/concurrency claims. F-R3-fixtures.json records them. F-R1 Context/lifecycle
fixture regression also passed with final45s test deadline. Real A backend timing
and fallback checks follow as a separately labeled checkpoint, never inferred here.

Screenshots private /private/tmp/minder-f-repair-mindbot-loaded.png and rail/context
shots. node checks and Git diff --check passed. Initial raw/derived untracked inputs
unchanged/excluded, private config/DB not exported/backed up by this repair.
