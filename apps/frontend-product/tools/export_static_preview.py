"""Build the separate, read-only Netlify Drop preview. Never reads runtime state."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'netlify-drop'
TEMPLATES = Path(__file__).resolve().parent / 'static-preview'
if OUT.exists() and not (OUT / 'PREVIEW_EXPORT.json').is_file():
    raise SystemExit('Refusing to replace a directory without the preview export marker.')
OUT.mkdir(exist_ok=True)
# Only tracked product source/static assets are eligible; no environment, database or upload paths.
repo = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT).decode().strip())
tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(ROOT)], cwd=repo).decode().split('\0')
selected = []
for value in tracked:
    if not value:
        continue
    file = repo / value
    rel = file.relative_to(ROOT)
    if len(rel.parts) == 1 and file.suffix in ('.js', '.css', '.html'):
        selected.append((file, rel))
    elif rel.parts[0] in ('assets', 'pages') and file.suffix in ('.js', '.html', '.css', '.svg', '.png', '.woff', '.woff2', '.ttf'):
        selected.append((file, rel))
for file, rel in selected:
    target = OUT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(file, target)
for name in ('client.js', 'auth.js', 'example-data.js', 'preview.css'):
    shutil.copyfile(TEMPLATES / name, OUT / name)
index = (OUT / 'index.html').read_text()
index = index.replace('<title>Minder · Your workspace</title>', '<title>Minder · Interface preview</title>')
index = index.replace('<script type="module"', '<link rel="stylesheet" href="preview.css"><script type="module"')
index = index.replace('<body>', '<body><aside class="preview-notice" role="note"><strong>Interface preview — live services unavailable.</strong><span>Example data only. No account is signed in. AI, uploads, saving and scheduled actions are unavailable.</span></aside>')
(OUT / 'index.html').write_text(index)
app = (OUT / 'app.js').read_text()
app = app.replace("authMode()==='local'?'Local demonstration':'Private account'", "authMode()==='preview'?'Example data · not signed in':'Interface preview'")
app = app.replace('<button type="button" class="button-outline" id="signOut">Sign out</button>', '<button type="button" class="button-outline" id="signOut">Preview information</button>')
start = app.index("document.querySelector('#signOut').onclick=")
end = app.index('\n', start)
app = app[:start] + "document.querySelector('#signOut').onclick=()=>window.dispatchEvent(new CustomEvent('minder-saved',{detail:'Interface preview — live services unavailable. No account is signed in.'}));" + app[end:]
(OUT / 'app.js').write_text(app)
# Display-only copy changes make the fixed example state explicit on smaller surfaces too.
replacements = {
 'pages/home.js': [('Profile saved', 'Example profile'), ('Your preferences are saved.', 'These are example preferences only.')],
 'pages/minder.js': [('Your messages save to your account. Plans and actions need explicit confirmation.', 'Preview only. Messages are not sent or saved.')],
 'pages/mindbots.js': [('One continuous private history. Review proposed changes before approval.', 'Preview only. Live messages and actions are unavailable.'), ('Saved activity loaded.', 'Example activity loaded.')],
 'pages/starter-matches.js': [('A few directions to explore', 'A few example directions'), ('Based on your reported background and interests. These are provisional topical suggestions, not competency scores or independently validated ML results.', 'Example data from the approved demonstration. Live personalisation and competency assessment are unavailable.')],
}
for relative, changes in replacements.items():
 file = OUT / relative
 content = file.read_text()
 for before, after in changes:
  content = content.replace(before, after)
 file.write_text(content)
(OUT / '_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-src 'none'; base-uri 'self'; form-action 'none'\n")
(OUT / 'README.txt').write_text('''Minder interface preview — Netlify Drop\n\nDrop THIS folder into Netlify Drop: index.html is at the root. No build, Python backend, environment variables or login service is required. Navigation uses hash routes.\n\nAll profile, direction, task/progress and bot settings are synthetic examples adapted from the approved Home reference. Live AI, authentication, uploads, server changes and scheduled actions are unavailable. Writes fail visibly without pretending to save. Data is not persisted as private server state.\n\nThe supplied CSS uses the existing Inter/system fallback font stack, with no remote font requirement. Icons and all approved avatar images are included locally.\n\nLocal verification: python3 -m http.server 9196 --bind 127.0.0.1 --directory <this-folder>\nOpen http://127.0.0.1:9196/ . This is only a static file server, not a service dependency.\n\nRebuild from repository: python3 apps/frontend-product/tools/export_static_preview.py\nProduction frontend and backend configuration are not modified. No secrets, environments, databases or CV uploads are read/exported.\n''')
files = {str(p.relative_to(OUT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'PREVIEW_EXPORT.json'}
(OUT / 'PREVIEW_EXPORT.json').write_text(json.dumps({'kind': 'read-only-static-interface-preview', 'source_frontend_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(), 'example_source': 'docs/Minder_Home_Package/assets/app.js', 'live_services': False, 'files': files}, indent=2)+'\n')
print(OUT)
