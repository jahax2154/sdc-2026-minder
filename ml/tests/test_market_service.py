"""Software fixtures are synthetic and never recorded as market evidence."""
import copy
import json
from pathlib import Path
import unittest
import tempfile
import zipfile
import io
import csv

from minder_ml.intelligence.data_pipeline import (normalize_postings, parse_dosm, MARKET_DATA,
    inspect_csv_bytes, inspect_source_file, audit_jobstreet_corpus, parse_published_role_counts, sha)
from minder_ml.intelligence.market_service import MarketEvidenceService
from minder_ml.intelligence.news import normalize_events, attention
from minder_ml.intelligence.service_contracts import validate

STAMP = '2026-10-23T12:00:00+00:00'


def ad(identifier='test', title='Software Engineer', country='my'):
    return {'id': identifier, 'name': title, 'releasedDate': '2026-10-22T01:00:00Z',
            'location': {'country': country, 'city': 'Test city'},
            'jobAd': {'sections': {'qualifications': {'text': 'Python required. SQL preferred. Java not required.'}}}}


class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.mapping = json.loads((MARKET_DATA / 'mapping.v1.json').read_text())

    def test_scope_dedup_and_positive_requests(self):
        rows, rejected = normalize_postings([ad(), ad(), ad('foreign', country='us')],
                                           retrieved_at=STAMP, mapping=self.mapping)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rejected), 2)
        self.assertEqual(rows[0]['role_ids'], ['15-1252.00'])
        self.assertEqual(rows[0]['skill_ids'], ['source-term:python'])
        self.assertEqual(rows[0]['available_at'], STAMP)
        self.assertEqual({m['kind'] for m in rows[0]['skill_mentions']}, {'requested', 'preferred', 'negated'})

    def test_future_and_internship(self):
        future = ad('future')
        future['releasedDate'] = '2027-01-01T00:00:00Z'
        rows, rejected = normalize_postings([future, ad('intern', 'Internship Software Engineer')],
                                           retrieved_at=STAMP, mapping=self.mapping)
        self.assertEqual(rows[0]['role_ids'], [])
        self.assertEqual(rejected[0]['reason'], 'future_publication')

    def test_template_is_not_duplicate_and_missing_qualifications_is_unknown(self):
        missing=ad('missing');missing['jobAd']['sections']['qualifications']['text']=''
        rows,rejected=normalize_postings([ad('first'),ad('second'),missing],retrieved_at=STAMP,mapping=self.mapping)
        self.assertEqual(len(rows),3)
        self.assertFalse(rejected)
        self.assertIn('same_template_distinct_native_requisition',rows[1]['quality_flags'])
        self.assertEqual(rows[2]['qualifications_status'],'missing')
        self.assertIn('missing_qualifications_not_zero_skills',rows[2]['quality_flags'])

    def test_source_csv_dates_are_not_invented_from_relative_labels(self):
        result=inspect_csv_bytes(b'job_id,listingDate,description\na,2024-01-01,SQL\nb,3 days ago,\n')
        self.assertEqual(result['date_fields']['listingDate']['parsed_dates'],1)
        self.assertEqual(result['date_fields']['listingDate']['min'],'2024-01-01')
        self.assertEqual(result['missing_fields']['description'],1)

    def test_actual_pinned_dosm_cells(self):
        rows, quality, provenance = parse_dosm()
        self.assertEqual(quality['rejected_rows'], 0)
        self.assertEqual(len(rows), 952)
        self.assertEqual(sum(r['value'] is not None for r in rows), 921)
        self.assertEqual(quality['period_min'], '2019-07-01')
        self.assertEqual(quality['period_max'], '2026-06-30')
        self.assertTrue(all(r['available_at'] == '2026-08-18' for r in rows))


