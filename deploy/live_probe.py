"""Public hosted boundary checks only; no fabricated login/persistence claims."""
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener
from deploy.operator import (DEFAULT_CONFIG, ROOT, NoRedirect, OperatorError,
                             approved_release, private_config)


def request(origin, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = Request(origin + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        response = build_opener(NoRedirect()).open(req, timeout=20)
    except HTTPError as error:
        response = error
    except (URLError, TimeoutError):
        raise OperatorError("hosted_origin_unreachable") from None
    with response:
        raw = response.read(524289)
        if len(raw) > 524288:
            raise OperatorError("hosted_probe_response_too_large")
        try:
            value = json.loads(raw)
        except ValueError:
            value = None
        return response.status, value


def check(values, sha):
    url = urlsplit(values.get("MINDER_JUDGE_URL", ""))
    if (url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment
            or url.path not in ("", "/") or url.hostname in ("localhost", "127.0.0.1")
            or url.port not in (None, 443)):
        raise OperatorError("verified_https_judge_origin_required")
    origin = url.scheme + "://" + url.netloc
    if origin not in [part.strip() for part in values.get("CLERK_AUTHORIZED_PARTIES", "").split(",")]:
        raise OperatorError("judge_origin_not_in_managed_auth_allowlist")
    code, health = request(origin, "GET", "/api/health")
    if code != 200 or not isinstance(health, dict) or health.get("runtime_revision") != sha:
        raise OperatorError("hosted_revision_or_health_mismatch")
    code, config = request(origin, "GET", "/api/auth/config")
    if (code != 200 or not isinstance(config, dict) or config.get("mode") != "managed" or config.get("anonymous_session_allowed") is not False
            or config.get("provider") != "clerk" or config.get("status") != "configured"):
        raise OperatorError("hosted_managed_sign_in_not_ready")
    for name in ("CLERK_SECRET_KEY", "GROQ_API_KEY", "RAILWAY_TOKEN"):
        if values.get(name) and values[name] in json.dumps(config):
            raise OperatorError("private_configuration_exposure_detected")
    paths = ("/api/auth/session", "/api/profile", "/api/plans", "/api/proposals",
             "/api/product/views/overview", "/api/product/documents", "/api/product/conversations")
    for path in paths:
        if request(origin, "GET", path)[0] != 401:
            raise OperatorError("hosted_unauthenticated_private_read_not_denied")
    if request(origin, "POST", "/api/session", {})[0] != 401:
        raise OperatorError("hosted_anonymous_session_bypass_detected")
    return dict(status="public_hosted_boundary_passed", public_url=origin, deployed_sha=sha,
                private_reads_unauthenticated="denied", anonymous_session="denied",
                live_login=False, two_account_isolation=False, restart_persistence=False,
                hosted_daily_event=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--approval", type=Path, default=ROOT / "deploy/RELEASE_APPROVAL.json")
    args = parser.parse_args()
    try:
        print(json.dumps(check(private_config(args.config), approved_release(args.approval))))
    except OperatorError as error:
        print(json.dumps({"status": "blocked", "code": str(error)}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
