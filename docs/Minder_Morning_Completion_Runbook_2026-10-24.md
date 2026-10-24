# Minder — morning completion runbook

24 October 2026 · Asia/Kuala_Lumpur · **Revision 3 — one Mindbot conversation and final launch**  
Purpose: finish a usable end-to-end prototype after sleep, then produce submission materials.  
This is the next execution addendum, not a restart of the completed A–F work.

### Revision 3 takes precedence

Final clarification: each user has exactly one continuous Mindbot conversation, presented as a messaging interface. Mindbot has no New chat, conversation list, branching or thread-switching feature. Minder retains its separate multiple-chat history. Apply this distinction to the UI, API, storage and scheduled messages; earlier instructions to offer new/list/open/delete conversations in both modules are superseded. Revision 3 also makes pre-credit RunPod preparation and the hosting selection rule explicit. The other revision 2 requirements below remain in force.

Junhong's morning clarification adds explicit requirements that were insufficiently covered in revision 1: Mindbot must have its own persistent conversation and action execution without redirecting to Minder; approved Profile/Careers/My Path designs are now ready for implementation; substantive advice and plan content must use real model generation with applicable evidence; daily automation must work on the hosted app. Do not use the old “defer Explore” or “questions continue in Minder” instructions.

The latest instruction also directs final judge-facing deployment. Prepare and publish the accepted prototype within the existing authorised resources, after verifying actual costs and configuration; do not ask for the same deployment permission again. This does not authorize billing upgrades, unrelated infrastructure or a main-branch merge. Existing branch-push authority continues; main merging retains its separate boundary in section 8.2.

Use the revised prompts in section 10. A incorporates this revision into the actual repository context so sessions do not execute conflicting copies. This is a plan for end-to-end completion, not a claim that the unfinished features already work.

## 1. Read this first

The critical path is useful chat → real login and durable user state → integrated frontend → hosted acceptance. RunPod proceeds independently and must not stall that path.

“Tomorrow morning” in the late-night conversation means the morning after sleep on **Saturday, 24 October 2026**. The user-stated deadline is Sunday, 25 October, 08:00 MYT; target submission earlier. Competition requirements and deadlines have not been independently verified by this runbook.

This plan is based on Junhong's pasted session reports and the attached screenshot. The author has not inspected the live Mac repository. A must reconcile any work completed since those reports before assigning new work. Do not treat unknown status as proof that code does not exist.

### Confirmed versus unfinished

| Area | Latest evidence | Remaining requirement |
| --- | --- | --- |
| Profile, tasks, progress and Explore services | D/E report local database-backed journeys and published branches | Integrate latest changes; verify against authenticated identities and hosted persistence |
| Frontend | Existing repairs passed; Junhong now has completed Profile/Explore HTML, images and logic context | Implement the approved full frontend, preserving repairs and binding real contracts |
| Minder conversation | A reports CHAT-01 repaired: evidence-only replies and unsaved-profile blocking were identified | Verify the specific roadmap request and an unseen conversational follow-up at the new revision; do not redo completed repairs |
| Mindbot | Loading repaired; new screenshot explicitly says questions continue in Minder | Replace redirect with its own persisted conversation; verify actions and daily automation there |
| Existing database | Reports explicitly describe SQLite | PostgreSQL implementation/migrations are **not confirmed** |
| Conversation storage | Screenshot says refresh clears the conversation | Persistent history is **not complete** unless newer code proves otherwise |
| CV/resume Library | Frontend flow exists; storage previously disabled; A explicitly deferred document retry repair | Complete retry repair and verify private durable storage, supported extraction, review and ownership |
| User login | Junhong reports no login page | Real authentication and server-side owner binding remain required |
| ML recommendations | Provisional scorer and partial current-market evidence work locally | Preserve scope and ranking semantics during release integration |
| Real market forecasts | Compatible history remains unavailable | Keep unavailable; neither GPU nor synthetic data closes this evidence gap |
| RunPod | Prepared launcher; zero paid jobs reported; user now explicitly says this is compulsory for the hackathon | Credit registration, key, one actual GPU fit and evidence; do not omit from submission checklist |
| Deployment | No deployment reported | Concrete hosting configuration, persistence, authentication and hosted acceptance |

Do not claim the project is finished because individual test counts passed. Each required user journey must work at the final integrated revision.

### Known checkpoints — inspect ancestry, never rewind

- Latest F repair: `8446ca801de8d8a0163c390f76d2aa609a5fec16`, branch `session/f-product-frontend`.
- F repair handoff: `docs/execution/product-v2/F/repairs/HANDOFF.md`.
- Earlier F delivery: `29281ec907ef031c1ec07be27c84e25aad69969e`.
- D reported delivery: `1cb81b1574e1ef263a47e3bb0e098c50482340c5`.
- E cumulative delivery: `c2628eceaf4700cd124a407ec4dfe43a6cdbd4ff`, including the earlier D delivery.
- B synthetic preparation: `d9ffd4f3cc7625c736ea081c52da3c1122b21c08`.
- A's latest reported pushed/remote-verified repair HEAD: `12856703ef187b09cbcb857b85923890fef331c4`, including F's repair handoff. Start from this or a verified later descendant.
- A's latest local UI is `http://127.0.0.1:9111/#minder` and Mindbots is `http://127.0.0.1:9111/#mindbots`. Confirm process revision before comparing an older 9106 page.
- A repair evidence: `docs/execution/product-v2/CHAT_REPAIR_ACCEPTANCE.md`; reported frontend revision `aeb3e08b6088cf06e6dc917d47a3e2097b5f1dd8`.

A reports 90 backend tests plus real browser/source/action/isolation/recovery checks. Deterministic application guidance measured 27 ms; Mindbots loaded in 109 ms while a real Qwen request finished at 788 ms. Those observations are not a general latency guarantee. Conversations remain temporary and document retry repair remains deferred. No main merge or deployment occurred.

Preserve later descendants and unfinished local edits. Do not duplicate already-merged commits.

## 2. Morning launch order and exclusive ownership

1. Open this file and send **A's prompt in section 10** to the existing A session. Continue from its completed repair; do not restart it.
2. Send B its prompt immediately; non-paid preparation is independent.
3. A performs a short state/ownership update and publishes the current base, actual contracts and file assignments. D/E/F can inspect now; dependent edits begin after their file ownership is settled. Do not wait for A to finish the whole application.
4. Resume D, E and F in their existing isolated worktrees using their prompts. No need for more sessions.
5. Junhong handles the RunPod account/credit/key and hosting access while the lanes implement.
6. A integrates committed deliveries continuously and owns final acceptance.

