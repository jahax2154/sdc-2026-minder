# Minder — frontend repair and Home completion gate

24 October 2026 · Asia/Kuala_Lumpur · Revision 1

## 1. Purpose and current evidence

Resume F's existing implementation and finish the specific user-facing defects below, then implement the newly supplied `minder_home_package`. This is an execution brief, not a redesign project or proof that the application is already fixed. It supplements Revision 3 of `Minder_Morning_Completion_Runbook_2026-10-24.md`; the newest explicit UI requirements here take precedence where they differ. Existing backend scoring, evidence, privacy and action-authority rules remain in force.

Latest reported F checkpoint: `3c7d105` on `session/f-product-frontend`, preserving `8446ca8`. Resolve the full SHA and inspect newer descendants; do not reset the worktree. Read `docs/execution/product-v2/F/MORNING_REV3_HANDOFF.md` and actual ownership/contracts. The reported local runtime is port 9106. Confirm the running process and assets match the intended revision before diagnosing.

F reports working local chat/history, accepted roadmaps, CV/PDF review, automation, approvals and retry protection. That does not establish complete visual or interaction acceptance. Live Clerk and cold matching performance remain with A/E. Do not erase these limits when reporting this gate.

The author inspected seven user screenshots, but has no access to the live Mac repository. The scroll failure and page-flash behavior are user reports requiring browser reproduction. Do not claim a CSS or router root cause until traced.

| Reference image | Observed or reported issue |
| --- | --- |
| image(20261024-075708).png | Minder has a horizontal Saved conversations selector with Delete and Refresh history controls; user finds conversation type too small |
| image(20261024-080839).png | Interaction reference: a chat sidebar with search, collapse, New chat, personal bot entry and conversation list; not a request to copy another product's branding, colours or project features |
| image(20261024-081029).png | Mindbot text needs larger sizing; Customize is disabled; global rail lacks the plus shown on Minder |
| image(20261024-081038).png | Top-right Mindbot panel needs proper layout, states and usable controls |
| image(20261024-081115).png | Profile setup's bottom actions are clipped; user cannot scroll to them |
| image(20261024-081834).png | Careers scroll is reported broken; rail layout changes on Explore |
| image(20261024-081927).png | My Path shares reported scrolling and tab-transition problems |

These screenshots are references, not runtime fixtures. Do not publish private screenshot contents or unrelated chat titles in the repository. The brief describes the defects sufficiently to begin if screenshots are not present in F's worktree.

## 2. Ownership and launch

- F remains the only frontend shell, styling, client-state and page owner. Resume `/Users/phuahjunhong/sdc-2026-minder-worktrees/session-f`; no additional frontend session is needed.
- A owns orchestration, shared route changes, integration, backend performance and final release acceptance. A imports approved design assets into a shared committed base if they exist only in the original checkout.
- D owns any necessary schema or persisted bot-preference change. Reuse existing user preferences first; do not add a second profile, bot or conversation database.
- E continues live authentication/hosting. B continues the separate RunPod experiment. Neither should edit F's shell.
- F can begin diagnosis and isolated fixes immediately. Request backend contracts early; continue independent frontend work while A/D deliver their specific changes. Never let two sessions concurrently edit the same owned files.

If A/D are idle, provide the focused handoff in section 10. If unavailable, A may explicitly transfer a small file set to F, record ownership, and then allow F to implement it. Do not silently cross ownership or leave a requested capability as a permanent disabled button.

Keep the current framework, fonts, colours, icon family, components, model and data contracts. Do not introduce a framework migration, dependency campaign or new recommendation formula.

## 3. Mandatory global behavior

### R1 — stable navigation rail and global New chat

Use one shared navigation implementation across Home, Profile/setup, Minder, Mindbot, Careers and My Path. Preserve the existing approved 72 CSS-pixel desktop rail unless the actual approved assets require a responsive exception. All routes use identical global icon order, spacing and behaviour; only selection state changes.

The global plus button remains visible in the same position on every module. It means **New Minder chat**. Clicking it opens a fresh Minder compose state; first send must create/use a new Minder conversation rather than append to an old thread. An empty draft need not become an empty database record. Preserve existing unsent drafts safely instead of silently overwriting them. Repeated clicks must not create duplicate records or replay a request.

