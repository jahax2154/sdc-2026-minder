"""One Railway instance: existing concurrent Python HTTP app and persisted worker.

The A-owned factory installs identity middleware, D migrations/storage, and model
orchestration. This wrapper never silently starts a local anonymous application.
"""
import importlib
import os
from pathlib import Path
import signal
import threading
from wsgiref.simple_server import make_server


def settings(environ=None):
    env = os.environ if environ is None else environ
    mount = env.get("RAILWAY_VOLUME_MOUNT_PATH", "")
    if not mount or not Path(mount).is_absolute() or Path(mount).is_symlink():
        raise ValueError("hosted_persistent_volume_required")
    root = Path(mount).resolve()
    if root == Path("/") or not root.is_mount():
        raise ValueError("hosted_volume_not_mounted")
    if env.get("MINDER_DATA_ROOT") != str(root) or env.get("MINDER_ENV") != "production":
        raise ValueError("hosted_explicit_production_data_root_required")
    database = Path(env.get("MINDER_DB_PATH", str(root / "minder/runtime.sqlite3"))).resolve()
    if not database.is_relative_to(root) or database == root:
        raise ValueError("hosted_database_must_be_inside_persistent_volume")
    if env.get("MINDER_DOCUMENT_STORAGE") != "private-volume":
        raise ValueError("hosted_private_document_volume_required")
    documents = Path(env.get("MINDER_DOCUMENT_STORAGE_ROOT", str(database.parent / "documents"))).resolve()
    if not documents.is_relative_to(root) or documents in (root, database):
        raise ValueError("hosted_documents_must_be_inside_private_volume")
    if env.get("MINDER_AUTH_MODE") != "managed" or env.get("MINDER_AUTH_PROVIDER") != "clerk":
        raise ValueError("hosted_managed_identity_required")
    if env.get("GROQ_MODEL") != "qwen/qwen3.8-27b" or not env.get("GROQ_API_KEY"):
        raise ValueError("hosted_verified_provider_configuration_required")
    port = int(env.get("PORT", "8080"))
    if not 1 <= port <= 65535:
        raise ValueError("invalid_hosted_port")
    return database, port


def main():
    os.umask(0o077)
    database, port = settings()
    from minder_app.auth_adapter import AuthConfig, _verifier
    _verifier(AuthConfig.from_env())  # Fail before accepting traffic.
    from deploy.artifacts import inventory
    inventory(verify=True)
    runtime = importlib.import_module("minder_ml.intelligence.product_runtime")
    factory = getattr(runtime, "build_hosted", None)
    if factory is None:
        raise RuntimeError("A_build_hosted_factory_not_integrated")
    app = factory(database=database)
    if getattr(app.store, "persistence_mode", None) != "mounted-sqlite":
        raise RuntimeError("D_verified_volume_store_not_integrated")
    # A must explicitly attest that its common boundary protects ALL private routes.
    if getattr(app, "managed_identity_required", False) is not True:
        raise RuntimeError("A_managed_identity_boundary_not_installed")
    if getattr(app, "scheduled_worker", None) is None:
        raise RuntimeError("A_persistent_mindbot_worker_not_integrated")
    from minder_app.hosted_worker import run
    stopping = threading.Event()
    failures = []
    from minder_ml.intelligence.product_runtime import ProductServer, QuietHandler, web_app
    with make_server("0.0.0.0", port, web_app(app), server_class=ProductServer, handler_class=QuietHandler) as server:
        def worker_main():
            try:
                run(app, stop_event=stopping)
            except Exception:
                failures.append("hosted_worker_failed")
                server.shutdown()
        worker = threading.Thread(target=worker_main, name="minder-existing-worker", daemon=True)
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


if __name__ == "__main__":
    main()