| Session | Owns | Must not concurrently edit |
| --- | --- | --- |
| A | Minder/Mindbot model orchestration, structured guidance/planning, tool execution, shared routes/middleware, integration | D migrations, E isolated auth adapter/worker wrapper, F frontend |
| D | Database/schema/migrations, user mapping, both conversation channels, CVs, persisted plans/automation records through existing services | Provider orchestration and frontend |
| E | Auth adapter/config, existing Explore read adapters if needed, hosting and scheduled-worker wrapper | Schema/migrations, A's model/action logic and frontend shell |
| F | All approved product frontend pages, separate Mindbot chat, login/history/CVs, actual output rendering | Database, provider and market scorer |
| B | Existing synthetic experiment's RunPod execution and evidence | Product code, live ranking policies and hosting |

A names actual files in the repository; these responsibilities do not invent new paths or endpoints. E exports its identity-verification function; A owns the shared middleware/route hook. D is the only new-migration writer. F is the only frontend shell/client writer.

Reuse the existing scheduling/action services and C's earlier worker implementation wherever possible. A owns what an automation may do; D owns its persisted state; E owns when/how the hosted worker runs; F owns controls and results. Do not create a second scheduler, state store or competing agent backend.

Use existing directories `/Users/phuahjunhong/sdc-2026-minder-worktrees/session-{a,b,d,e,f}`. Check `git worktree list --porcelain` first. Preserve reserved ports, separate databases and outputs. Share configuration securely through the established mechanism, not Git.

### Time budget, not a guarantee

- First 20–30 minutes after starting: current-state reconciliation, exact login/storage target, early contracts, owner/access checklist.
- Next 60–120 minutes: first working chat repair, persistence slice, authentication slice and frontend wiring, integrated incrementally.
- Next 45–90 minutes: deployable candidate, actual hosted journey, blocking repairs.
- Reserve at least 30 minutes for final evidence, push verification and submission handoff.

A substantial SQLite-to-PostgreSQL conversion, full approved frontend integration or unavailable account access can exceed this budget. Identify that in the first interval. Do not hide it behind repeated generic tests or promise morning completion regardless of evidence. E can inspect hosted access immediately; F can inspect approved designs while A assigns shared files. Keep RunPod independent of the app release path, while retaining it as required submission work.

## 3. The screenshot: exact defect and required chat behavior

User request shown: “now based on my profile, recommend the roadmap to become eML engineer”.

Observed answer includes:
- “Provide an anchored activity level and evidence description for Reading Comprehension.”
- “Calculated assessment” and internal scoring-policy explanation.
- Repeated “Limitations” sections.
- A generic proposal disclaimer despite no useful proposed roadmap.
- A temporary-conversation notice.

These are product defects for this request. A's subsequent report identifies the earlier cause: the backend could select only evidence/disclaimer statements and the frontend blocked unsaved profiles. This supports an application-design diagnosis, not a demonstrated deficiency in Qwen. A reports the general repair complete. The screenshot alone cannot tell whether that specific request now passes at the repaired revision or whether it called Qwen.

Read the existing repair evidence first and use the current 9111 runtime. Verify the roadmap request and its follow-up once. If already covered and passing, retain the evidence and proceed to persistence/authentication. Investigate only a remaining failure. Fast deterministic application guidance is legitimate, but does not by itself prove useful open-ended LLM conversation.

### A: verify the remaining path; trace only a reproduced failure

At the actual running revision, reuse existing traces/checks where they apply:
1. Reproduce the request with a minimal profile, a partial profile and an adequate test profile.
2. Locate the distinctive displayed strings in backend/frontend code and templates. Inspect intent routing, selected tool, assessment completeness gate and response envelope.
3. Trace whether the provider was called; selected model; supplied profile fields and conversation context; tool response; validation result; fallback reason; final rendered response. Record sanitized metadata, not credentials or private user content.
4. Confirm the browser's assets and API are from the expected revision. A running old process is not proof a new fix failed.
5. Repair the responsible layer. Keep genuine unknown competence unknown, but stop treating a complete numerical assessment as a prerequisite for useful conversation.

### Required behavior

- Read the available profile first. Do not ask for fields already saved.
- If “eML engineer” is ambiguous, briefly clarify the intended role; if context supports machine-learning engineer, state that assumption and continue.
- Ask one or two relevant questions, such as Python/project experience and weekly study time, instead of exposing assessment rubric language.
- Offer a provisional learning outline when useful, explain its assumptions briefly, and refine it with the user's reply.
- A draft roadmap is not a completed suitability score or proof of competence.
- Conversational intake and roadmap discussion must work even if numerical role-fit or market evidence is unavailable.
- Factual external claims about role requirements, companies, resources and market demand need applicable sources. Unsupported market forecasts remain unavailable.
- Greetings, clarification questions and descriptions of actual application capabilities do not need fabricated citations.
- Keep user facts, source facts, calculated results and proposed advice distinguishable without displaying repetitive engineering warnings.
- Respect direct-action authority: a specific request to change a schedule authorizes the scoped change; a request to recommend/discuss is not automatically a request to save it. Proactive/inferred edits need concrete approval.
- Preserve protections against arbitrary document/web instructions becoming agent commands.

Example tone, only if the named fields are actually missing:
“I can help build a roadmap towards machine-learning engineering. To choose a useful starting point, what have you built with Python, and how many hours a week can you study? I can sketch an initial plan now and adjust it after your answers.”

This illustrates behavior; do not implement that sentence as the only accepted output.

### Focused acceptance

Use unseen paraphrases and follow-up answers, not only the exact screenshot string:
- Partial-profile roadmap request receives useful guidance and relevant questions.
- The next reply uses the user's answer and existing profile.
- Source-backed market questions retain citations/scope.
- An unsupported forecast is honestly unavailable without blocking unrelated guidance.
- Provider failure produces a brief recoverable error, not fabricated generated content.
- A slow provider call does not block Mindbot state reads.
- Proposed and direct actions retain their different permission rules.

A records real-provider calls separately from deterministic app-help responses and mocks. No hidden model reasoning should be logged or stored.

### 3.1 Mindbot must converse and act inside Mindbot

The new screenshot contains a Mindbot composer and the footer “Questions continue in Minder. Changes use the exact task and proposal controls.” Junhong observes automatic navigation to Minder on send. This is a product-routing gap, not evidence of a model capability limitation.

