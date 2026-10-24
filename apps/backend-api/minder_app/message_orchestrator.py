"""A's one conversation callback for Minder and Mindbot, using D persistence.

D reserves a turn before this callback. No DB transaction spans model execution.
Model interpretations cannot invent targets, expected versions or write authority.
"""
import re
from .generation import generate, EMPIRICAL
from .store import AppError


def bind(app):
    def handler(owner, channel, message, history, request_id, body):
        return turn(app, owner, channel, message, history, request_id, body)
    app.conversation_turn_handler = handler
    app.generation_materializer = lambda owner, generation, role_id: materialize(app, owner, generation, role_id)


def materialize(app, owner, generation, role_id):
    """D calls only for explicit draft acceptance, never while discussing advice."""
    import uuid
    from .generation import profile_for, validate_advice
    from .generation_schemas import POLICY_ID
    if generation.get('policy_version') != POLICY_ID or generation.get('status') != 'unsaved_draft':
        raise AppError('unsupported_generation_policy')
    profile = profile_for(app.store, owner, generation.get('profile_version'))
    if profile['version'] is None:
        raise AppError('save_partial_profile_before_accepting_plan')
    role = next((r for r in app.services.roles if r['role_id'] == role_id), None)
    if role is None or role.get('eligibility') != 'supported':
        raise AppError('supported_selected_role_required')
    advice = validate_advice(generation['advice'], [], [])
    if advice['operation']['kind'] != 'none' or not advice['stages']:
        raise AppError('generation_has_no_acceptable_roadmap')
    tasks, parents = [], []
    for index, stage in enumerate(advice['stages']):
        current = []
        for offset, item in enumerate(stage['tasks']):
            identifier = str(uuid.uuid5(uuid.NAMESPACE_URL,
                '|'.join((owner, generation['draft_id'], role_id, str(index), str(offset)))))
            current.append(identifier)
            tasks.append(dict(task_id=identifier, title=item['title'],
                description=stage['title'] + '\n' + item['description'], state='proposed',
                activity_completion=False, mastery_verified=False, locked=False,
                prerequisite_task_ids=list(parents), scheduled_at=None,
                estimated_hours=item['estimated_hours'], evidence_ids=[], skill_ids=[], resource_id=None))
        parents = current
    plan = dict(plan_id='generated:'+generation['draft_id'], profile_id=owner, selected_role_id=role_id,
        state_version='draft', previous_version=None, task_ids=[t['task_id'] for t in tasks], tasks=tasks,
        progress_event_ids=[], constraints=[])
    from .plans import check_plan
    check_plan(plan, profile)
    return plan


def explicit_command(message, quote):
    if not isinstance(quote,str) or quote.strip()!=message.strip():
        return False
    text=message.strip()
    polite=re.match(r"^(?:can|could|would) you (?:please )?",text,re.I)
    if polite:
        text=text[polite.end():]
    verbs=r"mark|complete|finish|reschedule|schedule|move|set|add|create|edit|update|change|reset|remove|clear|pause|resume|cancel"
    framed=bool(re.match(r"^(?:please\s+)?(?:"+verbs+r")\b",text,re.I))
    framed=framed or bool(re.match(r"^I(?: am|'m) (?:not )?interested in\b",text,re.I))
    framed=framed or bool(re.match(r"^I(?: have|['’]ve)? (?:completed|finished)\b",text,re.I))
    uncertain=re.search(r"\b(?:maybe|should|suggest|recommend|pretend|quoted|example|if)\b|don't|do not|without saving",text,re.I)
    return framed and not uncertain


