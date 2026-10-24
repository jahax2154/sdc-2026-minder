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
        db.execute("CREATE TABLE IF NOT EXISTS app_users(id TEXT PRIMARY KEY, created_at TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS external_identities(issuer TEXT NOT NULL, subject TEXT NOT NULL, "
                   "owner TEXT NOT NULL REFERENCES app_users(id), PRIMARY KEY(issuer,subject))")
        db.execute("CREATE TABLE IF NOT EXISTS conversations(owner TEXT NOT NULL, id TEXT NOT NULL, "
                   "channel TEXT NOT NULL CHECK(channel IN ('minder','mindbot')), title TEXT NOT NULL, "
                   "version TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, "
                   "next_sequence INTEGER NOT NULL, status TEXT NOT NULL CHECK(status IN ('active','deleted')), "
                   "PRIMARY KEY(owner,id))")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS single_mindbot ON conversations(owner) WHERE channel='mindbot'")
        db.execute("CREATE TABLE IF NOT EXISTS conversation_requests(owner TEXT NOT NULL, key TEXT NOT NULL, "
                   "operation TEXT NOT NULL, scope_hash TEXT NOT NULL, conversation_id TEXT NOT NULL, "
                   "PRIMARY KEY(owner,key))")
        db.execute("CREATE TABLE IF NOT EXISTS conversation_messages(owner TEXT NOT NULL, conversation_id TEXT NOT NULL, "
                   "id TEXT NOT NULL, sequence INTEGER NOT NULL, role TEXT NOT NULL CHECK(role IN ('user','assistant')), "
                   "body TEXT NOT NULL, created_at TEXT NOT NULL, request_id TEXT NOT NULL, status TEXT NOT NULL, "
                   "PRIMARY KEY(owner,id), UNIQUE(owner,conversation_id,sequence), "
                   "FOREIGN KEY(owner,conversation_id) REFERENCES conversations(owner,id))")
        db.execute("CREATE TABLE IF NOT EXISTS conversation_turns(owner TEXT NOT NULL, conversation_id TEXT NOT NULL, "
                   "key TEXT NOT NULL, request_id TEXT NOT NULL, scope_hash TEXT NOT NULL, "
                   "status TEXT NOT NULL CHECK(status IN ('processing','completed','failed','uncertain')), "
                   "user_message_id TEXT NOT NULL, assistant_message_id TEXT, created_at TEXT NOT NULL, "
                   "finished_at TEXT, error_code TEXT, PRIMARY KEY(owner,conversation_id,key), "
                   "UNIQUE(owner,request_id), FOREIGN KEY(owner,conversation_id) REFERENCES conversations(owner,id))")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS conversation_inflight ON conversation_turns(owner,conversation_id) "
                   "WHERE status='processing'")
        db.execute("CREATE TABLE IF NOT EXISTS conversation_notice_links(owner TEXT NOT NULL, event_id TEXT NOT NULL, "
                   "conversation_id TEXT NOT NULL, message_id TEXT NOT NULL, PRIMARY KEY(owner,event_id))")
        db.execute("INSERT OR IGNORE INTO migrations VALUES(7)")
        if getattr(store, "engine", "sqlite") == "postgresql":
            # Native PostgreSQL layout: text JSON + durable internal event order.
            # Existing SQLite stays at v7; no anonymous data is imported.
            db.execute("INSERT OR IGNORE INTO migrations VALUES(8)")
