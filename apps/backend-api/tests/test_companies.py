from urllib.error import URLError
from support import AppCase, fixture
from minder_app.companies import CompanyExplorer


class CompanyTests(AppCase):
    def test_generic_company_context_uses_current_career_service_policy(self):
        from minder_ml.intelligence.app_context import CareerServices
        from minder_ml.intelligence.role_fit import POLICY_ID, MARKET_POLICY
        from minder_ml.intelligence.personal_service import PersonalMatchingService
        class ObservedPersonal(PersonalMatchingService):
            def assess(self, profile, roles, **kwargs):
                self.received = kwargs
                return super().assess(profile, roles, **kwargs)
        role = fixture("source_role")
        role["role_id"] = "onet:15-1252.00"
        personal = ObservedPersonal()
        services = CareerServices(personal, roles=[role])
        profile = self.save()
        result = CompanyExplorer(services, fetch=lambda _: b"country mock").explore(profile, "bosch", role["role_id"])
        self.assertEqual(personal.received["policy_version"], POLICY_ID)
        self.assertEqual(personal.received["market_period_policy_key"], MARKET_POLICY)
        selected = result["selected_posting"]
        self.assertEqual(selected["generic_occupation_assessment"]["policy_version"], POLICY_ID)
        self.assertEqual(result["result"]["matching_requirements"], [])
        self.assertIn("unavailable", selected["company_specific_assessment"])
        self.assertFalse(result["main_recommendations_changed"])

    def test_verified_preferred_criteria_keep_mandatory_and_competence_unknown(self):
        from support import fixture
        from test_chat import FixturePersonal
        from minder_ml.intelligence.app_context import CareerServices
        role = fixture("source_role")
        role["role_id"] = "onet:15-1252.00"
        service = CareerServices(FixturePersonal(), roles=[role])
        result = CompanyExplorer(service, fetch=lambda _: b"country page mock").explore(
            self.save(), "Bosch", "onet:15-1252.00")
        self.assertEqual(result["result"]["status"], "found")
        self.assertEqual(result["selected_posting"]["required"], [])
        self.assertTrue(result["selected_posting"]["preferred"])
        self.assertTrue(result["selected_posting"]["qualifications_requirement_level_unspecified"])
        self.assertEqual(result["result"]["matching_requirements"], [])
        self.assertIn("unknown", result["result"]["unknown_requirements"][0])
        self.assertFalse(result["main_recommendations_changed"])

    def test_missing_source_never_infers_universal_absence(self):
        p = self.save()
        def unavailable(url):
            raise URLError("offline mock")
        result = CompanyExplorer(self.app.services, fetch=unavailable).explore(p, "intel", "role")
        self.assertEqual(result["result"]["status"], "requirements_unavailable")
        self.assertIn("official_page_unavailable", result["result"]["searched_scope"][0])
        self.assertFalse(result["main_recommendations_changed"])
        self.assertEqual(self.app.dispatch("GET", "/api/profile", {}, self.token), p)

    def test_country_page_is_not_a_verified_vacancy(self):
        result = CompanyExplorer(self.app.services, fetch=lambda _: b"country careers page").explore(
            self.save(), "intel", "role")
        self.assertEqual(result["result"]["status"], "requirements_unavailable")
        self.assertEqual(len(result["result"]["official_evidence"]), 1)
