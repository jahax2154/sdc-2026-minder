# Minder product frontend

Dependency-free ES modules, one entry index.html. No build or package installation.
From the repository root: source .env.local, then run
`"$MINDER_PYTHON" -m minder_ml.intelligence.product_runtime --lane F`.
Open http://127.0.0.1:9106; API is same-origin /api and private backend8106.
Use only F's isolated DB. Preserve qwen/qwen3.8-27b server config. No deployment.

Visual source: docs/minder-ui-html-previews/minder-chat.html, mindbot.html and
assets/minder.css. Source artwork and CSS copied from the user-approved package;
icons extracted unchanged from its minder.js. No external artwork introduced.

Stable files: app.js owns router/shell; client.js owns transport/session/validation;
ui.js owns safe shared cards/sources/forms/diffs; product.css supplements intact
assets/minder.css. pages/minder.html is the approved chat body without fictional
context; pages/minder.js and pages/mindbots.js own actual behavior. G is inactive.
Temporary chat display is memory-only, never advertised as persisted history.

Profile/Explore modules: pages/profile.js, career.js, explore.js; documents.js
embeds the D owner-scoped library. Storage is disabled by default; to test local
fictional PDF/TXT files use `MINDER_DOCUMENT_STORAGE=local-development` before the
same launcher command. Only the assigned lane uploads directory is used. PDF
extraction/hosted durability remain unavailable. Saved profile data survives file deletion.

Browser checks are under tests/{chat_actions,workspace,documents,error_states,smoke}.cjs.
Set MINDER_PLAYWRIGHT_MODULE to an installed Playwright package and
PLAYWRIGHT_BROWSERS_PATH to its browser install. No production dependency required.
MINDER_PRODUCT_BASE_URL defaults to http://127.0.0.1:9106; A can set9111.
MINDER_BROWSER_OUTPUT_DIR defaults to /private/tmp (synthetic artifacts excluded).
chat_actions uses one actual provider call unless MINDER_SKIP_CHAT=1; error_states
is explicitly intercepted fixture-only evidence and makes no provider call.
workspace/documents/smoke use real same-origin APIs with fictional owners and no
provider calls. Same token/session remains across refresh within its browser tab.

Targeted chat/Mindbot repair checks: tests/repair_ui.cjs and repair_workspace.cjs
are explicitly injected transport/deadline fixtures (no provider calls).
repair_navigation.cjs uses the real shell/routes. repair_integrated.cjs uses actual
API/provider for unsaved/partial guidance, follow-up/source scope, pending-chat
workspace and action protection; MINDER_GUIDANCE_ONLY=1 skips empirical/provider
cases. repair_visuals.cjs captures real repaired states with one sourced call.
repair_baseline.cjs records actual current HEAD (or MINDER_FRONTEND_REVISION) and is
the historical reproduction helper, not an assertion that later replies are broken.

Only when the normal F server is stopped, tests/serve_provider_unavailable.py starts
actual committed handlers/server with an explicitly absent provider key and a
fresh disposable F-only DB on8106/9106; repair_provider_off.cjs verifies that mode.
Stop it normally and restore the standard --lane F launcher afterward. This is a
configured-unavailable test, not a real Groq incident. Private config is unchanged.
