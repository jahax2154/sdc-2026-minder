"""Origin-linked Minder requests become review-only singleton Mindbot proposals.

Reuse D's existing owned records/notice links and transaction-capable executor.
No migration, second conversation, model call on approval or implicit activation.
"""
import copy
import hashlib
import json
import re
from .store import AppError, now

POLICY = 'minder-mindbot-handoff-v1'
OPERATIONS = (('GET', '/api/product/minder-handoffs'), ('POST', '/api/product/handoff-decision'))


def wanted(message):
    from .message_orchestrator import explicit_command
    if explicit_command(message, message):
        return True
    return bool(re.match(r"^(?:please\s+)?(?:help me|I (?:want|would like|need) to|can we|could you help me)\b", message, re.I)
                and re.search(r'\b(plan|roadmap|reschedule|schedule|move|change|edit|update|create|add)\b', message, re.I))


def optional(store, owner, kind, identifier, db=None):
    try:
        return store.get(owner, kind, identifier, db=db)
    except AppError as error:
        if error.status != 404:
            raise
        return None


def summary(event):
    return {k:event.get(k) for k in ('event_id','version','policy_version','status','kind',
        'source_conversation_id','source_message_id','mindbot_conversation_id','mindbot_message_id','clarification_code')}


def prepare(app, owner, request_id, body, response, history, message):
    """All notice/proposal/event insertion is one transaction after model work."""
    event_id = 'minder:' + hashlib.sha256((owner+'|'+request_id).encode()).hexdigest()
    generation = response.get('generation')
    operation = generation.get('advice', {}).get('operation', {}) if generation else {}
    kind, preview, clarification, request = 'clarification', None, None, None
    try:
        if operation.get('kind', 'none') != 'none':
            from .message_orchestrator import operation_request, validate_command_kind
            validate_command_kind(operation['kind'], message)
            observed = app.store.get(owner, 'grounding', generation['draft_id'])
            # Direct-style target/time checks validate the actual user words,
            # but cross-chat authority is ALWAYS proposal-only.
            request = operation_request(app, owner, operation, message, True,
                observed['observed_plan_versions'], observed.get('observed_automation_version'))
            if request['kind']=='reschedule_task':
                plan = app.store.get(owner,'plan',request['target_id'])
                task = next(t for t in plan['tasks'] if t['task_id']==operation['task_id'])
                if task['state']=='proposed':
                    request['kind']='schedule_task'
                    request['diff'].append(dict(path='/tasks/'+task['task_id']+'/state',before='proposed',after='scheduled'))
            kind = 'action'
        elif generation and generation['advice'].get('stages'):
            profile = app.store.get(owner, 'profile', owner)
            direction = optional(app.store, owner, 'direction', owner)
            from .conversation import matched_roles
            named = matched_roles(app.services, message)
            role_id = named[0] if len(named) == 1 else direction.get('role_id') if direction else None
            if not role_id:
                raise AppError('choose_supported_career_for_roadmap')
            record = app.store.get(owner, 'generation', generation['draft_id'])
            plan = app.generation_materializer(owner, record['generation'], role_id)
            preview = dict(kind='save_roadmap', role_id=role_id, plan=plan,
                draft_id=generation['draft_id'], expected_generation_version=record['version'],
                expected_profile_version=profile['version'], activated=False)
            kind = 'roadmap'
        else:
            clarification = 'provider_unavailable' if response.get('provider', {}).get('status') != 'available' else 'clarify_specific_change'
    except AppError as error:
        clarification = error.code
        kind = 'clarification'
    with app.store.transaction() as db:
        event = optional(app.store, owner, 'minder_handoff', event_id, db)
        if event is None:
            source = db.execute("SELECT m.id,m.conversation_id FROM conversation_messages m JOIN conversations c "
                "ON c.owner=m.owner AND c.id=m.conversation_id WHERE m.owner=? AND m.request_id=? "
                "AND m.role='user' AND c.channel='minder'", (owner,request_id)).fetchone()
            if source is None:
                raise AppError('owned_origin_message_required',409)
            if request:
                try:
                    preview = app.actions.propose(owner, request, origin='inferred', db=db)
                except AppError as error:
                    kind, preview, clarification = 'clarification', None, error.code
            event = dict(event_id=event_id, policy_version=POLICY, kind=kind,
                status='pending' if preview else 'needs_input', created_at=now(),
                source_conversation_id=source['conversation_id'], source_message_id=source['id'],
                source_request_id=request_id, source_excerpt=message[:240],
                relevant_history_message_ids=[h['message_id'] for h in history[-6:] if h.get('message_id')],
                preview=preview, clarification_code=clarification, decision=None, decision_key=None)
            notice = dict(summary='Minder request: '+message[:180]+'\n'+(
                'Review the proposed change in Mindbot before approving it. Nothing has been changed.' if preview else
                'More details are needed before a safe proposal can be prepared. Your saved state is unchanged.'),
                created_at=event['created_at'], statements=[], sources=[], handoff_event_id=event_id)
            if kind == 'action':
                notice['proposal'] = preview
            db.execute('INSERT INTO notices VALUES(?,?,?)',(owner,event_id,json.dumps(notice,sort_keys=True)))
            from .conversations import append_notice
            link = append_notice(app.store,owner,event_id,db=db)
            event.update(mindbot_conversation_id=link['conversation_id'], mindbot_message_id=link['message_id'])
            event = app.store.put(owner,'minder_handoff',event_id,event,None,db=db)
    response = copy.deepcopy(response)
    response.setdefault('diagnostics', {})['handoff'] = summary(event)
    response['action_status'] = 'approval_required' if event['status']=='pending' else 'not_applied'
    response['answer'] = (response.get('answer','')+'\n\n'+(
        'I sent one proposal to your existing Mindbot for review. You can keep talking here; no task or schedule was changed.'
        if event['status']=='pending' else 'I sent your request to Mindbot with the missing detail. No change was applied.'))
    if event['kind']=='action':
        response['proposal_ids'] = [event['preview']['preview']['proposal_id']]
        response['actions'] = [event['preview']]
    return response


