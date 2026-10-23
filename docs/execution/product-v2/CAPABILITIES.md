# Product capability ledger — P1.4 incremental integration

Historical P0.1 inventory: INVENTORY.md; exported existing contract:
docs/execution/product/llm/FRONTEND_CONTRACT.md. This ledger is not feature completion.
Current verification is in P1.1/P1.2/P1.1-R01/P1.3/P1.3-R01 and P1.4 reports.
F1.1 implementation is integrated; its final filter/mobile/document UI work remains
separate until a committed handoff and A browser acceptance establish completion.

| User capability | Existing/first-slice status | Owner and next runnable work |
| --- | --- | --- |
| Partial Profile/evidence/preferences/availability save | D persisted partial merge/version/history; F explicit context/claim/anchored forms | D backend checks pass; F1.1 UI implemented, combined journey evidence in P1.4 |
| Supported intake | TXT<=64KiB reviewed draft and atomic correction; no automatic Profile/mastery update | D implemented; F1.1 TXT review; PDF extraction/OCR unavailable |
| Career Match/detail/feedback/reset | Actual A scoped MY groups, E projection and F1.1 page | No new scorer; ordinary internal matrices hidden; final browser sweep separate |
| Explicit direction/active plan | D persisted explicit selection; F direction/active-plan controls | Selecting a role does not generate a plan or establish readiness |
| Manual tasks | D versioned create/edit/reschedule/complete/undo/cancel over same C state | F controls respect supported operations; no task completion -> mastery |
| Canonical Progress | D selected-plan noncancelled task denominator; E delegates unchanged | F progress/refetch; filters never redefine progress |
| Roadmap & Skills | D selected state, E known requirement/evidence projection; F plan preview/explicit selection | Missing effort/gaps/readiness stay unknown; no invented new gap model |
| Reviewed resources | E uses two existing official learning metadata records | Zero new articles/videos; source dates/nulls/availability caveats retained |
| Resource save/dismiss/add-to-plan | D retry-safe interaction/addition, E filters/projection, F controls | Only two existing accepted learning IDs; no invented resolver |
| News & Trends | E partial learning/source statements; F read/filter presentation | No general news acquisition, broad feed or new demand formula |
| Minder | F approved chat layout with actual Qwen/source rendering | P1.2 A real-provider browser passed; transcript remains temporary |
| Mindbots | F actual proposals/actions/events/settings/history | P1.2 exact reject/approve/retry/stale passed; no continuous24/7 claim |
| Private PDF/TXT library | D migration6 and all5 handlers; A schemas/real HTTP tests |82 backend checks pass; storage default disabled, F UI pending, PDF extraction unavailable |
| Product shell/Profile/Explore | Separate F-owned modules inside approved shell | F1.1 integrated; final sweep pending; G remains inactive |
| Product routing/dev isolation | A registry/launcher; unique D/E/F resources; A8111/9111 | Auth boundary retained; missing or disabled capabilities explicit |
| Real future forecast/independent suitability accuracy | Unavailable/unvalidated | Separate B/data work, no product launch gate |
| Hosted auth/storage/scheduler/public API | Not deployed/verified | Separate release authority; localhost not remote hosting |

Do not enable an operation just because it appears in the proposed route table.
Use authenticated /api/product/capabilities plus actual response capability details.
All library handlers can be implemented while DocumentList.storage is unavailable;
the frontend must check both. Local-development configuration is not hosted storage.
Useful committed slices are integrated immediately; no end-only merge.
