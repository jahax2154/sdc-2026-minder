"""Verified app guidance and pinned role quotations; never model factual prose."""
import re
import json
from pathlib import Path
from urllib.parse import urlsplit
from minder_ml.intelligence.service_contracts import validate
from .store import AppError

POLICY_ID = json.loads((Path(__file__).resolve().parents[1] / 'data/conversation-policy.v1.json').read_text())['policy_id']


def intent_for(message, previous=None, *, named_role=False):
    previous = previous or {}
    text = message.casefold().strip()
    if re.search(r'\b(market|demand|malaysia|forecast|quarter|salary|qualification|requirements|shortage|hiring|evidence|score|recommend|rank|fit|compare|preparation|pathway|plans?|roadmap|progress|tasks?|skills|change|edit|complete|reschedule)\b', text):
        return 'grounded_evidence'
    if re.search(r'how.*(can|could).*(you|u).*help|what.*(can|could).*(you|u).*(help|assist)',text):
        return 'capabilities'
    if (named_role or re.search(r'\b(roles?|developers?|engineers?|accountants?|occupations?)\b', text)) and re.search(r'\b(explain|does|do|what|about|describe)\b', text):
        return 'role_reference'
    if re.search(r'\b(pdf|documents?|upload|resume|cv)\b', text):
        return 'documents'
    if re.search(r'\b(help|capabilities|features|assist)\b|what.*(can|could).*(you|u)|what.*(you|u).*do|who (are|r) (you|u)|introduce yourself', text):
        return 'capabilities'
    if re.fullmatch(r'(hi|hello|hey|good morning|good evening)[!., ]*(minder)?[!., ]*', text):
        return 'greeting'
    if re.search(r'fresh graduate|new graduate|career switch|where.*start|how.*(start|begin)|what.*next|i.*unsure|not sure|i.*(student|graduate|career switch)', text):
        return 'onboarding'
    if previous.get('question_id') in ('project','project_detail'):
        return 'followup'
    if previous and re.search(r'^(and|why|how|what|tell me|can you|yes|no|that|more)', text):
        return 'followup'
    return 'grounded_evidence'


def selections(services, roles, skills):
    for values, allowed in ((roles, {r['role_id'] for r in services.roles}),
                            (skills, services.skill_entity_ids)):
        if values is not None and (not isinstance(values, list) or len(values) > 3 or
                any(not isinstance(v, str) or v not in allowed for v in values) or len(set(values)) != len(values)):
            raise AppError('invalid_selected_context')


def matched_roles(services, message):
    words = {w.rstrip('s') for w in re.findall(r'[a-z]+', message.casefold())}
    found = []
    for role in services.roles:
        parts = {w.rstrip('s') for w in re.findall(r'[a-z]+', role['label'].casefold())}
        if len(parts) >= 2 and parts.issubset(words):
            found.append(role['role_id'])
    return found if len(found) == 1 else []


def guidance(app, profile, intent, previous):
    from .product_routes import module_for
    state = module_for('product_state')
    operations = getattr(state, 'OPERATIONS', ())
    tasks = ('POST', '/api/product/tasks') in operations
    capabilities = ['save a partial profile using your own experience and evidence']
    if app is not None and app.services.personal is not None and app.services.roles:
        capabilities.append('explore career roles and compare supported evidence')
    if tasks:
        capabilities.append('review a plan, tasks and recorded progress')
    capabilities.append('review proposed changes before approving them')
    question = 'Are you exploring your first career, changing careers, or considering a particular role?'
    question_id = 'direction'
    if intent == 'documents':
        library = getattr(app, 'document_library', None)
        enabled = bool(library is not None and library.storage is not None)
        answer = ('Private PDF/TXT storage is configured here.' if enabled else 'Private document storage is not configured here.') + ' You can still enter profile context manually or review UTF-8 TXT intake. PDF text extraction is unavailable; file upload does not establish skill competence.'
        question, question_id = 'Would you like to enter context manually or review a TXT file?', 'documents'
    elif intent in ('greeting', 'capabilities'):
        answer = "Hi, I'm Minder. You can start without a complete profile. I can help you " + ', '.join(capabilities[:-1]) + ', and ' + capabilities[-1] + '.'
    elif intent == 'followup' and previous.get('question_id') == 'project':
        answer = 'Describe the goal, what you personally did, and a result you can explain. Leave uncertain skills unknown; a project title alone is not a competence assessment.'
        question, question_id = 'What did you personally contribute?', 'project_detail'
    elif intent == 'followup' and previous.get('question_id') == 'project_detail':
        answer = 'You can review and save that context in My profile as your own statement. An anchored skill assessment stays separate; I have not changed your profile.'
        question, question_id = 'Would you like to review your profile context or explore a role next?', 'direction'
    else:
        answer = 'You can begin with coursework, a personal project, volunteering or work experience. We can use that as your self-reported context without inventing skill mastery.'
        question, question_id = 'Tell me about one thing you worked on and what you did yourself.', 'project'
        if profile.get('career_context', {}).get('goals') and profile.get('evidence'):
            question, question_id = 'Would you like to compare roles, prepare a plan, or review progress?', 'direction'
    library = getattr(app, 'document_library', None)
    storage_available = bool(library is not None and library.storage is not None)
    return answer + ' ' + question, question_id, dict(temporary_conversation=True,
        document_storage_available=storage_available, forecast_available=False)


def role_quote(services, role_ids):
    reader = getattr(services, 'role_reference', None)
    if not reader or not role_ids:
        return None
    role = next(r for r in services.roles if r['role_id'] == role_ids[0])
    reference = reader(role['role_id'])
    row = reference['occupation']
    source = next(s for s in reference['sources'] if s['source_id'] == 'onet_occupation_data')
    validate('Source', source)
    parsed = urlsplit(source['uri'])
    if (source != role['source'] or source['geography'] != 'US' or parsed.scheme != 'https'
            or not parsed.hostname or parsed.username or parsed.password
            or row['O*NET-SOC Code'] != role['role_id'].removeprefix('onet:') or row['Title'] != role['label']):
        raise ValueError('role_reference_identity_mismatch')
    description = row.get('Description')
    if not isinstance(description, str) or not description.strip() or len(description) > 6000:
        return None
    identifier = 'occupation-reference:' + role['role_id'] + ':' + source['sha256'][:16]
    return dict(id=identifier, evidence_ids=[identifier], category='external_fact',
        text=role['label'] + ': ' + description + ' This is a US occupational reference, not Malaysian demand or your assessed competence.',
        sources=[source], kind='occupation_reference', geography='US')
