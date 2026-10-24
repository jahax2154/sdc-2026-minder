"""Verify public static bytes against F's exact committed handoff; no credentials."""
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[4]
BASE='http://127.0.0.1:9111'
FRONTEND='0c74362344cc9a85044072b0b59085309f9744cf'
FILES=('app.js','client.js','chat-renderer.js','pages/careers.js','pages/profile.js',
       'pages/starter-matches.js','pages/minder.js','pages/mindbots.js',
       'pages/my-path.js','pages/task-controls.js')

def main():
    with urlopen(BASE+'/api/health',timeout=5) as response:health=json.load(response)
    rows=[]
    for name in FILES:
        expected=subprocess.check_output(['git','show',FRONTEND+':apps/frontend-product/'+name],cwd=ROOT)
        with urlopen(BASE+'/'+name,timeout=5) as response:
            actual=response.read(500001)
            assert response.status==200
        assert actual==expected,'Served frontend differs: '+name
        rows.append(dict(path=name,sha256=hashlib.sha256(actual).hexdigest(),matches_committed_handoff=True))
    report=dict(runtime=BASE,backend_revision=health['runtime_revision'],frontend_revision=FRONTEND,
        public_static_files=rows,no_provider_call=True,no_authentication_or_profile_created=True)
    output=ROOT/'ml/artifacts/session-a/product/morning/served-frontend-verification.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
