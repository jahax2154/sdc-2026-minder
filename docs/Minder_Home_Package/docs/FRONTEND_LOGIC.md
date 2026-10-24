# Minder Home — frontend logical context

24 October 2026 · Interactive frontend reference and integration contract

## Scope and ownership

Home assembles summaries from the existing Profile, Careers, My Path and Mindbot domains. Production must not create a second profile, task list, progress calculator or agent inbox just for Home. This standalone package uses browser-local fixtures to make the states reviewable without a backend. It does not share storage with the previous Explore demo; replace the fixture store with the actual shared application store during integration.

The correct term is Mindbot. It is the user's personal agent; its Home panel is a summary and entry point, not an additional agent product.

## Independent state model

| Area | Independent states | Main data |
|---|---|---|
| Profile | Not set up / Ready | Name, background, interests |
| Direction | Needs profile / Ready to match / Matches ready / Chosen without path / Active path | Matching result, user-selected career, path existence |
| Next steps | No path / Tasks / Skills / Progress | Active path, next task, skill practice, completed work |
| Mindbot | Unconfigured / Configured & paused / Enabled with message / Enabled & quiet | Name, enabled flag, preferences, pending message |

Only dependency-related views change. Profile setup unlocks matching; it does not create a path or configure Mindbot. Choosing a career does not create tasks. Creating a path enables meaningful Next steps; Mindbot stays untouched. Configuring Mindbot does not complete the profile. Completing a task changes the task recommendation and derived progress; it does not automatically upgrade a skill. Profile edits preserve the chosen path and all work.

The implementation may rerender the shell but preserves independent stored state. A production component implementation should isolate updates, preserve input/focus state, and cache shared queries.

## Main user workflow

1. First visit: name from the signed-in account, profile setup invitation, matching prerequisite, empty Next steps, Mindbot setup invitation.
2. Save profile: profile summary replaces invitation; Find career matches becomes available. No other setup is implicitly completed.
3. Find matches: show a result-ready state. Review possible directions in Careers (Matches / Compare / Outlook). Never choose a career on the user's behalf.
4. Select a direction: show the selected career and Build my path. Next steps is still empty.
5. Create a plan: populate My Path and derive the Home summaries from it.
6. Open the recommended task: inspect definition of done; save evidence/notes; mark complete.
7. Review progress: counts and latest completed work update from the same task state.
8. Mindbot can be configured before, during or after steps 1–7. Show quiet help when no message requires attention.

## Home content and action mapping

| Home control | Production destination | Standalone behaviour |
|---|---|---|
| Set up / Edit profile | My profile editor | Profile form dialog; saves locally |
| Find / Review career matches | Explore → Careers → Matches | Explicitly illustrative match dialog |
| Explore other careers | Careers | Match dialog; prevents replacing an active plan here |
| Build my path | My Path plan creation | Explicit sample-plan confirmation |
| Continue my path / My roadmap | Explore → My Path → Roadmap | Milestone summary dialog |
| Open task / My tasks | My Path → Next steps / task detail | Task dialog or list |
| View all skills | My Path → Skills | Skill/evidence summary dialog |
| Review progress | My Path → Progress | Progress detail dialog |
| Set up / Manage Mindbot | Mindbot settings | Name, enablement and suggestion-preference form |
| Review suggestion | Mindbot message detail | Accept/dismiss dialog |
| Message agent / quick prompts | Mindbot conversation | Local draft composer, clearly not sent |
| Ask Minder / New conversation | Minder Chat | Explicit integration explanation |
| Search anything | Application-wide search | Quick navigation dialog, not global search |

The dialogs are functional review equivalents for a Home-only deliverable, not replacements for the full feature pages. Rewire these actions to the existing application router in production. No broken links to absent modules are included.

## Next steps switch

- Default is Tasks. Selection is manual and persists locally; never auto-rotate.
- Before a path exists, all three tabs remain selectable with truthful, tab-specific explanations.
- Tasks: one recommended next task, its estimate/skill and optional schedule; one following task; full-list action.
- Skills: one relevant skill, an explicit self-reported practice status and action to practise. Saved work notes are unverified evidence.
- Progress: completed task count over all path tasks, latest completed work, and current milestone count. Counts derive from task state.
- Home does not duplicate the full Roadmap tab; Continue my path leads there.

## Mindbot behaviour

