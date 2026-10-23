# F — product frontend owner

F owns the intended product frontend, including Minder and Mindbots. C owns their backend, not this UI. Start in A's exact assigned worktree/branch. Read actual contracts, ownership, this pack and the earlier closure pack's `01_MINDER_MINDBOT_FRONTEND_CONTEXT.md`.

Do not wait for Minder/Mindbots HTML to inspect the app or build independent Profile/Explore/shared components using available design references. Do not claim exact visual fidelity to assets not yet supplied.

## F0.1 — source and design inventory

Inspect the current frontend, C's acceptance UI, Junhong's preferred standalone HTML/assets when supplied, and selected Replit source. Record actual framework, package manager/lockfile, entry point, router, styles, assets, current API client and run/build commands.

Map source-backed functional UI versus dummy content. The preferred HTML is the primary visual source; Replit is selective reuse, not authorization for an unrelated redesign or second app. Preserve source attribution/licensing of imported assets. Do not import another `.git`, secrets, database, dependency directory or unrelated backend.

Write a page/state inventory covering Profile, the five Explore areas, Minder and Mindbots. Identify missing design assets precisely. Screenshots supplement source; they do not establish actual interactions or responsive behavior. Commit F0.1.

## F0.2 — shared frontend foundation

Implement/reuse shell/navigation, design tokens, shared components, typed/validated API client where supported, auth/session handling, request errors and cache/refetch behavior. Keep a single final frontend entry. Preserve the acceptance UI as a test surface without presenting it as the finished product.

Shared components include forms, loading/empty/error/unavailable states, source details, requirements/unknown evidence, task/status controls, resource cards, proposal differences with approve/reject, and persisted action status.

Use actual API origin/proxy configuration. Replit localhost is not Junhong's Mac. Keep Groq keys and provider clients on the backend. Follow actual auth/CSRF/CORS requirements; do not use wildcard credentialed access as a shortcut. Browser fixtures must be explicit development mode, never normal runtime fallback.

Record a stable component/client contract and exact page paths. If G is enabled, commit the foundation first and transfer only those page files. G does not edit shell/router/client/global CSS/package files. If code is one HTML file and cannot be safely partitioned without disproportionate work, keep F as sole writer.

Commit and publish F0.2 early so page work and real API integration can proceed.

## F1.1 — Profile and Career Match

Implement partial profile saves, edit/validation/conflict states, skill evidence attribution, available CV intake/correction and study availability. Allow incomplete input; display A's focused missing questions. Do not display an invented completeness percentage or turn inferred skills into confirmed assessments.

Career Match consumes A/E's actual result contract: reasons, evidence scope/date, missingness, role detail, feedback/reset, exploration and explicit direction selection. No frontend ranking formula, guarantee of hiring, forced three roles or automatic industry exclusion.

Verify profile save/read/refresh, assessment sufficiency, dislike/reset semantics and selected-direction persistence. Keep internal market score matrices hidden. Commit F1.1. If G owns these pages, F integrates G1.1 instead of implementing them again.

## F1.2 — Tasks, Progress, Roadmap & Skills, News & Trends

Use one plan/task state source. Explicit edits and completion/undo call the real API. Show success after persistence, then refresh dependent views. Handle stale edits visibly. No client-only task store or separate progress formula.

Roadmap shows sourced requirements, supported gaps and unassessed areas distinctly. Progress shows the real numerator/denominator and chosen plan; never equate task completion with career readiness. Preserve historical plans and date/timezone behavior.

News & Trends shows type, publisher, source, dates, relevance explanation and permitted excerpts/summary. Support filters and available save/dismiss/add-to-plan actions. Distinguish news, learning resources, observed current market context and future forecasts. Do not fill an unavailable forecast panel with fabricated curves.

Preserve existing Future Explorer access/links under the working navigation interpretation. Empty/no-source/old-cache states must be understandable. Article links and Markdown use safe rendering; no model-provided raw HTML injection.

Verify a real resource interaction persists, source details resolve, task completion/undo updates Progress, and unsupported data is shown honestly. Commit F1.2, or integrate the relevant G phases if those page files were delegated.

## F2.1 — Minder using the supplied design

When HTML/screenshots arrive, port their visual intent into the shared frontend. Do not ask C to build a second UI. Bind C's actual exported chat/history/evidence/tool-result contracts to the named backend revision.

Implement empty/history, sending, validated answer with sources, insufficient evidence, provider failure/rate limit and safe retries. Distinguish pending request from persisted response. Render only the public validated answer, not hidden reasoning or internal prompts. Do not add unsafe streaming merely for appearance; use the supported contract.

External factual claims show actual backend source details. User statements are attributed to the user, and suggestions remain suggestions. Verify real chat and persistence, with at least one accepted non-Bosch evidence type when C/A support it. Commit F2.1.

## F2.2 — Mindbots and shared state

Implement actual event/activity, supported automation status, concrete proposals, approve/reject, stale proposal and action pending/completed/failed states. A local scheduled test does not justify a permanent '24/7 active' badge.

Direct specific requests use C's authorized action flow. Inferred/proactive changes display exact differences and require approval before writes. Rejection leaves state unchanged; repeated clicks/retries do not apply twice. After success, Tasks/Roadmap/Progress refetch the same persisted records.

Do not invent pause/schedule/delete controls unsupported by the backend. Keep true missing capabilities in the ledger. Verify approve/reject, stale versions, actual persisted result and cross-screen consistency. Commit F2.2.

## F3.1 — final product browser acceptance

Run the product frontend against the named integrated real backend. Check the journey in file 09, desktop/phone widths, keyboard navigation, visible labels/errors, page/console failures, refresh and session ownership. Use fictional test profiles.

Report live-provider tests separately from fixtures. Record final entry files, build/start command, API origin/proxy, backend SHA, contract revision and design references. Publish tested task-scoped checkpoints to F's branch under file 10 and hand A full SHAs. Do not deploy or push other branches.
