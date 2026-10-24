"""Private operator preflight and exact-commit Railway deployment.

No account/service/volume creation, interactive signup, password handling or test
identity bypass. Provider secrets stay in memory and never enter command arguments.
"""
import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tarfile
import tempfile
import io
import math
import base64
from urllib.error import HTTPError, URLError
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / ".env.deploy.local"
DEFAULT_CLI = Path("/private/tmp/minder-e-railway-cli/node_modules/.bin/railway")
FIELDS = {
    "RAILWAY_TOKEN", "RAILWAY_PROJECT_ID", "RAILWAY_ENVIRONMENT_ID", "RAILWAY_SERVICE_ID",
    "MINDER_DEPLOY_MAX_USD", "MINDER_JUDGE_URL", "CLERK_PUBLISHABLE_KEY", "CLERK_SECRET_KEY",
    "CLERK_JWT_KEY", "CLERK_ISSUER", "CLERK_AUTHORIZED_PARTIES", "CLERK_AUDIENCE",
    "CLERK_ACCEPTANCE_USER_A", "CLERK_ACCEPTANCE_USER_B", "GROQ_API_KEY", "GROQ_MODEL",
    "MINDER_LLM_DAILY_LIMIT",
}


class OperatorError(Exception):
    pass


def private_config(path=DEFAULT_CONFIG):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "r") as handle:
            info = os.fstat(handle.fileno())
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                    or stat.S_IMODE(info.st_mode) & 0o077 or info.st_size > 32768):
                raise OperatorError("private_config_requires_owner_only_regular_file")
            lines = handle.read().splitlines()
    except (OSError, UnicodeError):
        raise OperatorError("private_config_unavailable") from None
    values = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, value = line.partition("=")
        name, value = name.strip(), value.strip()
        if not separator or name not in FIELDS or name in values:
            raise OperatorError("private_config_invalid_or_unknown_field")
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except ValueError:
                raise OperatorError("private_config_invalid_quoted_value") from None
        elif value.startswith("'"):
            if not value.endswith("'"):
                raise OperatorError("private_config_invalid_quoted_value")
            value = value[1:-1]
        if not isinstance(value, str) or "\x00" in value:
            raise OperatorError("private_config_invalid_value")
        values[name] = value
    return values


def doctor(values):
    needed = FIELDS - {"CLERK_AUDIENCE"}
    return dict(status="ready_for_account_checks" if all(values.get(k) for k in needed) else "account_setup_pending",
                missing_fields=sorted(k for k in needed if not values.get(k)),
                cli_installed=DEFAULT_CLI.is_file(), secrets_disclosed=False)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise OperatorError("provider_redirect_rejected")


def railway(values, query, variables=None):
    if not values.get("RAILWAY_TOKEN"):
        raise OperatorError("railway_project_access_missing")
    payload = json.dumps(dict(query=query, variables=variables or {})).encode()
    request = Request("https://backboard.railway.com/graphql/v2", data=payload, method="POST",
                      headers={"Content-Type": "application/json", "Project-Access-Token": values["RAILWAY_TOKEN"]})
    try:
        with build_opener(NoRedirect()).open(request, timeout=20) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise OperatorError("railway_response_too_large")
        result = json.loads(raw)
    except (HTTPError, URLError, TimeoutError, ValueError):
        raise OperatorError("railway_request_failed_no_response_details_disclosed") from None
    if not isinstance(result, dict) or result.get("errors") or "data" not in result:
        raise OperatorError("railway_request_rejected_no_response_details_disclosed")
    return result["data"]


def verify_target(values):
    target = railway(values, "query { projectToken { projectId environmentId } }")["projectToken"]
    if (target["projectId"] != values.get("RAILWAY_PROJECT_ID")
            or target["environmentId"] != values.get("RAILWAY_ENVIRONMENT_ID")):
        raise OperatorError("railway_token_target_mismatch")
    service = railway(values, "query($id:String!){service(id:$id){id projectId}}",
                      {"id": values.get("RAILWAY_SERVICE_ID")})["service"]
    if service["projectId"] != target["projectId"] or service["id"] != values.get("RAILWAY_SERVICE_ID"):
        raise OperatorError("railway_service_target_mismatch")
    return target


