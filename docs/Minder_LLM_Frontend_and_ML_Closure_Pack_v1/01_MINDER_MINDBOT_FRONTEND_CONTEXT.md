# Minder and Mindbots — frontend logic context

Status: product behaviour specification grounded in the reported backend. Not a fabricated HTTP API.
C must attach the actual endpoint/payload export described below. F uses that export when wiring code.

## 1. Product boundaries
Minder is the conversational interface: understand the user, explain recommendations/evidence,
answer questions about their path, and accept specific user-requested actions.
Mindbots is the personal-agent interface: show relevant updates, proposed changes, execution results,
and the current automation/job state.
Both use the existing backend, user identity, profile, plan, tasks, evidence and action system.
Do not build another provider client, another task store or a frontend recommendation algorithm.

Use Junhong's preferred standalone HTML design as the main visual reference. Reuse useful Replit
elements after inspecting actual source. Do not replace tested behaviour with a fresh mock-only app.

## 2. Required contract export from C
C writes docs/execution/product/llm/FRONTEND_CONTRACT.md and schema-valid example responses.
For each existing operation document:
- actual method/path and API origin/proxy;
- request and response schemas, IDs/enums and nullable fields;
- authentication/session, CSRF/CORS and ownership behaviour;
- version/idempotency rules;
- synchronous response versus job/stream lifecycle;
- error states and retry expectations;
- policy/evidence version and what is safe to expose;
- implemented/unsupported capability status;
- the exact backend commit against which examples were checked.

Operations to inventory (these are logical names, NOT proposed endpoint paths):
conversation load/create; message send/history; grounded response and source detail;
profile/context summary; proposal list/detail; approve/reject; action/job result;
notifications/agent events; supported automation preferences; approved tool capabilities.