- Sending a message, pressing Enter or using a Mindbot suggestion must keep the user in Mindbot. Render the reply and subsequent turns there. Explicit navigation links may open another module when the user chooses them.
- Give each user exactly one persisted Mindbot conversation identity, reused on every visit and device. This is a continuous messaging interface: no New chat button, conversation list, new-thread suggestion, branching or thread selector in Mindbot. Minder retains its own multiple conversations. Enforce one Mindbot conversation per user through an atomic get-or-create operation and a database uniqueness constraint or equivalent invariant, including concurrent first visits; the API must not create additional Mindbot threads just because a client requests one.
- Minder and Mindbot use the same Groq model, server orchestration, tools and database. No second API subscription or duplicate backend is required.
- Share canonical user/profile/plan/task state across modules. Keep channel-specific history and any cross-channel context access explicit; do not silently merge every thread or replay an earlier action.
- Use real model interpretation for substantive natural-language requests, including paraphrases and follow-ups. A hardcoded button/keyword router alone is insufficient. Deterministic state reads and tool execution remain appropriate.
- Supported prototype actions: update explicitly requested profile/preferences, create/edit supported roadmap/tasks, schedule/reschedule tasks, update explicitly reported completion, and create/edit/pause/resume/cancel daily automation within the implemented tool allowlist.
- A specific instruction authorizes its scoped write. A discussion, pain point or inferred improvement produces a concrete proposal before a write. If an essential time, target or destructive scope is ambiguous, ask a focused question.
- Validate typed arguments, ownership, current record version and requested scope before execution. Keep idempotency and an audit/action ID. A model-produced sentence is not proof of a database change.
- After execution, show a concise confirmation linked to the saved result. Refresh affected views so a schedule change appears in My Path, Overview and Mindbot without divergent copies.
- Do not silently turn a failed tool call into “Done.” Preserve rejection, cancellation, retry and undo behavior where already supported.

Daily automation minimum: a persisted schedule with user timezone, enabled state, next run, task scope and last result; use Asia/Kuala_Lumpur as the product default while allowing the user to set it. The worker runs without an open browser or an active model loop. At the due time it reads saved tasks/progress, generates a useful summary/next-step message, and appends it to that user's single existing Mindbot conversation, linked to its activity/run record. It must not create a new chat for each day or event. An in-app result is sufficient; email/WhatsApp/push are not added requirements.

Creating a recurring check directly authorizes the stated recurring check, not arbitrary future roadmap edits. Autonomous schedule changes require an explicitly recorded recurring-edit scope; otherwise the check proposes changes. Track actual app updates and user reports, not imagined study activity or proficiency. Deduplicate execution, handle timezone boundaries and missed runs without repeated notifications, and make failure visible. Test pause/cancel and a catch-up policy.

Reuse existing task-completion, preference-change and verified-market-evidence event handlers if present. Market-triggered alerts require new relevant evidence from approved sources; do not fabricate an event or launch a broad crawler to fill the feed.

Acceptance: in Mindbot send a paraphrased planning request, reply to its clarification, issue a specific task change, create a daily check, and see actual saved outcomes without route changes. Then close the browser, execute a scheduled event on the hosted target, reopen Mindbot and verify one stored result in the same conversation. Refresh, login again and concurrently open another tab: the conversation identity remains the same and no New chat UI appears. Repeat delivery must not duplicate writes.

### 3.2 Dynamic guidance, stable calculations and persisted state

The requirement is personalised generated content, not a different random answer on every page refresh. Define each displayed value's origin. Existing reports do not prove that every current card or roadmap is LLM-generated; A/F must inspect actual data paths and replace substantive placeholders/template answers.

| Feature | Model-generated contribution | Authoritative backend contribution |
| --- | --- | --- |
| Career Matches | Personalised explanation, evidence summary and relevant questions | Eligible role IDs, policy scores/order, exclusions, feedback and evidence scope |
| Compare | Explain trade-offs for this user using the selected roles | Comparable measurements and differences; never invent missing comparison values |
| Outlook | Explain available current/forecast evidence and its limits | Actual market observations/forecast availability; no fabricated future chart |
| Skills | Explain supported gaps and propose learning priorities | Role requirement mappings and assessed/user-reported skills; unknown is not zero |
| Roadmap | Generate a structured draft with stages, goals, suggested effort and dependencies | Validate against user constraints; version and save only with action authority |
| Next Steps | Generate useful task descriptions/priorities from the accepted roadmap and current state | Due dates, ordering constraints, task status and actual scheduled records |
| Progress | Explain progress and suggest next actions | Completion/status calculations from saved events; task completion is not proven competence |
| Resources | Explain why an available resource suits the user/task | Verified resource IDs, title/link/source/date and existing availability |
| Minder / Mindbot | Interpret intent, converse naturally and propose/choose permitted tools | Identity, source retrieval, tool validation, execution and saved outcomes |

Use a shared typed generation contract. Concepts include user/role/plan IDs, input/profile version, model/policy version, generated explanation or stages/tasks, supporting evidence IDs, assumptions, missing fields and draft status. Export actual schemas/examples before F wiring; do not invent endpoint names in the frontend. Server validation rejects invalid IDs, unsupported factual quantities, impossible schedules and unauthorized mutations.

Generate from saved profile + supported requirements + applicable market evidence + resource records. Link factual claims to real source passages/records with title/URL/date/scope as available. Explain a recommendation using the user's inputs and applicable evidence; a citation supports its premises, not a guarantee the recommendation will succeed. User facts, backend calculations and proposed advice have different provenance. Do not invent URLs or cite unrelated evidence just to populate a Sources box.

Persist an accepted plan once, with stable IDs. All pages read that plan. Changing profile/time constraints can create a new proposed version; a browser refresh must not silently regenerate, overwrite or reschedule it. Store visible model outputs so they can be inspected, but not hidden reasoning. If generation fails, show a recoverable error or the last saved version; never relabel a static fallback as successful AI generation.

The existing provisional ranking policy remains authoritative. “No fixed answer” does not authorize the LLM to invent numerical scores, override source scope or replace the recommendation algorithm. Do not reopen coefficient design during this release.

Closure evidence must include real generation of a personalised reason and structured plan for an actual test profile, followed by a materially changed goal or time constraint and a useful corresponding revision. Trace the supplied inputs, applicable source IDs and validated saved output. Confirm substantive advice did not come from a fixed demo fixture or canned keyword response. Reusing the same saved accepted plan is correct; a refresh is not a demand for a newly generated answer. Keep ordinary UI labels, calculations and permission checks deterministic.

### 3.3 Approved full frontend scope

Junhong reports the Profile and Explore frontend logic, HTML and reference images are finished. A/F must locate the exact files, starting with the existing `docs/minder-ui-html-previews/` inventory, and commit only approved assets. Do not wait for a new design generation cycle. If files exist only in the original checkout, A imports them into the shared release base and names exact revisions for the worktrees.

If the new assets are still only in the design chat, Junhong must copy them into the repository. A reports exact missing filenames and continues independent backend work. Having an asset ready in another chat does not make it available in a worktree.

Implement the approved layouts with real contracts:
- Overview/home: keep approved design; show actual saved state and relevant next action.
- Profile: intake/editing, preferences/constraints, and CV/resume-only Library.
- Minder: its own conversation/history with useful generated guidance and sources.
- Mindbot: one continuous saved conversation per user, schedule/automation controls and action/activity results; no New chat or thread list.
- Explore expands to **Careers** and **My Path**, as separate pages rather than all features on one dashboard.
- Careers: **Matches, Compare, Outlook**, following the approved design context.
- My Path: **Skills, Next Steps, Progress, Roadmap**, with grouping/order taken from the supplied approved files. Keep “Next Steps” now; a possible later rename to “Plan” is not approved yet.

