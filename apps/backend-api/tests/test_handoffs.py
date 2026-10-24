"""Real canonical state/transaction/replay, declared model; no real provider."""
import copy
from support import AppCase
from test_generation import AdviceProvider, advice
from minder_app.api import Application
from minder_app.store import AppError, Store


class HandoffTests(AppCase):
    def setUp(self):
        super().setUp()
        self.plan = self.make_plan()['plan']
        # Scheduling requires an explicit effort estimate; do not bypass the
        # existing feasibility guard with the incomplete historical fixture.
        self.app.dispatch('POST','/api/product/task-action',dict(plan_id=self.plan['plan_id'],
            task_id='synthetic-task',operation='edit',changes={'estimated_hours':1},
            expected_state_version=self.plan['state_version'],idempotency_key='estimate'),self.token)
        self.plan = self.store.get(self.profile['profile_id'],'plan',self.plan['plan_id'])
        self.profile = self.app.dispatch('PUT','/api/profile',dict(profile={'onboarding':{'weekly_study_hours':6}},
            expected_version=self.profile['version']),self.token)
        self.app.services.roles = [dict(role_id='synthetic-role',label='Fictional developer',eligibility='supported')]
        self.conversation = self.app.dispatch('POST','/api/product/conversations',
            dict(title='Planning discussion',idempotency_key='discussion'),self.token)['conversation']

    def send(self, key='reschedule-1', message=None, operation=None):
        message = message or 'Please reschedule synthetic-task to 2026-12-01T15:00:00+08:00.'
        operation = operation or dict(kind='reschedule_task',task_id='synthetic-task',
            scheduled_at=None,instruction_quote=message)
        self.app.provider = AdviceProvider(advice(operation=operation))
        return self.app.dispatch('POST','/api/product/conversation-turn',dict(
            conversation_id=self.conversation['conversation_id'],message=message,
            expected_profile_version=self.profile['version'],idempotency_key=key),self.token)

    def events(self):
        return self.app.dispatch('GET','/api/product/minder-handoffs',{},self.token)['events']

    def decision(self, event, choice, key):
        return self.app.dispatch('POST','/api/product/handoff-decision',dict(event_id=event['event_id'],
            expected_version=event['version'],decision=choice,idempotency_key=key),self.token)

    def test_origin_link_singleton_one_proposal_exact_turn_replay_and_reject_changes_nothing(self):
        result = self.send()
        event = self.events()[0]
        self.assertEqual(event['status'],'pending')
        self.assertEqual(event['source_message_id'],result['messages'][0]['message_id'])
        self.assertEqual(event['source_conversation_id'],self.conversation['conversation_id'])
        self.assertEqual(result['response']['diagnostics']['handoff']['event_id'],event['event_id'])
        self.assertEqual(self.store.get(self.profile['profile_id'],'plan',self.plan['plan_id']),self.plan)
        replay = self.send()
        self.assertEqual(replay['response'],result['response'])
        self.assertEqual(len(self.events()),1)
        self.assertEqual(len(self.app.actions.proposals(self.profile['profile_id'])),1)
        bot = self.app.dispatch('GET','/api/product/mindbot-conversation',{},self.token)
        self.assertEqual(bot['conversation']['conversation_id'],event['mindbot_conversation_id'])
        self.assertEqual(len(bot['messages']),1)
        rejected = self.decision(event,'reject','reject-once')
        self.assertFalse(rejected['target_changed'])
        self.assertEqual(self.decision(event,'reject','reject-once'),rejected)
        self.assertEqual(self.store.get(self.profile['profile_id'],'plan',self.plan['plan_id']),self.plan)
        self.assertEqual(self.app.actions.history(self.profile['profile_id']),[])

    def test_approval_applies_once_and_restart_retains_event_history_and_saved_result(self):
        self.send()
        event = self.events()[0]
        applied = self.decision(event,'approve','approve-once')
        self.assertTrue(applied['target_changed'])
        self.assertEqual(applied['result']['action']['execution_status'],'applied')
        self.assertEqual(self.decision(event,'approve','approve-once'),applied)
        saved = self.store.get(self.profile['profile_id'],'plan',self.plan['plan_id'])
        self.assertEqual(saved['tasks'][0]['scheduled_at'],'2026-12-01T15:00:00+08:00')
        self.assertEqual(len(self.app.actions.history(self.profile['profile_id'])),1)
        restarted = Application(Store(self.store.path),self.app.services,self.app.provider)
        events = restarted.dispatch('GET','/api/product/minder-handoffs',{},self.token)['events']
        self.assertEqual(events[0]['status'],'approved')
        self.assertEqual(restarted.dispatch('GET','/api/product/mindbot-conversation',{},self.token)['messages'][0]['message_id'],event['mindbot_message_id'])

    def test_stale_approval_and_other_owner_cannot_widen_or_duplicate_action(self):
        self.send()
        event = self.events()[0]
        other = self.store.session()['token']
        with self.assertRaises(AppError):
            self.app.dispatch('POST','/api/product/handoff-decision',dict(event_id=event['event_id'],decision='approve',
                expected_version=event['version'],idempotency_key='foreign'),other)
        self.app.dispatch('POST','/api/product/task-action',dict(plan_id=self.plan['plan_id'],task_id='synthetic-task',
            operation='edit',changes={'title':'Explicit concurrent edit'},expected_state_version=self.plan['state_version'],
            idempotency_key='concurrent-edit'),self.token)
        before = self.store.get(self.profile['profile_id'],'plan',self.plan['plan_id'])
        with self.assertRaises(AppError):
            self.decision(event,'approve','stale-approve')
        self.assertEqual(self.store.get(self.profile['profile_id'],'plan',self.plan['plan_id']),before)
        self.assertEqual(self.events()[0]['status'],'stale')

    def test_questions_do_not_create_handoff_or_unsolicited_state_changes(self):
        self.send(message='Should I reschedule synthetic-task?')
        self.assertEqual(self.events(),[])
        self.assertEqual(self.app.actions.proposals(self.profile['profile_id']),[])
        self.assertEqual(self.store.get(self.profile['profile_id'],'plan',self.plan['plan_id']),self.plan)

    def test_existing_proposal_panel_decision_is_visible_in_handoff_projection(self):
        self.send()
        event = self.events()[0]
        proposal = event['preview']
        self.app.actions.decide(self.profile['profile_id'],proposal['preview']['proposal_id'],'reject',
            proposal['preview_hash'],proposal['preview']['request']['expected_state_version'])
        self.assertEqual(self.events()[0]['status'],'rejected')
        self.assertEqual(self.store.get(self.profile['profile_id'],'plan',self.plan['plan_id']),self.plan)

    def test_concurrent_same_approval_saves_one_action_and_scope_reuse_conflicts(self):
        from concurrent.futures import ThreadPoolExecutor
        self.send()
        event = self.events()[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _:self.decision(event,'approve','concurrent'),range(2)))
        self.assertEqual(results[0],results[1])
        self.assertEqual(len(self.app.actions.history(self.profile['profile_id'])),1)
        with self.assertRaises(AppError):
            self.decision(event,'reject','concurrent')

    def test_roadmap_is_approval_only_and_accepts_once_without_activating(self):
        self.app.dispatch('PUT','/api/product/direction',dict(role_id='synthetic-role',plan_id=self.plan['plan_id'],
            expected_version=None,idempotency_key='direction'),self.token)
        result = self.send(message='Please create a practical learning roadmap.',operation=dict(
            kind='none',task_id=None,scheduled_at=None,instruction_quote=None))
        event = self.events()[0]
        self.assertEqual(event['kind'],'roadmap')
        self.assertEqual(len(self.store.list(self.profile['profile_id'],'plan')),1)
        accepted = self.decision(event,'approve','accept-roadmap')
        self.assertFalse(accepted['result']['activated'])
        self.assertEqual(self.decision(event,'approve','accept-roadmap'),accepted)
        self.assertEqual(len(self.store.list(self.profile['profile_id'],'plan')),2)
        self.assertEqual(self.app.dispatch('GET','/api/product/direction',{},self.token)['direction']['plan_id'],self.plan['plan_id'])
