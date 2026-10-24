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


def revision():
    import os,re,subprocess
    value=os.environ.get('MINDER_RELEASE_SHA') or os.environ.get('RAILWAY_GIT_COMMIT_SHA')
    if value and re.fullmatch('[0-9a-f]{40}',value):
        return value
    try:
        value=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,timeout=2,check=True).stdout.strip()
        return value if re.fullmatch('[0-9a-f]{40}',value) else None
    except (OSError,subprocess.SubprocessError):
        return None


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
        from minder_app.model_gateway import CoordinatedGroq
        provider = CoordinatedGroq(key=config.api_key, model=MODEL)
        provider.daily_limit = config.daily_limit
    app, catalogue = application(target, namespace=namespace, provider=provider, role_ids=role_ids)
    app.runtime_revision=revision()
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
    from minder_app.model_gateway import CoordinatedGroq
    provider = CoordinatedGroq(key=config.api_key, model=MODEL)
    provider.daily_limit = config.daily_limit
    root = os.environ.get('MINDER_DATA_ROOT')
    if not root:
        raise ValueError('MINDER_DATA_ROOT_required')
    app, _ = application(database, provider=provider, durable_root=root)
    app.runtime_revision=revision()
    from minder_app.provider_budget import BudgetedProvider
    BudgetedProvider(app.store, 'bootstrap-no-call', provider)
    from minder_app.product_migrations import migrate
    migrate(app.store)
    app.managed_identity_required = True
    from minder_app.agents import Worker
    app.scheduled_worker = Worker(app.store, app.actions, provider=provider, services=app.services)
    return app


def build_replit(*, store=None, document_library=None):
    """E's Replit entrypoint. D supplies PostgreSQL/private-object semantics.

    No database URL is coerced to a path, SQLite fallback or volume claim. The
    injection arguments are trusted server objects, never HTTP/user inputs.
    """
    import os
    import sys
    sys.path.insert(0, str(ROOT / 'apps/backend-api'))
    if (os.environ.get('MINDER_ENV') != 'production'
            or os.environ.get('MINDER_AUTH_MODE') != 'managed'
            or os.environ.get('MINDER_AUTH_PROVIDER') != 'clerk'
            or os.environ.get('MINDER_DOCUMENT_STORAGE') != 'replit-app-storage'):
        raise ValueError('replit_managed_auth_and_private_storage_required')
    if store is None:
        try:
            from minder_app.postgres_store import PostgresStore
        except ModuleNotFoundError as error:
            if error.name != 'minder_app.postgres_store':raise
            raise RuntimeError('D_postgresql_store_handoff_not_integrated') from None
        configured = getattr(PostgresStore,'from_environment',None)
        if callable(configured):
            store = configured()
        else:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                raise ValueError('replit_database_url_required')
            store = PostgresStore(database_url,schema=os.environ.get('MINDER_DB_SCHEMA','minder'))
    if (getattr(store,'engine',None) != 'postgresql'
            or getattr(store,'persistence_mode',None) not in ('postgresql','managed-postgresql')):
        raise ValueError('D_managed_postgresql_store_required')
    from minder_app.config import load_provider_config
    config = load_provider_config()
    if config.model and config.model != MODEL:
        raise ValueError('preserve_verified_Qwen_product_configuration')
    from minder_app.model_gateway import CoordinatedGroq
    provider = CoordinatedGroq(key=config.api_key,model=MODEL)
    provider.daily_limit = config.daily_limit
    from .integration_cli import application_for_store
    app,_ = application_for_store(store,provider=provider)
    from minder_app.provider_budget import BudgetedProvider
    BudgetedProvider(store,'bootstrap-no-call',provider)
    from minder_app.product_migrations import migrate
    migrate(store)
    if document_library is None:
        from minder_app.documents import DocumentLibrary
        document_library = DocumentLibrary.from_environment(store)
    if (document_library.store is not store
            or getattr(document_library.backend(),'mode',None) != 'replit-app-storage'):
        raise ValueError('D_private_replit_document_backend_required')
    app.document_library = document_library
    app.managed_identity_required = True
    app.runtime_revision = revision()
    from minder_app.agents import Worker
    app.scheduled_worker = Worker(store,app.actions,provider=provider,services=app.services)
    return app


class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        pass


def content_security_policy():
    """Exact configured identity origin; no wildcard or executable inline code."""
    from minder_app.auth_adapter import AuthConfig
    from minder_app.store import AppError
    import os
    from urllib.parse import urlsplit
    scripts = ["'self'"]
    connections = ["'self'"]
    images = ["'self'", 'data:']
    frames = ["'self'"]
    try:
        config = AuthConfig.from_env()
    except AppError:
        config = None
    if config is not None:
        origin = config.issuer.rstrip('/')
        scripts += [origin, 'https://challenges.cloudflare.com']
        connections += [origin, 'https://clerk-telemetry.com', 'https://img.clerk.com']
        images += [origin, 'https://img.clerk.com']
        frames += [origin, 'https://challenges.cloudflare.com']
        # Clerk Protect can require instance-specific subdomains. Provision exact
        # observed hosts only, rather than opening *.protect.clerk.com or all HTTPS.
        for value in os.environ.get('MINDER_CLERK_ADDITIONAL_ORIGINS', '').split(','):
            value = value.strip()
            if not value:
                continue
            parsed = urlsplit(value)
            if (parsed.scheme != 'https' or not parsed.hostname or parsed.path or parsed.query
                    or parsed.fragment or parsed.username or parsed.password or parsed.port
                    or '*' in value or not (parsed.hostname.endswith('.protect.clerk.com')
                    or parsed.hostname.endswith('.clerk-telemetry.com'))):
                raise ValueError('invalid_exact_clerk_origin')
            scripts.append(value); connections.append(value); frames.append(value)
    return ('default-src \'self\'; script-src ' + ' '.join(scripts) +
        "; style-src 'self' 'unsafe-inline'; img-src " + ' '.join(images) +
        '; connect-src ' + ' '.join(connections) + '; frame-src ' + ' '.join(frames) +
        "; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")


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
            ('Content-Security-Policy', content_security_policy())])
        return [raw]
    return serve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lane', choices=('A', 'D', 'E', 'F'), required=True)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--worker',action='store_true',help='Explicit A-only local daily worker; hosted wrapper owns hosted supervision')
    args = parser.parse_args()
    if args.worker and args.lane!='A':
        parser.error('--worker is reserved for the explicitly authorized A runtime')
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
        worker_stop=threading.Event();worker_thread=None
        if args.worker:
            from minder_app.agents import Worker
            from minder_app.hosted_worker import run
            worker=Worker(app.store,app.actions,provider=app.provider,services=app.services)
            worker_thread=threading.Thread(target=run,kwargs=dict(app=app,worker=worker,stop_event=worker_stop),daemon=True)
            app.local_worker_thread=worker_thread
            worker_thread.start()
        print(json.dumps(dict(lane=args.lane, api_port=api.server_port, ui_port=ui.server_port,
            model=MODEL, revision=app.runtime_revision, loopback_only=True, scheduler_autostarted=bool(worker_thread), deployment=False)), flush=True)
        try:
            ui.serve_forever()
        finally:
            worker_stop.set()
            if worker_thread:worker_thread.join(timeout=5)
            api.shutdown();thread.join(timeout=5)


if __name__ == '__main__':
    main()