class CurrentTests(unittest.TestCase):
    def setUp(self):
        self.service = MarketEvidenceService()
        self.as_of = self.service.snapshot.get('available_at',self.service.snapshot['collected_at'])

    def test_actual_counts_and_contract(self):
        role = self.service.current('role', '15-1252.00', as_of=self.as_of)
        skill = self.service.current('skill', 'source-term:sql', as_of=self.as_of)
        self.assertEqual(role['value'], 5)
        self.assertEqual(skill['value'], 11)
        self.assertIsNone(role['internal_index'])
        self.assertIn('155-ad', role['explanation'])
        self.assertIn('154 inspected advertisements with observed qualification sections',skill['denominator'])
        self.assertEqual(len(self.service.source_facts('skill', 'source-term:sql')['supporting_ads']), 11)
        for result in (role, skill):
            validate('MarketResult', result)
            self.assertEqual(result['published_at'], self.as_of)

    def test_as_of_and_unknown_vs_zero(self):
        unknown = self.service.current('skill', 'unmapped', as_of=self.as_of)
        before = self.service.current('role', '15-1252.00', as_of='2020-01-01T00:00:00Z')
        zero = self.service.current('role', '15-2051.00', as_of=self.as_of)
        self.assertIsNone(unknown['value'])
        self.assertIsNone(before['value'])
        self.assertEqual(zero['value'], 0)
        empty = copy.deepcopy(self.service.snapshot)
        empty['ads'] = []
        self.assertIsNone(MarketEvidenceService(empty).current('role', '15-2051.00', as_of=self.as_of)['value'])

    def test_both_forecast_families_and_target(self):
        for kind, identifier in [('role', '15-1252.00'), ('skill', 'source-term:sql')]:
            result = self.service.forecast(kind, identifier, issued_at='2026-10-23T12:00:00Z')
            self.assertEqual(result['status'], 'unavailable')
            self.assertIsNone(result['value'])
            self.assertEqual(result['target_period'], {'start': '2027-01-01', 'end': '2027-03-31'})

    def test_aliases_and_preference_independence(self):
        mapped = MarketEvidenceService(aliases={'role': {'canonical-id': '15-1252.00'}})
        result = mapped.current('role', 'canonical-id', as_of=self.as_of)
        self.assertEqual(result['entity_id'], 'canonical-id')
        self.assertEqual(result['value'], 5)
        # No profile/preference input exists on the market adapter boundary.
        self.assertEqual(result['value'], self.service.current('role', '15-1252.00', as_of=self.as_of)['value'])
        self.assertEqual(len(self.service.broad_observations(as_of='2020-01-01T00:00:00Z')), 0)
        self.assertEqual(len(self.service.broad_observations(as_of=self.as_of)), 952)


