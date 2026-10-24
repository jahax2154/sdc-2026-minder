# F-FG1 functional repair

Verified against A's committed backend **0a39b392b1f2b594abb8b23a4f0a8f73a4bec0c4**, normally integrated with all prior F ancestry. F-only code changes; no backend/schema/scoring/provider/migration edit. Existing approved layout preserved; redesign/animation deferred. Actual F UI:http://127.0.0.1:9106/#home, assigned API8106. No worker/deployment.

## Connections repaired

- Compare, role details and My Path Skills consume A role-display-v1: source labels, grouped10skills with19distinct measurements, separate importance/activity level and personal evidence. Software Developers Reading Comprehension shows3.5importance and4.25activitylevel, not averaged or converted to an invented scale. Source links/geography/dates and unassessed/clarification distinctions preserved.
- Full paginated public catalogue supplies authoritative names/options outside the first50; a single-result search cannot empty Compare. Saved direction is read from backend, separate from temporary Compare/detail/Outlook choices. Default Outlook uses omitted-ID owner-scoped reads and actual forecast/error status; explicit inspection is encoded in route. Viewing/continuing an already chosen career never rewrites direction or clears its active plan.
- Matching coverage uses actual server counts, with direct links to Profile Skills for missing evidence. No numerical policy changed.
- Four My Path tabs have distinct no-plan and active-plan content. Skills can inspect saved-career requirements before a plan exists. Next uses canonical overview next_task and checks active-plan identity, matching Home. Roadmap reads accepted stages; Progress reads persisted canonical activity counts.
- Accepted roadmap Open My Path now refreshes on the same route; this previously left the saved-draft review onscreen despite successful activation. Review defaults/labels use saved direction, including careers outside the first catalogue page.
-409career/task writes disable stale actions and offer local saved-state reload before an explicit new action. Transport failures offer exact retries and never automatic replay.
- Closes F-UX3-R01: native hidden wins over flex on exhausted/empty/one-result Load more. Closes F-UX5-R01: undated notice says Your saved update.

## Actual checks

`functional_connections.cjs`: real backend subset with explicitly synthetic profile fixture; sourced grouped measures, outside-first50savedcareer, browse independence/refresh, single-result search→Compare, failed read/local retry, four no-plan views, actual Load-more invisibility. Undated notice case is an explicitly controlled agents READ fixture.0modelcalls.

`functional_onboarding_plan.cjs`: fresh Home→actual UI onboarding, no seeded profile/plan; zero-evidence explanation→three UI-entered source-anchored self-reports→actual matching910personal assessments/five comparable current-market careers→UI Software Developers choice→Compare/Outlook refresh→real Qwen draft2561ms/three stages→explicit save→separate activation→working Open My Path→four distinct active-plan tabs→Home/Next same task→completion0/3to1/3persisted on refresh, same plan and no regeneration. One model call in passing journey; initial1942ms call exposed the same-route product bug and is retained as failure evidence. Two calls total, no model rerun for visual polish. Self-reports/test passes do not certify competence or approve numerical policy.

`functional_action_recovery.cjs`: real concurrent fixture writes produce409for career choice and task completion; local reload makes current state actionable, does not replay, explicit undo returns progress to0and preserves active plan.0modelcalls.

`morning_explore.cjs`: real legacy-plan fixture, canonical complete/undo/refresh and all Careers/My Path views;0modelcalls. `final_ux_partial.cjs`: stable DOM/slow+rapid panels/filter-focus-caret/local error retry trace. `final_ux_history.cjs`: real25rows, rendered Load-more visible at20then hidden at25/one-result search. Node syntax and git diff checks passed.

See [sanitized evidence](FUNCTIONAL_REPAIR_EVIDENCE.json) for exact backend revision, reports, private screenshots/trace locations and initial failures. Browser credentials never copied/exported. Existing raw/derived inputs untouched/not backed up; local env/database/uploads/browser profiles/PDF fixtures/screenshots/traces excluded from commits. No ignore rule added.

A should merge the cumulative F branch normally and restart its own isolated runtime before combined acceptance. No frontend capability is waived based on backend test passes. Live hosted Clerk/Railway acceptance remains A/E-owned and is not inferred from these local flows.

## F-FG1-R01 — active preference actions and smaller sourced surfaces

Primary tested/pushed F-FG1:c76fe768603850a7ba647420242420db10914d52. A's follow-up action auditcd6cea3 was normally merged (5ec18a0); backend implementation remains exactly0a39b392, no backend file changes.

Restored optional Interested/Not interested/Reset in active career detail using the existing direct-action update_profile contract. Same-state buttons are no-ops. Confirmed writes refresh Profile/invalidate match presentation; saved direction and skill evidence are preserved. Lost responses retain the exact action body, lock new choices, offer profile read plus exact receipt retry, and never infer completion from a matching profile value.409requires saved-state reload before a new explicit choice. No scoring/preference formula change or mandatory role rating.

Home Skills now resolves source-backed skill names and evidence explanations rather than exposing raw subject IDs or standalone numerical values. Explicit user-defined confidence labels/text remain user text, not competence. Schedule plan labels and saved-path listings resolve authoritative career names. These are data connections, not a new design.

`functional_preferences.cjs` passed actual interested→notinterested→reset, same-state no-op, refresh, deliberately lost real action response→profile read remains locked→exact receipt, no duplicate action/version, preserved evidence/direction. Real active legacy plan verifies Home Reading Comprehension, daily Software Developers label/scope/create/pause/resume/cancel;0modelcalls. Synthetic profile/legacy-plan fixture and one actual UI-entered self-report are explicitly identified.

`morning_profile.cjs` passed actual Profile→My Record→CV files/upload/extraction→explicit review, text PDF and scanned/manual recovery, mobile and dirty-edit guard. `morning_structured_proposals.cjs` passed actual typed proposals/reject/approve, unchanged state before decision, canonical task edit/schedule/cancel inside Mindbot, approved scope reflected in daily controls and malicious content inert. No new provider invocation for this refinement. Screenshots/report paths and hashes are in the evidence JSON.

All current functional frontend repairs are tested locally against A0a39b392; A combined acceptance remains separately owned. No new endpoints, backend edits, migrations, deployment or visual/animation polish.
