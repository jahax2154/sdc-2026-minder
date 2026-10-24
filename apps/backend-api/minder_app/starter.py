"""Provisional topical exploration from normal intake, never competence scoring."""
import collections
import copy
import json
import math
import re
from .store import AppError

POLICY = 'starter-exploration-v1'
OPERATIONS = (('POST', '/api/product/starter-recommendations'),)
STOP = set('a an and are as at be by can do for from have i in is it my no none not of on or the to unsure uncertain with yet experience provided studying working'.split())
FALLBACK = ['onet:15-1252.00', 'onet:13-2011.00', 'onet:29-1141.00', 'onet:17-2141.00', 'onet:27-1024.00']


def normal_intake(app, owner, changes):
    """Map an explicitly changed intake time to canonical pathway capacity."""
    if not isinstance(changes, dict) or not isinstance(changes.get('onboarding'), dict) or 'weekly_study_hours' not in changes['onboarding']:
        return changes
    try:
        previous = app.store.get(owner, 'profile', owner)
    except AppError as error:
        if error.status != 404:
            raise
        previous = {}
    hours = changes['onboarding']['weekly_study_hours']
    if hours is not None and (type(hours) not in (int, float) or not math.isfinite(hours) or not 0 <= hours <= 80):
        raise AppError('invalid_weekly_study_hours', 422)
    if previous and previous.get('onboarding', {}).get('weekly_study_hours') == hours:
        return changes  # An unrelated full-profile edit must not restore old time.
    result = copy.deepcopy(changes)
    constraints = [c for c in result.get('constraints', previous.get('constraints', [])) if c['scope'] != 'weekly_hours']
    if hours is not None:
        constraints.append(dict(constraint_id='onboarding-weekly-hours', scope='weekly_hours', hard=True,
            value=hours, unit='hours_per_week', evidence_id='explicit-onboarding-capacity'))
    result['constraints'] = constraints
    return result


def words(value):
    result = []
    for token in re.findall(r'[a-z][a-z0-9+#.]*', str(value).casefold()):
        if token not in STOP and len(token) > 1:
            result.append(token[:-1] if token.endswith('s') and len(token) > 4 else token)
    return result


def index(app):
    if hasattr(app, '_starter_index'):
        return app._starter_index
    reader = getattr(app.services, 'role_reference', None)
    ref = getattr(app.services.personal, 'ref', {})
    documents, frequency = {}, collections.Counter()
    for role in app.services.roles:
        if role.get('eligibility') != 'supported':
            continue
        native = reader(role['role_id']) if reader else {}
        title = words(role['label'])
        description = native.get('occupation', {}).get('Description', '')
        software = ' '.join(str(v) for row in native.get('software_examples', [])
                            for k, v in row.items() if k in ('Example', 'Commodity Title'))
        skills = ' '.join(ref.get('skill_rubrics', {}).get(e['subject_id'], {}).get('label', '')
                          for e in role.get('requirements', []) if e['unit'] == 'onet:LV')
        industries = ' '.join(ref.get('industries', {}).get(m['target_id'], '')
            for m in role.get('industry_mappings', []) if m['status'] in ('source_accepted', 'policy_accepted'))
        tokens = collections.Counter(title * 3 + words(description) + words(software) * 2 + words(skills) + words(industries))
        documents[role['role_id']] = (role, tokens)
        frequency.update(tokens.keys())
    app._starter_index = documents, frequency
    return app._starter_index


def eligible(profile, roles):
    kept = set(roles)
    unresolved = []
    for restriction in profile.get('constraints', []):
        if not restriction['hard'] or restriction['scope'] in ('weekly_hours', 'budget', 'planning_horizon'):
            continue
        if restriction['scope'] in ('role_allowlist', 'role_denylist'):
            try:
                identifiers = json.loads(restriction['value'])
                if restriction['unit'] != 'role_ids_json' or not isinstance(identifiers, list) or any(not isinstance(i, str) for i in identifiers):
                    raise ValueError()
            except (ValueError, TypeError):
                raise AppError('invalid_explicit_role_restriction', 422) from None
            kept = kept.intersection(identifiers) if restriction['scope'] == 'role_allowlist' else kept.difference(identifiers)
        else:
            unresolved.append(restriction['constraint_id'])
    return kept, unresolved


