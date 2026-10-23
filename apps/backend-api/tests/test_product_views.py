from jsonschema import validate
from support import AppCase, ROOT
import json


class ProductViewTests(AppCase):
    def read(self, name, body=None):
        result = self.app.dispatch("POST", "/api/product/views/" + name, body or {}, self.token)
        schema = json.loads((ROOT / "docs/execution/product-v2/contracts.schema.json").read_text())
        validate(result, schema["$defs"]["ProductView"])
        return result

    def test_no_profile_and_unavailable_service_are_honest(self):
        result = self.read("career-match")
        self.assertEqual(result["status"], "unavailable")
        self.assertIsNone(result["profile_version"])
        profile = self.save()
        result = self.read("career-match")
        self.assertEqual(result["profile_version"], profile["version"])
        self.assertIsNone(result["data"]["recommendation"])
        self.assertNotIn("internal", result["data"])

    def test_actual_plan_tasks_empty_and_owner_isolation(self):
        self.assertEqual(self.read("tasks")["data"]["total"], 0)
        plan = self.make_plan()["plan"]
        result = self.read("tasks", {"plan_id": plan["plan_id"], "limit": 1})
        self.assertEqual(result["data"]["tasks"][0]["state_version"], plan["state_version"])
        self.assertEqual(result["data"]["total"], len(plan["tasks"]))
        self.assertEqual(self.read("roadmap")["data"]["plans"], [plan])
        other = self.store.session()["token"]
        self.assertEqual(self.app.dispatch("GET", "/api/product/views/tasks", {}, other)["data"]["total"], 0)
        from minder_app.store import AppError
        with self.assertRaises(AppError):
            self.app.dispatch("POST", "/api/product/views/tasks", {"plan_id": plan["plan_id"]}, other)

    def test_every_view_and_capabilities(self):
        for name in ("overview", "career-match", "roadmap", "tasks", "progress", "news"):
            self.read(name)
        result = self.app.dispatch("GET", "/api/product/capabilities", {}, self.token)
        operations = [o for o in result["operations"] if o["owner"] == "E"]
        self.assertTrue(all(o["status"] == "implemented" for o in operations))

    def test_d_snapshot_selected_plan_next_task_and_canonical_progress(self):
        from support import fixture
        self.app.services.roles = [fixture("source_role")]
        # Use the actual fixture role identity rather than assuming an alias.
        self.app.services.roles[0]["role_id"] = "synthetic-role"
        plan = self.make_plan()["plan"]
        self.app.dispatch("PUT", "/api/product/direction", dict(role_id=plan["selected_role_id"],
            plan_id=plan["plan_id"], expected_version=None, idempotency_key="select"), self.token)
        overview = self.read("overview")["data"]
        self.assertEqual(overview["active_plan"]["plan_id"], plan["plan_id"])
        self.assertEqual(overview["next_task"]["task_id"], plan["task_ids"][0])
        task = plan["tasks"][0]
        completed = self.app.dispatch("POST", "/api/product/task-action", dict(plan_id=plan["plan_id"],
            task_id=task["task_id"], expected_state_version=plan["state_version"],
            operation="complete", idempotency_key="complete"), self.token)
        progress = self.read("progress")["data"]
        canonical = self.app.dispatch("GET", "/api/product/progress", {}, self.token)
        for field in ("fraction", "eligible_count", "completed_count", "denominator", "state_version"):
            self.assertEqual(progress[field], canonical[field])
        filtered = self.read("tasks", {"state": "proposed"})["data"]
        self.assertEqual(filtered["total"], 0)
        self.assertEqual(filtered["progress"]["completed_count"], 1)
        self.assertIsNone(self.read("overview")["data"]["next_task"])
        self.assertFalse(completed["plan"]["tasks"][0]["mastery_verified"])

    def test_wsgi_auth_invalid_input_and_service_failure(self):
        from minder_ml.intelligence.integration_cli import wsgi_request
        from unittest.mock import patch
        status, result = wsgi_request(self.app, "GET", "/api/product/views/overview")
        self.assertEqual(status, 401)
        status, result = wsgi_request(self.app, "POST", "/api/product/views/tasks", {"limit": -1}, self.token)
        self.assertEqual(status, 422)
        self.assertEqual(set(result), {"code", "request_id"})
        self.save()
        with patch.object(self.app.services, "career_context", side_effect=RuntimeError("private backend detail")):
            status, result = wsgi_request(self.app, "POST", "/api/product/views/career-match", {}, self.token)
        self.assertEqual(status, 500)
        self.assertNotIn("private", str(result))
