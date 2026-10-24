from concurrent.futures import ThreadPoolExecutor
from threading import Event
from unittest.mock import Mock
import json
from support import AppCase
from minder_app.conversations import Conversations, dispatch
from minder_app.store import AppError, Store


class ConversationStoreTests(AppCase):
    def setUp(self):
        super().setUp()
        self.service = Conversations(self.store)
        self.owner = self.session["profile_id"]

    def create(self, key="first"):
        return self.service.create(self.owner, {"idempotency_key":key})["conversation"]

    def body(self, conversation, key="message", message="Fictional planning question"):
        return dict(conversation_id=conversation["conversation_id"], message=message,
                    idempotency_key=key, expected_profile_version=None)

    def test_minder_multiple_open_pagination_restart_delete_and_isolation(self):
        first, second = self.create(), self.create("second")
        self.assertNotEqual(first["conversation_id"], second["conversation_id"])
        handler = Mock(return_value={"answer":"Fictional server-visible reply", "statements":[]})
        body = self.body(first)
        result = self.service.continue_turn(self.owner, body, handler)
        self.assertEqual(result, self.service.continue_turn(self.owner, body, handler))
        self.assertEqual(handler.call_count, 1)
        restarted = Conversations(Store(self.store.path))
        page = restarted.open(self.owner, {"conversation_id":first["conversation_id"], "limit":1})
        self.assertTrue(page["has_more"])
        self.assertEqual(page["messages"][0]["role"], "user")
        page2 = restarted.open(self.owner, {"conversation_id":first["conversation_id"], "after_sequence":page["next_after_sequence"]})
        self.assertEqual(page2["messages"][0]["role"], "assistant")
        self.assertEqual(handler.call_count, 1) # Opening history never executes actions/provider.
        other = self.store.session()["profile_id"]
        self.assertEqual(restarted.list(other)["conversations"], [])
        with self.assertRaises(AppError):
            restarted.open(other, {"conversation_id":first["conversation_id"]})
        deletion = {"conversation_id":first["conversation_id"], "idempotency_key":"delete"}
        self.assertEqual(restarted.delete(self.owner,deletion), restarted.delete(self.owner,deletion))
        self.assertEqual(len(restarted.list(self.owner)["conversations"]),1)
        with self.assertRaises(AppError):
            restarted.open(self.owner,{"conversation_id":first["conversation_id"]})
        self.assertEqual(self.store.list(self.owner,"plan"), [])

    def test_mindbot_singleton_under_concurrent_creation_and_no_delete_or_branch(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            ids = list(pool.map(lambda _: self.service.mindbot(self.owner)["conversation"]["conversation_id"], range(24)))
        self.assertEqual(len(set(ids)),1)
        self.assertEqual(self.service.list(self.owner)["conversations"], [])
        with self.assertRaises(AppError) as error:
            self.service.delete(self.owner,{"conversation_id":ids[0], "idempotency_key":"delete"})
        self.assertEqual(error.exception.code,"mindbot_single_history_cannot_be_deleted")
        from jsonschema.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.service.create(self.owner,{"channel":"mindbot", "idempotency_key":"branch"})
        other = self.store.session()["profile_id"]
        self.assertNotEqual(self.service.mindbot(other)["conversation"]["conversation_id"], ids[0])

    def test_provider_call_holds_no_transaction_pending_retries_do_not_execute(self):
        conversation = self.create()
        entered, release = Event(), Event()
        def slow(owner, channel, message, history, request_id, body):
            entered.set()
            self.assertTrue(release.wait(3))
            return {"answer":"Finished server response", "statements":[]}
        body = self.body(conversation)
        with ThreadPoolExecutor(max_workers=2) as pool:
            future = pool.submit(self.service.continue_turn,self.owner,body,slow)
            self.assertTrue(entered.wait(2))
            # This real SQLite write would block/time out if the provider held a write transaction.
            self.store.put(self.owner,"test_marker","parallel",{"completed":True},None)
            pending = self.service.continue_turn(self.owner,body,lambda *args:self.fail("duplicate handler"))
            self.assertEqual(pending["turn"]["status"],"processing")
            with self.assertRaises(AppError):
                self.service.continue_turn(self.owner,self.body(conversation,key="another"),slow)
            release.set()
            completed = future.result(timeout=3)
        self.assertEqual(completed["turn"]["status"],"completed")
        self.assertEqual(len(self.service.open(self.owner,{"conversation_id":conversation["conversation_id"]})["messages"]),2)

    def test_server_owned_outcomes_context_bounded_stale_and_failure(self):
        conversation = self.create()
        handler = Mock(return_value={"answer":"Server answer", "statements":[]})
        first = self.body(conversation)
        self.service.continue_turn(self.owner,first,handler)
        second = self.body(conversation,"followup","Fictional follow-up")
        self.service.continue_turn(self.owner,second,handler)
        self.assertEqual([item["role"] for item in handler.call_args.args[3]], ["user","assistant"])
        with self.assertRaises(AppError) as error:
            self.service.continue_turn(self.owner,dict(first,message="changed scope"),handler)
        self.assertEqual(error.exception.code,"idempotency_scope_conflict")
        saved = self.save()
        with self.assertRaises(AppError) as error:
            self.service.continue_turn(self.owner,self.body(conversation,"stale"),handler)
        self.assertEqual(error.exception.status,409)
        failbody = dict(self.body(conversation,"failure"),expected_profile_version=saved["version"])
        failed = self.service.continue_turn(self.owner,failbody,Mock(side_effect=RuntimeError("private provider detail")))
        self.assertEqual(failed["turn"]["status"],"failed")
        self.assertNotIn("private provider detail",str(failed))
        self.assertEqual(failed,self.service.continue_turn(self.owner,failbody,Mock(side_effect=AssertionError("must not replay"))))
        hidden = dict(self.body(conversation,"hidden"),expected_profile_version=saved["version"])
        self.assertEqual(self.service.continue_turn(self.owner,hidden,lambda *args:{"answer":"Visible", "reasoning":"hidden"})["turn"]["status"],"failed")

    def test_scheduled_notice_appends_once_to_existing_mindbot(self):
        conversation = self.service.mindbot(self.owner)["conversation"]
        with self.store.transaction() as db:
            db.execute("INSERT INTO notices VALUES(?,?,?)",(self.owner,"daily:fictional",json.dumps({"summary":"Recorded fictional activity", "sources":[]})))
        with ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(lambda _: self.service.append_notice(self.owner,"daily:fictional"),range(8)))
        self.assertTrue(all(r["conversation_id"]==conversation["conversation_id"] for r in results))
        messages=self.service.mindbot(self.owner)["messages"]
        self.assertEqual(len(messages),1)
        self.assertEqual(messages[0]["response"]["diagnostics"]["event_id"],"daily:fictional")
        with self.assertRaises(AppError):
            self.service.append_notice(self.store.session()["profile_id"],"daily:fictional")
