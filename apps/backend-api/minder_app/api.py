"""Thin JSON WSGI API. Bearer capabilities isolate anonymous local demo users.

No user-selected owner, no cookies/CORS, no LLM route into mutation handlers.
Production identity and durable hosting remain integration/deployment work.
"""
import json
import os
from pathlib import Path
import uuid
from wsgiref.simple_server import make_server
from jsonschema.exceptions import ValidationError
from minder_ml.intelligence.app_context import CareerServices
from .profiles import save_profile, intake_draft
from .store import Store, AppError


class Application:
    def __init__(self, store, services=None, provider=None):
        self.store, self.services, self.provider = store, services or CareerServices(), provider
        from .actions import ActionExecutor
        self.actions = ActionExecutor(store)
        from .agents import migrate
        migrate(store)

    def dispatch(self, method, path, body, token):
        if path == "/api/health" and method == "GET":
            return {"status": "ok", "integration_mode": self.services.mode}
        if path == "/api/session" and method == "POST":
            return self.store.session()
        owner = self.store.authenticate(token)
        if path == "/api/direct-action" and method == "POST":
            return self.actions.direct(owner, body["request"], body["idempotency_key"])
        if path == "/api/proposals":
            if method == "GET":
                return {"proposals": self.actions.proposals(owner)}
            if method == "POST":
                return self.actions.propose(owner, body["request"])
        if path == "/api/proposal-decision" and method == "POST":
            return self.actions.decide(owner, **body)
        if path == "/api/action-history" and method == "GET":
            return {"history": self.actions.history(owner)}
        if path == "/api/undo" and method == "POST":
            return self.actions.undo(owner, body["action_id"], body["expected_state_version"], body["idempotency_key"])
        if path == "/api/agent-settings":
            from .agents import configure
            if method == "PUT":
                return configure(self.store, owner, body["settings"], body.get("expected_version"))
            if method == "GET":
                return self.store.get(owner, "agent_settings", owner)
        if path == "/api/agents" and method == "GET":
            from .agents import state
            return state(self.store, owner)
        if path == "/api/profile":
            if method == "GET":
                return self.store.get(owner, "profile", owner)
            if method == "PUT":
                return save_profile(self.store, owner, body["profile"], body.get("expected_version"))
        if path == "/api/intake" and method == "POST":
            return intake_draft(self.store, owner, **body)
        if path == "/api/chat" and method == "POST":
            from .chat import chat
            return chat(self.store, self.services, self.provider, owner,
                        body["message"], body["expected_profile_version"])
        if path == "/api/plans":
            from .plans import create_plan
            if method == "GET":
                return {"plans": self.store.list(owner, "plan")}
            if method == "POST":
                return create_plan(self.store, owner, body["plan"], body["idempotency_key"])
        if path == "/api/company-explorer" and method == "POST":
            from .companies import CompanyExplorer
            profile = self.store.get(owner, "profile", owner)
            return CompanyExplorer(self.services).explore(profile, body["employer_id"], body.get("role_id"))
        if path == "/api/career-context" and method == "GET":
            profile = self.store.get(owner, "profile", owner)
            return self.services.public_context(self.services.career_context(
                profile, expected_profile_version=profile["version"]))
        raise AppError("not_found", 404)

    def __call__(self, environ, start_response):
        rid, status = str(uuid.uuid4()), 200
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
            if length < 0 or length > 131072:
                raise AppError("request_too_large", 413)
            raw = environ["wsgi.input"].read(length)
            body = json.loads(raw) if raw else {}
            if not isinstance(body, dict):
                raise AppError("object_body_required")
            auth = environ.get("HTTP_AUTHORIZATION", "")
            token = auth[7:] if auth.startswith("Bearer ") else ""
            result = self.dispatch(environ["REQUEST_METHOD"], environ["PATH_INFO"], body, token)
        except AppError as exc:
            status, result = exc.status, {"code": exc.code, "request_id": rid}
        except (ValueError, KeyError, TypeError, ValidationError):
            status, result = 422, {"code": "invalid_request_or_service_contract", "request_id": rid}
        except Exception:
            status, result = 500, {"code": "internal_error", "request_id": rid}
        raw = json.dumps(result, allow_nan=False).encode()
        start_response(str(status) + " " + {200: "OK", 401: "Unauthorized", 404: "Not Found",
            409: "Conflict", 413: "Too Large", 415: "Unsupported", 422: "Invalid", 500: "Error"}.get(status, "Error"),
            [("Content-Type", "application/json"), ("Cache-Control", "no-store"),
             ("Content-Length", str(len(raw))), ("X-Content-Type-Options", "nosniff")])
        return [raw]


def main():
    root = Path(__file__).resolve().parents[3]
    path = os.environ.get("MINDER_DB_PATH", str(root / "ml/artifacts/session-c/runtime/dev.sqlite3"))
    with make_server("127.0.0.1", int(os.environ.get("MINDER_API_PORT", "8103")),
                     Application(Store(path))) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