The plus inside an attachment composer is a separate attachment action; do not change its meaning. Give both controls clear accessible names/tooltips. The global plus must never create a second Mindbot conversation.

Do not insert/remove global rail rows when Explore opens. Put Careers/My Path navigation in the existing content area or an anchored Explore flyout so the rail does not jump. Preserve browser back/forward and direct links. Mobile may use the established compact navigation, but every module must still expose the New Minder chat action consistently.

### R2 — reachable content and scrolling

Fix Profile setup and profile details, all Careers tabs/detail views, every My Path tab, and the new Home page. A short empty state need not scroll; overflowing content must always be reachable. Test with long actual/synthetic-user content, not only empty pages.

Inspect the real layout chain for clipped viewport heights, `overflow: hidden`, missing flex/grid shrink constraints, leftover drawer scroll locks and scroll handlers preventing default behavior. Choose a clear scroll container for each page. A fixed header/rail can coexist with scrolling main content. Do not apply a blanket body-overflow change that breaks chat or modal behavior.

Ensure the last button in each setup step can be reached and clicked at small laptop height, mobile height and increased browser zoom. Sticky footers/composers must reserve space rather than cover the final row. Chat transcript, history list and long dialogs may need their own bounded scrolling. Closing an overlay must restore prior scrolling and focus.

### R3 — update the affected region, preserve the surrounding interface

Use the existing client routing/rendering approach. Internal tab changes, searches, save actions, pagination, chat updates and bot settings must not reload the browser document or rebuild/blank the whole application shell.

- Between Careers Matches/Compare/Outlook or My Path Next steps/Roadmap/Skills/Progress, update the selected panel; keep header, rail, title and tab controls mounted.
- Between modules, replace the route's main content while preserving the shared shell. This is normal navigation, not a requirement to leave the old module visible.
- A mutation may require updates in several genuinely dependent views. Patch or invalidate those dependencies; do not preserve stale data just to obey a literal 'one section only' rule.
- Keep valid previous content visible during a refresh of that same content, with a subtle local busy state. Do not show another tab's content under the newly selected tab while its data loads.
- For first load, use a restrained component-sized placeholder/skeleton matching the target layout. Avoid full-page 'Loading...' replacement, white flashes and collapsed page height. Keep real error/retry and unavailable states visible.
- Use a short, restrained transition, approximately 120–180 ms where helpful, without delaying completed data. Respect reduced-motion settings; no unnecessary shimmer or animation loops.
- Preserve draft text, relevant focus, open state, filters and scroll positions where appropriate. A deliberate new route/tab may have its own remembered scroll; background updates must not jump the user to the top.
- Cancel or ignore obsolete requests. Rapid tab switches must not let a slower old response overwrite the current panel. Scope caches to user/input version and clear private state on logout/user switch.
- Never use a full reload as a retry strategy. Never automatically accept a plan or replay a mutation when opening a tab/history.

Identify whether the observed flash comes from actual navigation, entire-root replacement, temporary loading markup or blocking work. Fix that cause. Cosmetic fades alone do not fix slow matching or duplicate requests; A owns backend latency work.

### R4 — larger conversation text, same typography family

Measure actual computed CSS sizes at normal browser zoom; screenshot pixels are not CSS pixels. Increase the existing Minder and Mindbot conversation body size by **2 CSS px initially**, with up to **4 CSS px total** if the rendered result still needs it. A typical 16px baseline becomes 18px. Record before/after values. Use shared tokens so both interfaces stay consistent.

Apply this to user/assistant message bodies and their normal paragraph/list/link content; keep the composer comfortably legible at the corresponding scale. Preserve font family, weight hierarchy and the approved design. Do not swap fonts, enlarge every page heading or redesign the UI. Permit only the necessary line-height/spacing adjustment to prevent clipping at the new size. Ensure source controls and action labels remain legible and usable. Confirm desktop/mobile messages wrap without horizontal page overflow.

## 4. Minder sidebar — replace the current history bar

Remove the horizontal Saved conversations/select/Delete/Refresh history strip. Replace it with a collapsible left conversation sidebar next to the stable global rail. Keep Minder's existing visual language; the reference supplies the interaction pattern only.

