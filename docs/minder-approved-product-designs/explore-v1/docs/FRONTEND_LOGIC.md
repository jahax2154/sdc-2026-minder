# Minder Explore — frontend logical context

Version 2.0 · 24 October 2026

## 1. Scope and source of truth

This package implements the accepted Explore information architecture and local interactive behavior. It does not establish that matching, chat, agents, authentication, or market data are integrated into the real Minder backend. Keep the existing repository's authoritative API and matcher contracts when integrating.

The sidebar hierarchy is Explore → Careers and My Path. These are separate documents in the multipage source. The standalone HTML uses distinct page routes for portability and preserves exactly the same hierarchy. Never reintroduce a Careers/My Path switch inside the content area.

## 2. Routes and information

| Multipage route | Standalone route | User question and displayed content | Main actions |
| --- | --- | --- | --- |
| careers.html#matches | #/careers/matches | Which directions fit? Leading match, short rationale, score meaning, alternatives | View career; compare; refresh; search |
| careers.html#start | #/careers/start | What will matching use? Fictional profile summary and clear starting action | Review profile; Find my matches |
| careers.html#detail/ml | #/careers/detail/ml | What does this work involve? Work, fit, unknown skills, next learning areas | Compare; inspect explanation; Build my path |
| careers.html#compare | #/careers/compare | What differs between options? Two roles with consistent criteria | Change either career; View career |
| careers.html#outlook | #/careers/outlook | What possible directions should I consider? Two labeled scenarios and assumptions | Compare directions; View sources |
| careers.html#sources | #/careers/sources | What supports these outlook claims? Honest no-source state in this demo | Return to Outlook |
| my-path.html#next | #/path/next | What should I do now? Current milestone, first unfinished task, two following actions | Open task; complete/undo; all tasks |
| my-path.html#task/t4 | #/path/task/t4 | How do I complete this task? Instructions, criteria, resources, note | Complete/undo; save note; download CSV |
| my-path.html#roadmap | #/path/roadmap | How do the steps connect? Three milestones and actual task counts | Continue/view milestone; adjust preference |
| my-path.html#milestone/1 | #/path/milestone/1 | What work belongs to this milestone? Its task list and count | Open task; complete/undo |
| my-path.html#skills | #/path/skills | What capabilities matter and what is known? Contextual skills, self-reports, unknowns | Update self-report; open linked practice |
| my-path.html#progress | #/path/progress | What did I accomplish? Completion, recent tasks, evidence notes | Add evidence; return to next step |

Career IDs: ml, ds, de, ai. Task IDs: t1–t8. Milestone indices: 0–2. Detail routes keep the parent navigation item selected. Invalid IDs show a recoverable not-found message. Browser Back/Forward works with document and hash navigation.

## 3. Core workflows

### A. Discover and choose

Open Explore → Careers → Matches. Inspect a career without changing the active plan. Compare two different roles if useful. Build my path is a distinct explicit action. Selecting the current role reuses its plan. Selecting a different role presents a confirmation explaining that current work remains saved. A new role starts with unfinished tasks; a previously visited role restores its own work. Continue on the separate My Path page.

The preview already contains one sample plan so every screen is reviewable immediately. Preview options → No active path exposes the first-time My Path empty state. Preview options → Before matching exposes the matching entry state. These developer-preview controls are not production navigation requirements.

### B. Take action and review

My Path → Next steps chooses the first unfinished task in plan order. Open task shows what to do and what completion means. Checkboxes in the criteria list are working notes, not an automatic completion trigger. Mark complete is the explicit task-status mutation. It updates the next action, milestone counts, and Progress. Undo reverses the same status. A reload retains it when browser storage is available.

Task notes and work records are escaped before rendering. CSV download is a small generated practice dataset. Resource guidance is embedded and available without a network connection.

### C. Review skills

Skills show the selected direction's learning context, with one shared demo skill state. Unknown information remains Not assessed. Task completion does not change skill levels. A user may explicitly change a self-report using the labeled assessment dialog. Production must keep self-report, assessment evidence, and skill requirements separate.

### D. Reconsider direction

Careers → Outlook explains two illustrative directions. Compare these directions opens the same comparison experience with ML Engineer and AI Application Developer selected. Sources opens an explicit no-verified-market-data state. There are no invented forecasts or news metrics. Reconsidering a career does not mutate a plan until Build my path is confirmed.