Use the supplied navigation and design system. Do not invent missing backend capability from a mockup. Map design fields to actual contracts and expose the smallest genuine missing operation through its owner. F remains sole frontend owner; optional help needs an explicit disjoint-file assignment, not another session editing the shell.

Replace seeded mock recommendations with actual persisted/model/backend outputs. Include loading, empty, unavailable, validation, error, retry and saved states. Market scores remain internal; present explanations and supported visual comparisons. Source links must be usable from recommendation/plan content. Real forecasts stay unavailable where unsupported; a synthetic chart belongs only in a clearly separate experiment demonstration.

### 3.4 What the internal market system can currently support

Latest reported anchored-profile coverage: 910 personally assessed, five activity comparisons, seven related shortage contexts, zero exact whole-role shortage designations, 907 sector contexts, and 900 personal-only ranks. Counts overlap. Three activity comparisons use category proxies and two use employer observations; this is not 910 equally comparable national-demand scores.

Earlier code inspection reported an industry activity index through Q1 2026 (not wired into the current ranking), broad occupation-group indexes through Q2 2026, and source-specific skill-request counts without a normalized skill-market score. The active role policy was reported as 85% personal + 15% comparable activity, with bounded shortage context. A must export the exact active policy/version and applicability from current code for the pitch; do not present these historical reports as freshly reverified outputs.

Pitch the actual hybrid pipeline: profile/evidence → backend provisional fit and eligible market treatment → evidence retrieval → LLM explanation/structured plan → validated action → persisted state. Ridge/XGBoost experiments exist, but learned-model accuracy on independent real outcomes is unestablished. Distinguish the live provisional scorer from experimental models. Do not claim a fully learned, nationally validated forecast system or conceal the personal-only fallback.

A adds a small checked-in architecture/policy summary and one reproducible calculation trace using a synthetic profile. This is for judges/developers, not ordinary UI score displays. No new scoring formula is required for this handoff.

## 4. Database, login and storage: the concrete target

### Target for the judge prototype

Prefer one Replit-hosted frontend/API application, one durable relational database, one private file bucket and the existing Groq API. Reuse existing working adapters. Avoid a backend framework rewrite.

Hosting selection: Replit is the first candidate because the user already has an account/plan and it supplies a publishing workflow plus database/storage options. E verifies the actual Python app, durable persistence and hosted scheduling in its first bounded inspection. Do not publish only the design mockup. If Replit introduces a concrete blocker such as an unfinished database conversion or unavailable runtime/account access, evaluate Railway as the single fallback: it supports deployment from GitHub and persistent volumes. Choose the option with the fewest remaining verified changes, not a general platform ranking. Do not implement two hosts or begin new paid infrastructure without the required budget/access. A single-instance SQLite deployment on an appropriate persistent volume is an option only after verifying concurrency, backups, worker access and restart survival; it is not an automatic reason to abandon an already working PostgreSQL adapter. Independent cron services cannot be assumed to share a local SQLite volume.

The intended user experience is select the verified release, configure private settings once, publish, and open the judge URL. No provider can make the current local backend, login, durable chat/CV storage and automation work merely by uploading an HTML mockup. E prepares those minimum runtime settings so the final launch is simple. Use a provider subdomain; no custom domain or infrastructure redesign is required.

The last verified database is SQLite. Replit's published filesystem is not durable storage. If Replit is the target, D must implement/verify the required PostgreSQL adapter and migrations rather than treating a new URL as a conversion. PostgreSQL itself is not a universal requirement for a prototype; reliable hosted persistence is. Any alternative must have verified durable storage and preserve the existing feature contracts.

Do not put a writable SQLite file in object storage and treat it as a concurrent database. Do not deploy a static-only site and claim that its Python backend is hosted.

### Authentication choice

First preserve any actual working managed authentication already present. If none exists, the recommended addition is **managed Clerk authentication with a minimal login/sign-up interface**, adapting the existing vanilla-JavaScript frontend and Python backend.

Clerk documents Python backend verification and vanilla-JavaScript frontend support. Replit's managed Clerk setup is an option if provisionable in the existing project. Its documented automatic scaffold uses React/Express: do not accept a replacement application or a second backend merely to obtain login. E must verify compatibility and provision only the necessary auth/configuration, using the existing stack.

Replit Auth is a possible simpler alternative, but it requires users to sign in with Replit accounts and its documented setup uses Replit Agent. Do not silently impose that account requirement on judges or replace the chosen provider halfway through implementation. If the recommended route cannot be configured promptly, E reports the exact access/runtime constraint and the concrete alternative.

Required login behavior:
- Sign in, sign up or provisioned judge account, and sign out using the selected provider's maintained components.
- Verify identity server-side with the provider SDK: token validity, issuer, expiry and expected application/origin settings.
- Map the verified provider subject to one application user record. Never trust a browser-submitted user ID to authorize data.
- Each user sees only their profile, CVs, conversations, tasks, saved resources and proposals.
- Expired sessions return a sign-in state; signing out clears displayed private data.
- Keep development and hosted credentials/users distinct where the provider separates them.
- Do not store passwords in the application's profile tables or invent a password/session system for this deadline.
- No developer impersonation/default-user bypass in the hosted runtime.

A login page alone does not close authentication. Verify two accounts and deliberate cross-user access attempts.

### D: structured persistence

Reconcile existing tables before adding anything. Minimum concepts, not mandated duplicate tables:
- Application user and verified external identity mapping.
- Profile/preferences and existing plans/tasks/progress.
- Conversation and ordered visible messages, including channel identity for Minder/Mindbot and request/outcome states.
- Source references and proposal/action identifiers linked to messages.
- Versioned generated/accepted plans and existing automation schedule/run records, reusing current tables where possible.
- CV/resume metadata: owner, private storage reference, type, status and extracted-field review state.

Minder supports new/list/open/delete/continue conversations. Mindbot supports opening/loading older messages in and continuing its single conversation per user, not creating or selecting multiple chats. Keep both channels in the existing conversation/message infrastructure, with an enforced singleton invariant for Mindbot and user-scoped access throughout. Scheduled messages append to the same Mindbot history. If earlier development records contain multiple Mindbot threads, document a safe, explicit migration rather than silently dropping or merging user records.

Persist server-accepted user messages and actual final visible assistant messages; clients cannot author trusted assistant records. Retain history after refresh, sign-out/sign-in and application restart/redeploy. Apply retry/idempotency protection and do not replay old actions when opening history. History deletion/retention controls, if already present, must follow the explicit privacy policy; this clarification does not authorize erasing existing history.

