import os
from pathlib import Path
import tempfile
import unittest
from minder_app.config import load_provider_config, ConfigError


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / ".env.groq.local"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text, mode=0o600):
        self.path.write_text(text)
        self.path.chmod(mode)

    def test_empty_missing_and_environment_precedence(self):
        self.assertFalse(load_provider_config(path=self.path, environ={}).presence()["api_key_present"])
        self.write("GROQ_API_KEY='mock-secret-only'\nGROQ_MODEL=mock/model\n")
        config = load_provider_config(path=self.path, environ={"GROQ_API_KEY": "mock-environment"})
        self.assertEqual(config.api_key, "mock-environment")
        self.assertEqual(config.model, "mock/model")
        self.assertEqual(repr(config), "<ProviderConfig redacted>")
        self.assertNotIn("mock-secret", repr(config))

    def test_permissions_symlinks_and_unknown_fields_fail_closed(self):
        self.write("GROQ_API_KEY=mock-only\n", mode=0o644)
        with self.assertRaises(ConfigError):
            load_provider_config(path=self.path, environ={})
        self.path.chmod(0o600)
        link = Path(self.tmp.name) / "link"
        link.symlink_to(self.path)
        with self.assertRaises(ConfigError):
            load_provider_config(path=link, environ={})
        self.write("MINDER_DB_PATH=/somewhere/else\n")
        with self.assertRaises(ConfigError) as ctx:
            load_provider_config(path=self.path, environ={})
        self.assertNotIn("somewhere", str(ctx.exception))

    def test_literals_not_executed_and_no_values_in_failures(self):
        marker = Path(self.tmp.name) / "must-not-exist"
        self.write("GROQ_API_KEY=$(touch " + str(marker) + ")\n")
        load_provider_config(path=self.path, environ={})
        self.assertFalse(marker.exists())
        for text in ["GROQ_API_KEY=mock-private\nGROQ_API_KEY=again\n",
                     "GROQ_API_KEY='mock-private\n", "MINDER_LLM_DAILY_LIMIT=private-invalid\n"]:
            self.write(text)
            with self.assertRaises(ConfigError) as ctx:
                load_provider_config(path=self.path, environ={})
            self.assertNotIn("private", str(ctx.exception))
