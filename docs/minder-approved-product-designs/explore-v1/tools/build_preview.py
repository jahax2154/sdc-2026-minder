"""Regenerate the standalone HTML and the local QA copy. Python standard library only."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
css = (ROOT / 'assets/styles.css').read_text()
js = (ROOT / 'assets/app.js').read_text()
html = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Self-contained Minder Explore preview with distinct Careers and My Path page routes."><title>Minder Explore · Preview</title><style>''' + css + '''</style></head><body data-mode="standalone"><div id="app"></div><noscript>This interactive preview requires JavaScript.</noscript><script>''' + js + '''</script></body></html>'''
(ROOT / 'Minder_Explore_Preview.html').write_text(html)
preview = ROOT / '.preview'
if preview.exists():
    for name in ['index.html', 'careers.html', 'my-path.html', 'Minder_Explore_Preview.html']:
        shutil.copy2(ROOT / name, preview / name)
    shutil.copytree(ROOT / 'assets', preview / 'assets', dirs_exist_ok=True)
print('Standalone preview regenerated from canonical CSS and JavaScript.')