def verify_volume(values):
    schema = railway(values, 'query { __type(name:"VolumeInstance"){fields{name}} }')
    fields = {item["name"] for item in (schema.get("__type") or {}).get("fields", [])}
    if not {"mountPath", "serviceId", "environmentId"}.issubset(fields):
        raise OperatorError("volume_api_schema_requires_review")
    data = railway(values, "query($id:String!){project(id:$id){volumes{edges{node{id "
        "volumeInstances{edges{node{mountPath serviceId environmentId}}}}}}}}",
        {"id": values["RAILWAY_PROJECT_ID"]})
    instances = [instance["node"] for volume in data["project"]["volumes"]["edges"]
                 for instance in volume["node"]["volumeInstances"]["edges"]]
    attached = [item for item in instances if item["serviceId"] == values["RAILWAY_SERVICE_ID"]
                and item["environmentId"] == values["RAILWAY_ENVIRONMENT_ID"]]
    if len(attached) != 1 or attached[0]["mountPath"] != "/data":
        raise OperatorError("one_existing_data_volume_attachment_required")


def approved_release(path):
    try:
        record = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        raise OperatorError("A_release_approval_missing") from None
    if not isinstance(record, dict):
        raise OperatorError("A_release_approval_invalid")
    sha = record.get("approved_sha", "")
    if (record.get("approved_for") != "judge_deployment" or record.get("approved_by") != "A"
            or not re.fullmatch(r"[0-9a-f]{40}", sha) or not record.get("approval_reference")):
        raise OperatorError("A_release_approval_invalid")
    result = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "session/a-personal-integration"],
                            cwd=ROOT, capture_output=True)
    if result.returncode:
        raise OperatorError("approved_release_not_in_A_history")
    remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout.strip()
    if remote != "https://github.com/jahax2154/sdc-2026-minder.git":
        raise OperatorError("official_team_remote_not_verified")
    tip = subprocess.run(["git", "ls-remote", "--exit-code", "origin", "refs/heads/session/a-personal-integration"],
                         cwd=ROOT, capture_output=True, text=True, check=True, timeout=30).stdout.split()[0]
    if subprocess.run(["git", "merge-base", "--is-ancestor", sha, tip], cwd=ROOT, capture_output=True).returncode:
        raise OperatorError("approved_release_not_in_published_A_snapshot")
    return sha


def service_variables(values, sha):
    result = dict(MINDER_ENV="production", MINDER_AUTH_MODE="managed", MINDER_AUTH_PROVIDER="clerk",
                  MINDER_DATA_ROOT="/data", MINDER_DB_PATH="/data/minder/runtime.sqlite3",
                  MINDER_DOCUMENT_STORAGE="private-volume", MINDER_DOCUMENT_STORAGE_ROOT="/data/minder/documents",
                  MINDER_RELEASE_SHA=sha, GROQ_MODEL="qwen/qwen3.8-27b")
    for name in ("CLERK_PUBLISHABLE_KEY", "CLERK_SECRET_KEY", "CLERK_JWT_KEY", "CLERK_ISSUER",
                 "CLERK_AUTHORIZED_PARTIES", "GROQ_API_KEY", "MINDER_LLM_DAILY_LIMIT"):
        if not values.get(name):
            raise OperatorError("runtime_private_configuration_incomplete")
        result[name] = values[name]
    if values.get("CLERK_AUDIENCE"):
        result["CLERK_AUDIENCE"] = values["CLERK_AUDIENCE"]
    if values.get("GROQ_MODEL", "qwen/qwen3.8-27b") != result["GROQ_MODEL"]:
        raise OperatorError("preserve_verified_Qwen_model")
    from minder_app.auth_adapter import AuthConfig
    try:
        auth = AuthConfig.from_env(result)
        if not auth.publishable_key.startswith("pk_live_") or not auth.secret_key.startswith("sk_live_"):
            raise ValueError()
        encoded = auth.publishable_key.split("_", 2)[2]
        frontend_host = base64.b64decode(encoded + "=" * (-len(encoded) % 4), validate=True).decode().removesuffix("$")
        if "https://" + frontend_host != auth.issuer.rstrip("/"):
            raise ValueError()
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
        if not isinstance(load_pem_public_key(auth.jwt_key.encode()), RSAPublicKey):
            raise ValueError()
        site = urlsplit(values.get("MINDER_JUDGE_URL", ""))
        if (site.scheme != "https" or site.username or site.password or site.query or site.fragment
                or site.path not in ("", "/") or site.port not in (None, 443)
                or not site.hostname or site.hostname in ("localhost", "127.0.0.1")
                or (site.scheme + "://" + site.netloc) not in auth.authorized_parties):
            raise ValueError()
    except Exception:
        raise OperatorError("managed_auth_configuration_invalid") from None
    return result


