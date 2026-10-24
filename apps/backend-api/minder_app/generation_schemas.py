"""Versioned advice is distinct from verified facts and executable authority."""
from jsonschema import Draft202012Validator

POLICY_ID = 'minder-typed-guidance-v1'
TEXT = {'type': 'string', 'minLength': 1, 'maxLength': 1200}
TASK = {'type': 'object', 'additionalProperties': False, 'properties': {
    'title': dict(TEXT, maxLength=160), 'description': dict(TEXT, maxLength=400),
    'estimated_hours': {'type': ['number', 'null'], 'exclusiveMinimum': 0, 'maximum': 40}},
    'required': ['title', 'description', 'estimated_hours']}
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'kind': {'enum': ['guidance', 'roadmap', 'tasks', 'clarification']},
    'answer': dict(TEXT, minLength=30, maxLength=2000,
        description='A useful conversational introduction addressing the actual request, never just a role label.'),
    'assumptions': {'type': 'array', 'maxItems': 3, 'items': dict(TEXT, maxLength=240)},
    'questions': {'type': 'array', 'maxItems': 2, 'items': dict(TEXT, maxLength=240)},
    'stages': {'type': 'array', 'maxItems': 4, 'items': {'type': 'object', 'additionalProperties': False,
        'properties': {'title': dict(TEXT, maxLength=160), 'outcome': dict(TEXT, maxLength=300),
            'tasks': {'type': 'array', 'minItems': 1, 'maxItems': 3, 'items': TASK}},
        'required': ['title', 'outcome', 'tasks']}},
    'fact_ids': {'type': 'array', 'uniqueItems': True, 'maxItems': 8, 'items': {'type': 'string'}},
    'operation': {'type': 'object', 'additionalProperties': False, 'properties': {
        'kind': {'enum': ['none', 'complete_task', 'reschedule_task', 'schedule_task',
            'create_task', 'edit_task', 'update_preference', 'change_goal', 'configure_automation', 'update_context', 'set_availability']},
        'task_id': {'type': ['string', 'null'], 'maxLength': 100},
        'scheduled_at': {'type': ['string', 'null'], 'maxLength': 50},
        'instruction_quote': {'type': ['string', 'null'], 'maxLength': 500},
        'plan_id': {'type': ['string', 'null'], 'maxLength': 100},
        'payload': {'type': 'object', 'additionalProperties': False, 'properties': {
            'title': {'type': 'string', 'minLength': 1, 'maxLength': 160},
            'description': {'type': 'string', 'maxLength': 400},
            'estimated_hours': {'type': ['number','null'], 'exclusiveMinimum': 0, 'maximum': 40},
            'entity_type': {'enum': ['role','industry']}, 'entity_id': {'type':'string','maxLength':100},
            'preference_state': {'enum':['interested','not_interested','neutral','unknown',None]},
            'goals': {'type':'string','maxLength':4000},
            'education': {'type':'string','maxLength':4000},'experience': {'type':'string','maxLength':4000},
            'weekly_hours': {'type':['number','null'],'minimum':0,'maximum':168},
            'timezone': {'type':'string','maxLength':100}, 'enabled': {'type':'boolean'},
            'check_time': {'type':'string','pattern':'^(?:[01][0-9]|2[0-3]):[0-5][0-9]$'},
            'automation_state': {'enum':['active','paused','cancelled']}}}},
        'required': ['kind', 'task_id', 'scheduled_at', 'instruction_quote']}},
    'required': ['kind', 'answer', 'assumptions', 'questions', 'stages', 'fact_ids', 'operation']}
VALIDATOR = Draft202012Validator(SCHEMA)
