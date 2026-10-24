# Final frontend repair gate — F-UX0 inventory

Preserved base: `3c7d105d34e32c291bc7440764390f55a8fb515f` on `session/f-product-frontend`; no history rewrite. Existing F local runtime health reports that revision at http://127.0.0.1:9106; UI http://127.0.0.1:9106. Qwen configuration unchanged. No deployment.

Read the full final repair brief in the original checkout, including section 10. Actual approved Home source inspected at `docs/Minder_Home_Package/` in that checkout: HTML, CSS, reference controller, DESIGN_CONTEXT, FRONTEND_LOGIC, reference screens. A is importing that exact shared package; no substitute design. Existing frontend approved avatar assets include nimo PNG and frog/puff/star/heart SVG colour variants. Reference controller contains fictional profile/tasks/localStorage and will not be used as application state.

## Reproduced at 1280 × 720

Live browser baseline `/private/tmp/minder-f-ux/baseline.json`, screenshot `before-profile.png` (local, not committed). Profile view has 832px content and overflow visible inside a 645px available shell. Careers content is 4607px and overflow visible; the outer document is overflow hidden. Root Profile/Explore class replacement loses the page flex/scroll constraints. Global plus is hidden everywhere except Minder. Explore expands inline rail rows. Router replaces main and loading markup on every internal tab. Minder has the obsolete horizontal select/delete/refresh toolbar. Mindbot Customize is disabled and identity hardcoded.

## Dependencies requested immediately

A central registration/shared approved asset import; D persisted versioned bot preferences, trimmed nonempty name ≤40 and approved avatar allowlist; owned Minder title/message search with accurate scope. A confirms intended routes GET/PUT product/bot-preferences and POST product/conversations-search; F awaits committed exported schemas before wiring. Existing singleton history/schedule/profile storage must be preserved. No frontend implementation of backend policy or invented endpoints.

## Scope and exclusions

F alone owns shell, routes, clients, global styles, frontend assembly. Existing untracked raw/derived ML source inputs remain untouched and excluded; not backed up by these commits. Screenshots/traces contain only local synthetic demonstration state. Later F-UX phases remain incomplete until implemented and verified.

## F-UX1 implementation

Restored bounded flex/min-height/overflow on the actual Profile and Explore roots; fixed shrinking right-screen and small-height shell. Explore is an anchored flyout, leaving all rail rows in place. Global New Minder chat remains available in every authenticated module, keeps unsent drafts in account-cleared memory and creates no record until first send. Context and independent Mindbot scrolling are retained. Desktop assistant/user body CSS14→16px, mobile user12→14px, both composers13→15px; original font family retained.

Real browser 20 viewport/route combinations:1440×900,1280×720,390×844,640×360; wheel scroll reaches formerly clipped content; no horizontal document overflow; global plus visibility and unsent draft retention passed. JSON and screenshot at `/private/tmp/minder-f-ux/ux1-layout.json` and `ux1-minder.png`. 640×360 exercises the effective layout of1280×720 at200%; it is not claimed as actual browser zoom. Final full browser zoom/last-control acceptance still required in F-UX6. Provider calls:0.

## F-UX2 implementation

One mounted main; Careers/My Path headings and tab nodes persist across internal changes. New tabs immediately clear obsolete panel content and update selected state; same-panel reads retain valid content. Read abort/generation checks reject obsolete requests. Profile data is reused only across sibling panels; explicit refresh re-reads canonical data. Career query, comparison selection and match results survive panel visits in identity-cleared memory; profile-version keys invalidate match presentation. No private browser-storage cache added. Compare retains selected-control focus while refreshing. Reduced motion respected.

Actual browser trace `/private/tmp/minder-f-ux/ux2-partial-trace.zip` proves main/header/tab object identity across both modules, 700ms delayed reads and rapid switches, retained search draft, one initial document navigation, no page errors. No provider call. A asset/schema base29a6b9303a13b617a0698ea9c3a2c6fd4ebf796f integrated by normal merge; D routes await implementation.

