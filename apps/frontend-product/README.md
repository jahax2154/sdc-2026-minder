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
