"""D owns additive product migrations; existing state remains in Store documents."""


def migrate(store):
    with store.transaction() as db:
        # No profile/plan/task mirror: these rows only bind retries and audit edits.
        db.execute("CREATE TABLE IF NOT EXISTS product_requests("
                   "owner TEXT NOT NULL, key TEXT NOT NULL, scope TEXT NOT NULL, "
                   "result TEXT NOT NULL, PRIMARY KEY(owner,key))")
        db.execute("CREATE TABLE IF NOT EXISTS product_events("
                   "owner TEXT NOT NULL, id TEXT NOT NULL, body TEXT NOT NULL, "
                   "PRIMARY KEY(owner,id))")
        db.execute("INSERT OR IGNORE INTO migrations VALUES(5)")
