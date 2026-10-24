# MA2 combined acceptance findings — continuing

Actual A Python3.12 environment, committed f8675bd:143 backend discovered,141pass/
2fail, zero SDK/PDF skips; deploy4pass. Logs ignored morning/backend-312.log.
Failures owned by E test_hosted_worker.py (not a runtime due-work failure):
setup_schedule calls configure() at actual24Oct~06:40UTC and check_time00:00MYT,
which now correctly persists next_run25Oct00:00MYT; test tick uses24Oct06:00UTC,
EARLIER than creation and before next_run. Same issue for retry test reenabling.
Please E anchor save_automation_settings(...,at=explicit fixture time) and all
create/edit/tick instants coherently. Do NOT remove next_run due guard or fake
clock metadata. A own deterministic timezone/catchup/failure/cancel tests pass.
E owns its test file; A will merge committed focused correction only.

F178a7a8 reports actual realQwen draft2055ms, lost acceptance response/exact retry
one canonical plan, explicit activation, saved phases/refresh0generation and one-hour
follow-up preserving saved plan. A integrates this immutable slice next. This is
local real-provider behavior, not hosted login/durability or model accuracy.

A updated9111 at f8675bd with pinned private runtime3.12/PDF/SDK and local-development
private files. Actual unsaved screenshot request1654.629ms, Qwen available/intact
English intro+3stages+2questions, sourceProfile null,2savedmessages,0plans, exact
replay no new message. Detailed synthetic report stays in ignored morning artifacts.
Partial/unseen follow-up, rich current quality, actual action/provider failure/
combined browser/source/privacy checks remain in progress; old bounded evidence
is reused where applicable and all limitations remain explicit.

Hosting remains blocked on actual Railway resource/credit/volume access and managed
Clerk provisioning/two live accounts. No hosted login/history/CV/worker proof or
judge deployment has occurred. B actual GPU experiment proof pending latest handoff.
Do not mark the release complete while those required gates are missing.
