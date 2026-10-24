"""Combined actual persistence/route/orchestrator checks with declared mock model."""
from datetime import datetime, timezone, timedelta
from support import AppCase
from test_generation import AdviceProvider
from minder_app.agents import Worker, configure
from minder_app.conversations import Conversations


class IntegratedTurnTests(AppCase):
    def test_singleton_real_callback_history_and_exact_replay(self):
        self.app.provider=AdviceProvider()
        singleton=self.app.dispatch('GET','/api/product/mindbot-conversation',{},self.token)
        cid=singleton['conversation']['conversation_id']
        body=dict(conversation_id=cid,message='Plan a practical roadmap',idempotency_key='turn1',expected_profile_version=None)
        result=self.app.dispatch('POST','/api/product/conversation-turn',body,self.token)
        self.assertEqual(result['turn']['status'],'completed')
        self.assertEqual(result['response']['response_mode'],'generated_guidance')
        replay=self.app.dispatch('POST','/api/product/conversation-turn',body,self.token)
        self.assertEqual(replay['response'],result['response'])
        second=dict(body,message='My bus-delay notebook needs a better evaluation milestone',idempotency_key='turn2')
        self.app.dispatch('POST','/api/product/conversation-turn',second,self.token)
        import json
        sent=json.loads(self.app.provider.messages[-1]['content'])
        self.assertEqual(len(sent['recent_visible_messages']),2)
        loaded=self.app.dispatch('POST','/api/product/conversation',dict(conversation_id=cid),self.token)
        self.assertEqual(len(loaded['messages']),4)
        self.assertEqual(self.app.dispatch('GET','/api/product/mindbot-conversation',{},self.token)['conversation']['conversation_id'],cid)

    def test_direct_result_persists_server_action_id_without_reexecution(self):
        from test_generation import advice
        plan,_=self.setup_request()
        self.app.provider=AdviceProvider(advice(operation=dict(kind='complete_task',task_id='synthetic-task',
            scheduled_at=None,instruction_quote='Please mark synthetic-task done')))
        singleton=self.app.dispatch('GET','/api/product/mindbot-conversation',{},self.token)
        body=dict(conversation_id=singleton['conversation']['conversation_id'],message='Please mark synthetic-task done',
                  expected_profile_version=self.profile['version'],idempotency_key='direct-turn')
        first=self.app.dispatch('POST','/api/product/conversation-turn',body,self.token)
        self.assertEqual(first['turn']['status'],'completed')
        self.assertEqual(first['response']['action_status'],'applied')
        self.assertEqual(len(first['response']['action_ids']),1)
        again=self.app.dispatch('POST','/api/product/conversation-turn',body,self.token)
        self.assertEqual(again['response'],first['response'])
        self.assertEqual(len(self.app.actions.history(self.profile['profile_id'])),1)

    def test_due_result_in_singleton_pause_resume_and_restart_dedupe(self):
        owner=self.save()['profile_id']
        settings=configure(self.store,owner,dict(enabled=True,check_time='08:00'),None)
        at=datetime(2026,10,27,0,1,tzinfo=timezone.utc)
        worker=Worker(self.store,self.app.actions)
        worker.daily(at,owner=owner)
        paused=configure(self.store,owner,dict(enabled=False,check_time='08:00'),settings['version'])
        self.assertEqual(worker.tick(at,owner=owner)['status'],'idle')
        configure(self.store,owner,dict(enabled=True,check_time='08:00'),paused['version'])
        self.assertEqual(worker.tick(at,owner=owner)['status'],'processed')
        history=Conversations(self.store).mindbot(owner)
        self.assertEqual(len(history['messages']),1)
        restarted=Worker(self.store,self.app.actions)
        self.assertEqual(restarted.tick(at,owner=owner)['status'],'idle')
        self.assertEqual(len(Conversations(self.store).mindbot(owner)['messages']),1)
