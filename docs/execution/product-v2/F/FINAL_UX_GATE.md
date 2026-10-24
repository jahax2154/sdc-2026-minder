# Final frontend repair gate — F-UX0 inventory

Preserved base: `3c7d105d34e32c291bc7440764390f55a8fb515f` on `session/f-product-frontend`; no history rewrite. Existing F local runtime health reports that revision at http://127.0.0.1:9106; UI http://127.0.0.1:8106. Qwen configuration unchanged. No deployment.

Read the full final repair brief in the original checkout, including section 10. Actual approved Home source inspected at `docs/Minder_Home_Package/` in that checkout: HTML, CSS, reference controller, DESIGN_CONTEXT, FRONTEND_LOGIC, reference screens. A is importing that exact shared package; no substitute design. Existing frontend approved avatar assets include nimo PNG and frog/puff/star/heart SVG colour variants. Reference controller contains fictional profile/tasks/localStorage and will not be used as application state.

## Reproduced at 1280 × 720

Live browser baseline `/private/tmp/minder-f-ux/baseline.json`, screenshot `before-profile.png` (local, not committed). Profile view has 832px content and overflow visible inside a 645px available shell. Careers content is 4607px and overflow visible; the outer document is overflow hidden. Root Profile/Explore class replacement loses the page flex/scroll constraints. Global plus is hidden everywhere except Minder. Explore expands inline rail rows. Router replaces main and loading markup on every internal tab. Minder has the obsolete horizontal select/delete/refresh toolbar. Mindbot Customize is disabled and identity hardcoded.

## Dependencies requested immediately

A central registration/shared approved asset import; D persisted versioned bot preferences, trimmed nonempty name ≤40 and approved avatar allowlist; owned Minder title/message search with accurate scope. A confirms intended routes GET/PUT product/bot-preferences and POST product/conversations-search; F awaits committed exported schemas before wiring. Existing singleton history/schedule/profile storage must be preserved. No frontend implementation of backend policy or invented endpoints.

## Scope and exclusions

F alone owns shell, routes, clients, global styles, frontend assembly. Existing untracked raw/derived ML source inputs remain untouched and excluded; not backed up by these commits. Screenshots/traces contain only local synthetic demonstration state. Later F-UX phases remain incomplete until implemented and verified.