def decide(app, owner, body):
    required = {'event_id','decision','expected_version','idempotency_key'}
    if (not isinstance(body,dict) or set(body)!=required or body['decision'] not in ('approve','reject')
            or any(not isinstance(body[k],str) or not 1<=len(body[k])<=200 for k in required)):
        raise AppError('invalid_handoff_decision',422)
    event_id, decision, key = body['event_id'], body['decision'], body['idempotency_key']
    receipt_id = hashlib.sha256((event_id+'|'+key).encode()).hexdigest()
    scope = json.dumps(body,sort_keys=True)
    with app.store.transaction() as db:
        receipt = optional(app.store, owner, 'handoff_receipt', receipt_id, db)
        if receipt:
            if receipt['scope'] != scope:
                raise AppError('idempotency_scope_conflict',409)
            if receipt.get('error'):
                raise AppError(receipt['error'],409)
            return receipt['result']
        event = app.store.get(owner,'minder_handoff',event_id,db=db)
        resuming = event['status']=='applying' and event.get('decision_key')==key and event.get('decision')==decision
        if resuming and event.get('decision_scope')!=scope:
            raise AppError('idempotency_scope_conflict',409)
        if not resuming:
            if event['version']!=body['expected_version'] or event['status']!='pending':
                raise AppError('stale_handoff_or_decision',409)
            event.update(status='applying',decision=decision,decision_key=key,decision_scope=scope)
            event = app.store.put(owner,'minder_handoff',event_id,event,event['version'],db=db)
    result, error = None, None
    try:
        if event['kind']=='action':
            proposal = event['preview']
            result = app.actions.decide(owner,proposal['preview']['proposal_id'],decision,
                proposal['preview_hash'],proposal['preview']['request']['expected_state_version'])
        elif decision=='reject':
            result = dict(status='rejected',target_changed=False)
        elif event['kind']=='roadmap':
            from .generation_state import accept_generation
            preview = event['preview']
            result = accept_generation(app,owner,dict(draft_id=preview['draft_id'],role_id=preview['role_id'],
                expected_profile_version=preview['expected_profile_version'],
                expected_generation_version=preview['expected_generation_version'],
                idempotency_key='handoff:'+hashlib.sha256(event_id.encode()).hexdigest()))
        else:
            raise AppError('handoff_not_actionable',409)
    except AppError as failure:
        error = failure.code
    with app.store.transaction() as db:
        receipt = optional(app.store,owner,'handoff_receipt',receipt_id,db)
        if receipt:
            if receipt['scope']!=scope:
                raise AppError('idempotency_scope_conflict',409)
            if receipt.get('error'):
                raise AppError(receipt['error'],409)
            return receipt['result']
        event = app.store.get(owner,'minder_handoff',event_id,db=db)
        event.update(status='stale' if error else 'approved' if decision=='approve' else 'rejected',
            decided_at=now(), result=result, error=error)
        event = app.store.put(owner,'minder_handoff',event_id,event,event['version'],db=db)
        output = dict(event=event,result=result,target_changed=decision=='approve' and not error)
        app.store.put(owner,'handoff_receipt',receipt_id,dict(scope=scope,result=output,error=error),None,db=db)
    if error:
        raise AppError(error,409)
    return output


def dispatch(app, owner, method, path, body):
    if method=='GET':
        events = sorted(app.store.list(owner,'minder_handoff'),key=lambda e:e['created_at'],reverse=True)
        # The existing proposal panel remains a valid approval surface. Project
        # its authoritative decision without creating a second write authority.
        statuses = {p['preview']['proposal_id']:p['status'] for p in app.actions.proposals(owner)}
        for event in events:
            if event['kind']=='action' and event['status']=='pending':
                status = statuses.get(event['preview']['preview']['proposal_id'])
                event['canonical_proposal_status'] = status
                if status in ('applied','rejected'):
                    event['status'] = 'approved' if status=='applied' else 'rejected'
        return dict(policy_version=POLICY,events=events[:30])
    return decide(app,owner,body)
