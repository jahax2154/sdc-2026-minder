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
        db.execute("CREATE TABLE IF NOT EXISTS library_documents("
                   "owner TEXT NOT NULL, id TEXT NOT NULL, version TEXT NOT NULL, "
                   "status TEXT NOT NULL CHECK(status IN ('uploading','active','deleting','deleted')), "
                   "body TEXT NOT NULL, byte_size INTEGER NOT NULL CHECK(byte_size>=0), "
                   "created_at TEXT NOT NULL, PRIMARY KEY(owner,id))")
        db.execute("CREATE INDEX IF NOT EXISTS library_owner_status ON library_documents(owner,status)")
        db.execute("CREATE TABLE IF NOT EXISTS library_requests("
                   "owner TEXT NOT NULL, key TEXT NOT NULL, operation TEXT NOT NULL, "
                   "scope_hash TEXT NOT NULL, document_id TEXT NOT NULL, PRIMARY KEY(owner,key))")
        db.execute("CREATE TABLE IF NOT EXISTS library_drafts("
                   "owner TEXT NOT NULL, document_id TEXT NOT NULL, draft_id TEXT NOT NULL, "
                   "PRIMARY KEY(owner,document_id), UNIQUE(owner,draft_id))")
        db.execute("INSERT OR IGNORE INTO migrations VALUES(6)")
