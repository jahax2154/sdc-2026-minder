"""G3 observed activity indexes on frozen, source-native comparison cohorts.

DOSM offering aggregates are not hires, unique ads verified by us, narrow-role
counts, or forecasts. Unknown taxonomy/method versions restrict this index to
one pinned release and its published labels.
"""
from collections import defaultdict
from datetime import date
import json
from .market import comparability_key, observed_share, observed_yoy
from .data_schemas import validate_entity
from .policy import fingerprint, load_policy

VERSION = 'dosm-observed-offering-activity-v1'


def entity_key(row):
    return (row['dimension_scope'], row['occupation_code'], row['occupation_label'],
            row['industry_id'], row['industry_label'], row['group_kind'])


def build_indexes(rows):
    policy, active = load_policy()
    spec = policy['market']
    if (spec['weights'] != [.6, .4] or spec['minimum_cohort_size'] != 5
            or spec['normalization'] != 'fixed_cohort_midrank_percentile'):
        raise ValueError('market policy migration required')
    for row in rows:
        validate_entity(row, 'MarketObservation')
    if len({r['observation_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate observation ID')
    source_snapshot = fingerprint(sorted(rows, key=lambda r: r['observation_id']))
    def scope(r):
        return json.dumps([comparability_key(r), (r['denominator'] or {}).get('meaning')], sort_keys=True)
    cohorts, totals, history = defaultdict(list), {}, {}
    for r in rows:
        key = (scope(r), r['period_start'], r['period_end'])
        history_key = (scope(r), entity_key(r), r['period_start'])
        if history_key in history:
            raise ValueError('duplicate source series/window; pin one revision')
        history[history_key] = r
        if r['group_kind'] == 'overall':
            if key in totals:
                raise ValueError('multiple published totals in one scope')
            totals[key] = r
        else:
            cohorts[key].append(r)
    reports = []
    for key, population in sorted(cohorts.items()):
        total = totals.get(key)
        eligible, excluded, indicators = [], [], []
        for r in sorted(population, key=lambda r: r['observation_id']):
            d = date.fromisoformat(r['period_start'])
            prior = history.get((scope(r), entity_key(r), date(d.year - 1, d.month, 1).isoformat()))
            share = observed_share(r, total) if total else {'value': None, 'reasons': ['missing_published_total']}
            growth = observed_yoy(r, prior) if prior else {'value': None, 'reasons': ['missing_exact_prior_year_quarter']}
            reasons = []
            if r['group_kind'] != 'category':
                reasons.append('not_a_classified_category')
            if r['data_quality_status'] != 'valid' or (prior and prior['data_quality_status'] != 'valid'):
                reasons.append('quality_not_valid')
            if total and total['data_quality_status'] != 'valid':
                reasons.append('denominator_quality_not_valid')
            if r['indicator_id'] != 'online_job_offerings' or r['frequency'] != 'quarterly':
                reasons.append('measure_not_supported_by_this_specification')
            if r['dimension_scope'] not in ('occupation', 'industry'):
                reasons.append('dimension_not_supported_by_this_specification')
            if share['value'] is None:
                reasons += share.get('reasons', ['share_unavailable'])
            if growth['value'] is None:
                reasons += growth.get('reasons', ['growth_unavailable'])
            item = {'observation_id': r['observation_id'], 'entity': list(entity_key(r)),
                    'raw_count': r['value'], 'share': share, 'yoy_percent': growth,
                    'market_activity_index': None, 'source_record': r['source_record']}
            indicators.append(item)
            if reasons:
                excluded.append({'observation_id': r['observation_id'], 'reasons': sorted(set(reasons))})
            else:
                eligible.append(item)
        n = len(eligible)
        universe = sorted(i['observation_id'] for i in eligible)
        universe_hash = fingerprint({'snapshot': source_snapshot, 'specification': VERSION, 'members': universe})
        def percentile(value, values):
            return (sum(v < value for v in values) + .5 * sum(v == value for v in values)) / len(values)
        if n >= spec['minimum_cohort_size']:
            shares = [i['share']['value'] for i in eligible]
            growths = [i['yoy_percent']['value'] for i in eligible]
            for item in eligible:
                a, b = percentile(item['share']['value'], shares), percentile(item['yoy_percent']['value'], growths)
                item.update(share_percentile=a, growth_percentile=b, market_activity_index=100 * (.6*a + .4*b))
        r = population[0]
        reports.append({'specification_version': VERSION, 'policy_id': active['policy_id'],
            'policy_sha256': active['policy_sha256'], 'comparability_key': comparability_key(r),
            'period_start': r['period_start'], 'period_end': r['period_end'],
            'measurement_scope': 'Published source offering activity at its own occupation/industry marginal grain; not narrow-role demand or hires.',
            'original_population_ids': sorted(i['observation_id'] for i in population),
            'eligible_population_ids': universe, 'cohort_hash': universe_hash,
            'cohort_size': n, 'original_population_size': len(population), 'excluded': excluded,
            'status': 'supported' if n >= 5 else 'no_index_insufficient_eligible_cohort',
            'formula': '100*(0.60*midrank_P(share)+0.40*midrank_P(YoY)); fixed eligible universe, minimum N=5',
            'rows': indicators})
    return {'index_schema_version': 'minder-market-activity-g3-v1', 'source_snapshot_hash': source_snapshot,
            'specification_version': VERSION, 'cohorts': reports,
            'narrow_role_market_indices': None,
            'narrow_role_reason': 'No defensible mapping/allocation from published broad categories to the three O*NET roles.',
            'skill_view': {'status': 'not_supported_by_sources', 'rows': []},
            'employer_view': {'status': 'not_supported_by_sources', 'rows': []},
            'joint_views': {'status': 'not_supported_by_separate_marginals', 'rows': []},
            'future_forecast': None}


def project_index_rows(report, observation_ids):
    """Lookup frozen values; filtering never recomputes population percentiles."""
    wanted = set(observation_ids)
    return [dict(row, cohort_hash=c['cohort_hash'], cohort_size=c['cohort_size'])
            for c in report['cohorts'] for row in c['rows'] if row['observation_id'] in wanted]
