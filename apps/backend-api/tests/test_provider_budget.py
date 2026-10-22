from support import AppCase
from minder_app.provider_budget import BudgetedProvider
from minder_ml.intelligence.groq_adapter import ProviderError, GroqAdapter


class MockProvider:
    def complete(self, messages):
        return {"text": "mock-only"}


class BudgetTests(AppCase):
    def test_daily_budget_persists_and_is_per_user(self):
        budget = BudgetedProvider(self.store, self.session["profile_id"], MockProvider(), daily_limit=1)
        budget.complete([])
        with self.assertRaises(ProviderError) as ctx:
            BudgetedProvider(self.store, self.session["profile_id"], MockProvider(), daily_limit=1).complete([])
        self.assertEqual(ctx.exception.code, "provider_daily_budget_exceeded")
        BudgetedProvider(self.store, self.store.session()["profile_id"], MockProvider(), daily_limit=1).complete([])

    def test_context_limit_and_missing_access_no_outbound_quota(self):
        budget = BudgetedProvider(self.store, self.session["profile_id"], GroqAdapter(key="", model=""))
        with self.assertRaises(ProviderError):
            budget.complete([])
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM provider_calls").fetchone()[0], 0)
        with self.assertRaises(ProviderError) as ctx:
            budget.complete([{"role":"user","content":"x"*32769}])
        self.assertEqual(ctx.exception.code, "provider_context_budget_exceeded")
