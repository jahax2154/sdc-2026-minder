"""A-owned typed applicability and recommendation trace over committed B sources.

Personal evidence-fit stays unchanged. Unlike quantities never pool. Semantic
links are scoped engineering proxies, never a certified whole-taxonomy crosswalk.
"""
import copy
from datetime import datetime, timezone
import hashlib
import json
import math

from .policy import ROOT, fingerprint
from .service_contracts import validate

PREVIOUS_POLICY = 'personal-current-evidence-v2'
POLICY_ID = 'personal-current-evidence-v2.1'
CONFIGS = {PREVIOUS_POLICY: ROOT / 'ml/configs/intelligence/personal-current-evidence.v2.json',
           POLICY_ID: ROOT / 'ml/configs/intelligence/personal-current-evidence.v2_1.json'}
KINDS = ('employer_observation','published_offering_activity','occupation_shortage','sector_context')


def load_policy(policy_version=POLICY_ID):
    if policy_version not in CONFIGS:
        raise ValueError('unknown typed market policy')
    config = json.loads(CONFIGS[policy_version].read_text())
    path = (ROOT / config['links_path']).resolve()
    if (config['policy_id'] != policy_version or not config['active']
            or not path.is_relative_to(ROOT.resolve())
            or hashlib.sha256(path.read_bytes()).hexdigest() != config['links_sha256']):
        raise ValueError('typed market policy/mapping checksum incompatible')
    return config, json.loads(path.read_text())


def _source(sid, version, sha, uri, available):
    return dict(source_id=sid,version=version,sha256=sha,uri=uri,geography='MY',
                available_at=available,evidence_type='source-derived')


def _stamp(value):
    return value if 'T' in value else value + 'T00:00:00+00:00'


def _time(value):
    return datetime.fromisoformat(_stamp(value).replace('Z','+00:00'))


def _activity_key(row):
    return fingerprint({k:row[k] for k in ('measurement_type','source_universe_id','cohort_version','observation_period','unit')})


def _choose_comparable_activity(candidates, minimum):
    """Maximize covered roles, then prefer published activity among valid groups.

    The current source registry has one cohort per activity family. This avoids
    stranding a real employer comparison behind a singleton published category.
    Multiple future cohorts conservatively retain explicit primary selection.
    """
    published={rid:next((r for r in rows if r['ranking_eligibility']=='published_comparable'),None) for rid,rows in candidates.items()}
    employer={rid:next((r for r in rows if r['ranking_eligibility']=='employer_comparable'),None) for rid,rows in candidates.items()}
    published={k:v for k,v in published.items() if v is not None};employer={k:v for k,v in employer.items() if v is not None}
    if len({_activity_key(r) for r in published.values()})>1 or len({_activity_key(r) for r in employer.values()})>1:
        return {rid:(published.get(rid) or employer[rid]) for rid in set(published)|set(employer)}
    alternatives=[]
    if len(published)>=minimum:alternatives.append(published)
    if len(employer)>=minimum:alternatives.append(employer)
    both=set(published)&set(employer);only_p=set(published)-both;only_e=set(employer)-both
    needed=max(0,minimum-len(only_e))
    if len(only_p)+len(both)-needed>=minimum and len(only_e)+len(both)>=minimum:
        move=set(sorted(both)[:needed])
        alternatives.append({**{rid:published[rid] for rid in only_p|(both-move)},
                             **{rid:employer[rid] for rid in only_e|move}})
    return max(alternatives,key=lambda a:(len(a),sum(r['measurement_type']=='published_offering_activity' for r in a.values())),default={})


def public_trace(trace):
    """Per-user explanation references, excluding internal market arithmetic."""
    validate('RecommendationTrace', trace)
    return {key:copy.deepcopy(trace[key]) for key in ('trace_id','role_id','policy_version',
        'personal_score','score_status','personal_evidence_coverage','evidence_ids',
        'rank','ranking_group','ranking_basis','current_measurement','unknowns')}


