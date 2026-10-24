Minder interface preview — Netlify Drop

Drop THIS folder into Netlify Drop: index.html is at the root. No build, Python backend, environment variables or login service is required. Navigation uses hash routes.

All profile, direction, task/progress and bot settings are synthetic examples adapted from the approved Home reference. Live AI, authentication, uploads, server changes and scheduled actions are unavailable. Writes fail visibly without pretending to save. Data is not persisted as private server state.

The supplied CSS uses the existing Inter/system fallback font stack, with no remote font requirement. Icons and all approved avatar images are included locally.

Local verification: python3 -m http.server 9196 --bind 127.0.0.1 --directory <this-folder>
Open http://127.0.0.1:9196/ . This is only a static file server, not a service dependency.

Rebuild from repository: python3 apps/frontend-product/tools/export_static_preview.py
Production frontend and backend configuration are not modified. No secrets, environments, databases or CV uploads are read/exported.
