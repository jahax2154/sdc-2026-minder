"""Typed guidance software checks; provider is a declared mock, not live evidence."""
import copy
import json
from jsonschema import Draft202012Validator
from support import AppCase, ROOT
from minder_app.store import AppError
from minder_app.generation import validate_advice
from minder_app.message_orchestrator import turn


def advice(**updates):
    value = dict(kind='roadmap', answer='Try a small held-out evaluation before expanding your model.',
        assumptions=['This is a practice plan.'], questions=['What is your weekly study capacity?'],
        stages=[dict(title='Evaluate', outcome='Inspect generalization on unseen data.',
            tasks=[dict(title='Hold out a period', description='Compare a baseline and inspect errors.',estimated_hours=2)])],
        fact_ids=[], operation=dict(kind='none', task_id=None, scheduled_at=None, instruction_quote=None))
    value.update(updates)
    return value


class AdviceProvider:
    model = 'declared-software-provider'
    def __init__(self, value=None):
        self.value = value or advice()
    def complete_tool(self, messages, tool):
        self.messages, self.tool = messages, tool
        return dict(status='available', text=json.dumps(self.value), model=self.model,
                    request_id='software-only', tool_call={'arguments_validated': True})


class GenerationTests(AppCase):
    def test_incomplete_profile_generates_without_assessment_or_implicit_save(self):
        provider = self.app.provider = AdviceProvider()
        def forbidden(*args, **kwargs):
            raise AssertionError('guidance must not construct full assessment')
        self.app.services.career_context = forbidden
        response = self.app.dispatch('POST','/api/chat',dict(message='Plan a machine learning roadmap'),self.token)
        self.assertEqual(response['response_mode'],'generated_guidance')
        self.assertEqual(provider.tool['function']['name'],'propose_guidance')
        self.assertEqual(response['generation']['status'],'unsaved_draft')
        self.assertFalse(self.store.list(self.session['profile_id'],'profile'))
        self.assertFalse(self.store.list(self.session['profile_id'],'plan'))
        schema=json.loads((ROOT/'docs/execution/product/llm/frontend-envelope.schema.json').read_text())
        Draft202012Validator(schema).validate(response)

    def test_bounded_followup_owner_and_profile_scope(self):
        self.app.provider=AdviceProvider()
        first=self.app.dispatch('POST','/api/chat',dict(message='Help me prepare a roadmap'),self.token)
        self.app.dispatch('POST','/api/chat',dict(message='I can spare six hours, adapt that.',
            previous_context_id=first['conversation_context_id']),self.token)
        sent=json.loads(self.app.provider.messages[-1]['content'])
        self.assertIn('held-out',sent['recent_visible_messages'][0]['content'])
        self.assertNotIn(self.token,json.dumps(sent));self.assertNotIn(self.session['profile_id'],json.dumps(sent))
        other=self.store.session()['token']
        with self.assertRaises(AppError):
            self.app.dispatch('POST','/api/chat',dict(message='Continue',previous_context_id=first['conversation_context_id']),other)
        self.save()
        with self.assertRaises(AppError):
            self.app.dispatch('POST','/api/chat',dict(message='Continue'),self.token)

    def test_invalid_refs_scores_and_extra_properties_rejected(self):
        for bad in [advice(fact_ids=['invented']),advice(answer='Guaranteed 98% fit score'),
                    advice(scores=[99]),advice(answer='Read https://invented.example')]:
            self.app.provider=AdviceProvider(bad)
            result=self.app.dispatch('POST','/api/chat',dict(message='Make a learning roadmap'),self.token)
            self.assertIsNone(result['generation']);self.assertEqual(result['response_mode'],'limited_fallback')
            self.assertNotIn('98%',result['answer'])

    def test_provider_missing_has_no_fabricated_draft(self):
        from minder_ml.intelligence.groq_adapter import GroqAdapter
        self.app.provider=GroqAdapter(key='',model='qwen/qwen3.8-27b')
        result=self.app.dispatch('POST','/api/chat',dict(message='Make a roadmap'),self.token)
        self.assertIsNone(result['generation']);self.assertFalse(result['provider']['invoked'])
        self.assertFalse(self.store.list(self.session['profile_id'],'plan'))

    def test_real_typed_interpretation_direct_vs_inferred_scope(self):
        plan,_=self.setup_request();owner=self.session['profile_id']
        op=dict(kind='complete_task',task_id='synthetic-task',scheduled_at=None,
                instruction_quote='Please mark synthetic-task done')
        self.app.provider=AdviceProvider(advice(operation=op))
        direct=turn(self.app,owner,'mindbot','Please mark synthetic-task done',[],None,
            dict(expected_profile_version=self.profile['version'],idempotency_key='turn-1'))
        self.assertEqual(direct['action_status'],'applied')
        self.assertEqual(self.store.get(owner,'plan',plan['plan_id'])['tasks'][0]['state'],'completed')
        self.assertEqual(len(self.app.actions.history(owner)),1)

    def test_discussion_creates_proposal_without_mutation(self):
        plan,_=self.setup_request();owner=self.session['profile_id']
        op=dict(kind='complete_task',task_id='synthetic-task',scheduled_at=None,instruction_quote=None)
        self.app.provider=AdviceProvider(advice(operation=op))
        result=turn(self.app,owner,'mindbot','Would it help to mark this task done?',[],None,
            dict(expected_profile_version=self.profile['version'],idempotency_key='turn-1'))
        self.assertEqual(result['action_status'],'approval_required')
        self.assertEqual(self.store.get(owner,'plan',plan['plan_id']),plan)
        self.assertEqual(len(self.app.actions.history(owner)),0)
