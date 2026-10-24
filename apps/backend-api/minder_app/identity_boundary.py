"""Common identity boundary: explicit local capabilities or managed login only."""
import os
from .store import AppError


def managed():
    return os.environ.get('MINDER_ENV') == 'production' or os.environ.get('MINDER_AUTH_PROVIDER') == 'clerk'


def public_configuration():
    from .auth_adapter import public_config
    return dict(public_config(), mode='managed' if managed() else 'local',
                anonymous_session_allowed=not managed())


def authenticated_owner(app, token, request_context=None):
    if not managed():
        return app.store.authenticate(token)
    from .auth_adapter import verify_identity
    identity = verify_identity(token, request_context)
    try:
        from .identity_store import owner_for_identity
    except ImportError:
        raise AppError('verified_identity_storage_unavailable', 503) from None
    return owner_for_identity(app.store, identity)
