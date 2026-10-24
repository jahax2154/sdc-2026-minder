# Home actual state/read map — F implementation aid

Approved visual authority is docs/Minder_Home_Package plus the newer repair gate.
This map uses current implemented reads; no new aggregate store, ranking formula
or fabricated API. F owns all Home/client rendering; E owns additions to read views.

| Home region | Actual read / authoritative fields | Missing/error handling |
| --- | --- | --- |
| Greeting / Profile strip | GET profile: career_context/onboarding plus actual managed account fields where available | Missing name uses neutral greeting, not fixture Avery; profile error is not first-visit success |
| Direction / active path | GET product/views/overview: data.direction, active_plan | A selected role without active_plan is not a created path; preserve explicit selection/activation |
| Career label | Canonical role catalogue/detail for direction.role_id | Unknown label remains unavailable; no model-invented role |
| Next task | overview.data.next_task, already selected by backend prerequisite/unlocked/saved ordering | Null means no currently supported next step; do not invent a task |
| Task title/time | Canonical saved task.title, estimated_hours, scheduled_at | Generated estimates are proposed effort; missing effort/date remains unknown |
| Progress | overview.data.progress completed_count/eligible_count/fraction and denominator | Counts concern non-cancelled tasks in explicitly selected active plan, not all saved plans or skill mastery |
| Skills | GET product/views/progress skill_evidence / actual Profile evidence; current My Path representations | Self-report/practice/anchored assessment remain distinct; no inferred percent mastery |
| Bot name/avatar | GET product/bot-preferences from D committed implementation | configured means saved DISPLAY identity only; default My Bot/nimo-blue does not imply disabled bot |
| Actual schedule/status | GET agent-settings: state,enabled,timezone,next_run,last_result |404 means no saved schedule; errors remain errors. Never hide an actual active schedule merely because display identity was not customized |
| Same conversation | GET product/mindbot-conversation, paged open via product/conversation | This may get/create singleton but never creates a schedule; no per-event chat or automatic turn |
| Reviewable change | overview.data.pending_proposals or GET proposals; existing exact decision controls | Only actual pending proposals are reviewable. Reject/approve exact saved version, never regenerate/guess |
| Latest recorded activity | GET agents notices / agent-settings.last_result / persisted Mindbot messages | Quiet only after successful read. Local configured toggle is not hosted verification |

Overview uses D's consistent owner-scoped state snapshot. Its data.tasks can include
all saved plans when no active plan exists: **do not display those as active Home
progress/next steps**. active_plan and canonical progress are the boundaries.
The existing overview computes no model guidance and invokes no automatic global
matching request. Opening Home must not start ranking or regenerate a saved plan.

Matching-ready may use F's successful actual result cache, keyed by authenticated
owner and current Profile version and invalidated after relevant Profile changes.
No persisted server result-ready flag is currently exported; absence of an old
cached result is not failed matching or an invented recommendation. Link to explicit
Find matches. Do not add a second database or automatically recompute on every visit.

Current overview exports one next_task, not a second ordered eligible task. Existing
task lists are not equivalent to that readiness ordering. If the approved optional
following-task slot needs a new field, request E to expose it using the SAME existing
backend ordering; otherwise show the truthful main next step and My Path link.
Canonical milestone completion counts/most-recent-completion timestamp are not
currently exported by this overview. Reuse an existing validated My Path read if
available; otherwise request E's exact minimal projection or disclose absence.
Do not copy fixture milestone2/3, completed3/8 or Friday dates.

Bot customization does not itself turn on daily automation. Conversely existing
automation may run with the default identity. Display customization/configuration,
recurring state and actual delivered result separately. Custom name is untrusted
display text, not system instructions, a new agent or any change to authority.
Home drafts may open the same Mindbot composer explicitly; no implicit provider call.

Mutations reuse current Profile/task/plan/proposal/schedule APIs and version rules.
Refresh only affected reads, preserve successful other panels, clear owner caches
on identity change. Sources/market scopes and unavailable forecasts retain their
existing backend labels. Plain labels/CTA copy are UI; recommendations/explanations
must come from actual saved generation or backend source records when claimed.
