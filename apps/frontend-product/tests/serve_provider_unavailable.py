"""Disposable F-only acceptance server: actual API, explicitly absent provider key.

No backend policy edits. Imports the committed runtime/server class and preserves
its model, migrations/auth/action semantics. Never copies config or database.
"""
from contextlib import ExitStack
from pathlib import Path
import tempfile
import threading
from wsgiref.simple_server import make_server, WSGIServer
from minder_ml.intelligence import product_runtime as runtime
from minder_ml.intelligence.groq_adapter import GroqAdapter

root = runtime.ROOT / 'ml/artifacts/session-f/product'
root.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='f-r-provider-off-', dir=str(root)) as folder:
    app, reservation = runtime.build('F', database=Path(folder) / 'fixture.sqlite3')
    app.provider = GroqAdapter(key='', model=runtime.MODEL)
    server_type = getattr(runtime, 'ProductServer', WSGIServer)
    with ExitStack() as stack:
        api = stack.enter_context(make_server('127.0.0.1', reservation['api_port'], app,
            server_class=server_type, handler_class=runtime.QuietHandler))
        ui = stack.enter_context(make_server('127.0.0.1', reservation['ui_port'], runtime.web_app(app),
            server_class=server_type, handler_class=runtime.QuietHandler))
        thread = threading.Thread(target=api.serve_forever, daemon=True)
        thread.start()
        print('F synthetic acceptance only: same-origin9106/API8106; provider key absent; no deployment', flush=True)
        try:
            ui.serve_forever()
        finally:
            api.shutdown()
            thread.join(timeout=5)
