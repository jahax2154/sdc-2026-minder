"""Actual disposable PostgreSQL acceptance; no hosted credentials or shared DB.

Run with pgserver==0.1.4 + psycopg[binary]==3.3.6 and backend/test paths.
Reuses canonical service assertions against a native Store; synthetic data only.
"""
import hashlib
import importlib
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import fasteners
import pgserver
from minder_app.postgres_store import PostgresStore

MODULES = ('test_profiles','test_plans','test_actions','test_agents','test_provider_budget',
    'test_product_migrations','test_product_state','test_product_concurrency','test_generation_state','test_automation_state',
    'test_identity_store','test_conversations','test_bot_preferences','test_documents','test_document_storage','test_replit_storage')


def main():
    with tempfile.TemporaryDirectory(prefix='minder-d-pg-') as tmp:
        pgserver.PostgresServer.runtime_path=Path(tmp)/'runtime'
        pgserver.PostgresServer._lock=fasteners.InterProcessLock(Path(tmp)/'lock')
        with pgserver.get_server(Path(tmp)/'data',cleanup_mode='delete') as server:
            dsn=server.get_uri()
            class NativeTestStore(PostgresStore):
                def __init__(self,path):
                    # Test-only locator allows existing tests to reconnect to
                    # their own schema. Production never treats a URL as a path.
                    super().__init__(dsn,schema='d_'+hashlib.sha256(str(path).encode()).hexdigest()[:24])
                    self.path=str(path)
            modules=[importlib.import_module(name) for name in MODULES]
            with patch('support.Store',NativeTestStore):
                patches=[patch.object(module,'Store',NativeTestStore) for module in modules if hasattr(module,'Store')]
                for item in patches:item.start()
                try:
                    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(module) for module in modules)
                    result=unittest.TextTestRunner(verbosity=2).run(suite)
                finally:
                    for item in reversed(patches):item.stop()
            store=NativeTestStore(Path(tmp)/'acceptance')
            with store.connect() as db:
                print('actual_engine:', db.execute('SELECT version()').fetchone()[0].split(' on ')[0])
            if not result.wasSuccessful():raise SystemExit(1)
            from minder_app.product_migrations import migrate
            migrate(store)
            original=store.put("synthetic-owner","acceptance","restart",
                {"nested":{"enabled":True,"optional":None,"decimal":1.5},"timestamp":"2026-10-24T00:00:00Z"},None)
            with store.connect() as db:
                assert [row[0] for row in db.execute("SELECT version FROM migrations ORDER BY version")] == [1,5,6,7,8]
                db.execute("SELECT ? AS literal,'?' AS question,'50%' AS percent",("synthetic",))
            # Stop only the server created above, restart the same data directory,
            # then read through a fresh Python process, not a retained connection.
            pgserver.pg_ctl(['-w','stop'],pgdata=server.pgdata)
            server.ensure_postgres_running()
            child_env=dict(os.environ, MINDER_D_LOCAL_TEST_DSN=server.get_uri(),MINDER_D_LOCAL_TEST_SCHEMA=store.schema)
            child=subprocess.run([sys.executable,'-B','-c',
                "import os,json;from minder_app.postgres_store import PostgresStore;"
                "s=PostgresStore(os.environ['MINDER_D_LOCAL_TEST_DSN'],schema=os.environ['MINDER_D_LOCAL_TEST_SCHEMA']);"
                "print(json.dumps(s.get('synthetic-owner','acceptance','restart'),sort_keys=True))"],
                env=child_env,capture_output=True,text=True,check=True)
            import json
            assert json.loads(child.stdout)==original
            print('Native server stop/start + fresh-process refetch: PASS (JSON booleans/null/number/timestamp/version).')
            print('Hosted acceptance: NOT performed; local native PostgreSQL only.')

if __name__=='__main__':main()
