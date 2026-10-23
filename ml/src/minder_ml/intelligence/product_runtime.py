"""Isolated product-lane launcher over the existing C/A backend, not a new stack."""
import argparse
from contextlib import ExitStack
import importlib
import json
import mimetypes
from pathlib import Path
import threading
from wsgiref.simple_server import make_server, WSGIRequestHandler
from .policy import ROOT
from .integration_cli import application, wsgi_request
from .groq_adapter import GroqAdapter

MODEL = 'qwen/qwen3.8-27b'


def build(lane, *, database=None, role_ids=None):
    manifest = json.loads((ROOT / 'docs/execution/product-v2/OWNERSHIP.json').read_text())
    reservation = manifest['lanes'][lane]
    # The same published code can be used in a remote clone. Validate namespace,
    # not the historical Mac absolute directory; no sibling path is opened.
    namespace = reservation['namespace']
    target = Path(database or ROOT / reservation['database']).resolve()
    provider = GroqAdapter(key='', model=MODEL)
    if lane in ('A', 'F'):
        import sys
        sys.path.insert(0, str(ROOT / 'apps/backend-api'))
        from minder_app.config import load_provider_config
        config = load_provider_config()
        if config.model and config.model != MODEL:
            raise ValueError('preserve_verified_Qwen_product_configuration')
        provider = GroqAdapter(key=config.api_key, model=MODEL)
        provider.daily_limit = config.daily_limit
    app, catalogue = application(target, namespace=namespace, provider=provider, role_ids=role_ids)
    # Reuse the existing lazy v4 initializer, with no network/quota call, before
    # D's sole new product migration chain starts at5.
    from minder_app.provider_budget import BudgetedProvider
    BudgetedProvider(app.store, 'bootstrap-no-call', provider)
    from minder_app.product_routes import module_for
    migration = module_for('product_migrations')
    if migration is not None:
        migration.migrate(app.store)
    return app, reservation


class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        pass


def web_app(app):
    frontend = (ROOT / 'apps/frontend-product').resolve()
    allowed = {'.html', '.js', '.css', '.svg', '.png', '.webp', '.jpg', '.jpeg', '.ico', '.woff', '.woff2'}
    def serve(environ, start_response):
        path = environ['PATH_INFO']
        if path.startswith('/api/'):
            return app(environ, start_response)
        target = (frontend / ('index.html' if path == '/' else path.lstrip('/'))).resolve()
        if (environ['REQUEST_METHOD'] != 'GET' or not target.is_relative_to(frontend)
                or any(p.startswith('.') for p in Path(path).parts if p != '/') or target.suffix not in allowed):
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Not found']
        if not target.is_file():
            start_response('503 Unavailable' if path == '/' else '404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Product frontend is not implemented yet; API remains available.']
        raw = target.read_bytes()
        start_response('200 OK', [('Content-Type', mimetypes.guess_type(str(target))[0] or 'application/octet-stream'),
            ('Content-Length', str(len(raw))), ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff'),
            ('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")])
        return [raw]
    return serve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lane', choices=('A', 'D', 'E', 'F'), required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    app, reservation = build(args.lane)
    if args.check:
        status, health = wsgi_request(app, 'GET', '/api/health')
        assert status == 200
        print(json.dumps(dict(lane=args.lane, health=health, model=MODEL,
            provider_configured=bool(app.provider.key), api_port=reservation['api_port'], ui_port=reservation['ui_port'],
            namespace=reservation['namespace'], deployment=False)))
        return
    with ExitStack() as stack:
        api = stack.enter_context(make_server('127.0.0.1', reservation['api_port'], app, handler_class=QuietHandler))
        ui = stack.enter_context(make_server('127.0.0.1', reservation['ui_port'], web_app(app), handler_class=QuietHandler))
        thread = threading.Thread(target=api.serve_forever, daemon=True);thread.start()
        print(json.dumps(dict(lane=args.lane, api_port=api.server_port, ui_port=ui.server_port,
            model=MODEL, loopback_only=True, scheduler_autostarted=False, deployment=False)), flush=True)
        try:
            ui.serve_forever()
        finally:
            api.shutdown();thread.join(timeout=5)


if __name__ == '__main__':
    main()
