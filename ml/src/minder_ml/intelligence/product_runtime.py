"""Isolated product-lane launcher over the existing C/A backend, not a new stack."""
import argparse
from contextlib import ExitStack
import importlib
import json
import mimetypes
from pathlib import Path
import threading
from socketserver import ThreadingMixIn
from wsgiref.simple_server import make_server, WSGIRequestHandler, WSGIServer
from .policy import ROOT
from .integration_cli import application, wsgi_request
from .groq_adapter import GroqAdapter

MODEL = 'qwen/qwen3.8-27b'


class ProductServer(ThreadingMixIn, WSGIServer):
    """Bound local request workers; SQLite/action/provider limits remain authority."""
    daemon_threads = True
    block_on_close = False

    def __init__(self, *args, **kwargs):
        self.request_slots = threading.BoundedSemaphore(16)
        super().__init__(*args, **kwargs)

    def get_request(self):
        request, address = super().get_request()
        request.settimeout(45)
        return request, address

    def get_app(self):
        application = super().get_app()
        def serve(environ, start_response):
            environ['wsgi.multithread'] = True
            return application(environ, start_response)
        return serve

    def process_request(self, request, client_address):
        self.request_slots.acquire()
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.request_slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.request_slots.release()


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


def build_hosted(database):
    """E's mounted-volume factory; no claim that a mount/provider is provisioned."""
    import os
    import sys
    sys.path.insert(0, str(ROOT / 'apps/backend-api'))
    from minder_app.config import load_provider_config
    config = load_provider_config()
    if config.model and config.model != MODEL:
        raise ValueError('preserve_verified_Qwen_product_configuration')
    provider = GroqAdapter(key=config.api_key, model=MODEL)
    provider.daily_limit = config.daily_limit
    root = os.environ.get('MINDER_DATA_ROOT')
    if not root:
        raise ValueError('MINDER_DATA_ROOT_required')
    app, _ = application(database, provider=provider, durable_root=root)
    from minder_app.provider_budget import BudgetedProvider
    BudgetedProvider(app.store, 'bootstrap-no-call', provider)
    from minder_app.product_migrations import migrate
    migrate(app.store)
    app.managed_identity_required = True
    from minder_app.agents import Worker
    app.scheduled_worker = Worker(app.store, app.actions, provider=provider, services=app.services)
    return app


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
        api = stack.enter_context(make_server('127.0.0.1', reservation['api_port'], app, handler_class=QuietHandler, server_class=ProductServer))
        ui = stack.enter_context(make_server('127.0.0.1', reservation['ui_port'], web_app(app), handler_class=QuietHandler, server_class=ProductServer))
        thread = threading.Thread(target=api.serve_forever, daemon=True);thread.start()
        print(json.dumps(dict(lane=args.lane, api_port=api.server_port, ui_port=ui.server_port,
            model=MODEL, loopback_only=True, scheduler_autostarted=False, deployment=False)), flush=True)
        try:
            ui.serve_forever()
        finally:
            api.shutdown();thread.join(timeout=5)


if __name__ == '__main__':
    main()
