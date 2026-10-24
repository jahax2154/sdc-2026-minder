"""Managed Clerk identity verification; no routes, passwords or owner persistence.

A installs the common identity boundary; D alone maps this trusted result to an
application owner. Only provider session tokens are accepted, never user IDs.
"""
from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import lru_cache
import os
import time
from types import SimpleNamespace
from urllib.parse import urlsplit
from .store import AppError

CONTRACT_VERSION = "minder-managed-auth-v1"


@dataclass(frozen=True)
class VerifiedIdentity(Mapping):
    issuer: str
    subject: str
    session_id: str
    expires_at: int
    provider: str = "clerk"

    def __iter__(self):
        return iter(("issuer", "subject", "session_id", "expires_at", "provider"))

    def __len__(self):
        return 5

    def __getitem__(self, key):
        if key not in tuple(self):
            raise KeyError(key)
        return getattr(self, key)


@dataclass(frozen=True)
class AuthConfig:
    issuer: str
    authorized_parties: tuple
    publishable_key: str = field(repr=False)
    secret_key: str = field(repr=False)
    jwt_key: str = field(repr=False)
    audience: str = ""

    @classmethod
    def from_env(cls, environ=None):
        env = os.environ if environ is None else environ
        if env.get("MINDER_AUTH_PROVIDER") != "clerk":
            raise AppError("managed_auth_not_configured", 503)
        values = [env.get(key, "").strip() for key in
                  ("CLERK_ISSUER", "CLERK_AUTHORIZED_PARTIES", "CLERK_PUBLISHABLE_KEY",
                   "CLERK_SECRET_KEY", "CLERK_JWT_KEY")]
        if not all(values):
            raise AppError("managed_auth_not_configured", 503)
        issuer, parties, publishable, secret, jwt = values
        parsed = urlsplit(issuer)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
                or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
            raise AppError("managed_auth_invalid_configuration", 503)
        origins = tuple(p.strip() for p in parties.split(",") if p.strip())
        if not origins or len(origins) > 10:
            raise AppError("managed_auth_invalid_configuration", 503)
        for origin in origins:
            part = urlsplit(origin)
            local = env.get("MINDER_ENV") == "development" and part.hostname in ("localhost", "127.0.0.1")
            if (not part.hostname or (part.scheme != "https" and not (local and part.scheme == "http"))
                    or part.username or part.password or part.path or part.query or part.fragment or "*" in origin):
                raise AppError("managed_auth_invalid_configuration", 503)
        if not publishable.startswith(("pk_test_", "pk_live_")) or not secret.startswith(("sk_test_", "sk_live_")):
            raise AppError("managed_auth_invalid_configuration", 503)
        if publishable.split("_", 2)[1] != secret.split("_", 2)[1]:
            raise AppError("managed_auth_invalid_configuration", 503)
        return cls(issuer, origins, publishable, secret, jwt.replace("\\n", "\n"), env.get("CLERK_AUDIENCE", ""))


class ClerkIdentityVerifier:
    def __init__(self, config):
        self.config = config
        try:
            from clerk_backend_api import Clerk
            from clerk_backend_api.security import authenticate_request
            from clerk_backend_api.security.types import AuthenticateRequestOptions
        except ImportError:
            raise AppError("managed_auth_sdk_unavailable", 503) from None
        # Local signature verification avoids JWKS latency on ordinary reads.
        self.authenticate = authenticate_request
        self.options = AuthenticateRequestOptions(jwt_key=config.jwt_key,
            authorized_parties=list(config.authorized_parties), audience=config.audience or None,
            accepts_token=["session_token"], clock_skew_in_ms=0)
        self.client = Clerk(bearer_auth=config.secret_key, timeout_ms=3000)

    def verify_identity(self, token, request_context=None):
        if not isinstance(token, str) or not token or len(token) > 16384 or any(c.isspace() for c in token):
            raise AppError("sign_in_required", 401)
        context = request_context or {}
        origin = context.get("origin")
        if origin and origin not in self.config.authorized_parties:
            raise AppError("sign_in_required", 401)
        try:
            state = self.authenticate(SimpleNamespace(headers={"Authorization": "Bearer " + token}), self.options)
        except Exception:
            raise AppError("sign_in_required", 401) from None
        if not state.is_signed_in or not isinstance(state.payload, dict):
            raise AppError("sign_in_required", 401)
        claims = state.payload
        subject, session = claims.get("sub"), claims.get("sid")
        expires = claims.get("exp")
        if (claims.get("iss") != self.config.issuer or claims.get("azp") not in self.config.authorized_parties
                or not isinstance(subject, str) or not subject.startswith("user_")
                or not isinstance(session, str) or not session.startswith("sess_")
                or type(expires) is not int or expires <= time.time()):
            raise AppError("sign_in_required", 401)
        # A still-valid short JWT must stop authorizing after provider logout.
        # No status cache: revocation is checked on each private request.
        try:
            active = self.client.sessions.get(session_id=session, timeout_ms=3000, retries=None)
        except Exception as error:
            code = 401 if getattr(error, "status_code", None) in (401, 403, 404) else 503
            raise AppError("sign_in_required" if code == 401 else "managed_auth_temporarily_unavailable", code) from None
        if active.status != "active" or active.user_id != subject or active.id != session:
            raise AppError("sign_in_required", 401)
        return VerifiedIdentity(issuer=self.config.issuer, subject=subject, session_id=session, expires_at=expires)


@lru_cache(maxsize=1)
def _verifier(config):
    return ClerkIdentityVerifier(config)


def verify_identity(token, request_context=None):
    """Return SDK-verified immutable identity, or safe AppError401/503."""
    return _verifier(AuthConfig.from_env()).verify_identity(token, request_context)


def public_config():
    """Public login fields only; A owns the actual route and login-state hook."""
    try:
        config = AuthConfig.from_env()
    except AppError:
        return dict(contract_version=CONTRACT_VERSION, provider="clerk", status="unavailable",
                    publishable_key=None, sign_in_path="/", after_sign_in_path="/", after_sign_out_path="/")
    return dict(contract_version=CONTRACT_VERSION, provider="clerk", status="configured",
                publishable_key=config.publishable_key, sign_in_path="/", after_sign_in_path="/", after_sign_out_path="/")