def recommend(app, owner, limit=5):
    if type(limit) is not int or not 1 <= limit <= 5:
        raise AppError('starter_limit_must_be_1_to_5', 422)
    profile = app.store.get(owner, 'profile', owner)
    data, frequency = index(app)
    allowed, unresolved = eligible(profile, data)
    metadata, context = profile.get('onboarding', {}), profile.get('career_context', {})
    query = collections.Counter()
    inputs = [(metadata.get('context', ''), 2), (context.get('education', ''), 2),
              (' '.join(metadata.get('interests', []) + metadata.get('work_areas', [])), 3),
              (' '.join(metadata.get('self_reported_skills', [])), 2),
              (metadata.get('experience_summary', '') + ' ' + context.get('experience', ''), 1),
              (metadata.get('optional_enrichment', ''), 1), (context.get('goals', ''), 2)]
    for text, weight in inputs:
        for token in set(words(text)):
            query[token] += weight
    for evidence in profile.get('evidence', []):
        if evidence.get('unit') == 'self_report_text':
            for token in set(words(evidence['subject_id'])):
                query[token] += 1
    preferences = {(p['entity_type'], p['entity_id']): p['state'] for p in profile.get('preferences', [])}
    scores, matched, positive, negative = {}, {}, set(), set()
    for rid in allowed:
        role, document = data[rid]
        matched[rid] = sorted(set(query).intersection(document), key=lambda t: (-query[t], t))
        scores[rid] = sum(query[t] * math.log(1 + len(data) / (1 + frequency[t])) * min(document[t], 3)
                          for t in matched[rid])
        own = preferences.get(('role', rid))
        industry = [preferences.get(('industry', m['target_id'])) for m in role.get('industry_mappings', [])
                    if m['status'] in ('source_accepted', 'policy_accepted')]
        if own == 'interested' or 'interested' in industry:
            positive.add(rid)
        if own == 'not_interested' or (industry and all(v == 'not_interested' for v in industry)):
            negative.add(rid)
    fallback = {rid: i for i, rid in enumerate(FALLBACK)}
    ordered = sorted(allowed, key=lambda rid: (rid in negative, rid not in positive, -scores[rid], fallback.get(rid, 99), data[rid][0]['label']))
    # Market quantities only reorder slots belonging to the same measurement,
    # population, vintage and period. Missing evidence never receives zero demand.
    pool = [rid for rid in ordered[:24] if rid not in negative]
    markets, cohorts = {}, collections.defaultdict(list)
    personal = app.services.personal
    for slot, rid in enumerate(pool):
        try:
            records = personal.evidence_for(data[rid][0])['records'] if hasattr(personal, 'evidence_for') else []
        except (OSError, ValueError, AppError):
            records = []
        markets[rid] = records
        comparable = next((r for r in records if r['status'] == 'available' and
            r['ranking_eligibility'] in ('employer_comparable', 'published_comparable')
            and type(r['value']) in (int, float)), None)
        if comparable:
            key = json.dumps({k: comparable[k] for k in
                ('measurement_type', 'source_universe_id', 'cohort_version', 'observation_period', 'unit')}, sort_keys=True)
            # Preferences retain priority; negative roles stay in catalogue exploration.
            cohorts[(rid in positive, key)].append((slot, rid, comparable['value']))
    market_reordered = set()
    for items in cohorts.values():
        if len(items) < 2:
            continue
        for slot, replacement in zip(sorted(i[0] for i in items), sorted(items, key=lambda i: (-i[2], data[i[1]][0]['label']))):
            pool[slot] = replacement[1]
            market_reordered.add(replacement[1])
    from .role_display import presentation
    options = []
    for rid in ([] if unresolved else pool[:limit]):
        role = data[rid][0]
        topics = matched[rid][:6]
        reason = ('Your reported field, interests or experience share these source topics: ' + ', '.join(topics) + '.'
                  if topics else 'A broad starting point while you explore what interests you.')
        if rid in positive:
            reason += ' Your explicit interest also influences this suggestion.'
        if rid in market_reordered:
            reason += ' Comparable source activity influences its position within the same evidence group.'
        options.append(dict(role_id=rid, label=role['label'], explanation=reason,
            matched_topics=topics, sources=[copy.deepcopy(role['source'])],
            requirements=presentation(app, owner, role), market_evidence=markets[rid],
            market_evidence_status='available' if any(r['status'] == 'available' for r in markets[rid]) else 'unavailable',
            market_comparison_supported=rid in market_reordered,
            personal_assessment=None, status='provisional'))
    return dict(policy_version=POLICY, mode='starter', status='restriction_review_required' if unresolved else 'provisional',
        profile_version=profile['version'], options=options, personal_assessment=None,
        coverage=dict(supported_considered=len(data), after_explicit_restrictions=len(allowed),
            returned=len(options), assessed_personal_scores=0,
            returned_with_supported_market_comparison=sum(o['market_comparison_supported'] for o in options)),
        unresolved_constraint_ids=unresolved, deprioritized_role_ids=sorted(negative),
        further_exploration=dict(path='/api/roles', catalogue_order_not_rank=True),
        planning_input=dict(weekly_study_hours=next((c['value'] for c in profile['constraints'] if c['scope'] == 'weekly_hours'), None),
            experience_state=metadata.get('experience_state', 'uncertain')),
        limitations=['Provisional topic-based exploration, not numerical fit, proficiency or a hiring prediction.',
            'Self-reported skills are interests/background signals, never demonstrated competence.',
            'No CV or anchored competency assessment is required. Assessed matching remains separate.',
            'Different market populations are not pooled; missing evidence is neither zero demand nor proven opportunity.',
            'Study time belongs to pathway feasibility; no next-quarter forecast is inferred.'])


def dispatch(app, owner, method, path, body):
    if (method, path) not in OPERATIONS or not isinstance(body, dict) or set(body) - {'limit'}:
        raise AppError('invalid_starter_request', 422)
    return recommend(app, owner, body.get('limit', 5))
