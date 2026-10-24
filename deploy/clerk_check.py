"""Private Clerk instance preflight; never a substitute for live login acceptance."""
import base64
import json
from deploy.operator import (OperatorError, DEFAULT_CONFIG, private_config,
                             derive_clerk_public, save_derived_public)


def check(values):
    if (values.get("MINDER_CLERK_INSTANCE_MODE") != "preview"
            or not values.get("CLERK_PUBLISHABLE_KEY", "").startswith("pk_test_")
            or not values.get("CLERK_SECRET_KEY", "").startswith("sk_test_")):
        raise OperatorError("matching_Minder_Development_keys_required_for_server_session_checks")
    secret = values["CLERK_SECRET_KEY"]
    if not secret.isascii() or any(character.isspace() for character in secret):
        raise OperatorError("CLERK_SECRET_KEY_requires_full_unmasked_ASCII_value_in_private_configuration")
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
        from clerk_backend_api import Clerk
        public = load_pem_public_key(values["CLERK_JWT_KEY"].replace("\\n", "\n").encode())
        if not isinstance(public, RSAPublicKey):
            raise ValueError()
        fresh = derive_clerk_public(dict(values, CLERK_JWT_KEY=""))
        published = load_pem_public_key(fresh["CLERK_JWT_KEY"].encode())
        if not isinstance(published, RSAPublicKey) or published.public_numbers() != public.public_numbers():
            raise ValueError()
        # This authenticated operation actually needs the server secret. Public
        # Frontend API key discovery in derive-clerk does not use it.
        client = Clerk(bearer_auth=values["CLERK_SECRET_KEY"], timeout_ms=5000)
        keys = client.jwks.get_jwks(timeout_ms=5000, retries=None).keys
        expected = public.public_numbers()
        def number(encoded):
            return int.from_bytes(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)), "big")
        matched = any(key.kty == "RSA" and number(key.n) == expected.n and number(key.e) == expected.e
                      for key in keys)
    except Exception:
        raise OperatorError("Clerk_server_key_or_instance_verification_failed_no_private_details_disclosed") from None
    if not matched:
        raise OperatorError("Clerk_publishable_signing_and_server_keys_belong_to_different_instances")
    origin_ready = False
    if values.get("MINDER_JUDGE_URL") and values.get("CLERK_AUTHORIZED_PARTIES"):
        from minder_app.auth_adapter import AuthConfig
        try:
            AuthConfig.from_env(dict(values, MINDER_ENV="production", MINDER_AUTH_PROVIDER="clerk"))
            origin_ready = values["MINDER_JUDGE_URL"].rstrip("/") in values["CLERK_AUTHORIZED_PARTIES"].split(",")
        except Exception:
            raise OperatorError("Clerk_hosted_origin_configuration_invalid") from None
    return dict(status="Clerk_Development_instance_key_pair_verified", server_key_matches_public_signing_key=True,
                hosted_origin_configured=origin_ready, live_login=False, two_account_isolation=False,
                secrets_disclosed=False)


def main():
    try:
        values = private_config(DEFAULT_CONFIG)
        updates = derive_clerk_public(values)
        save_derived_public(DEFAULT_CONFIG, values, updates)
        print(json.dumps(check(dict(values, **updates))))
    except OperatorError as error:
        print(json.dumps(dict(status="blocked", code=str(error), secrets_disclosed=False)))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
