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


def turn(app, owner, channel, message, history, request_id, body):
    if channel not in ('minder', 'mindbot'):
        raise AppError('invalid_conversation_channel')
    if EMPIRICAL.search(message):
        from .chat import chat
        return chat(app.store, app.services, app.provider, owner, message,
            body.get('expected_profile_version'), request_id=request_id, app=app)
    response = generate(app, owner, message, body.get('expected_profile_version'),
                        history=history, request_id=request_id)
    generation = response.get('generation')
    if not generation:
        return response
    operation = generation['advice']['operation']
    if operation['kind'] == 'none':
        return response
    # Server-resolved canonical target/version and exact current-user quote.
    # Imperative authority is deliberately narrow; model semantics selects task
    # and operation, while uncertain suggestions produce immutable proposals.
    quote = operation.get('instruction_quote')
    direct = (isinstance(quote, str) and quote.strip() and quote.strip() in message and
        re.match(r'^(?:please\s+)?(?:mark|complete|finish|reschedule|move|set)\b', message.strip(), re.I) and
        '?' not in message and not re.search(r'\b(?:if|maybe|could|should|suggest|recommend|pretend|quoted|says)\b', message, re.I))
    if operation['kind'] == 'complete_task' and not re.search(r'\b(?:complete|completed|done|finish|finished)\b', message, re.I):
        direct = False
    plans = app.store.list(owner, 'plan')
    matches = [(p, t) for p in plans for t in p['tasks'] if t['task_id'] == operation['task_id']]
    if len(matches) != 1:
        raise AppError('specific_action_scope_required')
    plan, task = matches[0]
    field = 'state' if operation['kind'] == 'complete_task' else 'scheduled_at'
    value = 'completed' if field == 'state' else operation['scheduled_at']
    if field == 'scheduled_at':
        if not value or value not in message:
            response['answer'] += '\nPlease specify the exact new date, time and timezone before changing the schedule.'
            response['action_status'] = 'clarification_required'
            return response
    request = dict(kind=operation['kind'], target_id=plan['plan_id'], expected=plan['state_version'],
        diff=[dict(path='/tasks/'+task['task_id']+'/'+field, before=task[field], after=value)],
        reason='Conversation task instruction' if direct else 'Conversation suggested change', evidence_ids=[])
    try:
        if direct:
            key = body.get('idempotency_key')
            if not key:
                raise AppError('idempotency_key_required')
            result = app.actions.direct(owner, request, 'chat:'+key)
            response['action_status'] = 'applied'
            response['answer'] = 'The requested task change was saved.'
        else:
            result = app.actions.propose(owner, request)
            response['action_status'] = 'approval_required'
            response['answer'] = 'Here is the proposed task change. Review and approve it before it is applied.'
        response['action_result'] = result
    except AppError as error:
        # Never claim a generated operation succeeded when validation rejected it.
        response['action_status'] = 'not_applied'
        response['action_error'] = dict(code=error.code, status=error.status)
        response['answer'] = 'The task change was not applied (' + error.code + '). Your saved task remains unchanged.'
    return response