- Unconfigured: Make Mindbot yours; explain the personal agent; Set up Mindbot.
- Configured, disabled: paused message; saved preferences; Manage Mindbot.
- Enabled, pending proposal: agent identity, one message, Needs your review, Review suggestion, Open Mindbot. A real app should order actionable/urgent messages ahead of informational ones and provide a remaining-message count.
- Enabled, quiet: You're all caught up; How can I help you today?; two optional prompts and composer entry.
- Accept: apply the exact reviewed change once, acknowledge it, resolve the message, recompute relevant summaries. Demo schedules the data-cleaning task for Friday only in local data.
- Dismiss: resolve the message without touching task state.
- Disabling suggestion visibility hides the demo pending message. Production should persist visibility preference separately from read/resolved status and preserve inbox history.
- Setting up Mindbot does not fabricate a message. The sample message is available only through the explicit preview-state fixture.
- A bot being enabled does not grant tool access or permission to act. Production permission scopes, confirmation rules and audit records are separate integration responsibilities.

## Demo store and limits

Storage key: `minder.home.reference.v1`. Versioned plain JSON contains profile, matches flag, selected career, path flag, selected tab, bot settings/message status, task completion, work note, task schedule, optional draft, and Explore expansion. No network request, cookie, package install, font download or external API is required. Storage errors fall back to in-memory use. Do not treat localStorage as production authentication or secure storage.

The eight-task example has three previously completed fixture tasks. Creating the sample plan explains this before loading it. Completing Clean a small dataset changes 3/8 to 4/8 and milestone 2 from 1/4 to 2/4; undo reverses that. Milestone 1 remains 2/2 and milestone 3 remains 0/2. Task 5 opens a read-only example detail; full task editing belongs to My Path. The two career choices share a demonstration plan, not a production role-specific curriculum.

User-provided text is length-limited and HTML-escaped. Name/background/interests and agent name reject empty/whitespace-only input. Dialog forms do not transmit data. A draft message is saved, not sent. The greeting is fixed to morning for visual comparison; production should use local time and account identity.

The URL parameter `state` selects a deterministic fixture on every load. Remove it for normal persistence testing. `reference=1` applies a 94% screenshot-only scale. Preview states replace demo data only when explicitly selected through the picker; direct query fixtures are rendered immediately and subsequent interaction can persist them. Remove all fixture controls and query-driven state injection from production.

## Available fixtures

| Query value | Purpose |
|---|---|
| first | Profile, path and Mindbot not configured |
| profile | Profile ready; other setup untouched |
| matches | Matching results available but no chosen direction |
| chosen | Chosen career; plan not created |
| active | Active path, Tasks tab, pending Mindbot suggestion |
| quiet | Active path, Skills tab, enabled Mindbot without messages |
| progress | Active path, Progress tab, quiet Mindbot |
| bot-only | Mindbot configured while profile and path remain empty |

## Backend integration requirements (specified, not implemented)

- Profile service owns profile readiness criteria and revisions.
- Careers service owns match results, source/provenance and stale-result status. After profile edits mark outdated matches for refresh without silently replacing a chosen career.
- My Path owns plans, milestones, tasks, evidence and explicit completion timestamps. Derive counts; don't store divergent Home totals.
- Skill records distinguish self-report, practice evidence and verified assessment.
- Mindbot owns settings, inbox/messages, drafts, actions, permissions and action outcomes.
- Use stable IDs, request deduplication and optimistic concurrency for task completion and accepting agent actions.
- Fetch areas independently. A failed Mindbot request must not blank an available profile or task panel.
- Loading: reserve each section's shape and use understated placeholders. Error: keep last-known data with a scoped retry; never replace an error with an onboarding invitation.
- Empty inbox differs from offline/error. Only show You're all caught up after a successful inbox read.
- An all-complete path should show completed work and a review/next-goal action, not an invented task. Demo illustrates only partial completion.

## Acceptance criteria

1. Mindbot is the label everywhere in live HTML and documentation.
2. Four stable areas; no analytics tile grid or auto-rotating content.
3. Profile-only setup leaves task and Mindbot empty states intact.
4. Bot-only setup works while profile is incomplete.
5. A chosen career is distinct from computed matches and an existing plan.
6. Keyboard and pointer can select Tasks, Skills and Progress.
7. Task completion and evidence persist without implying assessed proficiency.
8. Agent proposal review does not apply a change before acceptance.
9. Reload persists browser-local changes when no fixture query is active.
10. Mobile layout stacks in a predictable order and keeps all three tabs accessible.
