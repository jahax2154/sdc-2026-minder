from support import AppCase
from minder_app.resources import learning_options
from minder_app.store import AppError


class ResourceTests(AppCase):
    def test_official_topics_unknown_effort_and_no_profile_mutation(self):
        profile = self.save()
        result = self.app.dispatch("POST", "/api/learning-resources", {"topic_ids": ["source-term:python"]}, self.token)
        self.assertEqual(len(result["resources"]), 1)
        item = result["resources"][0]
        self.assertIsNone(item["estimated_hours"])
        self.assertIsNone(item["total_cost"])
        self.assertTrue(item["source"]["uri"].startswith("https://docs.python.org/"))
        self.assertIn("not an employer", item["role_requirement_mapping"])
        self.assertEqual(self.app.dispatch("GET", "/api/profile", {}, self.token), profile)
        with self.assertRaises(AppError):
            learning_options(["arbitrary-evidence-is-not-a-topic"])
