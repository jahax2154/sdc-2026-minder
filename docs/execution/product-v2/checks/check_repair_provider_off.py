"""Real A HTTP/browser with explicit absent key; never a claimed live Groq outage."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
from wsgiref.simple_server import make_server
from minder_ml.intelligence.policy import ROOT
from minder_ml.intelligence.product_runtime import build, web_app, ProductServer, QuietHandler
from minder_ml.intelligence.groq_adapter import GroqAdapter


def main():
    output=ROOT/'ml/artifacts/session-a/product/chat-repair-final-browser'
    output.mkdir(parents=True,exist_ok=True)
    script=ROOT/'apps/frontend-product/tests/repair_provider_off.cjs'
    raw=script.read_text()
    adapted=raw.replace('docs/execution/product-v2/F/repairs/',str(output)+'/').replace(
        '/private/tmp/minder-f-repair-',str(output/'a-'))
    target=output/'repair_provider_off.cjs';target.write_text(adapted)
    with tempfile.TemporaryDirectory(prefix='provider-off-',dir=ROOT/'ml/artifacts/session-a/product') as folder:
        app,_=build('A',database=Path(folder)/'runtime.sqlite3')
        app.provider=GroqAdapter(key='',model='qwen/qwen3.8-27b')
        with make_server('127.0.0.1',0,web_app(app),server_class=ProductServer,handler_class=QuietHandler) as server:
            serving=threading.Thread(target=server.serve_forever,daemon=True);serving.start()
            env={key:value for key,value in os.environ.items() if key in
                 ('PATH','HOME','TMPDIR','LANG','LC_ALL','PLAYWRIGHT_BROWSERS_PATH','MINDER_PLAYWRIGHT_MODULE')}
            env['MINDER_PRODUCT_BASE_URL']='http://127.0.0.1:'+str(server.server_port)
            try:
                result=subprocess.run(['node',str(target)],cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
                (output/'provider-off-browser.log').write_text(result.stdout+result.stderr)
                assert result.returncode==0,'configured_provider_off_browser_failed_see_private_log'
                evidence=json.loads((output/'provider-off-real.json').read_text())
                assert evidence['provider']['invoked'] is False
                assert evidence['mindbots_added_chat_requests']==0
                evidence['upstream_runner_label']=evidence['mode']
                evidence['mode']='actual_HTTP_configured_provider_absent_disposable_A_database'
                evidence['environment']='Disposable A-only real HTTP/browser; key intentionally absent; no real account outage'
                evidence['persistent_config_changed']=False
                (output/'provider-off-A.json').write_text(json.dumps(evidence,indent=2)+'\n')
                print(json.dumps(dict(status='passed',provider=evidence['provider'],samples=evidence['samples'],
                    added_chat_requests=0,page_errors=evidence['page_errors'],persistent_config_changed=False)))
            finally:
                server.shutdown();serving.join(timeout=5)


if __name__=='__main__':main()
