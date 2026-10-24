"""Owner-scoped visible histories; model/actions belong to A, outside transactions."""
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
from .store import AppError, now, uid
from .product_migrations import migrate
from .conversation_schemas import check, visible_response, validate_search_result

CONTRACT_VERSION = "persistent-conversations-v1"
OPERATIONS = (("GET", "/api/product/conversations"), ("POST", "/api/product/conversations"),
    ("GET", "/api/product/conversation"), ("POST", "/api/product/conversation"),
    ("DELETE", "/api/product/conversation"), ("GET", "/api/product/mindbot-conversation"),
    ("POST", "/api/product/conversation-turn"), ("POST", "/api/product/conversations-search"))


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


class Conversations:
    def __init__(self, store, *, initialize=True):
        self.store = store
        if initialize:
            migrate(store)

    @staticmethod
    def metadata(row):
        return dict(conversation_id=row["id"], channel=row["channel"], title=row["title"],
            version=row["version"], created_at=row["created_at"], updated_at=row["updated_at"],
            status=row["status"], last_sequence=row["next_sequence"]-1)

    def owned(self, db, owner, conversation_id):
        row = db.execute("SELECT * FROM conversations WHERE owner=? AND id=? AND status='active'",
                         (owner, conversation_id)).fetchone()
        if row is None:
            raise AppError("conversation_not_found", 404)
        return row

    @staticmethod
    def message(row):
        body = json.loads(row["body"])
        value = dict(message_id=row["id"], sequence=row["sequence"], role=row["role"],
            content=body["answer"] if row["role"] == "assistant" else body["text"],
            created_at=row["created_at"], request_id=row["request_id"], status=row["status"])
        if row["role"] == "assistant":
            value["response"] = body
        return value

    def _new(self, db, owner, channel, title):
        identifier, stamp = uid(), now()
        db.execute("INSERT INTO conversations VALUES(?,?,?,?,?,?,?,?, 'active')",
                   (owner, identifier, channel, title, uid(), stamp, stamp, 1))
        return self.owned(db, owner, identifier)

    def _mindbot(self, db, owner):
        row = db.execute("SELECT * FROM conversations WHERE owner=? AND channel='mindbot'", (owner,)).fetchone()
        return row if row else self._new(db, owner, "mindbot", "Mindbot")

    def mindbot(self, owner):
        with self.store.transaction() as db:
            row = self._mindbot(db, owner)
            identifier = row["id"]
        return self.open(owner, {"conversation_id": identifier})

    def create(self, owner, body):
        check("create", body)
        with self.store.transaction() as db:
            previous = db.execute("SELECT * FROM conversation_requests WHERE owner=? AND key=?",
                                  (owner, body["idempotency_key"])).fetchone()
            if previous:
                if previous["operation"] != "create" or previous["scope_hash"] != digest(body):
                    raise AppError("idempotency_scope_conflict", 409)
                row = self.owned(db, owner, previous["conversation_id"])
            else:
                row = self._new(db, owner, "minder", body.get("title", "").strip() or "New conversation")
                db.execute("INSERT INTO conversation_requests VALUES(?,?,?,?,?)", (owner, body["idempotency_key"],
                    "create", digest(body), row["id"]))
            return dict(conversation=self.metadata(row))

    def list(self, owner):
        with self.store.connect() as db:
            rows = db.execute("SELECT * FROM conversations WHERE owner=? AND channel='minder' AND status='active' "
                              "ORDER BY updated_at DESC,id", (owner,)).fetchall()
            return dict(contract_version=CONTRACT_VERSION, conversations=[self.metadata(row) for row in rows])

    def search(self, owner, body):
        """Literal Unicode casefold substring in titles/visible text, never tools."""
        check("search", body)
        query = body["query"].strip()
        limit, offset = body.get("limit", 20), body.get("offset", 0)
        term = query.casefold()
        if getattr(self.store, "engine", "sqlite") == "postgresql":
            # PostgreSQL lower() is not Python Unicode casefold (e.g. Straße).
            # Read only owner-scoped visible text in one snapshot; never tools,
            # private source records or hidden provider output.
            with self.store.connect() as db:
                db.execute("BEGIN")
                rows = db.execute("SELECT * FROM conversations WHERE owner=? AND channel='minder' "
                    "AND status='active' ORDER BY updated_at DESC,id", (owner,)).fetchall()
                matches = {row["id"] for row in rows if term in row["title"].casefold()}
                if term:
                    visible = db.execute("SELECT m.conversation_id,m.role,m.body::jsonb->>'text' AS text, "
                        "m.body::jsonb->>'answer' AS answer,m.body::jsonb->'statements' AS statements "
                        "FROM conversation_messages m JOIN conversations c ON c.owner=m.owner AND c.id=m.conversation_id "
                        "WHERE c.owner=? AND c.channel='minder' AND c.status='active'", (owner,))
                    for message in visible:
                        texts = [message["text"] if message["role"] == "user" else message["answer"]]
                        if message["role"] == "assistant" and isinstance(message["statements"], list):
                            texts.extend(item.get("text") for item in message["statements"] if isinstance(item, dict))
                        if any(term in text.casefold() for text in texts if isinstance(text, str)):
                            matches.add(message["conversation_id"])
                selected = [row for row in rows if row["id"] in matches]
                page = selected[offset:offset+limit]
                more = offset+len(page) < len(selected)
                return validate_search_result(dict(contract_version="conversation-search-v1",
                    search_scope="title_and_visible_messages", conversations=[self.metadata(row) for row in page],
                    query=query, offset=offset, limit=limit, has_more=more,
                    next_offset=offset+len(page) if more else None))
        clause = """FROM conversations c WHERE c.owner=? AND c.channel='minder' AND c.status='active'
            AND (?='' OR instr(minder_casefold(c.title),?)>0 OR EXISTS(
                SELECT 1 FROM conversation_messages m WHERE m.owner=c.owner AND m.conversation_id=c.id
                AND instr(minder_casefold(CASE WHEN m.role='user' THEN json_extract(m.body,'$.text')
                          ELSE json_extract(m.body,'$.answer') END),?)>0
                OR (m.owner=c.owner AND m.conversation_id=c.id AND EXISTS(
                    SELECT 1 FROM json_each(m.body,'$.statements') s
                    WHERE instr(minder_casefold(CASE WHEN s.type='object'
                        THEN json_extract(s.value,'$.text') ELSE '' END),?)>0))))"""
        params = (owner, term, term, term, term)
        with self.store.connect() as db:
            db.create_function("minder_casefold", 1, lambda text: text.casefold() if isinstance(text,str) else "",
                               deterministic=True)
            db.execute("BEGIN")
            total = db.execute("SELECT count(*) " + clause, params).fetchone()[0]
            rows = db.execute("SELECT c.* " + clause + " ORDER BY c.updated_at DESC,c.id LIMIT ? OFFSET ?",
                              params + (limit, offset)).fetchall()
            more = offset+len(rows)<total
            return validate_search_result(dict(contract_version="conversation-search-v1", search_scope="title_and_visible_messages",
                        conversations=[self.metadata(row) for row in rows], query=query, offset=offset, limit=limit,
                        has_more=more, next_offset=offset+len(rows) if more else None))

    def open(self, owner, body):
        check("open", body)
        limit, after = body.get("limit", 100), body.get("after_sequence", 0)
        with self.store.connect() as db:
            db.execute("BEGIN")
            conversation = self.owned(db, owner, body["conversation_id"])
            rows = db.execute("SELECT * FROM conversation_messages WHERE owner=? AND conversation_id=? AND sequence>? "
                "ORDER BY sequence LIMIT ?", (owner, conversation["id"], after, limit+1)).fetchall()
            pending = [dict(request_id=row["request_id"], status=row["status"], created_at=row["created_at"], error_code=row["error_code"])
                for row in db.execute("SELECT * FROM conversation_turns WHERE owner=? AND conversation_id=? "
                    "AND status IN ('processing','uncertain') ORDER BY created_at", (owner, conversation["id"]))]
            messages = [self.message(row) for row in rows[:limit]]
            return dict(contract_version=CONTRACT_VERSION, conversation=self.metadata(conversation), messages=messages,
                pending_turns=pending, has_more=len(rows)>limit,
                next_after_sequence=messages[-1]["sequence"] if messages else after)

    def delete(self, owner, body):
        check("delete", body)
        with self.store.transaction() as db:
            receipt = db.execute("SELECT * FROM conversation_requests WHERE owner=? AND key=?",
                                 (owner, body["idempotency_key"])).fetchone()
            if receipt:
                if receipt["operation"] != "delete" or receipt["scope_hash"] != digest(body):
                    raise AppError("idempotency_scope_conflict", 409)
                return dict(conversation_id=receipt["conversation_id"], status="deleted")
            row = self.owned(db, owner, body["conversation_id"])
            if row["channel"] != "minder":
                raise AppError("mindbot_single_history_cannot_be_deleted", 409)
            if db.execute("SELECT 1 FROM conversation_turns WHERE owner=? AND conversation_id=? AND status='processing'",
                          (owner, row["id"])).fetchone():
                raise AppError("conversation_turn_in_progress", 409)
            db.execute("DELETE FROM conversation_messages WHERE owner=? AND conversation_id=?", (owner, row["id"]))
            db.execute("DELETE FROM conversation_turns WHERE owner=? AND conversation_id=?", (owner, row["id"]))
            db.execute("UPDATE conversations SET status='deleted',title='',version=?,updated_at=? WHERE owner=? AND id=?",
                       (uid(), now(), owner, row["id"]))
            db.execute("INSERT INTO conversation_requests VALUES(?,?,?,?,?)", (owner, body["idempotency_key"], "delete", digest(body), row["id"]))
            return dict(conversation_id=row["id"], status="deleted")

    def _append(self, db, owner, conversation_id, role, body, request_id, status):
        row = self.owned(db, owner, conversation_id)
        identifier, stamp = uid(), now()
        db.execute("INSERT INTO conversation_messages VALUES(?,?,?,?,?,?,?,?,?)", (owner, conversation_id,
            identifier, row["next_sequence"], role, encode(body), stamp, request_id, status))
        db.execute("UPDATE conversations SET next_sequence=next_sequence+1,version=?,updated_at=? WHERE owner=? AND id=?",
                   (uid(), stamp, owner, conversation_id))
        return identifier

    def _turn_result(self, db, owner, row):
        messages = []
        response = None
        for identifier in (row["user_message_id"], row["assistant_message_id"]):
            if identifier:
                saved = db.execute("SELECT * FROM conversation_messages WHERE owner=? AND id=?", (owner, identifier)).fetchone()
                messages.append(self.message(saved))
                if saved["role"] == "assistant":
                    response = json.loads(saved["body"])
        return dict(conversation=self.metadata(self.owned(db, owner, row["conversation_id"])),
            turn=dict(request_id=row["request_id"], status=row["status"], error_code=row["error_code"]),
            messages=messages, response=response)

    def begin_turn(self, owner, body):
        check("turn", body)
        if not body["message"].strip():
            raise AppError("chat_message_required_or_too_large")
        with self.store.transaction() as db:
            conversation = self.owned(db, owner, body["conversation_id"])
            cutoff = (datetime.now(timezone.utc)-timedelta(seconds=120)).isoformat().replace("+00:00", "Z")
            db.execute("UPDATE conversation_turns SET status='uncertain',error_code='turn_outcome_unknown' "
                       "WHERE owner=? AND conversation_id=? AND status='processing' AND created_at<?",
                       (owner, conversation["id"], cutoff))
            row = db.execute("SELECT * FROM conversation_turns WHERE owner=? AND conversation_id=? AND key=?",
                             (owner, conversation["id"], body["idempotency_key"])).fetchone()
            if row:
                if row["scope_hash"] != digest(body):
                    raise AppError("idempotency_scope_conflict", 409)
                return dict(execute=False, result=self._turn_result(db, owner, row))
            if db.execute("SELECT 1 FROM conversation_turns WHERE owner=? AND conversation_id=? AND status='processing'",
                          (owner, conversation["id"])).fetchone():
                raise AppError("conversation_turn_in_progress", 409)
            profile = db.execute("SELECT version FROM documents WHERE owner=? AND kind='profile' AND id=?", (owner, owner)).fetchone()
            if (profile[0] if profile else None) != body["expected_profile_version"]:
                raise AppError("stale_state_version", 409)
            history = []
            remaining = 12000
            rows = db.execute("SELECT * FROM conversation_messages WHERE owner=? AND conversation_id=? "
                              "ORDER BY sequence DESC LIMIT 12", (owner, conversation["id"])).fetchall()
            for previous in rows:
                item = self.message(previous)
                text = item["content"][-min(4000,remaining):]
                history.append(dict(role=item["role"], content=text, message_id=item["message_id"],
                    action_ids=item.get("response", {}).get("action_ids", []),
                    proposal_ids=item.get("response", {}).get("proposal_ids", [])))
                remaining -= len(text)
                if remaining <= 0:
                    break
            request_id, stamp = uid(), now()
            user_message_id = self._append(db, owner, conversation["id"], "user", {"text":body["message"]}, request_id, "accepted")
            db.execute("INSERT INTO conversation_turns VALUES(?,?,?,?,?,'processing',?,NULL,?,NULL,NULL)",
                       (owner, conversation["id"], body["idempotency_key"], request_id, digest(body), user_message_id, stamp))
            return dict(execute=True, request_id=request_id, channel=conversation["channel"], history=list(reversed(history)))

    def finish_turn(self, owner, request_id, response, *, error_code=None):
        response = visible_response(response)
        with self.store.transaction() as db:
            row = db.execute("SELECT * FROM conversation_turns WHERE owner=? AND request_id=?", (owner, request_id)).fetchone()
            if row is None:
                raise AppError("conversation_turn_not_found", 404)
            if row["status"] in ("completed", "failed"):
                return self._turn_result(db, owner, row)
            self.owned(db, owner, row["conversation_id"])
            for field, table in (("action_ids", "action_audit"), ("proposal_ids", "proposals")):
                if any(not db.execute("SELECT 1 FROM " + table + " WHERE owner=? AND id=?", (owner, identifier)).fetchone()
                       for identifier in response.get(field, [])):
                    raise AppError("conversation_reference_not_owned", 500)
            for identifier in response.get("plan_ids", []):
                self.store.get(owner, "plan", identifier, db=db)
            status = "failed" if error_code else "completed"
            assistant_id = self._append(db, owner, row["conversation_id"], "assistant", response, request_id, status)
            db.execute("UPDATE conversation_turns SET status=?,assistant_message_id=?,finished_at=?,error_code=? "
                       "WHERE owner=? AND request_id=?", (status, assistant_id, now(), error_code, owner, request_id))
            row = db.execute("SELECT * FROM conversation_turns WHERE owner=? AND request_id=?", (owner, request_id)).fetchone()
            return self._turn_result(db, owner, row)

    def continue_turn(self, owner, body, handler):
        accepted = self.begin_turn(owner, body)
        if not accepted["execute"]:
            return accepted["result"]
        request_id = accepted["request_id"]
        try:
            if not callable(handler):
                raise AppError("conversation_handler_unavailable", 500)
            # There is deliberately no open connection/transaction across this call.
            response = handler(owner, accepted["channel"], body["message"], accepted["history"], request_id, body)
            return self.finish_turn(owner, request_id, response)
        except Exception as error:
            code = error.code if isinstance(error, AppError) and re.fullmatch(r"[a-z0-9_]{1,80}", error.code) else "conversation_reply_failed"
            return self.finish_turn(owner, request_id,
                dict(answer="The reply could not be completed. Check saved activity before starting a new request.",
                     action_status="outcome_unconfirmed", provider={"status":"unavailable","code":code}), error_code=code)

    def append_notice(self, owner, event_id, *, db=None):
        if db is None:
            with self.store.transaction() as conn:
                return self.append_notice(owner, event_id, db=conn)
        existing = db.execute("SELECT * FROM conversation_notice_links WHERE owner=? AND event_id=?", (owner,event_id)).fetchone()
        if existing:
            return dict(conversation_id=existing["conversation_id"], message_id=existing["message_id"], status="already_appended")
        row = db.execute("SELECT body FROM notices WHERE owner=? AND id=?", (owner,event_id)).fetchone()
        if row is None:
            raise AppError("scheduled_notice_not_found", 404)
        notice = json.loads(row["body"])
        response = dict(answer=notice.get("summary") or "The scheduled check finished. Review its saved activity.",
            statements=notice.get("statements", []), sources=notice.get("sources", []),
            action_status="proposal_only_no_automatic_changes", diagnostics=dict(event_id=event_id))
        if notice.get("proposal"):
            response["proposal_ids"] = [notice["proposal"]["preview"]["proposal_id"]]
        response = visible_response(response)
        conversation = self._mindbot(db, owner)
        message_id = self._append(db, owner, conversation["id"], "assistant", response, "scheduled:"+event_id, "completed")
        db.execute("INSERT INTO conversation_notice_links VALUES(?,?,?,?)", (owner,event_id,conversation["id"],message_id))
        return dict(conversation_id=conversation["id"], message_id=message_id, status="appended")


