"""Source-grounded market adapter for minder-parallel-v1. No personal scoring.

Reads committed small snapshots by default, never a sibling worktree or live DB.
Canonical catalogue aliases are injected by A; no inferred taxonomy joins.
"""
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path

from .data_pipeline import MARKET_DATA
from .service_contracts import next_calendar_quarter, validate


def timestamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timezone required')
    return result


class MarketEvidenceService:
    def __init__(self, snapshot=None, *, aliases=None, forecast_registry=None):
        path = MARKET_DATA / 'snapshot.v1.json' if snapshot is None else snapshot
        self.snapshot = copy.deepcopy(path) if isinstance(path, dict) else json.loads(Path(path).read_text())
        if self.snapshot.get('synthetic') is not False:
            raise ValueError('service requires explicitly real evidence')
        self.version = hashlib.sha256(json.dumps(self.snapshot, sort_keys=True).encode()).hexdigest()
        self.mapping = json.loads((MARKET_DATA / 'mapping.v1.json').read_text())
        if self.snapshot['mapping_version'] != self.mapping['version']:
            raise ValueError('snapshot mapping version mismatch')
        self.aliases = copy.deepcopy(aliases or {})
        self.forecast_registry = forecast_registry

    def _source_id(self, entity_type, entity_id):
        return self.aliases.get(entity_type, {}).get(entity_id, entity_id)

    def _empty(self, entity_type, entity_id, issue, kind):
        if entity_type not in ('role', 'skill', 'industry') or not entity_id:
            raise ValueError('valid entity_type and entity_id required')
        timestamp(issue)
        day = issue[:10]
        return {'entity_type': entity_type, 'entity_id': entity_id, 'kind': kind,
                'status': 'unavailable', 'geography': 'MY',
                'source_universe_id': self.snapshot['source_universe_id'],
                'cohort_version': self.version, 'measurement': 'unique_valid_inspected_advertisements',
                'unit': 'advertisements', 'denominator': 'bounded inspected employer sample; not all Malaysian jobs',
                'observation_period': {'start': day, 'end': day},
                'published_at': None, 'available_at': None, 'ingested_at': None, 'issued_at': issue,
                'target_period': next_calendar_quarter(issue) if kind == 'forecast' else None,
                'horizon': 'next_full_calendar_quarter' if kind == 'forecast' else 'observed',
                'value': None, 'internal_index': None,
                'uncertainty': {'lower': None, 'upper': None, 'method': None},
                'missing_reasons': [], 'source_ids': [], 'model_version': None, 'explanation': ''}

    def current(self, entity_type, entity_id, *, as_of):
        result = self._empty(entity_type, entity_id, as_of, 'current')
        source_id = self._source_id(entity_type, entity_id)
        collected = self.snapshot['collected_at']
        if timestamp(collected) > timestamp(as_of):
            reason = 'snapshot_not_available_at_requested_time'
        elif not self.snapshot['ads']:
            reason = 'no_valid_ads_collected_not_observed_zero'
        elif entity_type not in ('role', 'skill'):
            reason = 'no_canonical_industry_mapping_from_employer_sample'
        else:
            mapping_key = 'roles' if entity_type == 'role' else 'skills'
            id_key = 'source_role_id' if entity_type == 'role' else 'source_skill_id'
            supported = {r[id_key] for r in self.mapping[mapping_key]}
            if source_id not in supported:
                reason = 'no_supported_source_to_canonical_entity_mapping'
            else:
                field = 'role_ids' if entity_type == 'role' else 'skill_ids'
                ads = [a for a in self.snapshot['ads'] if source_id in a[field]]
                # The collector release is our derived measurement publication.
                # Individual employer publication dates remain in source_facts().
                result.update(status='available', value=len(ads), published_at=collected,
                              available_at=collected, ingested_at=collected,
                              observation_period={'start': collected[:10], 'end': collected[:10]},
                              source_ids=['bosch-smartrecruiters-my'],
                              model_version='observed-ad-count-v1', missing_reasons=[],
                              explanation=(f'{len(ads)} unique inspected advertisements '
                                  f'{"mapped to this occupation" if entity_type == "role" else "requesting this technology"} '
                                  f'in a {len(self.snapshot["ads"])}-ad Bosch Malaysia sample observed '
                                  f'on {collected[:10]}. This is an active-ad snapshot, not a quarter inflow '
                                  'or a national employment count. Dictionary/title coverage is partial.'))
                return validate('MarketResult', result)
        result['missing_reasons'] = [reason]
        result['explanation'] = 'Current market evidence unavailable: ' + reason.replace('_', ' ') + '.'
        return validate('MarketResult', result)

    def forecast(self, entity_type, entity_id, *, issued_at):
        result = self._empty(entity_type, entity_id, issued_at, 'forecast')
        source_id = self._source_id(entity_type, entity_id)
        if self.forecast_registry is not None:
            from .forecasting import serve_forecast
            selected = serve_forecast(self.forecast_registry, entity_type, source_id, issued_at)
            if selected is not None:
                result.update(selected)
                return validate('MarketResult', result)
        collected = self.snapshot['collected_at']
        if timestamp(collected) <= timestamp(issued_at):
            result.update(observation_period={'start': collected[:10], 'end': collected[:10]},
                          available_at=collected, ingested_at=collected,
                          source_ids=['bosch-smartrecruiters-my'])
        result['missing_reasons'] = [
            'no_comparable_quarterly_unique_ad_history_for_' + entity_type,
            'active_ad_snapshot_is_not_quarterly_advertisement_inflow',
            'dosm_broad_aggregates_cannot_be_allocated_to_specific_roles_or_skills']
        result['explanation'] = ('Next-quarter forecast unavailable: insufficient comparable historical '
            f'{entity_type} advertisement counts. Target {result["target_period"]["start"]} to '
            f'{result["target_period"]["end"]}. No selected model or forecast accuracy is claimed.')
        return validate('MarketResult', result)

    def source_facts(self, entity_type, entity_id):
        """Internal provenance/explanation facts; consumer presents source links."""
        source_id = self._source_id(entity_type, entity_id)
        field = {'role': 'role_ids', 'skill': 'skill_ids'}.get(entity_type)
        return {'snapshot_sha256': self.version, 'collected_at': self.snapshot['collected_at'],
                'coverage': copy.deepcopy(self.snapshot['collection']),
                'sources': [{'source_id': 'bosch-smartrecruiters-my',
                             'url': 'https://www.bosch.com.my/careers/'}],
                'supporting_ads': [copy.deepcopy(a) for a in self.snapshot['ads']
                                   if field and source_id in a[field]],
                'limitations': copy.deepcopy(self.snapshot['limitations'])}

    def broad_observations(self, *, as_of):
        """Source-native broad measurements, never allocated to canonical roles."""
        return [copy.deepcopy(r) for r in self.snapshot['dosm_observations']
                if timestamp(r['available_at'] + 'T00:00:00+00:00') <= timestamp(as_of)]
