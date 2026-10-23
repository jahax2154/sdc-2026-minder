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
