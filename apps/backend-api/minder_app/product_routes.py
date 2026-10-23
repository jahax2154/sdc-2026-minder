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
            operations.append(dict(method=verb, path=route, owner='D' if name == 'product_state' else 'E',
                                   status='implemented' if ready else 'unavailable', module=name))
        return dict(contract_version=VERSION, operations=operations)
    name = ROUTES.get((method, path))
    if name is None:
        raise AppError('not_found', 404)
    module = module_for(name)
    if module is None or (method, path) not in getattr(module, 'OPERATIONS', ()):
        raise AppError('product_capability_unavailable', 404)
    return module.dispatch(app, owner, method, path, body)