## 4. Shared domain state

| Resource | Ownership and rule |
| --- | --- |
| Profile / skills | User-level information; one canonical set across modules; preserve source and unknown state |
| Career catalogue | Shared role IDs and descriptions; backend-reviewed facts in production |
| Match result | Matching engine output; frontend must not calculate a second score |
| Career plan | One retained plan per role in this reference, with a selected active plan |
| Milestone | Named outcome grouping ordered tasks |
| Task | Belongs to its plan and milestone; explicit status, criteria notes, optional work note |
| Evidence | User-entered work record; not independent verification |
| Progress | Derived from stored tasks; never a separately editable percentage |
| Outlook scenario | Assumptions and possible direction; not a probability forecast |

The package stores a versioned demo object at `minder.explore.reference.v2` in localStorage. Fields include expanded, matchesReady, compare, activePlan, plans, and skills. Each plan contains career, tasks, hours, and evidence. Storage exceptions are caught and reflected as session-only storage. This is not authentication or production data isolation.

Default milestone counts: foundation 2/2, data project 1/4, baseline model 0/2. Total 3/8; milestone completion 1/3. Completing t4 yields 4/8 and milestone 2 at 2/4. Empty plans must never imply career readiness or divide by zero. Fully completed plans show a completion state and link to review.

## 5. Interaction rules

- Explore parent toggles its child menu without changing the page.
- Selecting Careers or My Path changes document/page route. Only its local rounded bar is displayed.
- The sidebar shortcuts resolve to the same My Path routes and state; they are not independent task/roadmap modules.
- Search is local to the active page: careers on Careers, task titles/skills on My Path. It opens the appropriate result view. Clearing returns all sample content.
- Comparison uses two different roles. The demo initializes ML Engineer and Data Scientist; changing one selector to the other current role is rejected with feedback. Selecting alternative checkboxes retains at most two IDs; entering Compare with fewer than two uses the documented default pair.
- Weekly time preference is editable and saved, but this prototype does not reschedule or regenerate work.
- No automatic task, skill, or plan mutations are performed by chat/agents.
- Ask Minder shows its context and a draft field with an explicit no-AI-integration note; it sends nothing.
- Overview, Mindbot, and Profile provide boundary explanations. They are not silently broken links and are not simulated backend functionality.

## 6. Screen states

Implemented and reviewable: seeded content; before matching; brief sample matching transition; no active plan; empty career search; empty task search; invalid career/task/milestone; complete plan; task completed/undone; local note saved; explicit skill self-report; browser storage unavailable fallback; and no market evidence.

Production integration requirements: API loading/skeleton, unavailable matching engine, insufficient profile, empty match response, failed plan creation, failed status save with rollback/retry, unauthorized session, stale/updated plan version, and failed source fetch. These must be driven by real API outcomes. They are specified here but not claimed to be exercised by a real backend in this standalone package.

## 7. Suggested backend integration boundaries

Keep the currently established API contracts; do not infer new route authority from the static HTML. Map typed application adapters to profile reads/updates, career catalogue, matcher results, plan create-or-return, plan/task mutations, and sourced scenarios. The frontend navigation can change without rebuilding the backend's domain boundaries.

The server owns user/session identity and record authorization. Do not trust an arbitrary browser-provided user ID. Persist task status and derive counts from that canonical state. On failed writes, preserve the user's input and display a retryable error. Selecting the same plan should be idempotent; archived plans must retain completed work.

Model responses need score_type, explanation factors, engine_version, and source metadata. Market sources need publisher, URL, publication/retrieval date, region, and assumptions. A score is not a hiring probability without a valid calibration contract. The current 80/100 is demo data only.

## 8. Integration order and acceptance

First port the sidebar hierarchy, two page routes, shared tokens, and local bars. Then wire the narrow profile → match → choose plan → task complete → persisted progress journey. Add skill editing, scenarios, and contextual chat only after their contracts are ready. Use the existing Minder design components where available instead of duplicating the shell.

Acceptance: Careers and My Path have different routes and headings; no content-area switch connects them; exactly one local feature is visible; a selected career is distinct from a viewed career; completing and undoing a task updates every relevant view; a reload retains state; switching back restores prior work; unknown skills remain unknown; no task automatically proves proficiency; no fake source appears; keyboard and narrow-screen navigation remain usable.