def validate_command_kind(kind,message):
    vocabulary={
        'complete_task':r'\b(?:done|complete|completed|finish|finished)\b',
        'reschedule_task':r'\b(?:reschedule|move|shift|schedule)\b',
        'schedule_task':r'\b(?:schedule|move|set)\b',
        'create_task':r'\b(?:create|add|new)\b',
        'edit_task':r'\b(?:edit|update|change|rename)\b',
        'update_preference':r'\b(?:interest|interested|preference|preferences|reset|neutral|avoid|dislike)\b',
        'change_goal':r'\b(?:goal|goals|aim|direction)\b',
        'update_context':r'\b(?:education|experience|background|context|profile|goal|goals)\b',
        'set_availability':r'\b(?:availability|capacity|hours|time)\b',
        'configure_automation':r'\b(?:daily|automation|check)\b'}
    if kind not in vocabulary or not re.search(vocabulary[kind],message,re.I):
        raise AppError('clarify_requested_action_scope')


def requested_clock(message):
    values=list(re.finditer(r"\b([01]?\d|2[0-3]):([0-5]\d)(?:\s*(am|pm))?\b|\b(1[0-2]|0?[1-9])\s*(am|pm)\b",message,re.I))
    if not values or (len(values)>1 and re.search(r"\bor\b",message,re.I)):return None
    value=values[-1]
    if value[1]:hour,minute,period=int(value[1]),int(value[2]),value[3]
    else:hour,minute,period=int(value[4]),0,value[5]
    if period:
        if not 1<=hour<=12:return None
        hour=hour%12+(12 if period.lower()=='pm' else 0)
    return f"{hour:02}:{minute:02}"


def requested_time(message, timezone):
    from datetime import datetime,timedelta
    from zoneinfo import ZoneInfo
    from .plans import instant
    target=re.split(r"\bto\b",message,flags=re.I)[-1]
    full=list(re.finditer(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})",target))
    if full:return instant(full[-1].group())
    dates=list(re.finditer(r"\b\d{4}-\d{2}-\d{2}\b",target))
    local=datetime.now(ZoneInfo(timezone))
    if dates:local=datetime.fromisoformat(dates[-1].group()).replace(tzinfo=local.tzinfo)
    elif re.search(r"\btomorrow\b",target,re.I):local+=timedelta(days=1)
    elif not re.search(r"\btoday\b",target,re.I):return None
    clock=requested_clock(target)
    if not clock:return None
    hour,minute=map(int,clock.split(':'))
    return local.replace(hour=hour,minute=minute,second=0,microsecond=0)


