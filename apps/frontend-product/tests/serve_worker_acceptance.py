"""F-only isolated browser fixture: actual Worker, explicit synthetic due clock, no loop.

A private local control file coordinates the software test, never a product endpoint.
It does not start a background scheduler, edit policy, or touch another lane database.
"""
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
import json
import os
import tempfile
import threading
import time
from wsgiref.simple_server import make_server
from minder_ml.intelligence import product_runtime as runtime
from minder_ml.intelligence.groq_adapter import GroqAdapter
from minder_app.agents import Worker

control = Path(os.environ['MINDER_F_WORKER_TEST_CONTROL']).resolve()
if not str(control).startswith('/private/tmp/minder-f-'):
    raise ValueError('F_private_test_control_required')
control.mkdir(parents=True, exist_ok=True)
root = runtime.ROOT/'ml/artifacts/session-f/product'
with tempfile.TemporaryDirectory(prefix='f-worker-browser-', dir=str(root)) as folder:
    app, reservation = runtime.build('F', database=Path(folder)/'fixture.sqlite3')
    app.provider = GroqAdapter(key='', model=runtime.MODEL)
    worker = Worker(app.store, app.actions, provider=app.provider, services=app.services)
    with ExitStack() as stack:
        api = stack.enter_context(make_server('127.0.0.1', reservation['api_port'], app, server_class=runtime.ProductServer, handler_class=runtime.QuietHandler))
        ui = stack.enter_context(make_server('127.0.0.1', reservation['ui_port'], runtime.web_app(app), server_class=runtime.ProductServer, handler_class=runtime.QuietHandler))
        for server in (api, ui):
            threading.Thread(target=server.serve_forever, daemon=True).start()
        print('F isolated actual Worker acceptance; controlled due clock; provider absent; no deployment', flush=True)
        try:
            while True:
                command = control/'run.json'
                if command.exists():
                    value = json.loads(command.read_text()); command.unlink()
                    try:
                        at = datetime.fromisoformat(value['at'].replace('Z','+00:00'))
                        result = worker.tick(at, owner=value['owner'])
                        (control/'done.json').write_text(json.dumps({'ok':True,'controlled_clock':True,'result':result}))
                    except Exception as error:
                        (control/'done.json').write_text(json.dumps({'ok':False,'error_type':type(error).__name__}))
                time.sleep(.05)
        finally:
            api.shutdown(); ui.shutdown()
