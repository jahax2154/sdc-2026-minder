# Product capability ledger — P0.2

Current implementation inventory: INVENTORY.md; exported existing contract:
docs/execution/product/llm/FRONTEND_CONTRACT.md. This ledger is not feature completion.

| User capability | Existing/first-slice status | Owner and next runnable work |
| --- | --- | --- |
| Partial Profile/evidence/preferences/availability save | Existing GET/PUT profile with revision/history; optional career_context now schema-compatible | D reuses, tests context and adds missing correction/lifecycle |
| Supported intake | Existing TXT draft, no structured correction/status route | D bounded correction; unsupported PDF/OCR stays explicit |
| Career Match/detail/feedback/reset | Existing actual A baseline/scoped MY evidence and direct actions | E view adapter; F real page, no new scorer |
| Explicit direction/active plan | selected_role_id on plans exists; no canonical active selection | D product_state direction |
| Manual tasks | Existing completion/reschedule/undo, no full manual creation/edit surface | D adapters and titles/refs; retain C action authority |
| Canonical Progress | Persisted task flags exist; selected-plan denominator endpoint absent | D calculation; E projection, F refresh |
| Roadmap & Skills | Existing plans/pathway/requirements, unknown evidence/gaps | D selected state, E composition, F screen |
| Reviewed resources | Existing learning_options source library | E bounded metadata/feed, real provenance and filters |
| Resource save/dismiss/add-to-plan | Missing product state endpoints | D interaction state; E reads, F controls only when advertised |
| News & Trends | Existing B events/current context/forecast availability | E separate adapter; no crawler/new scoring |
| Minder | Actual grounded Qwen/typed-source backend available | F ports approved HTML to product root, replaces demo JS |
| Mindbots | Existing proposals/actions/events/settings and actual one-time clock evidence | F real state/diffs/approve/reject; no false24/7 |
| Product shell/Profile/Explore | Not implemented in current repo | F, G inactive until stable shared foundation and page transfer |
| Product routing/dev isolation | Implemented A bootstrap registry/launcher | D/E/F use own DB/ports; missing modules visibly unavailable |
| Real future forecast/independent suitability accuracy | Unavailable/unvalidated | Separate B/data work, no product launch gate |
| Hosted auth/storage/scheduler/public API | Not deployed/verified | Separate release authority; localhost not remote hosting |

Do not enable an operation just because it appears in the proposed route table.
Use authenticated /api/product/capabilities plus actual response capability details.
F can ship real Minder/Mindbots and existing profile/matching before all new D/E
routes. First useful committed slice is integrated immediately; no end-only merge.