The existing C acceptance UI is index.html/app.js/style.css on 9103 with same-origin 9103/api/*;
the API also listens on 8103. This does not prescribe the final product origin.
F must not hardcode Junhong's loopback address for a remote Replit environment.
No key, private prompt, full CV or internal ranking payload is part of a public contract fixture.

## 3. Shared interface foundation
Use the chosen project stack and existing session/client logic.
Build shared components for:
- plain-language grounded answer;
- source entry/detail;
- insufficient-data/provider-error state;
- proposal changes with approve/reject;
- pending/completed/failed action;
- notification/activity entry and safe refresh.

Backend is the source of truth for persisted messages, tasks, proposals and progress.
Frontend cached/optimistic state is provisional and must reconcile with the backend.
Reuse canonical IDs; do not join records by displayed job title.
Use actual capabilities to hide/disable unavailable controls; do not show a functioning pause/delete/
schedule control when the backend cannot support it.

## 4. Minder interaction
Initial screen:
- show actual conversation history if available;
- otherwise show a simple entry point for goals/interests/questions;
- explain missing profile inputs when the backend asks for them;
- do not demand a complete profile before allowing a question or profile save.

Message lifecycle:
1. User submits text; show a sending state and prevent accidental duplicate submissions.
2. Send only the established request fields; the backend resolves user identity and context.
3. Show waiting/tool activity as concise status, not private reasoning or hidden prompts.
4. Render only the grounded/validated answer intended for users.
5. Resolve source IDs through backend-supplied source records.
6. Reconcile resulting actions/proposals and refresh affected task/profile/progress views.
7. On failure show a retryable state where appropriate; do not invent an assistant response.

If streaming is implemented, use C's validated streaming contract. Do not display unsupported factual
text before a later validator retracts it. If no safe streaming exists, use a normal loading response.
Do not introduce streaming merely for appearance.

Sources:
- Display publisher/title, observation date where relevant, scope and link.
- Explain evidence meaning: employer observation, offering activity, related shortage group,
  broader sector context, or forecast where actually available.
- Do not call related-group membership an exact shortage designation.
- Do not expose raw internal market ranks; preserve existing public presentation policy.
- Links/Markdown must be safely rendered. Do not inject model HTML using an unsafe renderer.

Answer categories:
- External fact: source-backed.
- User statement: attributed to the user.
- System assessment: identified as an assessment with factors/limits.
- Plan/suggestion: explicitly proposed, not a guaranteed outcome.
Sources are for relevant factual claims, not invented citations attached to greetings.

## 5. Actions and approval
Direct specific request, e.g. move a named task to a named day:
- the backend applies existing authorization and version checks;
- no second approval is required merely because an LLM interpreted a clear scoped request;
- show success only after the persisted operation succeeds.

Proactive/inferred proposal, e.g. the user says they feel overwhelmed:
- show the concrete proposed changes and affected tasks/times;
- do not update the plan before approval;
- approve/reject targets the exact proposal/version;
- rejection leaves user state unchanged;
- a stale proposal requires a refreshed review, not a silent new action;
- retries do not apply the same action twice.

Frontend buttons request backend operations; they are not an authorization bypass.
A retrieved document or chat injection cannot grant more tools/permissions.
Existing separate destructive-operation confirmation rules remain applicable.

## 6. Mindbots interaction
Show available capabilities using real backend state:
- relevant market updates with actual evidence/date/scope;
- daily check summaries only when a check actually ran;
- task completion follow-up and next-step proposals;
- pending proposals awaiting approval;
- completed/failed actions;
- automation preferences or schedule controls only where implemented.

Do not display "24/7 active" from a successful one-off local scheduler test.
If background operation is unavailable, show that accurately and preserve interactive chat.
A queued job is not a completed job. Progress and proposed rescheduling are different states.
Market updates must not transform unavailable forecast history into a claimed future trend.

Both modules observe the same state:
a completed task in Tasks is reflected in Mindbots; an approved Mindbot schedule change appears in
the roadmap and Tasks after refetch. There is no client-only duplicate schedule.

## 7. States F must handle
Bind these meanings to C's actual enums:
- empty conversation;
- message sending / awaiting response;
- assistant response ready;
- incomplete profile / insufficient assessment evidence;
- source absent or unsupported response safely withheld;
- provider timeout/rate limit/unavailable;
- proposal awaiting approval / rejected / stale;
- action pending / completed / failed;
- no agent event / background service unavailable;
- session expired or unauthorized;
- recoverable fetch error.

An unavailable state is not a zero score, empty forecast chart or fabricated friendly success.
Error messages must not contain credentials, server paths, private prompts or another user's data.

## 8. Engineering phases
F-LLM1: source inventory + page/interaction map.
Inspect preferred HTML, Replit source and existing C acceptance behaviour. Identify reusable parts.
Commit the bounded import/map; don't copy unrelated backend, secrets, .git or generated output.

F-LLM2: common client and Minder real chat.
Bind C's exported schema; implement state/source rendering and provider failure behaviour.
Verify real conversation persistence and grounded responses. Commit.

F-LLM3: Mindbots, proposals and shared state.
Integrate events/actions/approve/reject with the current backend.
Verify direct specific action, proactive proposal, rejection, approval, stale version and duplicate retry.
Commit; unsupported controls remain honestly unavailable rather than mocked as live.

F-LLM4: product browser acceptance and handoff.
Run the preferred frontend against the named integrated backend revision using fictional profiles.
Verify source scope, refresh, invalid session, failed provider and mobile/desktop layout.
Record real provider checks separately from fixtures. Commit and publish the owned feature branch
under file 06, then give A the full SHA and test evidence.

Other product views can continue in D/E-owned backend modules; F remains sole frontend shell/client
owner unless A records an explicit non-overlapping transfer.

## 9. Definition of done
A user can chat, understand the evidence, request a scoped change, review a proactive proposal,
reject or approve it, and observe the persisted result in the same application.
At least one new A v2.1 non-Bosch evidence type is exercised in the combined real-provider flow.
Absent national/forecast evidence is acknowledged. No raw ranking matrices, fabricated citations,
unsupported market claims or false action-success displays appear in the accepted scenarios.
This verifies the tested flow; it is not a guarantee that all possible model outputs are correct.
