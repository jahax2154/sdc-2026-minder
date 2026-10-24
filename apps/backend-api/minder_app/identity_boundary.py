"""Common identity boundary: explicit local capabilities or managed login only."""
import os
from .store import AppError


def managed(app=None):
    return bool(getattr(app, 'managed_identity_required', False)) or os.environ.get('MINDER_ENV') == 'production' or os.environ.get('MINDER_AUTH_PROVIDER') == 'clerk'


def public_configuration(app=None):
    from .auth_adapter import public_config
    return dict(public_config(), mode='managed' if managed(app) else 'local',
                anonymous_session_allowed=not managed(app))


def authenticated_owner(app, token, request_context=None):
    if not managed(app):
        return app.store.authenticate(token)
    from .auth_adapter import verify_identity
    identity = verify_identity(token, request_context)
    try:
        from .identity_store import owner_for_identity
    except ImportError:
        raise AppError('verified_identity_storage_unavailable', 503) from None
    return owner_for_identity(app.store, identity)