def dispatch(app, owner, method, path, body):
    service = Conversations(app.store)
    if (method,path) not in OPERATIONS:
        raise AppError("product_capability_unavailable",404)
    if path.endswith("/mindbot-conversation"):
        check("empty",body)
        return service.mindbot(owner)
    if path.endswith("/conversations-search"):
        return service.search(owner, body)
    if path.endswith("/conversations"):
        if method == "GET":
            check("empty",body)
            return service.list(owner)
        return service.create(owner,body)
    if path.endswith("/conversation-turn"):
        return service.continue_turn(owner,body,getattr(app,"conversation_turn_handler",None))
    return service.delete(owner,body) if method == "DELETE" else service.open(owner,body)



def append_notice(store, owner, event_id, *, db=None):
    """A's inline worker hook; never nests a migration in its write transaction."""
    return Conversations(store, initialize=db is None).append_notice(owner, event_id, db=db)


def reconcile_notices(store, limit=50):
    """E's restart hook: append saved missing notices, never re-execute their jobs."""
    if type(limit) is not int or not 1 <= limit <= 100:
        raise AppError("invalid_notice_reconcile_limit")
    service = Conversations(store)
    with store.connect() as db:
        pending = list(db.execute("SELECT n.owner,n.id FROM notices n LEFT JOIN conversation_notice_links l "
            "ON l.owner=n.owner AND l.event_id=n.id WHERE l.event_id IS NULL ORDER BY n.owner,n.id LIMIT ?", (limit,)))
    appended = 0
    for row in pending:
        appended += service.append_notice(row["owner"], row["id"])["status"] == "appended"
    return dict(checked=len(pending), appended=appended)
