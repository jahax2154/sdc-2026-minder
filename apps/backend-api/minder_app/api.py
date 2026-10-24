"""Thin JSON WSGI API. Bearer capabilities isolate anonymous local demo users.

No user-selected owner, no cookies/CORS, no LLM route into mutation handlers.
Production identity and durable hosting remain integration/deployment work.
"""
import json
import os
import time
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
        from .message_orchestrator import bind
        bind(self)

    def dispatch(self, method, path, body, token, *, request_id=None, request_context=None):
        if path == "/api/health" and method == "GET":
            result={"status": "ok", "integration_mode": self.services.mode}
            if hasattr(self,'runtime_revision'):result['runtime_revision']=self.runtime_revision
            if hasattr(self,'local_worker_thread'):result['local_worker_running']=self.local_worker_thread.is_alive()
            return result
        from .identity_boundary import authenticated_owner, managed, public_configuration
        if path == '/api/auth/config' and method == 'GET':
            return public_configuration(self)
        if path == "/api/session" and method == "POST":
            if managed(self):
                raise AppError('managed_sign_in_required', 401)
            return self.store.session()
        owner = authenticated_owner(self, token, request_context)
        if path == '/api/auth/session' and method == 'GET':
            return dict(authenticated=True, user=dict(id=owner), mode='managed' if managed(self) else 'local')
        if path.startswith('/api/product/'):
            from .product_routes import dispatch
            return dispatch(self, owner, method, path, body)
        if path == "/api/assessment-reference" and method == "GET":
            if self.services.personal is None:
                raise AppError("assessment_unavailable", 404)
            return self.services.personal.reference()
        if path == "/api/role-evidence" and method == "POST":
            personal = self.services.personal
            if personal is None or not hasattr(personal, "evidence_for"):
                raise AppError("evidence_service_unavailable", 404)
            from .role_display import resolve_role
            role, selection = resolve_role(self, owner, body)
            result = personal.evidence_for(role)
            result = dict(result, role_selection=selection)
            from .role_display import forecast_view
            result.update(forecast_view(self, role))
            if body.get("trace_id"):
                profile = self.store.get(owner, "profile", owner)
                if body.get("expected_profile_version") != profile["version"]:
                    raise AppError("stale_trace_profile_version", 409)
                context = self.services.career_context(profile,
                    expected_profile_version=profile["version"], selected_role_ids=body.get("view_role_ids"))
                trace = next((t for t in context["recommendation"]["internal"].get("recommendation_traces", [])
                              if t["role_id"] == role["role_id"] and t["trace_id"] == body["trace_id"]), None)
                if trace is None:
                    raise AppError("trace_stale_or_outside_profile_view", 409)
                from minder_ml.intelligence.market_evidence import public_trace
                result["trace"] = public_trace(trace)
            return result
        if path == "/api/source-market-catalogue" and method == "GET":
            if self.services.market is None or not hasattr(self.services.market, "current_context_catalogue"):
                raise AppError("source_context_unavailable", 404)
            from datetime import datetime, timezone
            return dict(records=self.services.market.current_context_catalogue(as_of=datetime.now(timezone.utc).isoformat()),
                limitation="Source-native facts, not a canonical role catalogue or a count leaderboard. No role mapping is inferred.")
        if path == "/api/source-market-context" and method == "POST":
            if self.services.market is None or not hasattr(self.services.market, "current_context"):
                raise AppError("source_context_unavailable", 404)
            from datetime import datetime, timezone
            return self.services.market.current_context(as_of=datetime.now(timezone.utc).isoformat(),
                occupation_system=body.get("occupation_system"),occupation_version=body.get("occupation_version"),
                occupation_code=body.get("occupation_code"),evidence_ids=body.get("evidence_ids"))
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
        if path == "/api/roles" and method == "POST":
            query = str(body.get("query", "")).casefold()
            offset = max(0, int(body.get("offset", 0)))
            limit = max(1, min(50, int(body.get("limit", 20))))
            selected = [r for r in self.services.roles if query in (r["label"] + " " + r["role_id"]).casefold()]
            return dict(total=len(selected), offset=offset, catalogue_order_not_rank=True,
                roles=[{k: r[k] for k in ("role_id", "label", "eligibility", "missing_reasons")}
                       for r in selected[offset:offset + limit]],
                applied_query=query, can_clear_filter=True)
        if path == "/api/role-requirements" and method == "POST":
            from .role_display import resolve_role, presentation
            role, selection = resolve_role(self, owner, body)
            return dict(role=role, role_selection=selection, display=presentation(self, owner, role),
                limitation="Occupational reference ratings describe the work; they do not establish your competence.")
        if path == "/api/profile":
            if method == "GET":
                return self.store.get(owner, "profile", owner)
            if method == "PUT":
                from .starter import normal_intake
                body = dict(body, profile=normal_intake(self, owner, body['profile']))
                return save_profile(self.store, owner, body["profile"], body.get("expected_version"))
        if path == "/api/intake" and method == "POST":
            return intake_draft(self.store, owner, **body)
        if path == "/api/chat" and method == "POST":
            from .chat import chat
            return chat(self.store, self.services, self.provider, owner,
                        body["message"], body.get("expected_profile_version"),
                        body.get("selected_role_ids"), body.get("selected_skill_ids"),
                        body.get("previous_context_id"), request_id=request_id, app=self)
        if path == "/api/plans":
            from .plans import create_plan
            if method == "GET":
                return {"plans": self.store.list(owner, "plan")}
            if method == "POST":
                return create_plan(self.store, owner, body["plan"], body["idempotency_key"], body.get("design"))
        if path == "/api/pathway-preview" and method == "POST":
            from .pathways import preview
            return preview(self.services, self.store.get(owner, "profile", owner), body["role_id"])
        if path == "/api/plan-designs" and method == "GET":
            return {"designs": self.store.list(owner, "plan_design")}
        if path == "/api/learning-resources" and method in ("GET", "POST"):
            from .resources import learning_options
            return learning_options(body.get("topic_ids"))
        if path == "/api/company-explorer" and method == "POST":
            from .companies import CompanyExplorer
            profile = self.store.get(owner, "profile", owner)
            return CompanyExplorer(self.services).explore(profile, body["employer_id"], body.get("role_id"))
        if path == "/api/career-context" and method in ("GET", "POST"):
            profile = self.store.get(owner, "profile", owner)
            return self.services.public_context(self.services.career_context(
                profile, expected_profile_version=profile["version"],
                selected_role_ids=body.get("selected_role_ids"), selected_skill_ids=body.get("selected_skill_ids")))
        raise AppError("not_found", 404)

    def __call__(self, environ, start_response):
        rid, status = str(uuid.uuid4()), 200
        started = time.perf_counter()
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
            from .product_routes import request_body_limit
            limit = request_body_limit(environ['REQUEST_METHOD'], environ['PATH_INFO'])
            if length < 0 or length > limit:
                raise AppError("request_too_large", 413)
            raw = environ["wsgi.input"].read(length)
            body = json.loads(raw) if raw else {}
            if not isinstance(body, dict):
                raise AppError("object_body_required")
            auth = environ.get("HTTP_AUTHORIZATION", "")
            token = auth[7:] if auth.startswith("Bearer ") else ""
            result = self.dispatch(environ["REQUEST_METHOD"], environ["PATH_INFO"], body, token, request_id=rid,
                request_context={'origin': environ.get('HTTP_ORIGIN')})
        except AppError as exc:
            status, result = exc.status, {"code": exc.code, "request_id": rid}
        except (ValueError, KeyError, TypeError, ValidationError):
            status, result = 422, {"code": "invalid_request_or_service_contract", "request_id": rid}
        except Exception:
            status, result = 500, {"code": "internal_error", "request_id": rid}
        raw = json.dumps(result, allow_nan=False).encode()
        start_response(str(status) + " " + {200: "OK", 401: "Unauthorized", 404: "Not Found",
            409: "Conflict", 413: "Too Large", 415: "Unsupported", 422: "Invalid", 500: "Error", 503: "Unavailable"}.get(status, "Error"),
            [("Content-Type", "application/json"), ("Cache-Control", "no-store"),
             ("Content-Length", str(len(raw))), ("X-Content-Type-Options", "nosniff"),
             ("X-Request-ID", rid), ("Server-Timing", "application;dur=%.3f" % ((time.perf_counter()-started)*1000))])
        return [raw]


def main():
    from .runtime import application
    with make_server("127.0.0.1", int(os.environ.get("MINDER_API_PORT", "8103")),
                     application()) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
