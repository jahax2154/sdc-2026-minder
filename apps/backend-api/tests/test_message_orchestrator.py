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
        from minder_app.automation_state import save_automation_settings as schedule
        at=datetime(2026,10,27,0,1,tzinfo=timezone.utc)
        settings=schedule(self.store,owner,dict(enabled=True,check_time='08:00'),None,at=at-timedelta(minutes=2))
        worker=Worker(self.store,self.app.actions)
        worker.daily(at,owner=owner)
        paused=schedule(self.store,owner,dict(enabled=False,check_time='08:00'),settings['version'],at=at)
        self.assertEqual(worker.tick(at,owner=owner)['status'],'idle')
        schedule(self.store,owner,dict(enabled=True,check_time='08:00'),paused['version'],at=at)
        self.assertEqual(worker.tick(at,owner=owner)['status'],'processed')
        history=Conversations(self.store).mindbot(owner)
        self.assertEqual(len(history['messages']),1)
        restarted=Worker(self.store,self.app.actions)
        self.assertEqual(restarted.tick(at,owner=owner)['status'],'idle')
        self.assertEqual(len(Conversations(self.store).mindbot(owner)['messages']),1)

    def test_materializer_is_stable_draft_and_preserves_unknown_competence(self):
        from test_generation import advice
        from minder_app.message_orchestrator import materialize
        from minder_app.generation_schemas import POLICY_ID
        from minder_ml.intelligence.app_context import CareerServices
        profile=self.save();owner=profile['profile_id']
        self.app.services=CareerServices(roles=[dict(role_id='test-supported',eligibility='eligible')])
        generation=dict(policy_version=POLICY_ID,draft_id='synthetic-generation',status='unsaved_draft',
            profile_version=profile['version'],advice=advice())
        first=materialize(self.app,owner,generation,'test-supported')
        second=materialize(self.app,owner,generation,'test-supported')
        self.assertEqual(first,second)
        self.assertTrue(all(t['state']=='proposed' and not t['mastery_verified'] and not t['activity_completion']
                            and not t['evidence_ids'] and t['scheduled_at'] is None for t in first['tasks']))
        self.assertFalse(self.store.list(owner,'plan'))

    def test_typed_create_edit_and_reset_use_canonical_state(self):
        from test_generation import advice
        from minder_app.message_orchestrator import turn
        from minder_ml.intelligence.app_context import CareerServices
        plan,_=self.setup_request();owner=self.profile['profile_id']
        self.app.services=CareerServices(roles=[dict(role_id=plan['selected_role_id'],label='Synthetic supported role',eligibility='eligible')])
        message='Please create a task to inspect bus-delay prediction errors'
        operation=dict(kind='create_task',task_id=None,scheduled_at=None,instruction_quote=message,
            plan_id=plan['plan_id'],payload=dict(title='Inspect bus-delay errors',description='Inspect held-out errors.',estimated_hours=2))
        self.app.provider=AdviceProvider(advice(operation=operation))
        result=turn(self.app,owner,'mindbot',message,[],None,dict(expected_profile_version=self.profile['version'],idempotency_key='create'))
        self.assertEqual(result['action_status'],'applied')
        saved=self.store.get(owner,'plan',plan['plan_id']);task=saved['tasks'][-1]
        self.assertEqual(task['state'],'proposed');self.assertFalse(task['mastery_verified'])
        message='Please edit Inspect bus-delay errors title'
        operation=dict(kind='edit_task',task_id=task['task_id'],scheduled_at=None,instruction_quote=message,payload=dict(title='Inspect chronological errors'))
        self.app.provider=AdviceProvider(advice(operation=operation))
        result=turn(self.app,owner,'mindbot',message,[],None,dict(expected_profile_version=self.profile['version'],idempotency_key='edit'))
        self.assertEqual(result['action_status'],'applied')
        before_evidence=self.profile['evidence']
        for key,state in [('not-interested','not_interested'),('reset',None)]:
            message='Please '+('reset this role preference' if state is None else 'set this role to not interested')
            operation=dict(kind='update_preference',task_id=None,scheduled_at=None,instruction_quote=message,
                payload=dict(entity_type='role',entity_id=plan['selected_role_id'],preference_state=state))
            self.app.provider=AdviceProvider(advice(operation=operation))
            result=turn(self.app,owner,'mindbot',message,[],None,dict(expected_profile_version=self.profile['version'],idempotency_key=key))
            self.assertEqual(result['action_status'],'applied')
            self.profile=self.store.get(owner,'profile',owner)
        self.assertEqual(self.profile['evidence'],before_evidence)
        self.assertFalse(any(p['entity_id']==plan['selected_role_id'] for p in self.profile['preferences']))

    def test_goal_and_ambiguous_schedule_do_not_invent_capacity(self):
        from test_generation import advice
        from minder_app.message_orchestrator import turn,requested_time
        plan,_=self.setup_request();owner=self.profile['profile_id']
        message='Please change my goal to build reliable evaluation pipelines'
        operation=dict(kind='change_goal',task_id=None,scheduled_at=None,instruction_quote=message,
            payload=dict(goals='Build reliable evaluation pipelines'))
        self.app.provider=AdviceProvider(advice(operation=operation))
        result=turn(self.app,owner,'mindbot',message,[],None,dict(expected_profile_version=self.profile['version'],idempotency_key='goal'))
        self.assertEqual(result['action_status'],'applied')
        self.profile=self.store.get(owner,'profile',owner)
        self.assertEqual(self.profile['career_context']['goals'],'Build reliable evaluation pipelines')
        message='Please reschedule synthetic-task tomorrow'
        operation=dict(kind='reschedule_task',task_id='synthetic-task',scheduled_at=None,instruction_quote=message)
        self.app.provider=AdviceProvider(advice(operation=operation))
        result=turn(self.app,owner,'mindbot',message,[],None,dict(expected_profile_version=self.profile['version'],idempotency_key='unknown-time'))
        self.assertEqual(result['action_status'],'not_applied');self.assertEqual(result['status'],'clarify_exact_date_time')
        self.assertEqual(self.store.get(owner,'plan',plan['plan_id']),plan)
        self.assertEqual(requested_time('tomorrow at 6pm','Asia/Kuala_Lumpur').hour,18)
        self.assertIsNone(requested_time('tomorrow evening','Asia/Kuala_Lumpur'))

    def test_schedule_timezone_catchup_last_result_and_scope_are_canonical(self):
        from minder_app.automation_state import save_automation_settings
        from minder_app.profiles import save_profile
        owner=self.save()['profile_id']
        profile=self.store.get(owner,'profile',owner)
        save_profile(self.store,owner,{'timezone':'UTC'},profile['version'])
        save_automation_settings(self.store,owner,dict(check_time='09:00',timezone='Asia/Kuala_Lumpur',state='active'),
            None,at=datetime(2026,10,24,0,tzinfo=timezone.utc))
        worker=Worker(self.store,self.app.actions)
        at=datetime(2026,10,26,1,tzinfo=timezone.utc)
        self.assertEqual(worker.tick(at,owner=owner)['status'],'processed')
        settings=self.store.get(owner,'agent_settings',owner)
        self.assertEqual(settings['next_run'],'2026-10-27T01:00:00Z')
        self.assertEqual(settings['last_result']['status'],'processed')
        self.assertTrue(settings['last_result']['conversation_id'])
        self.assertEqual(worker.tick(at,owner=owner)['status'],'idle')
        self.assertEqual(len(Conversations(self.store).mindbot(owner)['messages']),1)

    def test_pending_provider_cannot_commit_after_cancellation(self):
        from minder_app.automation_state import save_automation_settings
        owner=self.save()['profile_id'];at=datetime(2026,10,26,1,tzinfo=timezone.utc)
        save_automation_settings(self.store,owner,dict(check_time='09:00',state='active'),None,
            at=at-timedelta(minutes=2))
        worker=Worker(self.store,self.app.actions)
        def cancel_during(event,instant):
            current=self.store.get(owner,'agent_settings',owner)
            save_automation_settings(self.store,owner,dict(state='cancelled'),current['version'],at=instant)
            return dict(summary='Never publish this cancelled result')
        worker.analyse=cancel_during
        self.assertEqual(worker.tick(at,owner=owner)['status'],'cancelled')
        self.assertFalse(Conversations(self.store).mindbot(owner)['messages'])
