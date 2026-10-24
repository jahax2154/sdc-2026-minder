# A-N0 — mandatory starter, live evidence, cross-chat approval and ordinary pace

Base c7953a378871e1293760cf24757ab4c47f6c6dbe. This continues and preserves the
completed functional repairs. The latest user explicitly requires these additional
behaviours; the old18/18 anchored-intake/65second acceptance is not proof of them.
No new billing, provider model switch, paid job, main merge or worktree overwrite.

## Baseline findings and lane release

At c795: ordinary onboarding produces zero assessed recommendations unless a user
later enters three source anchors. That is not usable initial recommendation
acceptance. No application internet retrieval tool exists: stored source URLs and
this agent's browsing tool are not a deployed application capability. Existing
Minder action routing does not supply the required durable one-message/proposal
handoff to the singleton Mindbot. The native model transport discards rate headers
and ordinary guidance uses the large roadmap/action schema on every turn.

A implements bounded new backend modules and shared contracts. F remains sole
frontend writer. D remains sole Store/migration/profile/plan/conversation writer;
A reuses its existing transaction-capable exported state operations and generic
records rather than editing D files or creating a second database. E retains
host/auth/deployment, C original provider/grounder/budget files remain untouched;
A will coordinate calls/transport diagnostics through A-owned runtime adapters.
B's explicit paid-job hold stays active.

## F early integration contract — implement with the coming A checkpoint

1. Normal short onboarding gathers stage/field (or uncertainty), interests (or
   unsure), self-reported skills/experience (including explicit none) and weekly
   study time or uncertainty. No CV/source-anchor/competency-rating requirement.
   A adds typed optional onboarding metadata: self_reported_skills:string[],
   experience_state:none_yet|provided|uncertain, experience_summary:string,
   interests_uncertain:boolean, weekly_study_hours:number|null. Existing stage,
   context, interests, objective remain. Known study time also uses the existing
   canonical weekly_hours constraint for pathway feasibility; no skill evidence.
2. POST `/api/product/starter-recommendations` `{limit?:1..5}` reads the saved
   normal intake. Response has policy_version=starter-exploration-v1, mode=starter,
   status=provisional, options[] (role_id,label,explanation,matched_topics,sources,
   market_evidence,requirements), coverage and limitations. No personal fit number,
   proficiency claim or invented market coverage. Catalogue IDs are validated.
   Display up to five as initial provisional directions immediately; preserve
   full-catalogue exploration, selected career and explicit negative/reset controls.
   Existing assessed matching stays separate and unchanged; do not replace its
   no-assessment result with a fake assessed score. Starter details follow normal
   selection→generate→save→activate→four distinct My Path views→complete/refresh.
3. Live factual chat returns source-supported answer/citations with actual fetched
   page title/URL/publication date (nullable), retrieval time and geography. F must
   render citations and source/unavailable states. No complete Profile required.
   A supports credential-free bounded official public-page retrieval; no search
   subscription is needed for that path. Public HTTP queries contain no CV or
   private conversation. Future broad search APIs may need separately named access.
4. Minder planning/specific change requests remain in Minder. A persists a
   handoff event linked to the originating saved message/request, prepares an
   approval-only draft/proposal and appends exactly one notice to existing Mindbot.
   Response exposes `handoff` metadata; GET `/api/product/minder-handoffs` reads
   owned events/previews. POST `/api/product/handoff-decision` takes event_id,
   decision=approve|reject, expected_version and idempotency_key. Task proposals
   reuse the existing executor/current-version validation. Planning drafts reuse
   canonical generation acceptance; approval saves once, activation remains an
   explicit separate choice. F shows concrete before/after or draft task preview,
   reject/approve and actual saved result; no redirect or automatic task writes.
   Ordinary questions create no unsolicited handoff. Existing direct Mindbot
   authority remains unchanged. Exact DTO/examples come with the A implementation.
5. Honest provider waiting/status may expose queue_ms/retry_after_seconds and
   bounded error codes. Keep exact-request receipt recovery; no auto-replay of
   writes. Do not use a65second artificial pause as conversational readiness proof.

## A phases / verification

A-N1 starter policy/schema/normal-intake API and actual-source software checks.
A-N2 actual public-page retrieval, typed grounded explanation, no-profile live proof.
A-N3 origin-linked transactional handoff and once-only approval/rejection/replay.
A-N4 actual Groq headers, concise ordinary-turn protocol, shared chat/background
coordination and bounded honest queue/cooldown. Preserve original quota failures.
A-N5 exact committed F/E integration; fresh normal onboarding only, live no-profile
web question, plan/progress, cross-chat reject/approve, ordinary consecutive turns,
refresh/restart. Report passed/failed/blocked individually with actual evidence.
Commit/push bounded phases; do not claim the new gate passed from old evidence.

## E exact baseline source confirmation

c7953a378871e1293760cf24757ab4c47f6c6dbe is accepted for an **explicitly labelled
baseline managed judge-preview smoke deployment**: application/deploy bytes are
identical to prior accepted40d55c2, with final evidence/docs added. This is not final
acceptance of the four new requirements above. E may finish private account,
real Clerk preview/JWKS/session validation and mounted-volume setup in parallel;
never advertise the baseline as having live retrieval or starter/handoff features.
The final judge candidate must be a later A-named tested integrated source after
these repairs. E d6b18e3 is a committed tooling handoff to inspect/integrate; no
secrets or private config may be copied into Git or client bundles. Source/runtime
will retain Qwen and existing resources; no upgrade or new subscription is allowed.
