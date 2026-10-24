"""Map only server-verified external identities, never claim local anonymous data."""
from .auth_adapter import VerifiedIdentity
from .store import AppError, now, uid
from .product_migrations import migrate


def owner_for_identity(store, identity):
    """Internal boundary: A calls after E's SDK verification, never from client JSON.

    Signature/token verification belongs to E; this function persists that mapping.
    No email/display-name matching, default-user bypass or anonymous-owner adoption.
    """
    if not isinstance(identity, VerifiedIdentity):
        raise AppError("verified_identity_required", 401)
    issuer, subject = identity.get("issuer"), identity.get("subject")
    if any(not isinstance(value, str) or not value.strip() or len(value) > 2048
           or any(ord(c) < 32 for c in value) for value in (issuer, subject)):
        raise AppError("verified_identity_required", 401)
    migrate(store)
    with store.transaction() as db:
        row = db.execute("SELECT owner FROM external_identities WHERE issuer=? AND subject=?",
                         (issuer, subject)).fetchone()
        if row:
            return row["owner"]
        owner = uid()
        db.execute("INSERT INTO app_users VALUES(?,?)", (owner, now()))
        db.execute("INSERT INTO external_identities VALUES(?,?,?)", (issuer, subject, owner))
        return owner


# Compatibility with A's committed common identity boundary.
resolve_owner = owner_for_identity
