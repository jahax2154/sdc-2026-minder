"""Composition guards only: these tests claim no real PG or hosted acceptance."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from deploy.replit_runtime import settings, validate_application, prepare_auth


class ReplitRuntimeTests(unittest.TestCase):
    def test_hosted_public_discovery_uses_environment_without_receiving_server_secrets(self):
        env = dict(CLERK_PUBLISHABLE_KEY="pk_test_example", CLERK_SECRET_KEY="server-only",
                   GROQ_API_KEY="private-provider", CLERK_ISSUER="https://existing.clerk.accounts.dev")
        with patch("deploy.operator.derive_clerk_public", return_value={"CLERK_JWT_KEY": "public-pem"}) as discovery:
            names = prepare_auth(env)
        self.assertEqual(names, ["CLERK_JWT_KEY"])
        self.assertEqual(env["CLERK_SECRET_KEY"], "server-only")
        self.assertEqual(env["CLERK_ISSUER"], "https://existing.clerk.accounts.dev")
        self.assertEqual(env["CLERK_JWT_KEY"], "public-pem")
        sent = discovery.call_args.args[0]
        self.assertNotIn("CLERK_SECRET_KEY", sent)
        self.assertNotIn("GROQ_API_KEY", sent)
        with self.assertRaises(ValueError):
            prepare_auth(dict(env, MINDER_CLERK_INSTANCE_MODE="production"))

    def config(self):
        return dict(MINDER_HOSTING_TARGET="replit", MINDER_DEPLOYMENT_KIND="reserved-vm",
            MINDER_ENV="production", MINDER_AUTH_MODE="managed", MINDER_AUTH_PROVIDER="clerk",
            MINDER_DOCUMENT_STORAGE="replit-app-storage", DATABASE_URL="postgresql://service:example@db/provider",
            MINDER_DOCUMENT_STORAGE_BUCKET_ID="private-bucket", MINDER_RELEASE_SHA="a"*40,
            MINDER_JUDGE_URL="https://minder.replit.app", CLERK_AUTHORIZED_PARTIES="https://minder.replit.app",
            GROQ_MODEL="qwen/qwen3.8-27b", GROQ_API_KEY="server-only-example")

    def test_published_filesystem_and_anonymous_modes_cannot_be_relabelled_durable(self):
        values = self.config()
        self.assertEqual(settings(values), 8080)
        for field, value in (("DATABASE_URL", "sqlite:///tmp/state.sqlite3"),
                ("MINDER_DOCUMENT_STORAGE", "private-volume"), ("MINDER_AUTH_MODE", "anonymous"),
                ("MINDER_HOSTING_TARGET", "railway"), ("MINDER_DEPLOYMENT_KIND", "autoscale"),
                ("MINDER_DOCUMENT_STORAGE_BUCKET_ID", ""), ("GROQ_API_KEY", ""),
                ("MINDER_RELEASE_SHA", "older-source"), ("MINDER_JUDGE_URL", "http://localhost:8080"),
                ("CLERK_AUTHORIZED_PARTIES", "https://another.replit.app"), ("PORT", "70000")):
            with self.subTest(field=field), self.assertRaises(ValueError) as error:
                settings(dict(values, **{field:value}))
            self.assertNotIn("server-only-example", str(error.exception))
            self.assertNotIn("service:example", str(error.exception))

    def test_actual_factory_components_must_match_shared_store_and_existing_worker(self):
        store = SimpleNamespace(engine="postgresql", persistence_mode="managed-postgresql")
        library = SimpleNamespace(store=store, backend=lambda: SimpleNamespace(mode="replit-app-storage"))
        app = SimpleNamespace(store=store, document_library=library, managed_identity_required=True,
                              scheduled_worker=object())
        validate_application(app)
        for replacement in (dict(store=SimpleNamespace(engine="sqlite", persistence_mode="managed-postgresql")),
                dict(document_library=SimpleNamespace(store=store, backend=lambda: SimpleNamespace(mode="local-development"))),
                dict(document_library=SimpleNamespace(store=object(), backend=lambda: SimpleNamespace(mode="replit-app-storage"))),
                dict(managed_identity_required=False), dict(scheduled_worker=None)):
            with self.subTest(replacement=list(replacement)), self.assertRaises(RuntimeError):
                validate_application(SimpleNamespace(**dict(vars(app), **replacement)))


if __name__ == "__main__":
    unittest.main()