def render_source_passage(record):
    """Closed template over typed source records, never arbitrary model prose."""
    validate('MarketEvidence',record)
    kind=record['measurement_type'].replace('_',' ')
    if record['status']=='unavailable':
        return f"{kind.capitalize()} for {record['role_id']} is unavailable or unmapped; unknown is not zero demand or a proven opportunity."
    period=record['observation_period']
    period_label=period.get('label') or f"{period['start']} to {period['end']}"
    published=record['published_at'] or 'not verified'
    quantity=('a listed related source-group designation, not an ad count'
              if record['measurement_type']=='occupation_shortage' else f"{record['value']} {record['unit']}")
    return (f"{kind.capitalize()}: {quantity} for source entity {record['source_entity_id']}, "
        f"period/edition {period_label}. Publication date {published}; available {record['available_at']}. "
        f"Applicability to {record['role_id']}: {record['mapping']['scope']} " + ' '.join(record['limitations']))


def make_source_passage(record, policy_id=POLICY_ID):
    text=render_source_passage(record)
    result=dict(schema_version='minder-evidence-passage-v1',evidence_policy_id=policy_id,
        derivation_method='typed-source-record-recomputation-v1',evidence_id=record['evidence_id'],
        record=copy.deepcopy(record),canonical_passage=text,
        passage_sha256=hashlib.sha256(text.encode()).hexdigest(),
        source_record_refs=copy.deepcopy(record.get('source_record_refs',[])))
    validate('EvidencePassage',result)
    return result


def evidence_statements(result, selected_role_ids=None):
    """Bounded public-source facts for C grounding; no raw personal evidence text.

    IDs are backend-generated, stable record references. C retains its mandatory
    policy/rank/coverage facts and only selects explanations, never calculations.
    """
    public=result['public']
    selected=set(selected_role_ids or [])
    if selected_role_ids is None:
        for group in public.get('ranking_groups',[]):
            selected.update(group['role_ids'][:1])
    rows=[r for r in result['internal'].get('evidence_records',[]) if r['role_id'] in selected]
    statements=[]
    for rid in sorted(selected):
        for kind in KINDS:
            matching=[r for r in rows if r['role_id']==rid and r['measurement_type']==kind]
            # At most one fact per role/type. Additional sector rows stay in the
            # per-role evidence interface rather than expanding provider context.
            available=[r for r in matching if r['status']=='available']
            row=(available or matching or [None])[0]
            if row is None:
                continue
            validate('MarketEvidence',row)
            if row['status']=='available':
                period=row['observation_period']
                period_label=period.get('label') or f"{period['start']} to {period['end']}"
                quantity='positive related-group designation' if kind=='occupation_shortage' else f"{row['value']} {row['unit']}"
                text=(f"{rid}: {kind.replace('_',' ')} — {quantity} for "
                      f"{row['source_entity_id']} during {period_label}. Mapping scope: {row['mapping']['scope']} "
                      + ' '.join(row['limitations']))
            else:
                text=f"{rid}: {kind.replace('_',' ')} unavailable; unknown, never an inferred zero."
            statements.append(dict(id='evidence-fact:'+row['evidence_id'].split(':',1)[1],text=text,
                sources=[row['source']] if row['source'] and row['status']=='available' else [],
                kind='market_evidence',measurement_type=kind,status=row['status'],
                period=row['observation_period'],evidence_id=row['evidence_id'],
                mapping_version=row['mapping']['version'],ranking_eligibility=row['ranking_eligibility']))
    return statements


