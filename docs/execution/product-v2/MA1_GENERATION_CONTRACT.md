# MA1 early consumer contract — typed guidance v1

M0 dependency719c873. A implements generation.py/generation_schemas.py and
message_orchestrator.py. Exact containing SHA is published with this checkpoint.
Actual model stays qwen/qwen3.8-27b. No scoring policy or market scopes change.

POST /api/chat retains legacy fields, adds response_mode=generated_guidance and
conversation_policy_version=minder-typed-guidance-v1. generation is null on provider
or validation failure; otherwise {policy_version,draft_id,status:unsaved_draft,
model,profile_version,advice,claim_scope}. advice has kind,answer,assumptions[],
questions[],stages[{title,outcome,tasks[{title,description,estimated_hours}]}],
fact_ids[],operation. The actual schema is generation_schemas.SCHEMA. answer is
also a readable plain-text rendering for older consumers. Render via textContent,
never model HTML. Advice is unsaved practice guidance; effort is proposed, not user
capacity. No fit/demand scores, claimed mastery or invented forecasts.

F should render advice stages/tasks and assumptions/questions, distinct from
source-backed statement cards. Do not duplicate answer plus full identical draft.
A model/provider failure returns limited_fallback, generation:null, truthful error,
no invented outline. Real generation is not a model-independent canned capability.
Questions about empirical market/evidence/ranking retain closed factual renderer;
free advice is not marked verified external evidence. Sources remain separate.

D callback app.conversation_turn_handler(owner,channel,message,history,request_id,body)
is installed by Application. history accepted visible entries {role,content} (or
text / assistant response.answer). Only current channel recent6, bounded text; no
cross-thread/raw CV injection. D persists turn and visible response, calls outside
transaction, reserves key before invocation. Add POST /api/product/conversation
for browser-readable open {conversation_id}, since fetch GET bodies are unsupported.
A registry includes this alias. Do not rely on GET bodies from frontend.

Operation selection is typed real model interpretation; server resolves owned task
and current version. Specific unambiguous completion/date-time commands can execute
through existing ActionExecutor; suggestions create immutable proposals. Exact
instruction quote is verified against current message and restricted imperative
framing, never a prior assistant/document. Ambiguous target/time or failed constraint
gets clarification/error. No mutation retry or model-produced authority. action_status
and action_result/action_error reflect executor outcome, never model assertion.
The first v1 operation schema supports complete_task/reschedule_task; other requested
operations still need typed orchestration and must not be portrayed as available.

## D/F additive onboarding and CV agreement

Canonical Profile now permits optional onboarding with stage/objective/context,
education_level/institution/interests/work_areas/optional_enrichment. Read exact enum/
bounds in contracts/parallel-services.v1.schema.json. D adds onboarding to save_profile
allowlist and preserves omission semantics; D/F decide matching enum UI labels from
approved design. This is self-report metadata, no scoring/mastery change. Existing
anchored Evidence and Preference semantics remain required for numerical assessment;
a mockup self-rating does not become an approved rubric.
DocumentUpload now requires purpose cv|resume. D persists new purpose; legacy records
are unclassified (never silently classified). Metadata enum includes unclassified.
F uses explicit CV/resume selection, not a general document vault. D owns backend
validation/metadata/migration and focused tests. pypdf>=5,<7 is in root foundation
requirements for bounded text PDF extraction, no OCR. Install only into a lane-owned
isolated environment, never mutate shared interpreter while lanes run.
E hosted Clerk requirement is separately recorded in morning-requirements.txt for
Python3.12; existing3.9 remains. E supplies actual secure auth adapter handoff.
