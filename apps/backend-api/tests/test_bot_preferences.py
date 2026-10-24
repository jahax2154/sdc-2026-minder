from concurrent.futures import ThreadPoolExecutor
from jsonschema.exceptions import ValidationError
from support import AppCase
from minder_app.api import Application
from minder_app.store import AppError,Store
from minder_app.conversations import Conversations
from minder_app.automation_state import save_automation_settings
from minder_app.bot_preferences import defaults
from minder_app.product_state_schemas import schemas


class BotPreferenceTests(AppCase):
    def read(self,token=None):
        return self.app.dispatch("GET","/api/product/bot-preferences",{},token or self.token)

    def save_bot(self,body,token=None):
        return self.app.dispatch("PUT","/api/product/bot-preferences",body,token or self.token)

    def test_defaults_are_read_only_and_owner_cache_cannot_be_mutated(self):
        result=self.read()
        self.assertEqual(result,dict(contract_version="bot-preferences-v1",configured=False,
            preferences=dict(display_name="My Bot",avatar_id="nimo-blue",version=None)))
        result["preferences"]["display_name"]="Changed caller copy"
        self.assertEqual(self.read()["preferences"]["display_name"],"My Bot")
        self.assertEqual(self.store.list(self.session["profile_id"],"bot_preferences"),[])
        self.assertEqual(self.store.list(self.session["profile_id"],"agent_settings"),[])
        with self.store.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM documents").fetchone()[0],0)

    def test_saved_identity_trim_isolation_restart_stale_and_noop(self):
        saved=self.save_bot(dict(display_name="  Study Buddy  ",avatar_id="frog-rose",expected_version=None))
        self.assertTrue(saved["configured"])
        self.assertEqual(saved["preferences"]["display_name"],"Study Buddy")
        version=saved["preferences"]["version"]
        self.assertEqual(self.save_bot(dict(display_name="Study Buddy",avatar_id="frog-rose",expected_version=version)),saved)
        with self.assertRaises(AppError) as error:
            self.save_bot(dict(display_name="Stale intent",avatar_id="nimo-blue",expected_version=None))
        self.assertEqual(error.exception.status,409)
        other=self.store.session()["token"]
        self.assertFalse(self.read(other)["configured"])
        self.save_bot(dict(display_name="Other user's bot",avatar_id="star-blue",expected_version=None),other)
        self.app=Application(Store(self.store.path))
        self.assertEqual(self.read(),saved)
        with self.assertRaises(AppError) as error:
            self.read("invalid-token")
        self.assertEqual(error.exception.status,401)

    def test_all_approved_avatars_and_normalized_unicode_name_bound(self):
        version=None
        self.assertEqual(len(schemas()["BotAvatarId"]["enum"]),25)
        for avatar in schemas()["BotAvatarId"]["enum"]:
            result=self.save_bot(dict(display_name=" "+"猫"*40+" ",avatar_id=avatar,expected_version=version))
            self.assertEqual(result["preferences"]["avatar_id"],avatar)
            self.assertEqual(len(result["preferences"]["display_name"]),40)
            version=result["preferences"]["version"]
        invalid=[dict(display_name=name,avatar_id="nimo-blue",expected_version=version)
                 for name in ("", "   ","x"*41,"bad\x00name","bad\x85name",None,2)]
        invalid += [dict(display_name="Bot",avatar_id=avatar,expected_version=version)
                    for avatar in ("unknown","https://example.invalid/avatar.png","../nimo-blue",None)]
        invalid.append(dict(display_name="Bot",avatar_id="nimo-blue",expected_version=version,owner="foreign"))
        for body in invalid:
            with self.subTest(body_type=type(body["display_name"]).__name__):
                with self.assertRaises(ValidationError):
                    self.save_bot(body)

    def test_customization_preserves_profile_singleton_plan_and_schedule(self):
        plan=self.make_plan()["plan"]
        owner=self.session["profile_id"]
        conversations=Conversations(self.store)
        bot=conversations.mindbot(owner)
        settings=save_automation_settings(self.store,owner,{"enabled":False,"check_time":"09:00"},None)
        self.save_bot(dict(display_name="Review Coach",avatar_id="heart-lime",expected_version=None))
        self.assertEqual(self.store.get(owner,"profile",owner),self.profile)
        self.assertEqual(self.store.get(owner,"plan",plan["plan_id"]),plan)
        self.assertEqual(self.store.get(owner,"agent_settings",owner),settings)
        self.assertEqual(conversations.mindbot(owner),bot)

    def test_concurrent_same_revision_has_one_winner_and_capabilities_are_implemented(self):
        def write(index):
            try:
                return self.save_bot(dict(display_name="Bot "+str(index),avatar_id="nimo-blue",expected_version=None))
            except AppError as error:
                return error.status
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(write,range(8)))
        self.assertEqual(sum(isinstance(result,dict) for result in results),1)
        self.assertEqual(results.count(409),7)
        caps=self.app.dispatch("GET","/api/product/capabilities",{},self.token)
        found=[row for row in caps["operations"] if row["path"]=="/api/product/bot-preferences"]
        self.assertEqual(len(found),2)
        self.assertTrue(all(row["status"]=="implemented" and row["owner"]=="D" for row in found))