class HistoricalSourceTests(unittest.TestCase):
    def test_numeric_source_labels_only_and_period_check(self):
        body='Big Data Analytics: Job Market Insights, First Quarter of 2026 Latest Release : 25 June 2026 '
        body+='Software Developers (20,089 job offerings). Services (494,182 job offerings). Accountants and Auditors.'
        args=dict(period='2026-Q1',source_url='https://www.dosm.gov.my/test-only',source_id='synthetic-test',
                  retrieved_at=STAMP,document_sha256='a'*64)
        observed,missing=parse_published_role_counts(body,**args)
        self.assertEqual(len(observed),1)
        self.assertEqual(observed[0]['value'],20089)
        self.assertEqual(observed[0]['available_at'],STAMP)
        self.assertEqual(len(missing),6)
        self.assertFalse(observed[0]['eligible_for_approved_unique_ad_forecasting'])
        with self.assertRaisesRegex(ValueError,'period_mismatch'):
            parse_published_role_counts(body,**dict(args,period='2026-Q2'))

    def test_frozen_corpus_counts_remain_ineligible_even_with_descriptions(self):
        # Entirely fictional software fixture; no output enters source evidence.
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);archive=folder/'test.zip';output=folder/'audit.json'
            stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=['job_id','job_title','location','listingDate','descriptions'])
            writer.writeheader()
            rows=[{'job_id':'a','job_title':'Software Engineer','location':'Test-only','listingDate':'2024-01-02','descriptions':'Python proficiency required. Java experience preferred. Excel in a dynamic environment.'},
                  {'job_id':'b','job_title':'Software Engineer','location':'Test-only','listingDate':'2025-05-01','descriptions':'We use Python.'}]
            writer.writerows(rows+[rows[0]])
            with zipfile.ZipFile(archive,'w') as z:z.writestr('test.csv',stream.getvalue())
            audit_jobstreet_corpus(archive,sha(archive),output)
            import json
            result=json.loads(output.read_text())
            self.assertEqual(result['unique_job_ids'],2)
            self.assertEqual(result['duplicate_job_ids'],1)
            self.assertEqual(set(result['dated_corpus_counts']),{'2024-Q1','2025-Q2'})
            self.assertEqual(result['dated_corpus_counts']['2024-Q1']['technology_explicit_request_clauses'],{'source-term:python':1})
            self.assertEqual(result['dated_corpus_counts']['2025-Q2']['technology_explicit_request_clauses'],{})
            self.assertFalse(result['eligible_for_approved_forecasting'])
            self.assertIsNone(result['historical_available_at_by_record'])

    def test_inspection_metadata_excludes_inline_images_and_unbounded_links(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'test.html'
            path.write_text('<title>Test</title><img src="data:image/png;base64,skills"><a href="/download.csv">Data</a>')
            result=inspect_source_file(path,'html')
            self.assertEqual(result['data_links'],['/download.csv'])


class NewsTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((MARKET_DATA / 'sources.v1.json').read_text())
        self.event = {'source_id': 'mida-official', 'url': 'https://www.mida.gov.my/example',
                      'event_key': 'synthetic-test-event', 'claim_type': 'announcement',
                      'direction': 'ambiguous', 'outcome_verified': False, 'topics': ['AI'],
                      'published_at': '2026-10-01T00:00:00Z', 'available_at': '2026-10-02T00:00:00Z',
                      'geography': 'MY', 'full_document_sha256': 'a' * 64,
                      'evidence_kind': 'underlying_document'}

    def test_deduplicate_event_not_url(self):
        another = dict(self.event, url='https://www.mida.gov.my/syndication')
        result = normalize_events([self.event, another], self.registry, as_of=STAMP)
        self.assertEqual(len(result['events']), 1)
        self.assertEqual(len(result['events'][0]['document_urls']), 2)

    def test_exclude_snippet_personal_future_fake_host_and_outcome(self):
        bad = [dict(self.event, source_id='personal-post'), dict(self.event, evidence_kind='snippet'),
               dict(self.event, available_at='2027-01-01T00:00:00Z'),
               dict(self.event, url='https://www.mida.gov.my.attacker.test/'),
               dict(self.event, outcome_verified=True)]
        result = normalize_events(bad, self.registry, as_of=STAMP)
        self.assertEqual(result['events'], [])
        self.assertEqual(len(result['rejected']), 5)

    def test_missing_coverage_and_global_separation(self):
        events = normalize_events([self.event], self.registry, as_of=STAMP)['events']
        args = dict(topic='AI', start='2026-10-01', end='2026-10-23', as_of=STAMP)
        self.assertIsNone(attention(events, coverage=[], **args)['value'])
        coverage = [{'source_id': 'mida-official', 'complete': True, 'documents': 10,
                     'start': args['start'], 'end': args['end'], 'available_at': STAMP}]
        self.assertEqual(attention(events, coverage=coverage, **args)['value'], .1)
        self.assertEqual(attention(events, coverage=coverage, geography='GLOBAL', **args)['value'], 0)
        coverage[0]['complete'] = False
        self.assertIsNone(attention(events, coverage=coverage, **args)['value'])


if __name__ == '__main__':
    unittest.main()