The entire saved transcript need not be sent to the model every time. Supply a bounded relevant context window. Do not hold a database write transaction open during a slow provider request.

### D: CV/resume-only Library

First-prototype purpose is CV/resume, not certificates or unrestricted objects. Prefer PDF/TXT; keep other formats only if already safely supported. Extension checks alone do not prove document purpose.

Complete upload → private storage → supported extraction → user review → accepted profile update. Resolve A's explicitly deferred document retry defect: a retry must recover cleanly without duplicate documents, contradictory processing states or repeated profile writes. Use a synthetic sample CV for testing. Reject unsupported types and oversized files; make scanned/non-extractable content explicit with a manual-entry option. No mandatory OCR project now.

Original bytes belong in private durable storage; structured metadata belongs in the database. App authorization must protect every list/read/download/delete operation. Source documents cannot issue instructions to the bot. CV statements are user-supplied claims, not independent competence validation.

Define deletion behavior for source bytes and derived fields without silently erasing unrelated accepted profile data. Avoid logging raw CV content.

### Migration acceptance

D must test actual PostgreSQL behavior if PostgreSQL is selected: IDs, JSON/boolean/time handling, parameter syntax, transactions, uniqueness, version checks and concurrent retries. SQLite-only tests are insufficient.

Back up existing local data before conversion. Preserve existing IDs/references where migrating. Do not automatically give historical anonymous/dev records to the first real account. Use an explicit verified mapping or leave them outside the new hosted user store. An empty hosted dataset may use synthetic demo seeds, but must not masquerade as migrated user data.

## 5. Your manual morning setup

### RunPod — Junhong's actions

1. Create/sign in to the RunPod account that will receive organiser credits. Keep individual/team account selection consistent for the key and endpoint.
2. Complete the organiser's registration/credit redemption instructions. The exact competition-specific redemption route is unknown here; do not substitute a random referral offer.
3. Open RunPod Billing and verify the actual credited balance. USD25 was previously expected, not currently confirmed. If missing, use the organiser/support route; B can finish preparation while you resolve it.
4. Open **Credentials → API Keys → Create API Key**. Name it for this experiment. B must specify the smallest permissions required for endpoint management and execution; a read-only key cannot launch a job.
5. Save the key directly in B's exact ignored secret file, using its actual variable name. Ask B to provide the absolute path first. Do not paste keys into chats, screenshots, shell history or Git.
6. Confirm to B only that the key is saved and credits are visible. Agree the first-run ceiling of USD2; leave automatic top-ups disabled.
7. If a private container registry requires separate access, enter its credential only through the designated secret interface. An SSH key or S3 key is not automatically required for a serverless job.

B owns image, endpoint, GPU/device, output and cleanup setup. Do not manually rent a separate always-on GPU while B is configuring the prepared serverless endpoint.

### Hosting/auth/storage — Junhong's actions

1. Open the intended existing Replit project. E must confirm whether it contains the actual app source or just the old mockup. Import/sync the verified integrated revision without overwriting the working Git histories.
2. Give E the project identity and the available publishing/account access; never send login passwords.
3. Check Database and App Storage availability in that project. E/D supply exact runtime settings and whether external local access is needed. Enter connection secrets through approved secrets interfaces.
4. Allow E to prepare the selected managed login setup. If your account requires browser actions, complete only those provider setup steps. Do not start a second Replit coding agent editing the same files while A/D/E/F are editing them.
5. Verify Groq configuration exists for the **published runtime**, not just the Mac or preview environment. Preserve the tested model; do not reselect models without a diagnosed reason.
6. Check the concrete release candidate, hosting cost and judge-access instructions E/A provide. The requested scoped judge deployment may proceed after acceptance within existing authorised resources; only new access or extra expenditure needs a separate resolution.

The required account actions may be quick, but code integration is still required. Neither creating a database nor creating a storage bucket wires the application automatically.

## 6. B: actual GPU experiment

Read `docs/execution/parallel/B/SYNTHETIC_HANDOFF.v1.md` and reuse the hash-pinned launcher.

**Objective:** execute the existing disclosed synthetic experiment on a cloud GPU and capture verifiable evidence. It does not improve source coverage by itself.

Start the engineering preparation immediately, without waiting for credit redemption. B can inspect the existing launcher, pin GPU-compatible dependencies/container configuration, validate the handler and request payload locally, prepare the ignored secret template and exact setup instructions, validate bounded retry/timeout logic, and prepare artifact download, cost reporting and cleanup commands. Reuse completed preparation; test only unverified changes. Record this as preparation-ready with live cloud checks pending. Actual account access, endpoint provisioning, GPU availability and CUDA execution cannot be certified by a local dry run. The credit/key delay gates the paid run and live credential-dependent checks, not all of B's work. Do not provision billable workers or an unfunded fallback account while waiting.

Junhong explicitly identifies RunPod execution as compulsory for the hackathon. Treat MB2 as required submission evidence, not an optional polish item. It demonstrates a repeatable cloud-training capability, but moving the same training to a GPU does not by itself improve prediction quality or train/fine-tune the Groq Qwen model. Better predictive capability requires suitable data and demonstrated held-out improvement; those are not established by this small synthetic run. Check any exact organiser instructions already in the repository against the proposed evidence, without inventing compliance claims.

- Preserve data hashes, chronological splits, seeds, metrics and validation/test discipline.
- Train XGBoost with actual GPU acceleration appropriate to the pinned package; fail the GPU objective if it silently uses CPU.
- Ridge and simple baselines may remain CPU and must be labelled.
- GPU arithmetic may differ slightly; compare meaningful tolerances rather than promise bitwise identity.
- Keep the previous validation-selected method. Do not choose XGBoost because it used GPU or retune against the final test.
- Leave ordinary runtime scores/forecasts unchanged.

Preflight: real credit/key access, Linux GPU-compatible container, reachable image, fitting resource size, durable artifact retrieval and cleanup. Set zero active workers, maximum one worker, one GPU, execution/job-lifetime limits and bounded retries. Calculate the permitted duration from verified pricing including startup/idle and any ancillary charges. A polling script on a sleeping Mac is not a sufficient cost control.

The first run is limited to USD2 once that prompt is sent/confirmed. No billing upgrade, top-up, extra campaign or silent switch to a persistent Pod. Report a preflight blocker if the bound cannot be respected.

Required record: source commit, data/image hashes, package versions, job ID, UTC start/end, GPU and effective training-device proof, successful fitted model, predictions, metrics, observed cost and final worker state. Retrieve artifacts before ephemeral worker cleanup. Do not invent final charges if billing is delayed.

The previous CPU synthetic results were role/skill MAE:
- Last value: 1.47 / 1.53.
- Seasonal: 2.18 / 1.88.
- Ridge: 10.47 / 5.79.
- XGBoost: 29.03 / 15.71.

