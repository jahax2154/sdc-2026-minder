import json
from pathlib import Path
import tempfile
import unittest
from minder_app.api import Application
from minder_app.store import Store

ROOT = Path(__file__).resolve().parents[3]


def fixture(name):
    return json.loads((ROOT / "contracts/fixtures/parallel-v1" / (name + ".json")).read_text())["payload"]


class AppCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "test.sqlite3")
        self.app = Application(self.store)
        self.session = self.store.session()
        self.token = self.session["token"]

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        return self.app.dispatch("PUT", "/api/profile", {"profile": fixture("complete_profile")}, self.token)

    def make_plan(self):
        self.profile = self.save()
        plan = fixture("plan_progress")
        plan["profile_id"] = self.profile["profile_id"]
        return self.app.dispatch("POST", "/api/plans", dict(plan=plan, idempotency_key="create-1"), self.token)

    def setup_request(self):
        plan = self.make_plan()["plan"]
        req = dict(kind="complete_task", target_id=plan["plan_id"], expected=plan["state_version"],
                   diff=[dict(path="/tasks/synthetic-task/state", before="scheduled", after="completed")],
                   reason="User clicked Complete", evidence_ids=[])
        return plan, req
