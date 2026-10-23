"""A namespace guard checks; no real provider calls or credential output."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from minder_ml.intelligence.policy import ROOT
from minder_ml.intelligence.integration_cli import a_provider_config,worker_run
sys.path.insert(0,str(ROOT/'apps/backend-api'))


class NamespaceTests(unittest.TestCase):
    def test_other_lane_secret_refused_before_any_private_read(self):
        for lane in ('session-b','session-c'):
            with patch.dict(os.environ,{'MINDER_GROQ_SECRET_FILE':str(ROOT.parent/lane/'.env.groq.local')}), patch('minder_app.config.load_provider_config') as load:
                with self.assertRaisesRegex(ValueError,'must_not_use_another_lane'):a_provider_config()
                load.assert_not_called()

    def test_other_lane_worker_database_refused_before_open(self):
        with patch.dict(os.environ,{'MINDER_DB_PATH':str(ROOT/'ml/artifacts/session-c/runtime/forbidden.sqlite3')}), patch('minder_app.store.Store') as store:
            with self.assertRaisesRegex(ValueError,'A worker adapter database'):worker_run('fictional-owner',once=False,max_seconds=1)
            store.assert_not_called()

    def test_missing_owner_refused_before_database_open(self):
        with patch.dict(os.environ,{'MINDER_DB_PATH':str(ROOT/'ml/artifacts/session-a/runtime/unused.sqlite3')}), patch('minder_app.store.Store') as store:
            with self.assertRaisesRegex(ValueError,'single-owner'):worker_run('')
            store.assert_not_called()

if __name__=='__main__':unittest.main()
