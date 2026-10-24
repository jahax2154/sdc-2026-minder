"""No real network/provider in these checks; native evidence kept separately."""
import copy
import json
from support import AppCase
from minder_app.web_evidence import validate_findings, current_question, guard_disclaimers


SOURCE = dict(id='official-public-fixture', url='https://www.talentcorp.com.my/mycol/', title='Official occupation scope fixture',
    published_at=None, retrieved_at='2026-10-24T12:00:00+00:00', geography='MY', scope='Occupation groups, not vacancies.',
    sha256='a'*64, cache_status='live_fetched', text='The occupations listed reflect skills shortages across economic sectors in Malaysia and are not a count of jobs.',
    passage='The occupations listed reflect skills shortages across economic sectors in Malaysia and are not a count of jobs.')
QUOTE = SOURCE['text']


class Retriever:
    def retrieve(self, question):
        return dict(sources=[copy.deepcopy(SOURCE)], failures=[], tool='retrieve_public_career_sources', limitation='Bounded fixture sources.')


class Provider:
    model = 'declared-software-provider'
    def complete_tool(self, messages, tool):
        self.messages = messages
        return dict(status='available', text=json.dumps(dict(introduction='I checked a public Malaysian occupation reference.',
            findings=[dict(quote_id='q1', explanation='This identifies shortage groups, rather than a national job vacancy total.')],
            limitations=['A shortage list is not a guarantee of individual opportunity.'])), model=self.model)


