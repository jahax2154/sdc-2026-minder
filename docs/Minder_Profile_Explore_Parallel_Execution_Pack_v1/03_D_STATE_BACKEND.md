# D — shared product state backend

Read the common context, actual launch/ownership manifest, `07_DATA_AND_API_CONTRACT.md` and `08_EVIDENCE_AND_PRIVACY.md`. Work only in the assigned isolated directory/branch. D is not a new backend: extend the services C already uses for profiles, plans, tasks, proposals and actions.

## D1.1 — persistence and migration alignment

Inspect existing tables/models/service functions and map the logical entities in file 07 onto them. Preserve stable IDs, ownership, versions, foreign keys and existing data. Add only missing columns/relationships needed by the agreed journey; no framework or database replacement.

Take the migration-writer role only after A records the transfer. Keep a single ordered chain. Test an empty development DB and upgrade of a disposable copy at the previous schema revision. Check indexes/constraints needed for ownership and idempotency. Do not migrate another running lane's DB or commit DB files.

Publish the state-service interfaces that E/C need before all features are finished. If no migration is necessary, record reuse rather than creating one. Commit D1.1 with actual results and migration dependencies.

## D1.2 — profile and input evidence

Implement missing save/read/edit operations for education, experience, interests/preferences, goals, constraints, availability and skill evidence. Reuse existing chat-derived intake; do not have two sources of profile truth.

Permit partial saves. Preserve unknown versus explicit neutral/dislike versus assessed zero. Validate an allowlist of editable fields, sizes and references. Server identity determines owner; body/path owner IDs are not authority. Optimistic version conflicts return the established conflict state rather than overwriting newer input.

Skill entries retain source kind, scale, assessed/self-reported status and evidence references. CV extraction produces reviewable candidate fields; do not infer assessed competence from occupational importance or a title. Reuse supported uploads. If adding a missing minimal intake, explicitly define accepted types/size, non-executable storage, parsing errors, user correction and cleanup; do not add OCR or broad document ingestion unless already supported/needed. A parsing failure leaves structured entry available and visible.

After relevant edits, mark dependent assessment results stale or invoke the existing refresh mechanism. Do not change selected direction or roadmap automatically. Availability changes can inform C's proposal workflow; they do not themselves authorize all resulting schedule edits.

Verify partial/complete input round trips, refresh persistence, malformed data, unknowns, stale edits and cross-user isolation. Verify supported CV intake with fictional documents if present. Commit D1.2 and release this slice to E/F/A immediately.

## D2.1 — selected direction, plan and task writes

Reuse the existing goal/plan and agent action services. Implement missing explicit manual operations with the same domain rules.

- Select a supported direction without duplicating plans on retry. If replacing the selected goal, preserve existing history and make the chosen plan explicit.
- Return requirements/skill-gap availability honestly; a selected role can exist before a complete detailed preparation plan exists.
- Create/edit tasks with known plan/skill/resource references and optional schedule. User-created tasks need not pretend to originate from an official requirement.
- Complete/undo/reschedule using established transitions, persisted events and versions. Avoid duplicate completion events on retry.
- Keep active plan scope and dependencies coherent. Flag conflicting or impossible schedules rather than falsely claiming feasibility.
- Proactive rescheduling remains a proposal through C; manual explicit edits execute directly after normal authorization.

Test manual UI operations and C tools against the same records, including stale-write conflicts and retries. A completed API request is successful only when the intended state is persisted. Commit D2.1 and publish the usable task slice.

## D2.2 — progress and saved resource state

Expose one canonical progress calculation based on persisted state. Specify eligible tasks/denominator, cancelled tasks, parent/child treatment, chosen plan and observation time. Return counts as well as any derived fraction. Empty plans return an explicit empty state, not NaN or implied skill readiness.

Implement saved/unsaved and dismissed/reset resource relationships requested by E. Key by stable content ID and owner; repeated saves/dismissals are idempotent. These actions do not create task completions or change assessment skills. Add-to-plan is a separate explicit operation, preserving the resource reference and any unknown duration/cost.

If E needs cached content persistence, expose the agreed storage adapter through the same schema ownership; distinguish public content metadata from private user interactions. Do not make E invent its own user database.

Test completion/undo effects after refetch, goal switches, denominator consistency, saved-resource isolation and retry behavior. Commit D2.2.

## D3.1 — lifecycle, contract completion and handoff

Preserve existing correction/deletion/reset behavior and implement concrete missing lifecycle controls within assigned scope. Distinguish a demo reset from permanent account deletion. Pending jobs/proposals must not resurrect removed state. Do not invent a legal retention period; report actual unresolved operator settings.

Finish actual contract examples for normal, empty, invalid, stale, forbidden and unavailable states. Give E/F/C/A the exact dependency SHAs and any ordered migration sequence. Include actual commands and evidence, not only test totals.

Commit and normally push tested D checkpoints to D's assigned feature branch under file 10. Do not push A/B/C/main or deploy. Record partial capabilities honestly, including unsupported input formats; do not close them by omission.
