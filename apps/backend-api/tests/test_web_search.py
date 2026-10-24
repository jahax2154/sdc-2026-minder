"""Declared search/HTTP fixtures, never a native search/provider proof."""
import io
import json
import tempfile
import unittest
from minder_app.web_search import MwmblSearch,SearchRetrieval,public_queries,candidate_url,detail_seeds,select_passage
from minder_app.web_evidence import current_question

class Response(io.BytesIO):
    status=200

class SearchTests(unittest.TestCase):
    def test_exact_ui_regressions_get_details_instead_of_registry_introductions(self):
        questions=['What are the market trends right now?', 'How is the software engineering job market now?',
            "What's the most relevant skills now to become a software engineer?"]
        for question in questions:
            self.assertTrue(current_question(question))
            self.assertTrue(detail_seeds(question))
            self.assertFalse(any('/faqs' in s[1] or '/mycol/' in s[1] for s in detail_seeds(question)))
        self.assertIn('technology',detail_seeds(questions[1])[0][1])
        self.assertTrue(any('onetonline' in s[1] for s in detail_seeds(questions[2])))
        self.assertTrue(any('mozilla' in s[1] for s in detail_seeds(questions[2])))
        self.assertIn('job market',public_queries(questions[1])[0])
        self.assertIn('curriculum',public_queries(questions[2])[1])
        record=dict(text='The registry describes a national programme for occupational groups.\nSoftware engineers develop systems and test software against user requirements.\nSubscribe for our latest email marketing information and cookie policies.')
        self.assertTrue(select_passage(record,questions[2]).startswith('Software engineers'))

    def test_documented_v2_query_and_cached_results_never_send_private_question(self):
        sent=[]
        def open_request(request,timeout):
            sent.append(request.full_url)
            return Response(json.dumps(dict(results=[dict(url='https://www.dataquest.io/blog/data-analyst-skills/',title='Public skills',content='snippet is not a verified page')])).encode())
        with tempfile.TemporaryDirectory() as root:
            search=MwmblSearch(opener=open_request,state_root=root)
            queries=public_queries('My CV contact private-person@example.test: which data analyst skills do Malaysian jobs seek?')
            first=search.search(queries[0]);second=search.search(queries[0])
            self.assertEqual(len(sent),1)
            self.assertIn('/api/v2/search/?q=Malaysia+data+analyst',sent[0])
            self.assertNotIn('private-person',sent[0]);self.assertNotIn('CV',sent[0])
            self.assertEqual(first['status'],'available');self.assertEqual(second['cache_status'],'recent_search_cache')
            self.assertNotIn('content',first['results'][0])

    def test_discovery_is_not_page_evidence_and_partial_fetch_keeps_official_page(self):
        class Search:
            def search(self,query):return dict(query=query,status='available',provider='declared',results=[
                dict(url='https://www.dataquest.io/blog/data-analyst-skills/',title='Discovered skills'),
                dict(url='https://www.randstad.com.my/jobs/',title='Unavailable public source')])
        class Page:
            def fetch(self,seed):
                if 'randstad' in seed[1]:raise TimeoutError()
                return dict(id=seed[0],url=seed[1],title=seed[2],geography=seed[3],scope=seed[4],
                    text='Actual fetched page teaches analysis skills and states its own measurement scope.',
                    published_at=None,retrieved_at='2026-10-24T00:00:00Z',sha256='0'*64,cache_status='live_fetched')
        result=SearchRetrieval(search=Search(),fetcher_factory=lambda **kw:Page(),predefined=Page()).retrieve('What do Malaysian data analyst jobs require?')
        self.assertEqual(result['mode'],'search_and_fetch')
        self.assertTrue(any(s['origin']=='search_discovered' for s in result['sources']))
        self.assertTrue(any(s['origin']=='predefined_official' for s in result['sources']))
        self.assertTrue(result['failures'])
        self.assertTrue(all('Actual fetched page' in s['passage'] for s in result['sources']))

    def test_private_destinations_unknown_hosts_and_unrelated_question_routes(self):
        for url in ('http://127.0.0.1/admin','https://user:password@www.dosm.gov.my/','https://evil.example/',
                    'https://www.dataquest.io:8443/path'):
            self.assertIsNone(candidate_url(url))
        for question in ('Which skills do Malaysian data analyst jobs require?',
            'What is happening in the Malaysian labour market now?',
            'Are cyber jobs growing around Kuala Lumpur?'):
            self.assertTrue(current_question(question))
        self.assertFalse(current_question('How can I practise debugging my Python project?'))
        self.assertFalse(current_question('Please reschedule my task to tomorrow.'))
