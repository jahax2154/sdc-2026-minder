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
        if (self.snapshot['mapping_version'] != self.mapping['version']
                or self.snapshot['mapping_sha256'] != hashlib.sha256((MARKET_DATA / 'mapping.v1.json').read_bytes()).hexdigest()):
            raise ValueError('snapshot mapping version mismatch')
        self.aliases = copy.deepcopy(aliases or {})
        published_path = MARKET_DATA / 'published-role-observations.v1.json'
        self.published_roles = json.loads(published_path.read_text()) if published_path.is_file() else {'observations': [], 'limitations': []}
        self.published_version = hashlib.sha256(published_path.read_bytes()).hexdigest() if published_path.is_file() else None
        if self.published_roles.get('synthetic', False):
            raise ValueError('synthetic_published_role_evidence')
        context_path=MARKET_DATA/'current-public-evidence.v1.json'
        self.context_evidence=json.loads(context_path.read_text()) if context_path.is_file() else None
        self.context_version=hashlib.sha256(context_path.read_bytes()).hexdigest() if context_path.is_file() else None
        self.forecast_registry = forecast_registry
        registry_path = MARKET_DATA / 'serving-registry.v1.json'
        if snapshot is None and forecast_registry is None and registry_path.is_file():
            from .forecasting import ForecastRegistry
            self.forecast_registry = ForecastRegistry(registry_path)
            expected = self.forecast_registry.manifest['current_snapshot_sha256']
            if hashlib.sha256((MARKET_DATA / 'snapshot.v1.json').read_bytes()).hexdigest() != expected:
                raise ValueError('current_snapshot_checksum_mismatch')
            if self.published_version != self.forecast_registry.manifest.get('published_role_snapshot_sha256'):
                raise ValueError('published_role_snapshot_checksum_mismatch')
            if self.context_version != self.forecast_registry.manifest.get('public_context_snapshot_sha256'):
                raise ValueError('public_context_snapshot_checksum_mismatch')

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
        if entity_type == 'role' and source_id.startswith('dosm:jmi:published-role-label:'):
            known = [r for r in self.published_roles['observations'] if r['entity_id'] == source_id]
            eligible = [r for r in known if timestamp(r['available_at']) <= timestamp(as_of)]
            result.update(source_universe_id='dosm-jmi-published-top-occupation-labels',
                          cohort_version=self.published_version or self.version,
                          measurement='published_online_job_offerings_for_source_role_label',
                          unit='published job offerings',
                          denominator='DOSM-covered online recruitment platforms; not all Malaysian employment or vacancies')
            if not eligible:
                reason = 'published_role_record_not_available_at_requested_time' if known else 'no_explicit_published_role_count'
                result.update(missing_reasons=[reason],explanation='Published role evidence unavailable: '+reason.replace('_',' ')+'.')
            else:
                latest = max(eligible, key=lambda r: (r['period']['end'], timestamp(r['published_at'])))
                result.update(status='available', value=latest['value'], observation_period=latest['period'],
                    published_at=latest['published_at'], available_at=latest['available_at'],
                    ingested_at=latest['available_at'], source_ids=[latest['source_id']],
                    model_version='dosm-explicit-published-role-count-v1', missing_reasons=[],
                    explanation=(f'DOSM reported {latest["value"]:,} online job offerings for its '
                        f'{latest["label"]} category during {latest["period"]["start"]} to {latest["period"]["end"]}, '
                        f'published on {latest["published_at"][:10]}. This source quantity is separate from '
                        'the inspected employer-ad sample. Unique-ad deduplication, positions per advertisement '
                        'and a canonical occupation crosswalk are unverified; this is not all Malaysian employment.'))
            return validate('MarketResult',result)
        collected = self.snapshot['collected_at']
        available = self.snapshot.get('available_at',collected)
        if timestamp(available) > timestamp(as_of):
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
                denominator = len(self.snapshot['ads']) if entity_type == 'role' else sum(
                    a.get('qualifications_status','observed') == 'observed' for a in self.snapshot['ads'])
                if not denominator:
                    result['missing_reasons']=['no_observed_qualification_sections_not_zero_skill_requests']
                    result['explanation']='Skill advertisement evidence unavailable: no qualification sections were observed.'
                    return validate('MarketResult',result)
                # The collector release is our derived measurement publication.
                # Individual employer publication dates remain in source_facts().
                result.update(status='available', value=len(ads), published_at=available,
                              available_at=available, ingested_at=available,
                              observation_period={'start': collected[:10], 'end': collected[:10]},
                              source_ids=['bosch-smartrecruiters-my'],
                              model_version='observed-ad-count-v2', missing_reasons=[],
                              denominator=f'{denominator} inspected '+('advertisements with observed qualification sections' if entity_type=='skill' else 'advertisements')+'; not all Malaysian jobs',
                              explanation=(f'{len(ads)} unique inspected advertisements '
                                  f'{"mapped to this occupation" if entity_type == "role" else "requesting this technology"} '
                                  f'in a {denominator}-ad Bosch Malaysia inspected population observed '
                                  f'on {collected[:10]}. This is an active-ad snapshot, not a quarter inflow '
                                  'or a national employment count. Dictionary/title coverage is partial; '
                                  'old release dates remain visible in source facts. Missing qualifications are excluded from skill coverage.'))
                return validate('MarketResult', result)
        result['missing_reasons'] = [reason]
        result['explanation'] = 'Current market evidence unavailable: ' + reason.replace('_', ' ') + '.'
        return validate('MarketResult', result)

    def forecast(self, entity_type, entity_id, *, issued_at):
        result = self._empty(entity_type, entity_id, issued_at, 'forecast')
        source_id = self._source_id(entity_type, entity_id)
        if entity_type == 'role' and source_id.startswith('dosm:jmi:published-role-label:'):
            result.update(source_universe_id='dosm-jmi-published-top-occupation-labels',
                cohort_version=self.published_version or self.version,
                missing_reasons=['published_offerings_not_verified_unique_advertisements',
                    'top_list_censoring_is_missing_not_zero','insufficient_comparable_publication_aware_history'],
                explanation='Next-quarter forecast unavailable: the acquired published role-label offerings '
                    'do not establish the approved unique-ad target, complete comparable history or archived availability.')
            return validate('MarketResult',result)
        if self.forecast_registry is not None:
            from .forecasting import serve_forecast
            selected = serve_forecast(self.forecast_registry, entity_type, source_id, issued_at)
            if selected is not None:
                result.update(selected)
                return validate('MarketResult', result)
        collected = self.snapshot['collected_at']
        available=self.snapshot.get('available_at',collected)
        if timestamp(available) <= timestamp(issued_at):
            result.update(observation_period={'start': collected[:10], 'end': collected[:10]},
                          available_at=available, ingested_at=available,
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
        if entity_type == 'role' and source_id.startswith('dosm:jmi:published-role-label:'):
            observations=[copy.deepcopy(r) for r in self.published_roles['observations'] if r['entity_id']==source_id]
            return {'snapshot_sha256':self.published_version,'sources':[
                {'source_id':r['source_id'],'url':r['source_url'],'published_at':r['published_at'],
                 'available_at':r['available_at'],'sha256':r['source_document_sha256']} for r in observations],
                'supporting_ads':[],'published_observations':observations,
                'limitations':copy.deepcopy(self.published_roles['limitations'])}
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

    def published_role_observations(self, *, as_of):
        """Explicit source-label facts, separate from canonical employer counts."""
        return [copy.deepcopy(r) for r in self.published_roles['observations']
                if timestamp(r['available_at']) <= timestamp(as_of)]

    def current_context(self, *, as_of, occupation_system=None, occupation_version=None,
                        occupation_code=None, evidence_ids=None):
        """Targeted source facts, never coerced into the numeric MarketResult.

        MASCO codes are source-native. No title-only canonical join, inferred
        child membership, negative shortage status or numerical blend exists.
        This additive B interface is proposed to A for context integration.
        """
        import re
        timestamp(as_of)
        if occupation_code is None and not evidence_ids:
            raise ValueError('explicit_source_occupation_or_evidence_ids_required')
        if evidence_ids and len(evidence_ids)>20:
            raise ValueError('bounded_selected_evidence_query_required')
        if occupation_code is not None and (occupation_system!='MASCO' or occupation_version!='2020'
                or not re.fullmatch(r'\d{4}(?:-\d{2})?',occupation_code)):
            raise ValueError('explicit_MASCO_2020_code_required; canonical_mappings_are_not_inferred')
        records=[]
        if self.context_evidence:
            for r in self.context_evidence['records']:
                occupation=r.get('occupation',{})
                match=(occupation_code is not None and occupation.get('system')==occupation_system
                       and occupation.get('version')==occupation_version and occupation.get('code')==occupation_code)
                explicit_child=(occupation_code is not None and occupation.get('system')==occupation_system
                        and occupation.get('version')==occupation_version
                        and occupation_code in r.get('coverage',{}).get('explicit_six_digit_codes',[]))
                if (match or explicit_child or (evidence_ids and r['evidence_id'] in evidence_ids)) and timestamp(r['available_at'])<=timestamp(as_of):
                    selected=copy.deepcopy(r)
                    if explicit_child:
                        selected['query_scope']={'occupation_code':occupation_code,
                            'relationship':'explicitly_enumerated_six_digit_member',
                            'title_limit':'Publication nominated-job-title restriction retained; individual code-to-title pairing not invented',
                            'source_pdf_page':r['source']['six_digit_scope_pdf_page']}
                    records.append(selected)
        reason=None if records else ('six_digit_membership_not_verified' if occupation_code and '-' in occupation_code
                                    else 'no_matching_available_source_fact; non_listing_is_unknown_not_low_demand')
        return {'version':'current-public-market-evidence-v1','status':'available' if records else 'unknown',
                'issued_at':as_of,'source_snapshot_sha256':self.context_version,'records':records,
                'missing_reason':reason,'numeric_comparison_eligible':False,
                'usage':'Source-coded explanation facts only; shortage designations and broad published levels are not advertisement-count ranking inputs.'}

    def current_context_catalogue(self, *, as_of):
        """Discover codes/labels/types without a raw score/count leaderboard."""
        timestamp(as_of)
        return [{'evidence_id':r['evidence_id'],'entity_type':r['entity_type'],
                 'entity':copy.deepcopy(r.get('occupation') or r.get('sector')),
                 'measurement_type':r['measurement_type'],'observation_period':r['observation_period']}
                for r in (self.context_evidence or {}).get('records',[])
                if timestamp(r['available_at'])<=timestamp(as_of)]
