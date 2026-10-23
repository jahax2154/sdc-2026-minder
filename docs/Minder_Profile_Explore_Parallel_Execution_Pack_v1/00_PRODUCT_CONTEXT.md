# Product context and required behavior

## 1. Audience and purpose

Minder supports students and fresh graduates, career switchers, workers facing displacement or job loss, and people uncertain about their next direction. Understand the person, recommend supported directions, let the person explore, build a preparation path after direction selection, then track and update progress.

Collect education, skills/evidence, experience, CV/resume where supported, goals, interests, preferences, constraints and availability. Support structured inputs and the existing chat intake. A person may save a partial profile before they supply enough evidence for scoring.

Malaysia is the initial market scope. International companies with Malaysian opportunities remain eligible for the separate company-exploration behavior already agreed. Do not build foreign-market forecasts or let a chosen company silently replace overall role matching.

## 2. Navigation interpretation for this pack

Junhong's latest list is interpreted as five Explore destinations:
1. Career Match.
2. Progress.
3. Tasks.
4. Roadmap & Skills — the reskilling path and its skill requirements.
5. News & Trends — current relevant evidence plus articles, videos and other learning resources.

Profile is a separate main feature. Minder and Mindbots are separate conversational/agent features. Keep Overview as the existing entry point where present.

The statement about five features in News/Trends is ambiguous. This pack does not invent another five large submodules. Resource formats are filters within a feed, not separate systems. Preserve existing Future Explorer functionality and contracts: provisionally expose current/future market views from News & Trends, retaining existing routes or compatibility links. Keep a separate route if already implemented. Do not delete an existing screen or rename public APIs merely to change navigation labels.

This is a reversible navigation assumption, not permission to remove agreed capabilities. If Junhong supplies a different menu arrangement, adjust navigation without rebuilding the domain model.

## 3. Profile

Minimum functions:
- View, save and edit personal career context and study availability.
- Preserve evidence provenance and unknowns. Show focused missing-input questions from A's assessment service, not an invented completeness percentage.
- Support role/industry interests, explicit neutral/dislike, reset, goals and constraints using current policy semantics.
- Reuse supported CV intake; if missing, implement a bounded secure intake/extraction path only within assigned scope and record formats/limits. Structured entry remains usable independently.
- Let users correct extracted fields before they are treated as confirmed profile input. An extracted job title or course name does not establish proficiency.

Saving a profile may make an old assessment stale or trigger an authorized recalculation. It must not silently select a new role, rewrite a plan or reschedule tasks. Existing direct-action and proactive-proposal boundaries still apply.

## 4. Career Match

Consume A's existing scorer, supported catalogue, preference feedback and evidence policies. Consider supported roles across industries unless the user expressly restricts the search. A dislike is a reversible preference state, not permanent exclusion; repeated feedback is idempotent.

Required interactions: obtain current recommendations, inspect reasons/evidence, explore a role, give/reset feedback, and select a direction. Preserve the ability to explore even when numerical scoring is unavailable.

Do not compute another scorer in D/E/F. Do not reinterpret internal scores as hiring probabilities. Hide internal market matrices from ordinary UI/chat. Display understandable reasons, evidence dates/scope and limitations.

Latest reported implementation facts to verify against code, not blindly hardcode:
- provisional personal scorer and market policy v2.1 are active;
- active role activity weighting was reported as 85% personal and 15% market on supported comparisons, with bounded shortage context;
- only five roles had activity comparisons, seven related shortage contexts, and 907 broader sector contexts for one anchored example profile; counts overlap;
- historical industry scoring and broad-group scoring have different latest eligible quarters and are not interchangeable with role-level demand;
- observed skill request counts do not yet establish a normalized national skill-demand score.

Adding new ranking effects remains A/B work. Product presentation must accurately reflect the returned mode and scope, including personal-only results. Do not combine separately ranked populations into a new universal numerical order.

## 5. Roadmap & Skills

After selection, show the chosen direction, source-supported role requirements, existing skill evidence, unknown assessment areas and supported skill gaps. Map activities/tasks to requirements where the relationship is supported.

Distinguish: known required skill; known user evidence; insufficient evidence to assess; assessed gap. Missing evidence is not zero competence. A task completion or watched video is activity, not proof of mastery.

Display ordered preparation stages, actual planned activities, dates where known, resources and next steps. An activity suggestion is a proposal, not an external fact. Unknown effort, cost or prerequisites must stay unknown; user-entered estimates retain their source. Any generated planning estimate must be labelled and cannot masquerade as validated preparation feasibility.

Support explicit user plan edits through the same domain services as Mindbots. Keep previous goals/plan history when the user changes direction. Do not build a second roadmap engine or duplicate task store.

## 6. Tasks and Progress

Tasks: list/filter, inspect, create supported user tasks, edit, schedule/reschedule, complete and undo; support cancellation/archival only through established semantics. Record owner, plan, optional requirement/resource, status, schedule, version and event provenance.

Progress: derive from persisted tasks and events. Reuse the existing progress definition if valid; otherwise define the denominator explicitly in the contract. A useful default is completed non-cancelled leaf tasks divided by eligible non-cancelled leaf tasks in the selected plan. Do not count parent stages and their child tasks twice. A zero denominator is an empty-plan state, not a readiness percentage.

Keep activity completion, assessed skill evidence and career readiness distinct. Filters such as today's tasks must not silently redefine the whole-plan denominator. Goal switches identify which plan is displayed. Undo updates the same state and progress after refresh.

Use the user's timezone for calendar dates; default to Asia/Kuala_Lumpur only when no user setting exists. Preserve date-only deadlines as dates and instants with timezone semantics. Do not reschedule merely because a timezone conversion changed a displayed day.

## 7. News & Trends and resources

Deliver a bounded, useful feed relevant to the selected direction, skills and expressed interests. Include reliable current market observations and verified links to news, articles, videos, documentation, courses or reports. Show each item's actual type, publisher, source link and available dates.

Use existing B/C evidence/retrieval services and a small reviewed source list. Do not start an unrestricted crawler, create another market ingestion system, or fabricate links with an LLM. Metadata and permissible excerpts suffice for the first release.

Explain why an item is relevant using actual topic/role/skill mappings. This is resource relevance, not a new market-demand score. Do not claim a source proves an outcome just because a URL exists.

Allow view/open, supported filters and save/unsave/dismiss/reset where D implements persistence. Reading/saving does not complete a learning task. Adding a resource to a plan is an explicit user action or an approved concrete proposal.

Keep four meanings distinct: news attention; observed current market evidence; learning resources; actual forecasts. Forecasts stay unavailable without eligible history. Current evidence is not extrapolated into a flat or rising forecast to fill a chart. Synthetic experiments stay outside ordinary observed-evidence feeds.

## 8. Shared authority and evidence rules

- Manual UI, Minder and Mindbots use the same records and authorization services.
- An explicit specific user change authorizes that scoped operation, subject to normal ownership/version checks. Do not add a redundant AI approval step.
- Inferred/proactive changes require a concrete proposal and approval before mutation. Rejecting leaves state unchanged. Approval binds exact target versions; retries do not duplicate writes.
- External factual claims use supporting source records/passages. User statements are attributed to the user; system assessments identify their basis; plans are presented as suggestions.
- No broad source context becomes exact whole-role demand, no unsupported forecast is invented, and no guarantee of employment or total AI replacement is made.
- Backend identity determines ownership. Public citations never expose CVs, private conversations or another user's data.
- Missing credentials/history/design assets block only dependent work. Do not falsely report those capabilities complete.
