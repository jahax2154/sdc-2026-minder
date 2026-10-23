# Optional G — page-only frontend parallelism

Default: do not start G. D/E/F already add three concurrent sessions. Enable G only after F0.2 and an explicit A/F ownership record demonstrate disjoint files and a stable client/component interface.

The proposed split, if enabled:
- F retains shell/navigation registration, shared API client, shared components/styles/tokens, dependency files, Minder/Mindbots and final frontend integration.
- G implements specifically assigned Profile/Explore page/component directories using F's exported interface.

Assign exact actual paths. No fuzzy 'G can edit any frontend file' permission. If there are no separate page files, keep F's single-writer mode or perform a small justified separation first. Do not adopt a new frontend framework merely to create another lane.

## G1.1 — Profile and Career Match pages

Implement the F1.1 behavior only in assigned pages, consuming F's client/shared components and actual D/E/A contracts. No root route registration, scoring, backend code, global styles, package/lockfile changes or second client. Hand F the exact page exports and route-registration request. Commit and publish G1.1.

## G1.2 — Tasks, Progress and Roadmap & Skills pages

Implement the corresponding F1.2 behavior. Use server-derived progress, persisted writes, requirement/unknown distinctions and shared date handling. Supply a dependency/refetch request through F's agreed interface; do not modify it concurrently. Commit/publish G1.2.

## G1.3 — News & Trends page

Implement source/type/date presentation, filters, supported saved/dismissed states, add-to-plan and honest current/future availability. Keep source scope and no false forecast behavior. Use E's actual data, not handcrafted production feed items. Commit/publish G1.3.

## G2.1 — handoff and bounded fixes

Verify owned page behavior through F's test harness or agreed isolated entry; identify fixtures versus real backend runs. Give F exact SHAs, dependency revisions and route requests. F integrates/registers the pages and owns the final assembled browser flow. Repair only assigned defects.

G normally pushes only its assigned branch, suggested `session/g-explore-pages`, under file 10. A creates or verifies its worktree when enabled. No frontend shared-file edits, other-branch push or deployment. F1.1/F1.2 become integration/verification of G's delivery rather than duplicate implementation.
