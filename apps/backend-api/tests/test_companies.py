from urllib.error import URLError
from support import AppCase, fixture
from minder_app.companies import CompanyExplorer


class CompanyTests(AppCase):
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
