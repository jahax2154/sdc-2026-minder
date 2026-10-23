"""Shared application call budgets for chat and workers; no provider credentials."""
from datetime import datetime, timezone
import json
import os
import threading
from minder_ml.intelligence.groq_adapter import GroqAdapter, ProviderError
from .store import uid

SLOTS = threading.BoundedSemaphore(2)


class BudgetedProvider:
    def __init__(self, store, owner, provider, *, daily_limit=None):
        self.store, self.owner, self.provider = store, owner, provider
        self.limit = max(1, min(100, int(daily_limit if daily_limit is not None else
            getattr(provider, "daily_limit", os.environ.get("MINDER_LLM_DAILY_LIMIT", "20")))))
        with store.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS provider_calls(owner TEXT, day TEXT, attempts INTEGER, "
                       "PRIMARY KEY(owner,day))")
            db.execute("INSERT OR IGNORE INTO migrations VALUES(4)")

    def complete(self, messages):
        if len(json.dumps(messages).encode()) > 32768:
            raise ProviderError("provider_context_budget_exceeded", uid())
        if isinstance(self.provider, GroqAdapter) and (not self.provider.key or not self.provider.model):
            return self.provider.complete(messages)  # missing access consumes no outbound-call quota
        if not SLOTS.acquire(timeout=1):
            raise ProviderError("provider_concurrency_limit", uid(), retryable=True)
        try:
            day = datetime.now(timezone.utc).date().isoformat()
            with self.store.transaction() as db:
                db.execute("INSERT OR IGNORE INTO provider_calls VALUES(?,?,0)", (self.owner, day))
                row = db.execute("SELECT attempts FROM provider_calls WHERE owner=? AND day=?", (self.owner, day)).fetchone()
                if row[0] >= self.limit:
                    raise ProviderError("provider_daily_budget_exceeded", uid())
                db.execute("UPDATE provider_calls SET attempts=attempts+1 WHERE owner=? AND day=?", (self.owner, day))
            return self.provider.complete(messages)
        finally:
            SLOTS.release()