Sidebar order:
1. Header with history-search icon and sidebar-toggle icon.
2. **New chat** action, using the same behavior as the global plus.
3. **My Bot** entry, showing the user's saved avatar and custom bot name when set. Use My Bot as fallback and accessible context; do not hardcode Nimo for every user.
4. Scrollable Minder conversation history, most recently updated first, with current-conversation indication and sensible title/date treatment.

Clicking My Bot opens that user's single Mindbot conversation. It is not a Minder history item and never creates a Mindbot thread. The history list contains only Minder conversations. On Mindbot itself preserve its single messaging interface, without New chat or a bot conversation selector; the shared global plus still explicitly opens Minder.

Search icon opens a focused history search control. Search owned saved Minder history using the existing contract; never expose another user's messages. Prefer title and message search where supported. If only title search is supported, label it accurately and request a minimal A/D extension for message search rather than pretending unloaded messages were searched. Debounce requests and show empty/no-match/error states. Preserve message history beyond the first page; use existing pagination or incremental loading.

Collapse/expand controls remain reachable when collapsed. Desktop sidebar must not squeeze the conversation into an unusable column; mobile uses a dismissible drawer with Escape/backdrop/focus behavior. Preserve collapse preference as a UI setting. Do not store private message content in localStorage.

Keep existing delete functionality in a conversation row's menu with appropriate confirmation. Do not add folders/projects/branching from the reference screenshot. History updates automatically after actual sends/deletes; the old manual Refresh history strip is removed. Opening history never replays actions. Preserve the transcript position when loading older messages and don't force-scroll a user reading older content.

## 5. Mindbot panel and customisation

Replace the unfinished top-right presentation using the supplied design system/components. Provide coherent avatar/name heading, current saved schedule/status, supported activity controls and a reachable Customize action. Long panel content scrolls; controls never leave the viewport. Close icon and Escape work and return focus. Do not overlay the composer unintentionally. If a modal is chosen, use its normal focus/scroll rules; do not treat a nonmodal panel as a modal without reason.

Find the approved bundled avatar assets in the existing design packages. Record exact paths and available choices. Use those assets, not newly generated artwork or arbitrary remote avatar URLs. If the files are absent from F's worktree, have A import the existing approved files; continue other phases meanwhile.

Minimum working Customize flow: edit display name, choose one approved avatar, preview, Save or Cancel. Use a nonempty trimmed name with the existing validated limit (if absent, propose/implement a bounded 40-character limit with A/D). Store an allowlisted avatar ID and name in the existing user-owned settings. No avatar upload, generation, personality editor or new bot is required.

Save must persist through the backend and survive refresh/login; Cancel must discard the draft. Show errors locally and retain the draft for retry. Apply the saved identity consistently to the Mindbot page/panel, Minder's My Bot entry and any Home bot entry. A rename/avatar change must not change permissions, conversation identity, tasks or schedules. The custom name is data, not a system instruction.

If persistence is absent, F immediately requests the minimal contract from A/D. A coordinates route registration and D owns schema changes if actually needed. Browser-only persistence does not close this requirement. Retain current single-Mindbot invariant and action/approval behavior.

Do not label scheduled operation as verified merely because a local toggle is on. Show an understandable actual status and next run where known; hosted daily-run proof remains A/E's responsibility.

## 6. Home implementation from the supplied package

Locate `minder_home_package` in the actual repository, including any archive and its extracted contents. Read its design context, frontend logic, HTML/CSS, reference images and assets. The user reports it has just been added; it may be present only in the original checkout. A coordinates bringing the exact approved files into F's branch. Record actual paths/hashes and do not accidentally execute an older Home mockup.

Implement the approved Home layout faithfully in the existing frontend. The package's source files are visual/behavior specifications, not authority to copy fixture data or replace the application backend.

Render the documented before-setup and after-setup states from real state. At minimum, before setup, route the user toward profile setup and career discovery; after setup, use the package's specified current direction, immediate next steps, progress and bot content where the underlying records actually exist. A partial profile is not automatically a completed roadmap. Retain explicit empty, unavailable, error and retry states and do not manufacture tasks or career recommendations to fill the design.

