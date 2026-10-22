"""Software fixtures are synthetic and never recorded as market evidence."""
import copy
import json
from pathlib import Path
import unittest

from minder_ml.intelligence.data_pipeline import normalize_postings, parse_dosm, MARKET_DATA

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

    def test_actual_pinned_dosm_cells(self):
        rows, quality, provenance = parse_dosm()
        self.assertEqual(quality['rejected_rows'], 0)
        self.assertEqual(len(rows), 952)
        self.assertEqual(sum(r['value'] is not None for r in rows), 921)
        self.assertEqual(quality['period_min'], '2019-07-01')
        self.assertEqual(quality['period_max'], '2026-06-30')
        self.assertTrue(all(r['available_at'] == '2026-08-18' for r in rows))


if __name__ == '__main__':
    unittest.main()
