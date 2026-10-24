"""Rebuild the portable preview and local QA distribution from canonical sources."""
from pathlib import Path
import shutil
root = Path(__file__).resolve().parents[1]
html = (root / 'home.html').read_text()
css = (root / 'assets/styles.css').read_text()
js = (root / 'assets/app.js').read_text()
standalone = html.replace('<link rel="stylesheet" href="assets/styles.css">', '<style>\n' + css + '\n</style>').replace('<script src="assets/app.js"></script>', '<script>\n' + js + '\n</script>')
(root / 'Minder_Home_Preview.html').write_text(standalone)
(root / 'index.html').write_text(html)
dist = root / 'dist'
dist.mkdir(exist_ok=True)
for name in ['index.html', 'home.html', 'Minder_Home_Preview.html']:
    shutil.copyfile(root / name, dist / name)
shutil.copytree(root / 'assets', dist / 'assets', dirs_exist_ok=True)
print('Standalone preview and QA distribution rebuilt.')
