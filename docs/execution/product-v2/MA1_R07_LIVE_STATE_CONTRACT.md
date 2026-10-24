# MA1-R07 — registered generated-plan acceptance and canonical daily worker

D3299176066dcee3e2f5244986e04affc19994c8f integrated. All generation_state.OPERATIONS
are now registered: GET generations, POST generation{draft_id}, POST generation-accept
under /api/product/. Read exact MD1.3/D accept schema; never send model advice from
browser as authoritative input. Successful A generator calls D record_generation,
then exposes generation.record_version (actual Store version) to F. The original
immutable stored generation has the original7fields; record_version is server-output
metadata only. F acceptance uses it as expected_generation_version; exact repeat
replays same canonical plan. Separate explicit direction activation remains required.
No-profile generation is useful but acceptance needs a partial saved source Profile;
if Profile changed since generation, request regeneration/review rather than guessing.

Current guidance-v1 facts list is empty: factual questions use the separate closed
source renderer; practice guidance is proposed advice. materializer rejects unknown
nonempty fact_ids instead of discarding citations. That is an unsupported draft,
not evidence that an arbitrary matching ID proves a claim. Applicable role-fact
retrieval/revalidation can be added as a bounded refinement without changing scoring.

Task/profile actions now guard exact pre-provider Profile revision and server-stored
observed plan versions. If another view edits state while Qwen is pending, stale
instruction is not widened to the newer state. Server ledger contains only own
version references/visible answer, not hidden reasoning or raw CV.

agents.configure now delegates D save_automation_settings. Existing PUT
/api/agent-settings {settings,expected_version} accepts D enabled/check_time/timezone/
state/scope. GET same route returns canonical settings including next_run,last_result.
No new route or scheduler. Worker uses schedule timezone (independent of Profile),
explicit scope, next_run/due check and one today's catch-up. Same daily date+scope
fingerprint deduplicates; changing time/timezone/scope invalidates queued old scope.
Completed same-day legacy events aren't rerun on upgrade. Pause/cancel invalidates
processing leases and result commit returns actual paused/cancelled status, no
phantom notice. Successful real notice/event completion records D last_result and
next_run in the SAME transaction, with one singleton Mindbot message. Old backlog
is superseded, not a run storm. E cohost wrapper can verify this exact Worker now.

26 focused software checks passed, including UTC Profile vs MY automation timezone,
next_run, stored last_result/message, missed-day catch-up/dedupe, cancellation during
analysis with no notice, exact turn/action replay, draft acceptance and state scopes.
One initial pause/resume test mixed a real24Oct config clock with simulated27Oct run;
fixed the test to one explicit schedule clock, no behavior/guard was relaxed.

F can wire acceptance and schedule controls immediately after this immutable commit;
E can run actual worker integration independently. Conversational configure_automation
operation is still explicit pending until its next bounded action tool refinement;
UI configured canonical schedule and worker are live locally. No hosted/login/GPU
acceptance or deployment is claimed. External account/volume/Clerk access remains.
