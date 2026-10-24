"""A-owned registry; D/E publish OPERATIONS and dispatch in separate modules.

Planned operations fail explicitly until their committed owner implements them.
Authentication/error serialization remain in the existing Application.
"""
import importlib
from .store import AppError

VERSION = 'product-v2-bootstrap-v1'
ROUTES = {}
for method, path in (
    ('GET', 'direction'), ('PUT', 'direction'), ('POST', 'tasks'),
    ('POST', 'task-action'), ('GET', 'progress'), ('GET', 'resource-state'),
    ('PUT', 'resource-state'), ('POST', 'resource-to-plan'), ('POST', 'intake-correction'),
):
    ROUTES[(method, '/api/product/' + path)] = 'product_state'
for name in ('overview', 'career-match', 'roadmap', 'tasks', 'progress', 'news'):
    for method in ('GET', 'POST'):
        ROUTES[(method, '/api/product/views/' + name)] = 'product_views'
for method, path in (('POST', 'resources'), ('POST', 'resource-detail')):
    ROUTES[(method, '/api/product/' + path)] = 'product_content'
for method, path in (('GET', 'documents'), ('POST', 'document-upload'),
                     ('POST', 'document-download'), ('POST', 'document-delete'),
                     ('POST', 'document-extract')):
    ROUTES[(method, '/api/product/' + path)] = 'documents'

for method, path in (('GET', 'conversations'), ('POST', 'conversations'),
                     ('POST', 'conversations-search'),
                     ('GET', 'conversation'), ('POST', 'conversation'), ('DELETE', 'conversation'),
                     ('GET', 'mindbot-conversation'), ('POST', 'conversation-turn')):
    ROUTES[(method, '/api/product/' + path)] = 'conversations'
for method in ('GET', 'PUT'):
    ROUTES[(method, '/api/product/bot-preferences')] = 'bot_preferences'
for method, path in (('GET', 'generations'), ('POST', 'generation'), ('POST', 'generation-accept')):
    ROUTES[(method, '/api/product/' + path)] = 'generation_state'

DEFAULT_BODY_LIMIT = 131072
MAX_DOCUMENT_BYTES = 1048576
MAX_UPLOAD_BODY_LIMIT = 4 * ((MAX_DOCUMENT_BYTES + 2) // 3) + 4096


def request_body_limit(method, path):
    """Only document upload may opt into a larger bounded JSON body.

    D owns decoded-byte/quota configuration and exports upload_request_limit().
    Missing implementation retains the existing transport limit and unavailable
    dispatch. No request value may select the transport limit.
    """
    if (method, path) != ('POST', '/api/product/document-upload'):
        return DEFAULT_BODY_LIMIT
    module = module_for('documents')
    getter = getattr(module, 'upload_request_limit', None)
    if getter is None:
        return DEFAULT_BODY_LIMIT
    limit = getter()
    if type(limit) is not int or not DEFAULT_BODY_LIMIT <= limit <= MAX_UPLOAD_BODY_LIMIT:
        raise AppError('document_transport_configuration_invalid', 500)
    return limit


def module_for(name):
    full = __package__ + '.' + name
    try:
        return importlib.import_module(full)
    except ModuleNotFoundError as error:
        if error.name == full:
            return None
        raise


def dispatch(app, owner, method, path, body):
    if (method, path) == ('GET', '/api/product/capabilities'):
        operations = []
        for (verb, route), name in sorted(ROUTES.items()):
            module = module_for(name)
            ready = module is not None and (verb, route) in getattr(module, 'OPERATIONS', ())
            operations.append(dict(method=verb, path=route, owner='D' if name in ('product_state', 'documents', 'conversations', 'generation_state', 'bot_preferences') else 'E',
                                   status='implemented' if ready else 'unavailable', module=name))
        return dict(contract_version=VERSION, operations=operations)
    name = ROUTES.get((method, path))
    if name is None:
        raise AppError('not_found', 404)
    module = module_for(name)
    if module is None or (method, path) not in getattr(module, 'OPERATIONS', ()):
        raise AppError('product_capability_unavailable', 404)
    return module.dispatch(app, owner, method, path, body)