## F-UX3 implementation

Replaced horizontal Saved conversations/select/delete/refresh strip with collapsible adjacent history sidebar: server title/message search,250ms debounce and stale-request abort,20-row pagination, current selection/date/wrapped titles, row-menu confirmed deletion, New chat shared with global handler and saved bot name/avatar. No model calls on open/search/delete. Sidebar auto-reloads after actual send/delete; history errors have local Retry. Desktop collapse preference alone uses localStorage; transcript/drafts remain server/private-memory. Mobile drawer has backdrop, Escape, focus loop and reachable collapsed toggle. Context remains separate.

Merged Dd734d95cf68cb4945562bd9166714798edc2fb23 normally; F integrationa5000c269ad35e926b27242e4e0389ca10890e96. Restarted only known F runtime; schema7/no worker. Real browser test created25synthetic owned conversations, proved20+5pagination/title search/open/retained query+draft/delete and mobile Escape/focus. Message-content search additionally covered by D backend tests and final provider browser journey. Screenshot `/private/tmp/minder-f-ux/ux3-mobile-collapsed.png`; console clean.

## F-UX4 implementation

Native, bounded customization dialog supports trimmed name1..40Unicode codepoints and exactly25approved avatars; hashes byte-equal to A allowlist. Preview updates plain text and allowlisted asset paths. Cancel/Escape writes nothing and restores focus. Real versioned PUT saves to D existing storage; errors retain draft, conflict/uncertain save disables further Save until explicit saved-identity reload. No auto retry. Successful identity updates page/profile panel/sidebar/Home through scoped event; every page reads current server identity and identity clear removes drafts. Default My Bot replaces hardcoded Nimo. Home deep links open actual Customize/settings or seed same-channel Mindbot composer. Mindbot transcript no longer forces a reader at older content to bottom on incidental repaint; own sends still scroll down.

Actual browser identity acceptance passed save/cancel/refresh,409conflict→reload retaining draft→explicitsave, singleton ID unchanged, sidebar/page/Home consistency,390px modal bottom-control access/Escape/focus, separate owner defaults. Evidence `/private/tmp/minder-f-ux/ux4-customize-mobile.png`; no console errors. D schema7, no new dependency/configuration.

## F-UX5 implementation

Home replaces Overview in navigation and default route; old overview hash remains an alias. Body CSS generated directly/scoped from committed `docs/Minder_Home_Package/assets/styles.css`; supplied standalone238px shell, demo JavaScript, fixtures/localStorage and preview controls are excluded. Four actual sections preserve approved hierarchy/layout, with keyboard Tasks/Skills/Progress switching. Real local-time greeting and saved profile; chosen direction versus active path; exact E canonical overview next_task/order/progress; existing plan-design labels for older saved tasks. No copied progress store, hidden matching/model call or regenerate-on-refresh. Skills retain evidence/self-report distinctions.

Bot identity/settings/proposals/notices load independently from profile/path. Actual pending proposal or saved notice takes priority; unconfigured/paused/quiet states differ. ON requires actual enabled settings. Home actions navigate to existing real Profile/Careers/My Path or same-channel Mindbot controls. Errors have local retries rather than fabricated empty states.

Actual browser before/profile-only/chosen-no-plan/active-path/bot-only tests passed; canonical progress and next-task ID compared to server composition, Tasks/Skills/Progress at1280×720 and390×844 without horizontal overflow,0model calls. Canonical plan fixture is synthetic real D persisted state (legacy pathway-preview), not a claim of generated model quality; final provider flow separately verified. Screens `/private/tmp/minder-f-ux/ux5-{first-visit,profile-only,active-progress,home-390}.png`. Full Chromium installed only in temporary acceptance directory; actual extension setZoom2 reports innerWidth1280→640/devicePixelRatio1→2 and wheel reaches Profile Continue, screenshot `ux6-real-200pct-profile.png`.