class WebTests(AppCase):
    def test_discovered_but_uncited_page_does_not_relabel_predefined_answer_sources(self):
        from unittest.mock import Mock
        self.app.public_retrieval.retrieve=Mock(return_value=dict(sources=[dict(SOURCE,origin='predefined_detail')],
            failures=[],tool='search_then_fetch_public_pages',mode='search_and_fetch',
            discovery=[dict(status='available',provider='declared',query='public query')],limitation='Declared discovery fixture'))
        result=self.app.dispatch('POST','/api/chat',dict(message='What do Malaysian job shortage sources say?'),self.token)
        self.assertIn('This explanation cites predefined detail/reference pages',result['answer'])
        self.assertFalse(result['diagnostics']['retrieval']['answer_uses_search_discovered_pages'])
        self.assertEqual(result['diagnostics']['retrieval']['answer_source_origins'],['predefined_detail'])

    def test_quota_failure_is_not_misrepresented_as_rejected_evidence(self):
        from minder_app.model_gateway import QuotaError
        from unittest.mock import Mock
        self.app.provider.complete_tool=Mock(side_effect=QuotaError('provider_rate_limited',retry_after=37,attempts=0))
        result=self.app.dispatch('POST','/api/chat',dict(message='What do Malaysian job shortage sources say?'),self.token)
        self.assertIn('usage limit',result['answer'])
        self.assertIn('37 seconds',result['answer'])
        self.assertNotIn('could not validate',result['answer'])
        self.assertEqual(result['diagnostics']['validation']['status'],'not_run_provider_or_sources_unavailable')
        self.assertFalse(result['provider']['invoked'])
        self.assertTrue(result['sources'])

    def test_bad_optional_sentence_does_not_discard_supported_sentence(self):
        from minder_app.web_evidence import partial_findings
        kept='This source identifies occupation groups without counting available jobs.'
        removed='There are 999999 jobs available for everyone.'
        value=dict(introduction='This is a limited public occupational reference.',
            findings=[dict(quote_id='q1',explanation=kept+' '+removed)],limitations=[])
        result=partial_findings(value,[SOURCE])
        self.assertEqual(result['findings'][0]['explanation'],kept)
        self.assertEqual(result['rejected_claims'][0]['claim']['explanation'],removed)
        self.assertEqual(result['rejected_claims'][0]['rule'],'unsupported_web_quantity')

    def test_actual_dosm_thousands_to_rounded_millions_rejection_regression(self):
        from minder_app.web_evidence import partial_findings,quantities_supported,LFS_URL
        passage='Month 2026-08: unemployment rate 2.9%; participation rate 71.0%; employed persons 16874.4 thousand; unemployed persons 511.6 thousand.\nMonth 2026-07: unemployment rate 3.0%; participation rate 70.9%; employed persons 16845.6 thousand; unemployed persons 520.3 thousand.'
        source=dict(SOURCE,url=LFS_URL,text=passage,passage=passage,observation_period='2026-08')
        claims=[
            'Unemployment edged down to 2.9% in Aug 2026 from 3.0% in Jul, with participation at 71.0% and 16.87m employed. This is a two-month national trend, not a sector or role-level signal.',
            'The July baseline (3.0% unemployment, 70.9% participation, 16.85m employed) shows the small month-on-month improvement, but only two months are available, so the direction is preliminary.']
        value=dict(introduction='The latest retrieved observation is August 2026.',findings=[dict(quote_id='q'+str(i+1),explanation=c) for i,c in enumerate(claims)],limitations=[])
        result=partial_findings(value,[source])
        self.assertEqual(len(result['findings']),2)
        self.assertEqual(result['rejected_claims'],[])
        for invalid in ['16.88m employed','999999m employed','16.87 employed without a unit']:
            self.assertFalse(quantities_supported(invalid,[source]))
        self.assertFalse(quantities_supported('16.87m employed',[dict(source,url='https://example.invalid')]))

    def test_compact_public_context_retains_quote_mapping_dates_scope_without_duplicate_quotes_or_urls(self):
        from minder_app.web_evidence import model_sources,quote_index
        source=dict(SOURCE,observation_period='2026-08')
        compact=model_sources([source])
        self.assertEqual(list(compact[0]['passages']),list(quote_index([source])))
        self.assertEqual(compact[0]['passages']['q1'],SOURCE['passage'])
        self.assertEqual(compact[0]['observation_period'],'2026-08')
        self.assertEqual(compact[0]['scope'],SOURCE['scope'])
        self.assertNotIn(SOURCE['url'],json.dumps(compact))
        self.assertNotIn(SOURCE['id'],json.dumps(compact))
        short_first=dict(source,passage='Skills\n'+SOURCE['passage'])
        self.assertEqual(model_sources([short_first])[0]['passages']['q1'],SOURCE['passage'])

    def test_undated_description_cannot_become_current_trend_but_dated_observation_can(self):
        from minder_app.web_evidence import partial_findings
        candidate=dict(introduction='Here is what the retrieved evidence establishes.',findings=[
            dict(quote_id='q1',explanation='Hiring is growing right now across these occupations.')],limitations=[])
        result=partial_findings(candidate,[SOURCE])
        self.assertEqual(result['findings'],[])
        self.assertEqual(result['rejected_claims'][0]['rule'],'undated_source_cannot_establish_current_trend')
        # Observation months and article publication dates remain separate fields.
        observed=dict(SOURCE,observation_period='2026-08')
        dated=dict(candidate,findings=[dict(quote_id='q1',explanation='The cited observation is a dated context, not a role-level hiring forecast.')])
        self.assertEqual(len(partial_findings(dated,[observed])['findings']),1)

    def test_distinct_passages_from_one_source_are_not_consolidated_as_duplicates(self):
        page=dict(SOURCE,text=SOURCE['text']+' A skills taxonomy identifies work activities without certifying personal proficiency.',
            passage=SOURCE['passage']+'\nA skills taxonomy identifies work activities without certifying personal proficiency.')
        value=dict(introduction='This source provides two different types of context.',findings=[
            dict(quote_id='q1',explanation='The first passage describes occupation-level shortages, rather than individual competence.'),
            dict(quote_id='q2',explanation='The second describes work activities, rather than an assessment of your proficiency.')],limitations=[])
        self.assertEqual(len(validate_findings(value,[page])['findings']),2)

    def test_optional_unsupported_claim_is_omitted_without_losing_supported_explanation(self):
        from unittest.mock import Mock
        second=dict(SOURCE,id='second-public-fixture',text='A public skills reference describes analytical work without measuring hiring demand.',
            passage='A public skills reference describes analytical work without measuring hiring demand.')
        self.app.public_retrieval.retrieve=Mock(return_value=dict(sources=[SOURCE,second],failures=[],
            tool='search_then_fetch_public_pages',limitation='Declared fixture',mode='search_and_fetch'))
        rejected='There are 999999 jobs available for everyone.'
        candidate=dict(introduction='These public references describe different evidence scopes.',
            findings=[dict(quote_id='q1',explanation='The source identifies shortage occupation groups, without proving a vacancy count.'),
                      dict(quote_id='q2',explanation=rejected)],limitations=[],
            advice='Compare the stated skills with a small set of current job descriptions before choosing practice activities.')
        self.app.provider.complete_tool=Mock(return_value=dict(status='available',text=json.dumps(candidate),model='declared'))
        result=self.app.dispatch('POST','/api/chat',dict(message='What do Malaysian job shortage sources say?'),self.token)
        self.assertEqual(result['provider']['status'],'available')
        self.assertEqual(result['provider']['validation_status'],'partial')
        self.assertEqual(len(result['statements']),1)
        self.assertIn('shortage occupation groups',result['answer'])
        self.assertIn('Practical advice',result['answer'])
        self.assertNotIn('999999',result['answer'])
        ledger=self.store.get(self.session['profile_id'],'public_web_evidence',result['context_version'])
        self.assertEqual(ledger['rejected_claims'][0]['claim']['explanation'],rejected)
        self.assertEqual(ledger['rejected_claims'][0]['rule'],'unsupported_web_quantity')
        self.assertEqual(self.store.list(self.session['profile_id'],'plan'),[])
        self.assertEqual(self.store.list(self.session['profile_id'],'profile'),[])

    def setUp(self):
        super().setUp()
        self.app.public_retrieval = Retriever()
        self.app.provider = Provider()

    def test_no_profile_question_uses_retrieved_page_and_persists_cited_reply_without_mutation(self):
        conversation = self.app.dispatch('POST','/api/product/conversations',dict(title='Question', idempotency_key='new'),self.token)
        result = self.app.dispatch('POST','/api/product/conversation-turn',dict(
            conversation_id=conversation['conversation']['conversation_id'], message='What do Malaysian job shortage sources say?',
            expected_profile_version=None,idempotency_key='question'),self.token)
        response = result['response']
        self.assertEqual(response['response_mode'], 'grounded_evidence')
        self.assertEqual(response['provider']['status'], 'available')
        self.assertEqual(response['statements'][0]['text'], QUOTE)
        self.assertEqual(response['statements'][0]['citation']['url'], SOURCE['url'])
        self.assertIsNone(response['statements'][0]['published_at'])
        self.assertEqual(self.store.list(self.session['profile_id'], 'profile'), [])
        self.assertEqual(self.store.list(self.session['profile_id'], 'plan'), [])
        self.assertNotIn('user_context', self.app.provider.messages[-1]['content'])

    def test_unverified_quotes_unknown_sources_or_quantities_never_become_answers(self):
        base = dict(introduction='Here is a bounded explanation of public source information.',
            findings=[dict(quote_id='q1',explanation='This describes occupational shortage groups with a limited scope.')],limitations=[])
        for field, value in [('quote_id','invented'),('quote','This invented quote does not occur in the retrieved source.'),
                             ('explanation','There are 999999 guaranteed available jobs in this field.')]:
            bad = copy.deepcopy(base);bad['findings'][0][field]=value
            with self.assertRaises(Exception):
                validate_findings(bad,[SOURCE])

    def test_personal_action_and_current_plan_do_not_route_to_public_search(self):
        self.assertFalse(current_question('Please reschedule my current task to tomorrow at 3pm.'))
        self.assertFalse(current_question('Help me review my current plan.'))
        self.assertTrue(current_question('Which skills are in demand in Malaysia?'))

    def test_negative_guarantee_lists_remain_disclaimers_not_blocked_positive_claims(self):
        for sentence in ['It does not show the total number of jobs, guaranteed individual employment opportunities, or all roles.',
                         'MyCOL is not a count of jobs or a guarantee of individual opportunity.',
                         'The source cannot guarantee a job.']:
            self.assertNotIn('guarantee', guard_disclaimers(sentence))
        for sentence in ['You have guaranteed employment.', 'It does not show low demand but guarantees a job.']:
            self.assertIn('guarantee', guard_disclaimers(sentence))
