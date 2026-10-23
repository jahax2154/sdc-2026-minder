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