Those are fictional-advertisement-count errors, not real Malaysian accuracy. Seasonal won validation and remained selected despite last value doing better on the test.

## 7. E/A: deployment completion

E prepares the actual app target while D finishes persistence; A integrates it. Use the current Python app and frontend. Prefer one origin and existing API routing.

Required deliverables:
- Verified build/start commands, dependency installation and compatible Python runtime.
- Reachable host/port configuration; no reliance on Mac-only absolute paths.
- Server concurrency that preserves the repaired non-blocking behavior.
- Hosted auth verification and a usable login return URL.
- Durable database settings, tested migrations and backup/recovery instructions.
- Private storage connection and user-scoped operations.
- Groq secrets in the correct deployment environment.
- An inventory of required catalogue/evidence artifacts and lawful packaging. The 13 preserved untracked inputs do not arrive through Git automatically.
- One actual hosted scheduling path with duplicate-execution protection. Do not rely on a local worker or sleeping web process for scheduled operations.
- Cost estimate, ready-to-publish revision and a minimal judge walkthrough.

Prefer the smallest deployment configuration that runs the existing app and chosen scheduler correctly. Do not introduce containers, queues or a separate service unless the actual hosting/runtime requires them.

Junhong's latest request directs final internet deployment for judges. Publish the accepted candidate to the intended project within existing authorised resources after actual cost/configuration checks. Do not repeat a generic deployment approval request. If access is absent or a new expense/plan is required beyond those resources, finish all independent preparation and report that exact dependency. Main merging and billing upgrades are not included automatically.

## 8. Bounded checkpoints and evidence

| Gate | Owner | Completion evidence |
| --- | --- | --- |
| M0 state/contract release | A | Current ancestry, clean/unfinished work identified, ownership and runtime/access checklist |
| MA1 chat repair | A | Screenshot request + unseen follow-up works through traced real provider path |
| MA1-R01 Mindbot conversation/actions | A/F, D storage | Own-route multi-turn conversation, real scoped action, persisted history and no redirect |
| MA1-R02 structured guidance | A, D state | Real generated explanations/plan/tasks with sources and validated persisted output |
| MD1 durable persistence | D | Selected hosted DB migration/service tests; history and ownership correct |
| MD2 CV Library | D | Private upload/extract/review/delete with actual configured storage |
| ME1 authentication | E + A hook | Real sign-in and server identity; two-user isolation |
| MF1 frontend completion | F | Login/history/CV/both chats wired to real contracts |
| MF2 approved Profile/Explore pages | F | Separate Careers/My Path pages use approved assets and actual generated/persisted outputs |
| MB1 GPU preflight | B | Credentials/balance/runtime/cost/output controls verified |
| MB2 GPU execution | B | Actual fitted GPU model, outputs, evaluation, cost/cleanup |
| ME2 deployment candidate | E | Actual build/runtime/secrets/DB/storage/scheduler configuration |
| ME2-R01 hosted daily automation | E/A/D | Due job while browser closed, one persistent result, pause/cancel and repeat safety |
| MA2 release acceptance | A/F | One integrated browser/API journey at the target revision |
| MA3 hosted handoff | A/E | Published URL acceptance within authorized scope; exact SHA and demo instructions |
| MA4 main/submission handoff | A | Reviewed integrated release PR; history-preserving merge after authorization; main/tag/URL verified |

Reuse existing phase IDs if these tasks are already underway; cross-reference these gates rather than duplicating history. Commit each completed bounded phase/refinement, not every small edit. Stage only owned task files.

D/E/F publish their assigned branches. A publishes A and B/C snapshots under existing coordination. B hands exact evidence SHAs to A. Verify remote containment; do not reset, squash historical checkpoints, force-push, merge main or publish publicly without applicable authorization. No secrets, private CVs, personal chats, local databases or restricted raw datasets in Git.

If blocked, state: exact failed operation, evidence, responsible dependency, next concrete action and independent work continuing. Do not mark a required feature passed because it is disabled, mocked or documented.

### 8.1 Standing push instructions

Existing task-scoped push authorization persists. A, D, E and F should commit and normally push passed, meaningful checkpoints to their assigned branches without asking Junhong again each time. B/C deliver their exact commits to A for coordinated publication, so not every lane independently pushes. Report any real credential, branch-protection or tool-approval block instead of silently calling a local commit published.

Git commit and push remain separate operations. No automatic Git feature publishes every commit. Each handoff must report branch, local HEAD, verified remote SHA and any intentionally unpushed work. Never use a blanket all-branches push. The present A report verifies that `12856703ef187b09cbcb857b85923890fef331c4` is already published.

### 8.2 Final phase: bring the completed project into main

Only one commit on main does not mean the checkpoint history is lost. It usually means development is still on the session branches. A must verify the actual graph. Leaving the default branch with only the initial scaffold can confuse judges and cause them to run the wrong code; resolve that before submission.

1. Integrate the required final D/E/F and B evidence commits into the tested A release branch, checking ancestry and content. Do not separately re-merge lanes already included through a cumulative handoff.
2. Freeze one candidate and run the final acceptance. Create a concise release README with run/login instructions, demo URL when live, limitations and a phase-to-SHA index.
3. Inspect outgoing history for secrets/private data and verify the required checkpoint SHAs are ancestors of the candidate. A normal merge preserves commits actually present; it cannot recover history previously discarded by squashing.
4. Open one reviewable release PR from the integrated branch into main. Record current head/base SHAs and passed checks. Opening the PR prepares the result; it is not itself the final merge.
5. After explicit authorization for this main update, use a normal **merge commit**, preserving phase commits. Do not squash or rebase the release history. Respect branch protections; do not bypass or change them silently.
6. Verify remote main contains the release/checkpoint commits. Create/publish the agreed submission tag, such as `prototype-submission-v1`, if authorized and not already used; never move an existing tag.
7. Align the deployed source revision with the released candidate, rerun affected hosted checks if code changed, and record the exact deployed SHA and tag. Give teammates the final main/tag, not a stale branch.

The current conversation asks for this release phase; it does not override the earlier no-main-merge boundary by itself. A can prepare the PR and evidence now. Junhong can authorize the concrete merge when ready with: “Merge the reviewed release PR into main using a merge commit, preserve all checkpoint history, and publish the submission tag.” The latest instruction already authorizes the scoped prototype deployment; do not let pending main approval block deployment of a verified integrated release commit. No need to repeat ordinary branch-push approval.

## 9. Final acceptance — finish once, repair real failures

Use the integrated candidate, two synthetic test users and a synthetic CV.

