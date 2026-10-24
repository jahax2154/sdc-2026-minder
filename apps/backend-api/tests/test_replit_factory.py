"""A composition tests with DECLARED SQLite-backed adapters; no PG/hosting claim."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from minder_app.store import Store,AppError
from minder_ml.intelligence.product_runtime import build_replit,MODEL

ENV=dict(MINDER_ENV='production',MINDER_AUTH_MODE='managed',MINDER_AUTH_PROVIDER='clerk',
    MINDER_DOCUMENT_STORAGE='replit-app-storage')


class ReplitFactoryTests(unittest.TestCase):
    def test_d_environment_export_and_managed_marker_are_supported(self):
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as root:
            store=Store(Path(root)/'declared-environment-fixture.sqlite3')
            store.engine='postgresql';store.persistence_mode='managed-postgresql'
            configured=Mock(return_value=store)
            module=SimpleNamespace(PostgresStore=SimpleNamespace(from_environment=configured))
            library=SimpleNamespace(store=store,backend=lambda:SimpleNamespace(mode='replit-app-storage'))
            with patch.dict('os.environ',ENV,clear=True),patch.dict('sys.modules',{'minder_app.postgres_store':module}),\
                    patch('minder_app.config.load_provider_config',return_value=SimpleNamespace(api_key='',model=MODEL,daily_limit=20)):
                app=build_replit(document_library=library)
            configured.assert_called_once_with()
            self.assertIs(app.store,store)

    def test_d_export_receives_server_url_and_schema_without_path_conversion(self):
        with tempfile.TemporaryDirectory() as root:
            store=Store(Path(root)/'declared-constructor-fixture.sqlite3')
            store.engine='postgresql';store.persistence_mode='postgresql'
            captured={}
            def constructor(url,*,schema):
                captured.update(url=url,schema=schema)
                return store
            module=SimpleNamespace(PostgresStore=constructor)
            library=SimpleNamespace(store=store,backend=lambda:SimpleNamespace(mode='replit-app-storage'))
            env=dict(ENV,DATABASE_URL='postgresql://test.invalid/minder',MINDER_DB_SCHEMA='bounded_test')
            with patch.dict('os.environ',env,clear=True),patch.dict('sys.modules',{'minder_app.postgres_store':module}),\
                    patch('minder_app.config.load_provider_config',return_value=SimpleNamespace(api_key='',model=MODEL,daily_limit=20)):
                app=build_replit(document_library=library)
            self.assertEqual(captured,dict(url=env['DATABASE_URL'],schema='bounded_test'))
            self.assertIs(app.store,store)
            self.assertNotEqual(store.path,env['DATABASE_URL'])

    def test_missing_host_boundary_fails_before_constructing_any_store(self):
        with patch.dict('os.environ',{},clear=True),self.assertRaisesRegex(ValueError,'managed_auth_and_private_storage'):
            build_replit()

    def test_missing_committed_d_adapter_fails_closed_without_sqlite_fallback(self):
        with patch.dict('os.environ',ENV,clear=True),patch.dict('sys.modules',{'minder_app.postgres_store':None}):
            with self.assertRaisesRegex(RuntimeError,'D_postgresql_store_handoff_not_integrated'):
                build_replit()

    def test_actual_sqlite_store_cannot_be_passed_as_production_postgresql(self):
        with tempfile.TemporaryDirectory() as root,patch.dict('os.environ',ENV,clear=True):
            with self.assertRaisesRegex(ValueError,'D_managed_postgresql_store_required'):
                build_replit(store=Store(Path(root)/'fixture.sqlite3'))

    def test_declared_adapter_composition_reuses_worker_and_managed_boundary(self):
        # Markers exercise ONLY A's wiring. This remains a SQLite fixture and is
        # explicitly not evidence that D's SQL adapter works on PostgreSQL.
        with tempfile.TemporaryDirectory() as root,patch.dict('os.environ',ENV,clear=True):
            store=Store(Path(root)/'declared-composition-fixture.sqlite3')
            store.engine='postgresql';store.persistence_mode='postgresql'
            backend=SimpleNamespace(mode='replit-app-storage')
            library=SimpleNamespace(store=store,backend=lambda:backend)
            config=SimpleNamespace(api_key='',model=MODEL,daily_limit=20)
            with patch('minder_app.config.load_provider_config',return_value=config):
                app=build_replit(store=store,document_library=library)
            self.assertIs(app.store,store)
            self.assertIs(app.document_library,library)
            self.assertIs(app.scheduled_worker.store,store)
            self.assertIs(app.scheduled_worker.provider,app.provider)
            self.assertTrue(app.managed_identity_required)
            self.assertEqual(app.provider.model,MODEL)
            self.assertTrue(app.public_retrieval)
            with self.assertRaises(AppError):
                app.dispatch('POST','/api/session',{},'')
            with store.connect() as db:
                self.assertEqual(db.execute('SELECT COALESCE(SUM(attempts),0) FROM provider_calls').fetchone()[0],0)

    def test_declared_private_storage_is_required_after_composition(self):
        with tempfile.TemporaryDirectory() as root,patch.dict('os.environ',ENV,clear=True):
            store=Store(Path(root)/'declared-fixture.sqlite3')
            store.engine='postgresql';store.persistence_mode='postgresql'
            library=SimpleNamespace(store=store,backend=lambda:SimpleNamespace(mode='local-development'))
            with patch('minder_app.config.load_provider_config',return_value=SimpleNamespace(api_key='',model=MODEL,daily_limit=20)):
                with self.assertRaisesRegex(ValueError,'D_private_replit_document_backend_required'):
                    build_replit(store=store,document_library=library)