class EvidenceContext:
    def __init__(self, market, *, policy_version=POLICY_ID):
        self.market = market
        self.policy, self.links = load_policy(policy_version)
        self.version = self.links['version']
        self._broad_cache = {}
        self._shortage_cache = {}
        manifest=json.loads((ROOT/'ml/minder_ml_starter/sources_manifest.json').read_text())
        self.source_metadata={r['id']:r for r in manifest['sources']}

    def verify_passage(self, payload, role, *, checked_at=None):
        """Recompute from B's pinned records and A links; a hash/ID alone cannot prove a claim."""
        validate('EvidencePassage',payload)
        if payload['evidence_policy_id']!=self.policy['policy_id'] or payload['record']['role_id']!=role['role_id']:
            raise ValueError('passage policy or role mismatch')
        stamp=payload['record']['as_of']
        if _time(stamp)>_time(checked_at or datetime.now(timezone.utc).isoformat()):
            raise ValueError('passage issue time is in the future')
        record=payload['record']
        if record['status']=='available' and self.market is not None:
            kind=record['measurement_type']
            if kind in ('employer_observation','sector_context'):
                snapshot=self.market.snapshot
                digest=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()
                if snapshot.get('synthetic') is not False or digest!=self.market.version:
                    raise ValueError('source snapshot integrity mismatch')
            if kind=='employer_observation':
                facts=self.market.source_facts('role',role['role_id']);rows=facts['supporting_ads']
                native=self.market.aliases.get('role',{}).get(role['role_id'],role['role_id'])
                ids=[r['ad_id'] for r in rows]
                if (len(ids)!=len(set(ids)) or record['value']!=len(ids)
                        or any(r['country'].lower()!='my' or native not in r['role_ids'] for r in rows)):
                    raise ValueError('employer count not supported by actual unique source rows')
            for supported_kind,filename,attribute,digest_attribute in (
                    ('published_offering_activity','published-role-observations.v1.json','published_roles','published_version'),
                    ('occupation_shortage','current-public-evidence.v1.json','context_evidence','context_version')):
                if kind==supported_kind:
                    path=ROOT/'ml/data/market'/filename;raw=path.read_bytes()
                    if (hashlib.sha256(raw).hexdigest()!=getattr(self.market,digest_attribute,None)
                            or json.loads(raw)!=getattr(self.market,attribute,None)):
                        raise ValueError('source record artifact integrity mismatch')
        current=None
        if self.market is not None:
            current=self.market.current('role',role['role_id'],as_of=stamp)
            validate('MarketResult',current)
        for row in self.records(role,stamp,current):
            expected=make_source_passage(row,self.policy['policy_id'])
            if expected['evidence_id']==payload['evidence_id']:
                if expected!=payload:
                    raise ValueError('passage or derivation differs from actual source record')
                return copy.deepcopy(expected)
        raise ValueError('no current committed source record supports this passage')

    def _record(self, role, kind, stamp, *, source_entity=None, status='unavailable',value=None,
                unit='unknown', universe='unavailable', cohort='unavailable', period=None,
                source=None, published=None, available=None, relation='unmapped', scope='No supported source applicability link.',
                eligibility='unsupported', reasons=None, limitations=None, record_refs=None, source_value=None, bridge=None,
                source_scope=None):
        period = period or dict(start=stamp[:10],end=stamp[:10])
        mapping = dict(mapping_id='link:' + fingerprint([role['role_id'],kind,source_entity,relation])[:20],
                       version=self.version,relation=relation,scope=scope)
        if bridge:
            mapping['bridge']=copy.deepcopy(bridge)
        row = dict(role_id=role['role_id'],measurement_type=kind,source_entity_id=source_entity,
            status=status,value=value,unit=unit,geography='MY',source_universe_id=universe,cohort_version=cohort,
            observation_period=period,published_at=published,available_at=available,source=source,mapping=mapping,
            ranking_eligibility=eligibility,missing_reasons=reasons or ([] if status=='available' else ['no_supported_source_record_or_mapping']),
            limitations=limitations or [],as_of=stamp,source_record_refs=record_refs or [],
            source_value=value if source_value is None else source_value)
        if source_scope:
            row['source_scope']=copy.deepcopy(source_scope)
        row['evidence_id'] = 'market-evidence:' + fingerprint({k:v for k,v in row.items() if k!='as_of'})
        validate('MarketEvidence', row)
        return row

    def records(self, role, stamp, current=None):
        records = []
        m = self.market
        if current and current['status']=='available':
            src = _source('bosch-smartrecruiters-my',current['cohort_version'],current['cohort_version'],
                'https://www.bosch.com.my/careers/',current['available_at'])
            records.append(self._record(role,'employer_observation',stamp,source_entity=role['role_id'],
                status='available',value=current['value'],unit=current['unit'],universe=current['source_universe_id'],
                cohort=current['cohort_version'],period=current['observation_period'],published=current['published_at'],
                available=current['available_at'],source=src,relation='native_identity',
                scope='Exact native O*NET identity accepted by B title mapping; inspected employer feed only.',
                eligibility='employer_comparable',limitations=[current['explanation']],
                record_refs=['derived-snapshot:'+current['cohort_version']]+['ad:'+r['ad_id'] for r in m.source_facts('role',role['role_id'])['supporting_ads']]
                    if m is not None and hasattr(m,'source_facts') else []))
        for link in self.links['published_roles']:
            if link['role_id']!=role['role_id'] or m is None:
                continue
            rows=[r for r in getattr(m,'published_roles',{}).get('observations',[])
                  if r['entity_id']==link['source_entity_id'] and _time(r['available_at'])<=_time(stamp)]
            if not rows:
                continue
            row=max(rows,key=lambda r:(r['period']['end'],r['published_at']))
            if (row.get('geography')!='MY' or row.get('measurement')!='published_online_job_offerings_for_source_role_label'
                    or row.get('unit')!='published job offerings'):
                continue
            latest=max((r['period']['end'] for r in getattr(m,'published_roles',{}).get('observations',[])
                        if _time(r['available_at'])<=_time(stamp)),default=None)
            src=_source(row['source_id'],getattr(m,'published_version','source-version-unavailable'),
                        row['source_document_sha256'],row['source_url'],row['available_at'])
            records.append(self._record(role,'published_offering_activity',stamp,
                source_entity=row['entity_id'],status='available',value=row['value'],unit='published job offerings',
                universe='dosm-jmi-published-top-occupation-labels',cohort=m.published_version,period=row['period'],
                source=src,published=row['published_at'],available=row['available_at'],relation=link['relation'],
                scope=link['scope'],eligibility='published_comparable' if link['ranking'] and row['period']['end']==latest else 'context_only',
                limitations=['Source-category offering activity, not dedup-verified unique ads, vacancies or verified hiring.',
                             'Latest comparable source period required; older categories remain dated context.'],
                record_refs=[row['source_id']+':'+row['entity_id']+':'+row['period']['end']]))
        # New source families are consumed only through an explicit committed B interface.
        if m is not None and hasattr(m,'shortage_observations'):
            if stamp not in self._shortage_cache:
                self._shortage_cache[stamp]=m.shortage_observations(as_of=stamp)
            rows=self._shortage_cache[stamp]
            for link in self.links['shortage_roles']:
                if link['role_id']!=role['role_id']:
                    continue
                eligible=[r for r in rows if r['entity_id']==link['source_entity_id'] and r['value']==1]
                if not eligible:
                    continue
                row=max(eligible,key=lambda r:r['published_at'])
                src=_source(row['source_id'],row['source_version'],row['source_document_sha256'],row['source_url'],row['available_at'])
                records.append(self._record(role,'occupation_shortage',stamp,source_entity=row['entity_id'],
                    status='available',value=1,unit='positive shortage designation',universe=row['source_universe_id'],
                    cohort=row['source_version'],period=row['period'],source=src,published=row['published_at'],
                    available=row['available_at'],relation=link['relation'],scope=link['scope'],
                    eligibility='shortage_adjustment',limitations=['Dated official designation; not ad frequency, competence or entry-level hiring probability.']))
        if m is not None and hasattr(m,'current_context'):
            for link in self.links['shortage_roles']:
                if link['role_id']!=role['role_id'] or 'occupation_code' not in link:
                    continue
                key=(stamp,link['occupation_code'])
                if key not in self._shortage_cache:
                    self._shortage_cache[key]=m.current_context(as_of=stamp,occupation_system='MASCO',
                        occupation_version='2020',occupation_code=link['occupation_code'])
                envelope=self._shortage_cache[key]
                for row in envelope['records']:
                    if (row['evidence_id']!=link['source_entity_id'] or row['value']!='listed_in_national_MyCOL'
                            or row['geography']['country_code']!='MY'):
                        continue
                    src=_source(row['source']['source_id'],row['record_version']+':'+envelope['source_snapshot_sha256'],
                        row['source']['sha256'],row['source']['url'],row['available_at'])
                    refs=[row['evidence_id'],'pdf-page:'+str(row['source']['pdf_page']),
                          'crosswalk-row:'+str(link['bridge']['data_row_index'])]
                    records.append(self._record(role,'occupation_shortage',stamp,source_entity=row['evidence_id'],
                        status='available',value=1,source_value=row['value'],unit=row['unit'],
                        universe='talentcorp-mycol-2024-2025-national-groups',cohort=envelope['source_snapshot_sha256'],
                        period=row['observation_period'],source=src,published=row['published_at'],available=row['available_at'],
                        relation=link['relation'],scope=link['scope'],eligibility='shortage_context_adjustment',
                        limitations=['Related source group designation only; not proof the entire O*NET role or every six-digit child is critical.',
                            'Edition scope is not an October 2026 measurement; publication and continuous fieldwork dates unverified.',
                            'Positive designation indicator is not an ad count, hiring probability or personal competence.'],
                        record_refs=refs,bridge=link['bridge'],source_scope=dict(
                            occupation_system=row['occupation']['system'],occupation_version=row['occupation']['version'],
                            occupation_code=row['occupation']['code'],occupation_level=row['occupation']['level'],
                            applies_to_all_children=row['coverage']['applies_to_all_six_digit_children'],
                            explicit_six_digit_codes=row['coverage'].get('explicit_six_digit_codes',[]),
                            six_digit_scope_pdf_page=row['source'].get('six_digit_scope_pdf_page'),
                            nominated_title_limit='Only source nominated job titles; no individual code-to-title pairing or unlisted-child inference.')))
        if m is not None and hasattr(m,'broad_observations'):
            sectors={s for link in role['industry_mappings'] if link['status'] in ('source_accepted','policy_accepted')
                     for s in self.links['industry_to_sector'].get(link['target_id'],[])}
            if stamp not in self._broad_cache:
                latest={}
                for r in m.broad_observations(as_of=stamp):
                    label=r['industry_label']
                    if r['dimension_scope']=='industry' and r['group_kind']=='category' and (
                            label not in latest or r['period_end']>latest[label]['period_end']):
                        latest[label]=r
                self._broad_cache[stamp]=latest
            rows=self._broad_cache[stamp]
            for label in sorted(sectors):
                row=rows.get(label)
                if row is None:
                    continue
                available=max((_stamp(row['available_at']),row['retrieved_at']),key=_time)
                if _time(available)>_time(stamp):
                    continue
                metadata=self.source_metadata.get(row['source_id'],{})
                uri=row.get('source_url') or metadata.get('resolved_url') or metadata.get('url')
                if not uri:
                    continue
                src=_source(row['source_id'],row['source_version'],row['source_version'],
                    uri,available)
                known=row['value'] is not None
                records.append(self._record(role,'sector_context',stamp,source_entity='dosm:sector:'+label,
                    status='available' if known else 'unavailable',value=row['value'],unit='published sector job offerings',
                    universe='dosm-jmi-economic-activity-marginals',cohort=row['source_version'],
                    period=dict(start=row['period_start'],end=row['period_end']),source=src,
                    published=_stamp(row['published_at']),available=available,relation='industry_related_context',
                    scope=self.links['industry_scope'],eligibility='context_only',
                    limitations=['Broad section context via US industry relationship; no narrow-role allocation or ranking contribution.'],
                    record_refs=[row['observation_id'],row['source_record']['sheet']+':'+row['source_record']['cell']]))
        present={r['measurement_type'] for r in records}
        for kind in KINDS:
            if kind not in present:
                records.append(self._record(role,kind,stamp,reasons=[
                    ('no_accepted_code_bridge_to_acquired_shortage_designation' if m is not None and hasattr(m,'current_context')
                     else 'source_family_not_acquired_or_committed') if kind=='occupation_shortage'
                    else 'no_supported_applicability_or_available_source_record']))
        return records

    def apply(self, result, roles, stamp):
        """Replace ordering only; leave personal assessments and external facts intact."""
        result=copy.deepcopy(result)
        public,internal=result['public'],result['internal']
        options={o['role_id']:o for o in public['options']}
        native={r['entity_id']:r for r in internal['current_market']}
        all_records=[];by_id={};scores={};chosen={};shortage={};activity_candidates={}
        published_rows=[r for r in getattr(self.market,'published_roles',{}).get('observations',[])
                        if _time(r['available_at'])<=_time(stamp)]
        latest_period=max((r['period']['end'] for r in published_rows),default=None)
        for role in roles:
            rid=role['role_id']
            if rid not in options:
                continue
            rows=self.records(role,stamp,native.get(rid));all_records.extend(rows);by_id[rid]=rows
            o=options[rid]
            o.update(rank=None,ranking_group=None,ranking_basis='unassessed',
                evidence_refs=[r['evidence_id'] for r in rows if r['status']=='available'])
            shortage[rid]=max((self.policy['shortage_points'] if r['ranking_eligibility']=='shortage_adjustment'
                              else self.policy.get('shortage_context_points',0)
                              for r in rows if r['status']=='available' and r['ranking_eligibility'] in
                              ('shortage_adjustment','shortage_context_adjustment')),default=0)
            if o['personal_score'] is None:
                continue
            scores[rid]=o['personal_score']+shortage[rid]
            eligible=[r for r in rows if r['status']=='available' and r['ranking_eligibility']=='published_comparable'
                      and r['observation_period']['end']==latest_period]
            employer=[r for r in rows if r['status']=='available' and r['ranking_eligibility']=='employer_comparable']
            activity_candidates[rid]=eligible+employer
            if eligible:
                chosen[rid]=eligible[0]
            else:
                if employer:
                    chosen[rid]=employer[0]
        if self.policy['policy_id']==POLICY_ID:
            chosen=_choose_comparable_activity(activity_candidates,self.policy['minimum_personally_assessed_per_comparison_group'])
        cohorts={}
        for rid,row in chosen.items():
            key=_activity_key(row)
            cohorts.setdefault(key,[]).append((rid,row))
        groups=[];trace_values={};combined=[]
        for key,rows in sorted(cohorts.items()):
            if len(rows)<self.policy['minimum_personally_assessed_per_comparison_group']:
                continue
            kind=rows[0][1]['measurement_type'];is_published=kind=='published_offering_activity'
            if is_published:
                period=rows[0][1]['observation_period']
                denominator=max((r['value'] for r in published_rows if r['period']==period),default=0)
                basis='personal_and_published_offerings';normalization='log_count_over_latest_source_category_max'
                label='Published occupation-category comparison'
            else:
                denominator=(getattr(self.market,'snapshot',{}) or {}).get('collection',{}).get('accepted_ads',0)
                basis='personal_and_comparable_current';normalization='log_count_over_inspected_employer_sample'
                label='Inspected employer-feed comparison'
            if not denominator or any(not 0<=r['value']<=denominator for _,r in rows):
                continue
            gid=kind+':'+key[:16];ranked={}
            for rid,row in rows:
                idx=100*math.log1p(row['value'])/math.log1p(denominator)
                points=self.policy['current_fraction']*idx
                score=min(100,self.policy['personal_fraction']*options[rid]['personal_score']+points+shortage[rid])
                ranked[rid]=score;combined.append(dict(role_id=rid,score=score))
                options[rid].update(ranking_group=gid,ranking_basis=basis)
                trace_values[rid]=dict(current_measurement=kind,normalization=normalization,
                    normalization_denominator=denominator,current_index=idx,current_points=points)
            order=sorted(ranked,key=lambda rid:(-ranked[rid],-options[rid]['personal_score'],rid))
            for rank,rid in enumerate(order,1):options[rid]['rank']=rank
            groups.append(dict(group_id=gid,basis=basis,label=label,role_ids=order,
                limitation=('Within the same latest DOSM source-category period only; scoped occupation-label proxies, not an exact national crosswalk.'
                            if is_published else 'Within this inspected employer feed only; not national demand.')+
                           ' No comparison to ranks in other groups.'))
        fallback=sorted((rid for rid in scores if options[rid]['rank'] is None),key=lambda rid:(-scores[rid],-options[rid]['personal_score'],rid))
        if fallback:
            has_shortage=any(shortage[rid] for rid in fallback)
            basis='personal_with_shortage_context' if has_shortage else 'personal_only_market_unsupported'
            for rank,rid in enumerate(fallback,1):
                options[rid].update(rank=rank,ranking_group='exploration',ranking_basis=(
                    'personal_with_shortage_context' if shortage[rid] else 'personal_only_market_unsupported'))
            groups.append(dict(group_id='exploration',basis=basis,label='Exploration without comparable role-level activity',role_ids=fallback,
                limitation='Personal evidence fit with at most a dated shortage adjustment when supported. Missing activity/shortage evidence is unknown. This fallback is not full market comparison.'))
        # The display order of groups has no cross-group rank semantics.
        groups.sort(key=lambda g:({'personal_and_published_offerings':0,'personal_and_comparable_current':1}.get(g['basis'],2),g['group_id']))
        ordered=[rid for g in groups for rid in g['role_ids']]
        ordered+=sorted(rid for rid in options if rid not in scores)
        traces=[]
        for rid,o in options.items():
            values=trace_values.get(rid,dict(current_measurement=None,normalization=None,
                normalization_denominator=None,current_index=None,current_points=None))
            t=dict(role_id=rid,policy_version=self.policy['policy_id'],personal_score=o['personal_score'],score_status=o['score_status'],
                personal_evidence_coverage=o['evidence_coverage'],evidence_ids=o['evidence_refs'],rank=o['rank'],
                ranking_group=o['ranking_group'],ranking_basis=o['ranking_basis'],**values,
                shortage_points=shortage[rid] if rid in scores else 0,
                final_internal_score=next((r['score'] for r in combined if r['role_id']==rid),min(100,scores[rid]) if rid in scores else None),
                unknowns=[] if rid in trace_values else (['personal_assessment_unavailable'] if o['personal_score'] is None
                    else ['no_comparable_selected_measurement_for_this_view']))
            t['trace_id']='recommendation-trace:'+fingerprint([public['profile_version'],rid,self.policy['policy_id'],self.policy['links_sha256'],t])
            o['trace_id']=t['trace_id'];traces.append(t)
        c=public['coverage']
        c.update(employer_comparable_ranked=sum(o['ranking_basis']=='personal_and_comparable_current' for o in options.values()),
            published_offering_comparable_ranked=sum(o['ranking_basis']=='personal_and_published_offerings' for o in options.values()),
            published_offering_supported=sum(any(r['measurement_type']=='published_offering_activity' and r['status']=='available' for r in rows) for rows in by_id.values()),
            shortage_supported=sum(any(r['measurement_type']=='occupation_shortage' and r['status']=='available' for r in rows) for rows in by_id.values()),
            shortage_adjusted_ranked=sum(bool(shortage[rid]) for rid in scores),
            shortage_context_supported=sum(any(r['status']=='available' and r['ranking_eligibility']=='shortage_context_adjustment' for r in rows) for rows in by_id.values()),
            shortage_exact_role_supported=sum(any(r['status']=='available' and r['ranking_eligibility']=='shortage_adjustment' for r in rows) for rows in by_id.values()),
            sector_context_supported=sum(any(r['measurement_type']=='sector_context' and r['status']=='available' for r in rows) for rows in by_id.values()),
            personal_only_ranked=sum(not shortage[rid] for rid in fallback))
        c['current_comparable_ranked']=c['employer_comparable_ranked']+c['published_offering_comparable_ranked']
        complete=bool(options) and c['current_comparable_ranked']==len(options) and len(groups)==1
        public.update(market_period_policy_key=self.policy['policy_id'],options=[options[rid] for rid in ordered],ranking_groups=groups,
            overall_ranking_complete=complete,status='available' if complete else 'partial')
        public['limitations'] = ['Provisional partial essential-skill evidence fit; not validated career accuracy or hiring probability.',
            'Groups have independent ranks; display group order does not compare opportunities across coverage.',
            'Different measurements retain their source units and mapping scope; neither broad totals nor shortage flags become ad counts.',
            'Published category activity has declared priority over a narrow employer sample where supported; classifications use declared engineering applicability links.',
            'Current assessment and next-quarter forecasts remain separate; unavailable forecasts do not block supported current activity.']
        if c['shortage_context_supported']:
            public['limitations'].append('Related shortage-group context is not an exact whole-role critical designation; nominated-job-title and six-digit restrictions remain.')
        if not complete:
            public['limitations'].append('Partial market/evidence coverage: personal-only or shortage-context fallback is not full comparable-market completion.')
        internal.update(combined_score_policy_version=self.policy['policy_id'],combined_scores=combined,market_comparison=[],
                        evidence_records=all_records,recommendation_traces=traces)
        validate('Recommendation',result)
        return result