## F-UX6 targeted regression refinement

Acceptance found that reusing a ready profile across sibling panels could miss a concurrently saved partial profile. Every route context now re-reads its saved profile; the mounted frame/valid same-panel content stays in place. Main exposes current route/render state and is programmatically focusable for keyboard scrolling. Removed toolbar remains removed; uncertain Minder turns offer only local Reload saved history and Retry exact request controls, retain the exact body and lock new instructions until resolved. Processing/uncertain successful HTTP results receive the same explicit recovery. Historical tests now target row deletion/global shell plus instead of removed select/strip.

Real Qwen final journey passed: original question969ms, unseen notebook follow-up1710ms, same-channel Mindbot complete-task1300ms. All generated_guidance/provideravailable, exactly3model invocations;2extraHTTP receipt retries reused stored outcomes, preserved task version and one action record. Stop waiting clears Working; reload does not infer receipt or replay; title/message search finds notebook; refresh restores both histories; Context closes; independent Mindbot frame6ms/ready29ms. Computed desktop assistant/user16px,composer15px, original Inter/system stack. Profile/CV/PDF, Careers/My Path, malicious-content, two-local-owner/auth-expiry, typed proposal approval and canonical task edits passed. Actual managed Clerk remains a separate external acceptance gap.

## F-UX6 final interaction refinement

Valid panel content now remains during slow refresh and on refresh failure, with a local Retry outside the temporarily inert old controls. Filter focus/caret and scroll restore after successful replacement. Real trace verifies stable main/header/tabs, delayed/rapid switches, retained data while pending, failed read with retained data and successful local retry; one document navigation. Per-conversation in-memory scroll restoration preserves older reading position without loading or replaying actions. Schedule-panel Escape returns its actual opener; Activity reveals and scrolls to saved activity. Added the exact supplied Home icon and approved progress track treatment. All original3c7d105back/document/info shapes retained.

Provider-absent actual server test passed: truthful unavailable reply/Working cleanup, Mindbot frame7ms/ready31ms initially then2–3ms, no extra turns,401clearsprivateUI and explicit new local owner sees no previous history. Controlled transport-loss tests over actual saved state passed uncertain identity-save draft→GETreconcile→explicit no-op save with unchanged version; Home profile retry preserves other sections; global plus from Home/Profile/Careers/My Path/Mindbot creates no empty records or changes singleton;12real provider-absent turns prove long-history reading-position restoration. No extra paid calls for these refinements.

## F-UX6 acceptance status

All six final no-model browser suites passed on the exact refinement snapshot: layout20viewport/routes; stable partial DOM/content/focus/caret/error-retry trace;25history rows with loaded pages retained when opening an older row; identity save/cancel/conflict/isolation; five real Home states; actual200%Chromium Profile creation and all Home/Profile/Careers/My Path panels via wheel/keyboard. Extra actual-provider-absent recovery and preserved historical profile/CV/PDF, task/proposal, auth expiry/switching and safe-content regressions passed. Node syntax and git diff checks passed. A25avatar+25Home/brief hashes/schema registry check passed. Full details/sanitized requests/modes/timings/screenshots/trace hashes are in [F_UX6_EVIDENCE.json](F_UX6_EVIDENCE.json).

No new backend endpoint beyond A/D handoff GET/PUT product/bot-preferences and POST product/conversations-search; Home reuses E views/overview + existing plan-designs and saved reads. No policy/provider/grounder/scoring edit by F. No new migration/configuration dependency; schema7. No deployment. Live managed Clerk/two-account hosted acceptance, Railway access and B GPU work remain external release gaps; local browser passes do not close them.

Excluded from commits/exports: existing untracked ML raw/derived source inputs (untouched/not backed up), local environment/credentials, F SQLite/uploads, browser profiles, synthetic PDF fixtures, screenshots and trace binaries. Screenshot/trace locations/hashes are given for A's local review; these private temporary artifacts are not remotely backed up. No ignore rules added.