def confirmed_budget(values):
    try:
        limit = float(values.get("MINDER_DEPLOY_MAX_USD", "0"))
        if not math.isfinite(limit) or limit <= 0:
            raise ValueError()
    except ValueError:
        raise OperatorError("confirmed_existing_budget_missing") from None


def prepare_service(values, sha):
    confirmed_budget(values)
    verify_target(values)
    verify_volume(values)
    # Verify the provider's current input shape before mutating settings.
    schema = railway(values, 'query {__type(name:"ServiceInstanceUpdateInput"){inputFields{name}}}')
    fields = {x["name"] for x in schema["__type"]["inputFields"]}
    update = dict(railwayConfigFile="/deploy/railway.json", sleepApplication=False, numReplicas=1)
    if not set(update).issubset(fields):
        raise OperatorError("railway_current_config_schema_requires_review")
    # Values are private JSON request data, never arguments/logs; preserve other variables.
    variables = dict(projectId=values["RAILWAY_PROJECT_ID"], environmentId=values["RAILWAY_ENVIRONMENT_ID"],
                     serviceId=values["RAILWAY_SERVICE_ID"], variables=service_variables(values, sha), skipDeploys=True)
    railway(values, "mutation($input:VariableCollectionUpsertInput!){variableCollectionUpsert(input:$input)}",
            {"input": variables})
    railway(values, "mutation($serviceId:String!,$environmentId:String!,$input:ServiceInstanceUpdateInput!){"
            "serviceInstanceUpdate(serviceId:$serviceId,environmentId:$environmentId,input:$input)}",
            dict(serviceId=values["RAILWAY_SERVICE_ID"], environmentId=values["RAILWAY_ENVIRONMENT_ID"], input=update))
    return dict(status="existing_service_prepared", approved_sha=sha, secrets_disclosed=False)


def deploy(values, sha, cli=DEFAULT_CLI):
    confirmed_budget(values)
    service_variables(values, sha)
    verify_target(values)
    verify_volume(values)
    if not cli.is_file():
        raise OperatorError("railway_cli_missing")
    # Upload exactly A's approved committed tree, never this active checkout/private files.
    source = subprocess.run(["git", "archive", "--format=tar", sha], cwd=ROOT,
                            capture_output=True, check=True).stdout
    with tempfile.TemporaryDirectory(prefix="minder-approved-release-") as folder:
        with tarfile.open(fileobj=io.BytesIO(source)) as archive:
            archive.extractall(folder, filter="data")
        env = {key: os.environ[key] for key in ("PATH", "LANG", "LC_ALL", "SYSTEMROOT") if key in os.environ}
        env.update(RAILWAY_TOKEN=values["RAILWAY_TOKEN"], CI="true", DO_NOT_TRACK="1")
        command = [str(cli), "up", "--detach", "--json", "--project", values["RAILWAY_PROJECT_ID"],
                   "--environment", values["RAILWAY_ENVIRONMENT_ID"], "--service", values["RAILWAY_SERVICE_ID"],
                   "--message", "Minder approved release " + sha]
        result = subprocess.run(command, cwd=folder, env=env, stdin=subprocess.DEVNULL,
                                capture_output=True, timeout=300)
        if result.returncode:
            raise OperatorError("railway_upload_failed_no_private_logs_disclosed")
    return dict(status="deployment_submitted_not_yet_verified", approved_sha=sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("doctor", "inspect", "prepare-service", "deploy"))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--approval", type=Path, default=ROOT / "deploy/RELEASE_APPROVAL.json")
    args = parser.parse_args()
    try:
        values = private_config(args.config)
        if args.operation == "doctor":
            result = doctor(values)
        elif args.operation == "inspect":
            verify_target(values)
            verify_volume(values)
            result = dict(status="existing_project_environment_service_and_volume_verified", secrets_disclosed=False)
        else:
            sha = approved_release(args.approval)
            result = prepare_service(values, sha) if args.operation == "prepare-service" else deploy(values, sha)
        print(json.dumps(result))
    except OperatorError as error:
        print(json.dumps({"status": "blocked", "code": str(error), "secrets_disclosed": False}))
        raise SystemExit(1)
    except (subprocess.SubprocessError, OSError):
        # Do not print exception/CLI/HTTP strings that might carry secret values.
        print(json.dumps({"status": "blocked", "code": "operator_preflight_or_provider_action_failed", "secrets_disclosed": False}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