def operation_request(app, owner, operation, message, direct, observed_versions, observed_automation=None):
    import uuid
    from .generation import profile_for
    plans=app.store.list(owner,'plan');kind=operation['kind'];payload=operation.get('payload',{})
    if kind in ('update_context','set_availability'):
        profile=app.store.get(owner,'profile',owner)
        if kind=='update_context':
            diffs=[dict(path='/career_context/'+key,before=profile.get('career_context',{}).get(key),after=payload[key])
                   for key in ('education','experience','goals') if key in payload]
            if not diffs:raise AppError('specific_profile_context_required')
        else:
            if 'weekly_hours' not in payload:raise AppError('clarify_weekly_availability')
            capacity=payload['weekly_hours']
            if capacity is None and direct and not re.search(r'\b(reset|remove|clear|unknown|unspecified)\b',message,re.I):
                raise AppError('clarify_availability_reset')
            rows=[c for c in profile['constraints'] if c['scope']=='weekly_hours']
            if len(rows)>1:raise AppError('clarify_conflicting_capacity_records')
            if capacity is not None:
                value=re.search(r'\b(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*(?:a|per|/)\s*week\b',message,re.I)
                if not value or float(value[1])!=capacity:raise AppError('clarify_explicit_weekly_hours')
            if rows and capacity is None:
                diffs=[dict(path='/constraints/'+rows[0]['constraint_id'],before=rows[0],after=None)]
            elif rows:
                diffs=[dict(path='/constraints/'+rows[0]['constraint_id']+'/value',before=rows[0]['value'],after=capacity)]
            elif capacity is None:raise AppError('availability_already_unknown')
            else:
                identifier='weekly-hours-'+str(uuid.uuid4())
                constraint=dict(constraint_id=identifier,scope='weekly_hours',hard=True,value=capacity,
                    unit='hours_per_week',evidence_id='self-reported-availability')
                diffs=[dict(path='/constraints/'+identifier,before=None,after=constraint)]
        return dict(kind='update_profile',target_id=owner,expected=profile['version'],diff=diffs,
            reason='Explicit user-reported context or pathway availability; not skill competence',evidence_ids=[])
    if kind in ('update_preference','change_goal'):
        profile=app.store.get(owner,'profile',owner)
        if kind=='change_goal':
            if 'goals' not in payload:raise AppError('specific_goal_required')
            path='/career_context/goals';before=profile.get('career_context',{}).get('goals');after=payload['goals']
        else:
            entity_type,entity_id=payload.get('entity_type'),payload.get('entity_id')
            if entity_type=='role':
                known={r['role_id'] for r in app.services.roles}
            elif entity_type=='industry':
                from minder_ml.intelligence.role_fit import reference
                known=set(reference()['industries'])
            else:raise AppError('specific_preference_required')
            if entity_id not in known or 'preference_state' not in payload:raise AppError('known_preference_target_required')
            prior=next((p for p in profile['preferences'] if p['entity_type']==entity_type and p['entity_id']==entity_id),None)
            path='/preferences/'+entity_type+'/'+entity_id;before=prior['state'] if prior else None;after=payload['preference_state']
        return dict(kind='update_profile' if kind=='update_preference' else kind,target_id=owner,expected=profile['version'],
            diff=[dict(path=path,before=before,after=after)],reason='Conversation scoped profile instruction',evidence_ids=[])
    if kind=='configure_automation':
        try:before=app.store.get(owner,'agent_settings',owner)
        except AppError as error:
            if error.status!=404:raise
            before=None
        if (before['version'] if before else None)!=observed_automation:
            raise AppError('stale_state_version',409)
        changes={}
        if 'automation_state' in payload:changes['state']=payload['automation_state']
        elif 'enabled' in payload:changes['enabled']=payload['enabled']
        state=changes.get('state',('active' if changes['enabled'] else 'paused') if 'enabled' in changes else None)
        if direct and state and state!=(before or {}).get('state'):
            requested=('cancelled' if re.search(r'\b(cancel|stop)\b',message,re.I) else
                'paused' if re.search(r'\b(pause|disable)\b',message,re.I) else
                'active' if re.search(r'\b(resume|enable|start|create)\b',message,re.I) else None)
            if state!=requested:raise AppError('clarify_requested_automation_state')
        if 'check_time' in payload:
            supplied=payload['check_time']
            if supplied!=(before or {}).get('check_time') and requested_clock(message)!=supplied:
                raise AppError('clarify_requested_daily_time')
            changes['check_time']=supplied
        if 'timezone' in payload:
            zone=payload['timezone']
            named=zone.casefold().replace('_',' ') in message.casefold().replace('_',' ')
            default=zone=='Asia/Kuala_Lumpur' and before is None
            if zone!=(before or {}).get('timezone') and not named and not default:raise AppError('clarify_requested_timezone')
            changes['timezone']=zone
        if before is None and 'check_time' not in changes:
            raise AppError('clarify_daily_check_time')
        plan_id=operation.get('plan_id')
        if plan_id:
            if plan_id not in {p['plan_id'] for p in plans}:raise AppError('specific_saved_plan_required')
            changes['scope']={'plan_ids':[plan_id]}
        if not changes:raise AppError('specific_automation_change_required')
        return dict(kind=kind,target_id=owner,expected=before['version'] if before else 'missing',
            diff=[dict(path='/settings/'+k,before=before.get(k) if before else None,after=v) for k,v in changes.items()],
            reason='Conversation daily automation instruction',evidence_ids=[])
    matches=[(p,t) for p in plans for t in p['tasks'] if t['task_id']==operation['task_id']]
    if kind=='create_task':
        plan=next((p for p in plans if p['plan_id']==operation.get('plan_id')),None)
        if plan is None and len(plans)==1:plan=plans[0]
        if plan is None:raise AppError('specific_saved_plan_required')
        if not payload.get('title'):raise AppError('task_title_required')
        # Generated proposed activity cannot invent mastery/source/resource IDs.
        task=dict(task_id=str(uuid.uuid4()),title=payload['title'],description=payload.get('description',''),
            state='proposed',activity_completion=False,mastery_verified=False,locked=False,
            prerequisite_task_ids=[],scheduled_at=None,estimated_hours=payload.get('estimated_hours'),
            evidence_ids=[],skill_ids=[],resource_id=None)
        changes=[dict(path='/tasks/'+task['task_id'],before=None,after=task)]
    else:
        if len(matches)!=1:raise AppError('specific_action_scope_required')
        plan,task=matches[0]
        named=task['task_id'] in message or bool(task.get('title') and task['title'].casefold() in message.casefold())
        if direct and not named and sum(len(p['tasks']) for p in plans)>1:
            raise AppError('clarify_specific_task_target')
        if kind in ('reschedule_task','schedule_task'):
            profile=app.store.get(owner,'profile',owner)
            target=requested_time(message,profile['timezone'])
            if target is None:raise AppError('clarify_exact_date_time')
            changes=[dict(path='/tasks/'+task['task_id']+'/scheduled_at',before=task['scheduled_at'],after=target.isoformat())]
            if kind=='schedule_task':
                changes.append(dict(path='/tasks/'+task['task_id']+'/state',before=task['state'],after='scheduled'))
        elif kind=='complete_task':
            changes=[dict(path='/tasks/'+task['task_id']+'/state',before=task['state'],after='completed')]
        elif kind=='edit_task':
            changes=[dict(path='/tasks/'+task['task_id']+'/'+k,before=task.get(k),after=v)
                     for k,v in payload.items() if k in ('title','description','estimated_hours')]
            if not changes:raise AppError('specific_task_edit_required')
        else:raise AppError('unsupported_conversation_operation')
    if observed_versions.get(plan['plan_id']) != plan['state_version']:
        raise AppError('stale_state_version',409)
    return dict(kind=kind,target_id=plan['plan_id'],expected=plan['state_version'],diff=changes,
        reason='Conversation scoped task instruction' if direct else 'Conversation suggested task change',evidence_ids=[])


