import json
from support import AppCase
from minder_app.product_migrations import migrate
from minder_app.store import Store


class MigrationTests(AppCase):
    def test_fresh_and_repeat(self):
        migrate(self.store)
        migrate(self.store)
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM migrations WHERE version=5").fetchone()[0], 1)
            db.execute("INSERT INTO product_requests VALUES('a','k','s','{}')")
            db.execute("INSERT INTO product_requests VALUES('b','k','s','{}')")

    def test_disposable_v4_upgrade_preserves_state_and_history(self):
        from minder_app.provider_budget import BudgetedProvider
        BudgetedProvider(self.store, "test-no-provider", None)
        profile = self.save()
        before = self.store.list(profile["profile_id"], "profile")
        migrate(self.store)
        restarted = Store(self.store.path)
        self.assertEqual(restarted.list(profile["profile_id"], "profile"), before)
        with restarted.connect() as db:
            self.assertEqual([r[0] for r in db.execute("SELECT version FROM migrations ORDER BY version")], [1,2,3,4,5])
            self.assertEqual(json.loads(db.execute("SELECT body FROM history WHERE kind='profile'").fetchone()[0]), profile)