1. Sign up/sign in; refresh and logout behave correctly.
2. User A cannot list/read/change user B's profile, CV, conversation, task or proposal.
3. Save a partial profile; ask a free-form ML-engineer roadmap question; receive useful questions/advice rather than rubric boilerplate.
4. Continue the conversation with a new answer; verify actual context use.
5. Reopen Minder histories and the same single Mindbot conversation after refresh, sign-out/sign-in and server restart; no duplicate messages/actions or cross-channel confusion. Two concurrent initial Mindbot loads must resolve to one conversation; no New chat or conversation selector exists there.
6. Upload a supported CV, review extracted fields, apply chosen changes, reopen the file and delete it.
7. View supported career matches and truthful source/scope labels; unavailable forecasts remain unavailable.
8. Select a direction, create/review tasks, complete one, and see consistent progress.
9. In Mindbot, send a message and follow-up without leaving its route. Execute a direct requested change; approve/reject a proactive proposal; persisted outcomes are correct across pages.
10. While a real provider call is pending, Mindbot and profile state remain responsive.
11. Create a daily check through Mindbot, close the browser, trigger one due event on the hosted configuration, reopen and see its stored result. Verify pause/cancel and no duplicate writes.
12. Verify durable state after a hosted restart/redeploy, using a safe test environment.
13. Check mobile/desktop login, Context closing, Working states and icon navigation.
14. Record the actual deployed commit, test evidence, limitations and judge access procedure.
15. Verify Profile, Careers (Matches/Compare/Outlook) and My Path (Skills/Next Steps/Progress/Roadmap) against approved assets, with distinct pages and actual state.
16. Trace one career explanation, one supported skill gap and one generated roadmap/task set to model request, evidence IDs, validation and saved version. An unchanged refresh reads saved content; changing a relevant constraint supports a new proposal without silently replacing the plan.

Run focused checks during development and this combined journey when its candidate is ready. Repeat only affected checks after repairs. Capture a short backup demo video after the working build; do not replace the requested working app with the video.

Freeze further design and model-tuning work once this journey passes. Real forecasting validity, broad national market coverage, independent suitability labels, OCR, a general document library and advanced account administration remain separately disclosed work. GPU execution is not evidence those problems are solved.

## 10. Copyable launch prompts

Place this file in the repository's docs directory and make it available in each worktree through A's committed handoff. Prompts below refer to its filename; resolve the actual location rather than guessing a new path. No need to resend all historical packs.

### A — send first, launch revision 2

```text
Read REVISION 3 of Minder_Morning_Completion_Runbook_2026-10-24.md and the current
repository rules/ownership. Continue from actual HEAD; preserve ongoing
work and completed checkpoints.

Your repair is pushed at 12856703ef187b09cbcb857b85923890fef331c4,
including F 8446ca801de8d8a0163c390f76d2aa609a5fec16. Reuse that
verified work or its later descendant. Publish M0: current integrated
base, actual auth/conversation/storage contracts, named file ownership,
runtime/access dependencies and lane handoff instructions. Do not wait
for whole-release completion to release independent D/E/F work.

This revision supersedes the old Explore deferral and Mindbot redirect.
Locate and share the approved Profile/Careers/My Path design assets.
Implement sections 3.1–3.4: one continuous Mindbot conversation per user,
without New chat, thread switching or per-event chats; own-channel actions,
typed real LLM guidance/roadmap/task generation, shared persisted state,
and an honest pitch trace of the active scoring/evidence pipeline.
Do not replace the ranking policy with model-invented scores.

Read CHAT_REPAIR_ACCEPTANCE.md first. On the current 9111 runtime,
verify the screenshot's roadmap request and an unseen follow-up using
actual Qwen. If already passing, reuse evidence and proceed. Investigate
only remaining failures through routing, profile/tool/provider,
validation and renderer. Preserve useful guidance with incomplete
profiles and factual grounding; a canned capability reply alone is
not evidence of open-ended conversation. Track the deferred document
retry repair with D.

D owns persistence/migrations, E auth/hosted worker/deployment, F the full
approved frontend, B the compulsory bounded GPU experiment. You own
model/action orchestration and common route/middleware hooks. Export
actual generation and conversation contracts early for F/D. Preserve
existing provider/scorer semantics and action-authority boundaries.

Integrate early committed slices and finish the section 9 journey.
Commit bounded repairs, coordinate authorised pushes and report actual
local versus hosted status. Do not silently waive login, chat history
or durable CV storage. Prepare the concrete publish candidate and a
history-preserving release PR to main under section 8.2. Existing
branch pushes are authorised. The final scoped judge deployment is now
requested: publish the tested candidate with E within existing resources.
Main merging retains its separate authorization boundary. No upgrades.
```

### D — persistence and CV/resume

```text
Read REVISION 3 of Minder_Morning_Completion_Runbook_2026-10-24.md. Resume your existing
isolated worktree after A's current ownership/base handoff; preserve
any already-completed storage work.

Own the database adapter, schemas/migrations, verified identity mapping,
persistent conversations and CV/resume Library services. Confirm the
actual current engine. Implement the selected durable target with E;
a PostgreSQL URL alone is not a completed SQLite conversion.

Support multiple conversations in Minder and exactly one continuous
Mindbot conversation per user, enforced under concurrent creation.
Persist versioned generated/accepted plans and existing automation
schedules/run results. Append scheduled messages to that same Mindbot history.
Reuse canonical state and current services; do not create duplicate stores.

Export contracts early to A/F. Complete Minder new/list/open/delete/
continue and Mindbot single-history load/continue, server-owned message
outcomes, retries and source/action
references. Reopening history must not replay actions. Do not hold
transactions during provider calls.

Complete CV/resume-only private storage, the deferred document retry
repair, supported extraction and review before profile changes.
Preserve manual entry and honest extraction
limits. Prove actual configured storage, user isolation, migrations and
refresh/restart survival. Existing local anonymous records must not be
assigned to the first logged-in user.

Commit/push bounded tested phases on session/d-profile-state.
Give A/F exact SHAs, schema version, real acceptance results and
remaining configuration dependencies. Do not edit their owned files.
```

### E — authentication and deployment

```text
Read REVISION 3 of Minder_Morning_Completion_Runbook_2026-10-24.md. Continue on your
isolated E branch under A's updated ownership.

Immediately inspect the actual Replit project, current runtime and
existing auth/storage configuration. Apply section 4's Replit-first,
Railway-only-if-blocked selection rule; choose one verified target early
and do not implement both. Prepare a simple publish flow with the existing
Python app, durable data and hosted worker; not a static mockup upload.
Reuse working managed auth if
present. Otherwise prepare the recommended Clerk login integration
compatible with our existing Python backend and frontend. Do not
replace the app with React/Express scaffolding or build custom passwords.
Report exact provider provisioning/access needs early.

Own the isolated auth adapter and deployment configuration; A owns
common route/middleware insertion, D user persistence/migrations,
F the login UI. Export verified-user and login-state contracts early.
Bind all private reads/writes to verified server identity and test
two accounts, expiry and logout.

Coordinate durable database/storage with D. Prepare actual build/start,
environment, migration/recovery, data-artifact packaging and one hosted
scheduler path. Preserve non-blocking service behavior. Complete all
independent preparation while account access is pending. Reuse the
existing scheduler: prove one due daily Mindbot check runs without an
open browser, stores a result, and handles pause/cancel/retry safely.
Coordinate any minimal Explore read-adapter gaps with A/D.

Commit/push bounded checkpoints only on session/e-explore-resources.
Give A one concrete deployable candidate with exact remaining steps
and cost. Coordinate the now-requested judge deployment after acceptance
within existing authorised resources; no extra plans or billing upgrades.
```

