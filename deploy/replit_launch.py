"""Sanitized workflow-environment evidence before the unchanged Replit runtime.

The diagnostic and application run in the same process. No credentials are
rewritten, persisted, or returned, and no extra server or worker is created.
Diagnostic failure does not change the application's existing auth enforcement.
"""
import json
import os

from deploy.clerk_check import check
from deploy.operator import OperatorError
from deploy.replit_runtime import main as runtime_main, prepare_auth


SAFE_ERRORS = {
    "Clerk_preview_publishable_key_or_issuer_invalid",
    "Clerk_public_JWKS_discovery_failed_no_private_details_disclosed",
    "Clerk_JWKS_rotation_requires_dashboard_PEM_selection",
    "matching_Minder_Development_keys_required_for_server_session_checks",
    "Clerk_server_key_or_instance_verification_failed_no_private_details_disclosed",
    "Clerk_publishable_signing_and_server_keys_belong_to_different_instances",
    "Clerk_hosted_origin_configuration_invalid",
    "CLERK_SECRET_KEY_requires_full_unmasked_ASCII_value_in_private_configuration",
}


def credential_evidence():
    """Return flags and fixed error codes only, never credential material."""
    present = bool(os.environ.get("CLERK_SECRET_KEY"))
    ascii_valid = present and os.environ["CLERK_SECRET_KEY"].isascii()
    result = {
        "event": "minder_workflow_auth_preflight",
        "key_present": present,
        "key_ASCII": ascii_valid,
        "authenticated_instance_match": False,
        "application_uses_same_process_environment": True,
        "secrets_disclosed": False,
    }
    if not present:
        result["code"] = "workflow_clerk_secret_missing"
        return result
    if not ascii_valid:
        result["code"] = "workflow_clerk_secret_non_ascii"
        return result
    try:
        prepare_auth()
        verified = check(dict(os.environ, MINDER_CLERK_INSTANCE_MODE=os.environ.get("MINDER_CLERK_INSTANCE_MODE", "preview")))
        result["authenticated_instance_match"] = (
            verified.get("server_key_matches_public_signing_key") is True
        )
        result["code"] = (
            "workflow_clerk_instance_verified"
            if result["authenticated_instance_match"]
            else "workflow_clerk_instance_not_verified"
        )
    except OperatorError as error:
        result["code"] = (
            str(error) if str(error) in SAFE_ERRORS else "workflow_auth_check_failed"
        )
    except Exception:
        result["code"] = "workflow_auth_check_failed"
    return result


def main():
    print(json.dumps(credential_evidence()), flush=True)
    try:
        runtime_main()
    except Exception:
        print("Minder_Replit_startup_or_worker_failed_check_private_configuration", flush=True)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
