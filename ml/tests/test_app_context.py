import unittest
from minder_ml.intelligence.app_context import CareerServices, grounded_statements


class ContextBoundsTests(unittest.TestCase):
    def test_explicit_view_and_typed_skills_required(self):
        import json
        from pathlib import Path
        profile = json.loads((Path(__file__).resolve().parents[2] /
            "contracts/fixtures/parallel-v1/complete_profile.json").read_text())["payload"]
        service = CareerServices(roles=[{"role_id": "role-1"}])
        with self.assertRaises(ValueError):
            service.career_context(profile, expected_profile_version=profile["version"],
                                   selected_skill_ids=["arbitrary-evidence-subject"])
        with self.assertRaises(ValueError):
            service.career_context(profile, expected_profile_version=profile["version"],
                                   selected_role_ids=["role-1"] * 4)
        with self.assertRaises(ValueError):
            service.career_context(profile, expected_profile_version=profile["version"], selected_role_ids=["not-known"])