Map each visible field and button to an existing read contract, saved state or action. Use real saved task counts/progress/dates. Use model-generated explanations where the feature calls for advice; the frontend must not hardcode recommendations or call Groq directly. Bind source controls to actual supporting records, preserving market scope and unavailable real forecasts. Cache/persist generated content under the established version rules; no generation on every tab change or render.

Reuse existing Overview/Explore adapters. If an approved Home section needs a missing read field, send A/E the exact minimal addition and keep building the independent layout. Do not build a second aggregate database or duplicate progress calculation in the client. Complete the real wiring before claiming Home complete.

Home must obey the same fixed navigation, working plus, scrolling, targeted refresh, motion, readable text and saved bot-identity rules. Do not introduce a separate shell through copied standalone HTML.

## 7. Phases, checkpoints and work loop

Use these IDs if unused; otherwise record a clear mapping to existing phase IDs. Keep each phase reviewable. Execute the repeatable loop: reproduce the defect → identify the responsible code → make a bounded fix → test the actual interaction → inspect the rendered result → commit and publish. A later repair is that phase's `-R01`, `-R02`, etc.; do not conceal it in an unrelated checkpoint.

| Phase | Deliverable / exit evidence |
| --- | --- |
| F-UX0 | Verified branch/runtime, approved Home/avatar inventory, reproduced defects, exact backend extension request if needed |
| F-UX1 | Shared stable rail/plus, reachable scrolling and conversation typography; Profile bottom-button journey succeeds |
| F-UX2 | Partial updates and request/state handling; tabs and mutations produce no document reload or shell flash |
| F-UX3 | Real Minder history sidebar/search/collapse/New chat/My Bot; saved history and deletion still work |
| F-UX4 | Finished Mindbot panel and persisted name/avatar customisation integrated with A/D if required |
| F-UX5 | Approved Home before/partial/after states wired to real backend records and actions |
| F-UX6 | Final browser acceptance, regression evidence, reviewed screenshots and integration handoff |

Start the avatar/settings backend dependency in F-UX0 so it can proceed while F fixes layout. Home asset inspection can also happen immediately. Avoid overlapping frontend writers. Commit meaningful completed portions even if a later phase has an external dependency, and mark that later phase honestly blocked rather than marking the whole gate complete.

Existing authority permits normal task-scoped commits and pushes to `session/f-product-frontend`. Do not ask for ordinary push permission again. Stage only owned, relevant files; preserve other changes and read-only/untracked inputs. Exclude secrets, user databases, CV bytes, logs containing private messages and unrelated screenshots. No force push, history rewrite, main push/merge or independent deployment. A retains coordinated integration/release ownership. Resolve ancestry before integrating A/D deliveries; do not duplicate already-merged commits.

## 8. Browser acceptance required to close F-UX6

Test the actual app against the actual backend. Separate mocked faults, local auth substitutes and real-provider/live-auth results. Use synthetic user records/documents for evidence.

1. At 1440×900 and 1280×720 CSS pixels, Profile setup reaches and clicks every bottom action with wheel/trackpad and keyboard; forms retain entered data. Repeat on a 390×844 mobile viewport. Verify usable reflow at 200% browser zoom.
2. Scroll long Careers matches/details and every populated My Path tab to the last control. Repeat after opening/closing a panel and switching modules. Short empty panels need no forced scrollbar.
3. Visit Home → Profile → Careers → My Path → Minder → Mindbot. Rail dimensions/order and global plus remain stable. Click plus from every module; send a message and prove it goes to a new Minder conversation, leaving the single Mindbot identity unchanged.
4. Measure before/after computed message font sizes and unchanged font family. Inspect real long replies, lists, source references and composer on both chat pages.
5. Create at least three Minder conversations. Search, open, collapse/reopen sidebar and delete one; refresh and verify persistence and correct current selection. Check empty/no-match and long-title cases. Verify actual search scope, not just the visible list.
6. Change bot name/avatar and save. Confirm sidebar, Mindbot panel/page and applicable Home view update without a document reload; refresh and verify persistence. Cancel another edit and confirm no write. Verify settings cannot cross users.
7. Exercise rapid Careers and My Path tab switches under deliberately slow responses. Prove no new document navigation, no stale response winning, no duplicated requests causing writes, and no header/rail remount or blanking. Preserve relevant focus/drafts/scroll. Capture a short recording or browser trace because static screenshots cannot prove absence of flashing.
8. Verify Home before setup, partial setup and populated state against saved backend data. Follow every primary call-to-action to its actual destination/action. Unknown data is displayed honestly.
9. Preserve Context close/toggle/Escape, Working… terminal-state cleanup, timeout/cancel, responsive state reads during a pending provider call, accepted-roadmap consistency, CV/PDF review, direct actions, proactive approval/rejection and no retry/history replay.
10. Verify one real Minder follow-up and one real Mindbot action path after integration, using existing authorized provider configuration. Do not rerun paid calls unnecessarily for CSS-only changes. Check console/network failures and inspect desktop/mobile final rendering against the approved assets.