def turn(app, owner, channel, message, history, request_id, body):
    if channel not in ('minder', 'mindbot'):
        raise AppError('invalid_conversation_channel')
    from .conversation import intent_for,matched_roles
    role_reference=intent_for(message,named_role=bool(matched_roles(app.services,message)))=='role_reference'
    if EMPIRICAL.search(message) or role_reference:
        from .chat import chat
        return chat(app.store, app.services, app.provider, owner, message,
            body.get('expected_profile_version'), request_id=request_id, app=app)
    response = generate(app, owner, message, body.get('expected_profile_version'),
                        history=history, request_id=request_id)
    generation = response.get('generation')
    if not generation:return response
    operation = generation['advice']['operation']
    if operation['kind']=='none':return response
    direct=explicit_command(message,operation.get('instruction_quote'))
    try:
        if direct:validate_command_kind(operation['kind'],message)
        from .generation import profile_for
        profile_for(app.store,owner,body.get('expected_profile_version'))
        scope=app.store.get(owner,'grounding',generation['draft_id'])
        request=operation_request(app,owner,operation,message,direct,scope['observed_plan_versions'],scope.get('observed_automation_version'))
        if direct:
            key=body.get('idempotency_key')
            if not key:raise AppError('idempotency_key_required')
            import hashlib,json
            scoped_key='chat:'+hashlib.sha256(json.dumps([body.get('conversation_id'),key]).encode()).hexdigest()
            result=app.actions.direct(owner,request,scoped_key)
            response.update(action_status='applied',answer='The requested change was saved.',action_ids=[result['action']['action_id']])
        else:
            result=app.actions.propose(owner,request)
            response.update(action_status='approval_required',answer='Review this proposed change before approving it.',
                proposal_ids=[result['preview']['proposal_id']])
        response['actions']=[result]
    except AppError as error:
        response.update(action_status='not_applied',status=error.code,
            answer='The change was not applied ('+error.code+'). Please clarify the target or required details; saved state remains unchanged.')
    return response
