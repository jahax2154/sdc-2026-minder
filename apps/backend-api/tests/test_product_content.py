from unittest.mock import patch
from support import AppCase
from minder_app.store import AppError


class ProductContentTests(AppCase):
    def read(self, body=None):
        return self.app.dispatch("POST", "/api/product/resources", body or {}, self.token)

    def test_verified_library_filters_pagination_and_unknown_metadata(self):
        first = self.read({"limit": 1})
        self.assertEqual(first["total"], 2)
        second = self.read({"offset": first["next_offset"], "limit": 1})
        self.assertNotEqual(first["resources"][0]["resource_id"], second["resources"][0]["resource_id"])
        result = self.read({"topic_ids": ["source-term:python"]})
        item = result["resources"][0]
        self.assertEqual(item["resource_id"], "python-tutorial")
        self.assertIsNone(item["published_at"])
        self.assertIsNone(item["summary"])
        self.assertEqual(item["retrieved_at"], item["source"]["available_at"])
        self.assertFalse(result["cache"]["revalidated_on_request"])
        self.assertEqual(self.read({"types": ["video"]})["status"], "empty")
        self.assertEqual(self.read({"topic_ids": ["unsupported"]})["total"], 0)
        self.assertEqual(self.read({"published_from": "2026-01-01"})["total"], 0)

    def test_detail_rejects_unknown_id_and_url_fetch_inputs(self):
        with self.assertRaises(AppError):
            self.app.dispatch("POST", "/api/product/resource-detail", {"resource_id": "https://127.0.0.1"}, self.token)
        from jsonschema.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.read({"url": "http://169.254.169.254/"})
        result = self.app.dispatch("POST", "/api/product/resource-detail", {"resource_id": "python-tutorial"}, self.token)
        self.assertEqual(result["resource"]["publisher"], "Python Software Foundation")

    def test_source_failure_does_not_become_fixture_and_dedup(self):
        from minder_app.resources import learning_options
        library = learning_options()
        library["resources"].append(dict(library["resources"][0]))
        with patch("minder_app.product_content.learning_options", return_value=library):
            self.assertEqual(self.read()["total"], 2)
        library["resources"][0]["source"]["uri"] = "https://localhost/private"
        with patch("minder_app.product_content.learning_options", return_value=library):
            with self.assertRaises(AppError):
                self.read()
        with patch("minder_app.product_content.learning_options", side_effect=OSError("source unavailable")):
            with self.assertRaises(OSError):
                self.read()