Run focused checks while changing each phase and the relevant existing suite once at the final integrated revision. Do not repeat full suites without changes or an unresolved concern. Passing backend tests alone does not close a scrolling/sidebar/visual defect. Browser pass at F does not replace A's integrated and E's hosted acceptance.

## 9. Required handoff and completion language

Deliver a defect matrix with observed cause, changed files, actual before/after result, test/evidence path and phase SHA. Include full final SHA and verified remote SHA, model/backend/schema/asset revisions, runtime URL, screenshots at representative sizes, transition trace/recording, exact API additions and any remaining dependency with its named owner.

Declare this frontend gate complete only when R1–R4, sidebar, persisted customisation and Home are integrated and the checks above pass. If live Clerk, hosted scheduler proof or cold matching performance remains open, distinguish that release dependency from completed frontend behavior. Do not claim a loading animation resolved backend latency. Do not describe the whole prototype as deployed or submission-ready without A/E's final hosted proof.

## 10. Copyable prompts

### Send to F now

```text
Resume session/f-product-frontend from your reported 3c7d105 or its
verified current descendant. Read Minder_Frontend_Final_Repair_and_Home_Gate.md,
your MORNING_REV3_HANDOFF.md, actual ownership/contracts, and the approved
minder_home_package plus existing avatar assets.

Execute F-UX0 through F-UX6. You remain the sole frontend owner.
Fix blocked scrolling and inconsistent navigation first. Keep the global
plus on every module and make it open a new Minder chat. Enlarge Minder
and Mindbot message text by 2–4 CSS px without changing font families.
Replace the horizontal saved-chat selector with the specified collapsible
Minder sidebar: search/toggle, New chat, saved My Bot identity, then history.
Mindbot still has exactly one continuous conversation per user.

Fix whole-page flashing/reloading through targeted updates, stable shell,
local loading states and stale-request protection across the entire app.
Complete the Mindbot panel and persisted avatar/name customisation using
approved assets. Request the minimal A/D contract immediately if missing;
continue independent UI work. Implement the supplied Home package with
real before/partial/after state and the same global interaction rules.

Preserve working chat, sources, actions/approvals, saved plans, document
review and retries. Do not change scoring, fonts, framework or ownership.
Inspect real browser rendering and interactions after fixes. Static
screenshots alone cannot prove scrolling or smooth transitions.

Commit and normally push each tested bounded phase/refinement to your own
branch under existing authorization. Give A full SHAs, dependency/asset
revisions and the final defect/acceptance matrix. Do not push main or deploy.
Continue through the gate; report exact external blockers while completing
independent work. No broad redesign or repeated unchanged full test runs.
```

### Send to A alongside F

```text
F has a new bounded repair/Home gate in
Minder_Frontend_Final_Repair_and_Home_Gate.md and remains sole frontend owner.
Preserve/integrate F's 3c7d105 ancestry and subsequent phase checkpoints.
Make the newly added minder_home_package and approved avatar assets
available to F as committed source inputs, with actual paths/revisions.

Coordinate only minimal backend additions requested by F: user-owned saved
bot display name/avatar, history search if missing, and actual Home read
fields. Reuse existing state/contracts; D owns any migration. Keep Mindbot's
single conversation and all action-authority rules. Publish dependency
contracts early so F can continue. Do not edit F's shell concurrently.

Continue live auth/hosting and cold matching work with E. Integrate F's
committed fixes and verify the combined browser journey. Preserve all
phase history and existing normal push authority; main merge retains
its prior approval boundary. Report local frontend acceptance separately
from hosted release acceptance.
```
