# A-N3 — one origin-linked, review-only Mindbot handoff

Continues A-N2 f4693e87a753043560dc900f9fb37a6e3e076fe0. No migration, second
conversation, scorer change, frontend edit or provider switch.

Minder explicit planning/change requests use existing real typed generation. The
server validates target IDs, observed record versions, explicit times, effort and
capacity before making a preview. It atomically saves one owned generic handoff,
one existing executor proposal (for task/profile changes), and one linked notice
in the existing singleton Mindbot. Source conversation/message/request IDs and
relevant prior message IDs remain linked. No task/schedule changes on arrival.
Ordinary questions suppress unsolicited actions and do not create events.
Unavailable generation or missing feasibility inputs produce needs_input, not a
fake actionable success. Direct Mindbot authority is unchanged.

## F integration contract

Conversation response metadata is `response.diagnostics.handoff`, NOT a new
unregistered top-level field. It contains event_id/version/status/kind and source
and Mindbot message/conversation IDs. Keep the user in Minder.

GET /api/product/minder-handoffs returns {policy_version, events:[...]}, newest30.
Each event has version, status=pending|needs_input|applying|approved|rejected|stale,
kind=action|roadmap|clarification, source_excerpt, clarification_code, preview.
Action preview is the existing {preview:{proposal_id,request:{kind,target_id,
expected_state_version,diff}},preview_hash,status,target_changed:false} envelope.
Show readable before/after fields. Roadmap preview has kind=save_roadmap, role_id,
plan with tasks, draft_id, expected_generation_version, expected_profile_version,
activated:false. Show the concrete draft. Approval saves once; it does not activate.
Existing proposal controls remain supported; GET projects their actual applied or
rejected state so a second panel cannot falsely show pending.

POST /api/product/handoff-decision exact body:
{event_id, decision:"approve"|"reject", expected_version, idempotency_key}.
All fields are strings. Use the event's returned version and a stable unique key
per click/decision. Return {event,result,target_changed}. Show actual result and
refresh canonical profile/plan/progress. Do not optimistically claim changes.
HTTP409 means stale target, stale event or conflicting decision; refresh and let
user review a new proposal. Do not automatically retry a write with a new key.
The same exact key/body replays its saved result. Owner isolation, rejection,
current-version validation and canonical operation idempotency remain enforced.

## Checks and limits

191 backend tests pass in10.738s, including seven new canonical SQLite handoff
checks: source linkage; exact-turn replay/one proposal/one singleton notice;
rejection with identical targets; approval once + application reconstruction;
foreign owner; stale target; ordinary question; roadmap acceptance without
activation; concurrent same approval; existing proposal panel projection.
These are declared-provider software checks, not real Qwen/browser acceptance.
Log ml/artifacts/session-a/product/morning/next-handoffs-full-permitted.log.
The first scheduling fixture failed because effort and capacity were unknown.
Tests now explicitly provide those through canonical input routes; guards stay.
An initial sandbox-only run could not bind ephemeral HTTP sockets; the permitted
run passes. Raw inputs, DBs, browser profiles and private native traces are excluded.