### F — full approved frontend and both conversation modules

```text
Read REVISION 3 of Minder_Morning_Completion_Runbook_2026-10-24.md. Preserve your
completed repair checkpoint 8446ca801de8d8a0163c390f76d2aa609a5fec16.

You remain sole frontend shell/client owner. Wire real login/logout,
Minder conversation new/list/open/delete/continue, and Mindbot's single
continuous message history per user. Mindbot has no New chat button,
conversation list, branching or thread switching; scheduled messages
appear in that same history. Wire CV/resume upload/extraction-review
to actual contracts.

Remove Mindbot's send-to-Minder redirect, including quick suggestions.
Keep messages, replies, actions and follow-ups inside Mindbot.
Wire daily automation create/edit/pause/cancel, activity and saved
results through the actual server contract.

Fix the screenshot's presentation alongside A's backend repair: helpful
conversation first, relevant sources/status second, no repeated internal
policy/rubric blocks. Do not conceal real errors or mark unsaved actions
completed. Render model/source content safely.

Keep Context close, Working terminal-state cleanup, icon rail and
independent Mindbot loading. The Profile/Explore designs are now ready:
implement approved assets, with Explore -> separate Careers/My Path pages.
Careers contains Matches/Compare/Outlook; My Path contains Skills,
Next Steps, Progress and Roadmap. Follow supplied layout/order.
Replace substantive mock/static outputs with validated model/backend
results. Read persisted plans consistently across pages; no regeneration
on every refresh. Do not start another design iteration.
Do not invent endpoints, call Groq directly or use localStorage as
the authoritative private chat history.

Verify real backend/provider browser flows, auth expiry/user switching,
refresh/history, retries and no action replay. Commit/push tested bounded
work only on session/f-product-frontend and hand A exact dependencies.
```

### B — preflight now, one paid run after private setup

```text
Read REVISION 3 of Minder_Morning_Completion_Runbook_2026-10-24.md and reuse
docs/execution/parallel/B/SYNTHETIC_HANDOFF.v1.md plus the existing
hash-pinned launcher. RunPod execution is compulsory submission work.
Do not restart research or redesign the experiment.

Our RunPod credits have not yet been redeemed and the key is not saved.
Start all independent preparation now: existing launcher/config review,
GPU-compatible package/image configuration, local handler/payload checks,
secret template, bounded execution and artifact/cost/cleanup handling.
Reuse completed work, and separate preparation-ready from live GPU proof.
Do not create billable workers while credits/access are pending.
Give me the exact ignored
secret-file absolute path, actual variable names, minimum key
permissions and endpoint/image requirements for private setup.

After I confirm credits are visible and the key is saved, I authorize
one actual GPU experiment within USD2 total, with no top-up, billing
upgrade, repeated campaign or automatic runtime model promotion.
Verify bounded execution/retries/cost, artifact retrieval and cleanup.
If those conditions cannot be met, report the exact blocker first.

Use the same declared synthetic data/splits/metrics. Prove actual GPU
XGBoost fitting, not merely GPU availability; label CPU baselines.
Retain validation/test discipline and record unfavorable results too.

Commit preparation and actual run evidence separately. Give A exact
SHAs for coordinated publication, with job/device/model/metric/cost/
shutdown records. Keep real forecasts unavailable and application
market coverage unchanged.
```

### A — final handoff request after integrated acceptance

```text
Report one consolidated release status: deployed/local revision and URL;
login and two-user isolation; persistent chat; CV storage/extraction;
useful real-provider conversation in both modules without redirect;
Mindbot actions/daily scheduled event; approved Profile/Careers/My Path
frontend; generated guidance/plan provenance; database engine/migration;
RunPod actual
evidence; remaining factual/model limits. Mark untested/blocked items.

Verify authorised branch pushes and preserve all phase history.
Prepare MA4: reviewed release PR to main, checkpoint ancestry index
and submission tag proposal. Do not squash the phase commits. Complete
the main merge/tag only when explicitly authorised, then verify them.
Provide the judge sign-in procedure, a five-minute demo sequence,
submission-safe claims, deployed SHA/URL and any exact access or cost
blocker still preventing the authorised scoped deployment. Do not substitute test totals
for the end-to-end acceptance evidence.
```

## 11. Submission claims and official references

Safe claims must match the final evidence:
- Existing personalised recommendation workflow with disclosed partial current-market context.
- Real Groq-powered conversation/tool actions only where actual integration is verified.
- Saved profiles/conversations/CVs and hosted login only after the release tests pass.
- RunPod GPU training on synthetic scenarios only after a successful recorded fit.
- No established real-world forecasting accuracy; no invented national demand coverage or legal certification.

Minimum security acceptance includes server-verified login and owner checks, private file access, server-only secrets, safe rendering of model/source content, bounded uploads, action validation/idempotency, appropriate request-origin protections for the chosen session scheme, and no private-data logging. Passing these checks is not a legal-compliance certification.

Current official references checked on 24 October 2026:
- Replit publishing and filesystem constraints: https://docs.replit.com/build/troubleshooting
- Replit publishing workflow: https://docs.replit.com/build/publish-your-app
- Railway fallback deployment: https://docs.railway.com/quick-start
- Railway persistent volumes: https://docs.railway.com/volumes
- Replit database: https://docs.replit.com/features/data-and-storage/sql-database
- Replit App Storage: https://docs.replit.com/features/data-and-storage/object-storage
- Replit Clerk Auth: https://docs.replit.com/features/auth-and-identity/clerk-auth
- Replit Auth: https://docs.replit.com/features/auth-and-identity/authentication
- Clerk Python integration: https://clerk.com/articles/how-to-add-authentication-to-a-python-backend
- RunPod credentials: https://docs.runpod.io/get-started/credentials
- RunPod billing: https://docs.runpod.io/accounts-billing/billing
- RunPod endpoint controls: https://docs.runpod.io/serverless/endpoints/endpoint-configurations
- XGBoost GPU configuration: https://xgboost.readthedocs.io/en/stable/gpu/
- GitHub merge methods and history: https://docs.github.com/en/pull-requests/reference/pull-request-merges

Use the installed package versions and actual account interfaces. These references do not verify your account balances, the repository's current implementation or competition eligibility.

