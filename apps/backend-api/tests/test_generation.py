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
        value = {k:self.value[k] for k in ('answer','questions')} if tool['function']['name']=='reply_concisely' else self.value
        if tool['function']['name']=='propose_schedule':value={k:self.value[k] for k in ('answer','operation')}
        return dict(status='available', text=json.dumps(value), model=self.model,
                    request_id='software-only', tool_call={'arguments_validated': True})


class GenerationTests(AppCase):
    def test_compact_turn_excludes_full_plan_and_retains_exact_rejected_claim_rule(self):
        self.make_plan()
        claim='There are 9000 jobs waiting for you.'
        provider=self.app.provider=AdviceProvider(advice(answer=claim))
        result=self.app.dispatch('POST','/api/chat',dict(message='How should I practise debugging?',
            expected_profile_version=self.profile['version']),self.token)
        self.assertEqual(provider.tool['function']['name'],'reply_concisely')
        payload=json.loads(provider.messages[-1]['content'])
        self.assertNotIn('saved_tasks',payload['user_context'])
        self.assertLess(len(json.dumps(provider.messages)),6500)
        self.assertEqual(result['provider']['validation_code'],'unsupported_market_quantity')
        ledger=self.store.get(self.profile['profile_id'],'grounding',result['context_version'])
        self.assertEqual(ledger['validation_failure']['rule'],'unsupported_market_quantity')
        self.assertEqual(ledger['validation_failure']['rejected_visible_claims']['answer'],claim)
        self.assertEqual(len(self.store.list(self.profile['profile_id'],'plan')),1)

    def test_rate_limited_own_channel_action_is_saved_without_mutation_or_action_retry(self):
        from unittest.mock import Mock
        from minder_ml.intelligence.groq_adapter import ProviderError
        provider = self.app.provider = AdviceProvider()
        provider.complete_tool = Mock(side_effect=ProviderError('provider_rate_limited', 'software-only'))
        profile = self.save()
        conversation = self.app.dispatch('GET', '/api/product/mindbot-conversation', {}, self.token)
        body = dict(conversation_id=conversation['conversation']['conversation_id'],
            message='Please set my study availability to 6 hours per week.',
            expected_profile_version=profile['version'], idempotency_key='limited-action')
        first = self.app.dispatch('POST', '/api/product/conversation-turn', body, self.token)
        self.assertEqual(first['response']['provider']['code'], 'provider_rate_limited')
        self.assertIn('temporarily busy', first['response']['answer'])
        self.assertEqual(first['response']['action_status'], 'no_mutation_requested_or_executed')
        self.assertEqual(self.app.dispatch('POST', '/api/product/conversation-turn', body, self.token), first)
        self.assertEqual(provider.complete_tool.call_count, 1)
        self.assertEqual(self.store.get(profile['profile_id'], 'profile', profile['profile_id']), profile)
        self.assertEqual(self.app.actions.history(profile['profile_id']), [])
        self.assertEqual(self.store.list(profile['profile_id'], 'plan'), [])

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

    def test_proposed_data_partition_is_not_an_assessment_percentage(self):
        for train, test in [('80','20'), ('70','30'), ('99.5','0.5')]:
            value=advice()
            description=f'Split the bus-delay data into training ({train}%) and test ({test}%) sets. Inspect held-out errors.'
            value['stages'][0]['tasks'][0]['description']=description
            self.app.provider=AdviceProvider(value)
            response=self.app.dispatch('POST','/api/chat',dict(message='Plan a machine learning roadmap for my bus-delay notebook'),self.token)
            self.assertEqual(response['response_mode'],'generated_guidance')
            self.assertEqual(response['generation']['advice']['stages'][0]['tasks'][0]['description'],description)
            self.assertFalse(self.store.list(self.session['profile_id'],'plan'))
        value=advice()
        description='Pick a public tabular dataset, split it into training (80%) and test (20%) sets.'
        value['stages'][0]['tasks'][0]['description']=description
        self.assertEqual(validate_advice(value,[],[])['stages'][0]['tasks'][0]['description'],description)
        value=advice(answer='For a proposed experiment, split the data into training (80%) and test (20%) sets.')
        self.assertEqual(validate_advice(value,[],[])['answer'],value['answer'])

    def test_percentage_exception_cannot_cover_unrelated_claims(self):
        for text in ['Split the data into train (80%) and test (30%) sets.',
                     'Split it into train (80%) and test (20%) sets.',
                     'Split the data into train (100%) and test (0%) sets.',
                     'Split the data into train (80%) and test (20%) sets. Your fit is 99%.',
                     'Split the data into train (80%) and test (20%) sets. Expected accuracy is 95%.',
                     'Use a 90% readiness score.', 'Read https://invented.example']:
            value=advice();value['stages'][0]['tasks'][0]['description']=text
            with self.assertRaises(ValueError):validate_advice(value,[],[])
        for field in ('answer','stage_title','task_title'):
            value=advice();text='This is a guaranteed 99% fit score for your career.'
            if field=='answer':value['answer']=text
            elif field=='stage_title':value['stages'][0]['title']='Guaranteed 99% fit'
            else:value['stages'][0]['tasks'][0]['title']='Guaranteed 99% fit'
            with self.assertRaises(ValueError):validate_advice(value,[],[])

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

    def test_guidance_minimizes_contacts_credentials_and_profile_identifiers(self):
        from minder_app.generation import generate
        provider=self.app.provider=AdviceProvider()
        owner=self.session['profile_id']
        generate(self.app,owner,'I can study six hours. Email private@example.org. Bearer gsk_software_canary',None,
            history=[dict(role='user',content='My contact is +6012 345 6789')])
        payload=json.dumps(provider.messages)
        for private in ('private@example.org','gsk_software_canary','+6012 345 6789',owner):
            self.assertNotIn(private,payload)
        self.assertIn('six hours',payload)

    def test_measured_cut_intro_and_unexpected_language_fail_without_fake_success(self):
        for bad in [advice(answer='I can help you with a practical roadmap or a'),
                    advice(answer='Here is a practical roadmap. 剩下的'),
                    advice(answer='There are 9000 jobs available today.')]:
            self.app.provider=AdviceProvider(bad)
            result=self.app.dispatch('POST','/api/chat',dict(message='Prepare a practice roadmap'),self.token)
            self.assertIsNone(result['generation'])
            self.assertEqual(result['action_status'],'no_mutation_requested_or_executed')

    def test_cut_trailing_fragment_is_omitted_without_inventing_completion(self):
        first='Use your existing notebook to test generalization.'
        value=advice(answer=first+' Compare a baseline before adding more features. If that does not work, the')
        self.app.provider=AdviceProvider(value)
        response=self.app.dispatch('POST','/api/chat',dict(message='Refine my draft practice milestone'),self.token)
        self.assertEqual(response['response_mode'],'generated_guidance')
        actual=response['generation']['advice']['answer']
        self.assertEqual(actual,first+' Compare a baseline before adding more features.')
        self.assertTrue(value['answer'].startswith(actual))
        self.assertEqual(response['provider']['visible_text_adjustments'],['incomplete_intro_tail_omitted'])
        self.assertFalse(self.store.list(self.session['profile_id'],'plan'))
