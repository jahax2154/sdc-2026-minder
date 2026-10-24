"""Replit Reserved VM: existing Python app, managed state and cohosted worker.

Business data must be PostgreSQL/private App Storage. No SQLite or writable
published-filesystem fallback is provided. Deployment settings still need actual
provider verification; environment declarations alone do not prove durability.
"""
import importlib
import os
import re
import signal
import threading
from urllib.parse import urlsplit
from wsgiref.simple_server import make_server


def prepare_auth(environ=None):
    """Derive public auth settings from deployment environment, not a Mac file."""
    env = os.environ if environ is None else environ
    if env.get("MINDER_CLERK_INSTANCE_MODE", "preview") != "preview":
        raise ValueError("existing_Minder_Development_instance_required")
    from deploy.operator import derive_clerk_public
    public = {name: env.get(name, "") for name in ("CLERK_PUBLISHABLE_KEY", "CLERK_ISSUER",
              "CLERK_JWT_KEY", "CLERK_AUTHORIZED_PARTIES", "MINDER_JUDGE_URL")}
    public["MINDER_CLERK_INSTANCE_MODE"] = "preview"
    updates = derive_clerk_public(public)  # No server secret is passed to discovery.
    for name, value in updates.items():
        if not env.get(name):
            env[name] = value
    return sorted(updates)


def settings(environ=None):
    env = os.environ if environ is None else environ
    required = {"MINDER_ENV": "production", "MINDER_AUTH_MODE": "managed",
                "MINDER_AUTH_PROVIDER": "clerk", "MINDER_DOCUMENT_STORAGE": "replit-app-storage",
                "MINDER_HOSTING_TARGET": "replit", "MINDER_DEPLOYMENT_KIND": "reserved-vm",
                "GROQ_MODEL": "qwen/qwen3.8-27b"}
    if any(env.get(name) != value for name, value in required.items()):
        raise ValueError("Replit_explicit_managed_postgres_object_storage_runtime_required")
    try:
        database = urlsplit(env.get("DATABASE_URL", ""))
        if (database.scheme not in ("postgres", "postgresql") or not database.hostname
                or not database.username or not database.path.strip("/") or database.fragment):
            raise ValueError()
    except ValueError:
        raise ValueError("Replit_managed_PostgreSQL_configuration_required") from None
    if not env.get("MINDER_DOCUMENT_STORAGE_BUCKET_ID", "").strip():
        raise ValueError("Replit_explicit_private_bucket_required")
    if not env.get("GROQ_API_KEY", "").strip():
        raise ValueError("Replit_private_provider_credential_required")
    if not re.fullmatch(r"[0-9a-f]{40}", env.get("MINDER_RELEASE_SHA", "")):
        raise ValueError("Replit_accepted_integrated_release_SHA_required")
    try:
        site = urlsplit(env.get("MINDER_JUDGE_URL", ""))
        if (site.scheme != "https" or not site.hostname or site.hostname in ("localhost", "127.0.0.1")
                or site.username or site.password or site.path not in ("", "/") or site.query or site.fragment
                or site.port not in (None, 443)):
            raise ValueError()
        origin = site.scheme + "://" + site.netloc
        if origin not in [part.strip() for part in env.get("CLERK_AUTHORIZED_PARTIES", "").split(",")]:
            raise ValueError()
        port = int(env.get("PORT", "8080"))
        if not 1 <= port <= 65535:
            raise ValueError()
    except ValueError:
        raise ValueError("Replit_verified_HTTPS_origin_and_port_required") from None
    return port


def validate_application(app):
    store = getattr(app, "store", None)
    if (getattr(store, "engine", None) != "postgresql"
            or getattr(store, "persistence_mode", None) != "managed-postgresql"):
        raise RuntimeError("D_managed_PostgreSQL_store_not_integrated")
    library = getattr(app, "document_library", None)
    if (library is None or getattr(library, "store", None) is not store
            or getattr(library.backend(), "mode", None) != "replit-app-storage"):
        raise RuntimeError("D_private_Replit_document_storage_not_integrated")
    if getattr(app, "managed_identity_required", False) is not True:
        raise RuntimeError("A_verified_server_identity_boundary_not_integrated")
    if getattr(app, "scheduled_worker", None) is None:
        raise RuntimeError("A_existing_persisted_worker_not_integrated")


def serve(app, port):
    from minder_app.hosted_worker import run
    from minder_ml.intelligence.product_runtime import ProductServer, QuietHandler, web_app
    stopping = threading.Event()
    failures = []
    with make_server("0.0.0.0", port, web_app(app), server_class=ProductServer, handler_class=QuietHandler) as server:
        def worker_main():
            try:
                run(app, stop_event=stopping)
            except Exception:
                # No provider/DB exception strings or private job content in logs.
                failures.append("existing_hosted_worker_failed")
                server.shutdown()
        worker = threading.Thread(target=worker_main, name="minder-existing-worker", daemon=True)
        app.local_worker_thread = worker  # A's existing health liveness field.
        worker.start()
        def stop(signum, frame):
            stopping.set()
            threading.Thread(target=server.shutdown, daemon=True).start()
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        try:
            server.serve_forever(poll_interval=0.5)
        finally:
            stopping.set()
            worker.join(timeout=30)
        if failures:
            raise RuntimeError(failures[0])


def main():
    os.umask(0o077)
    prepare_auth()
    port = settings()
    from minder_app.auth_adapter import AuthConfig, _verifier
    _verifier(AuthConfig.from_env())
    from deploy.artifacts import inventory
    inventory(verify=True)
    runtime = importlib.import_module("minder_ml.intelligence.product_runtime")
    factory = getattr(runtime, "build_replit", None)
    if factory is None:
        raise RuntimeError("A_Replit_factory_not_integrated")
    app = factory()
    validate_application(app)
    serve(app, port)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Connection/SDK exceptions may embed credentials. Diagnose through
        # sanitized configuration checks, never raw production tracebacks.
        print("Minder_Replit_startup_or_worker_failed_check_private_configuration", flush=True)
        raise SystemExit(1) from None
