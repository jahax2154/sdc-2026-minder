"""One Groq transport for explanations and agents; never executes model tools.

Credentials, prompts, responses and personal data are deliberately absent from logs.
No default model: discover /models and require an explicitly configured model ID.
"""
import json
import logging
import os
import socket
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LOG = logging.getLogger(__name__)
BASE = "https://api.groq.com/openai/v1"


def safe_usage(data):
    usage = data.get("usage") or {}
    if not isinstance(usage, dict):
        raise ValueError("invalid usage")
    return {k: v for k, v in usage.items()
            if k in ("prompt_tokens", "completion_tokens", "total_tokens") and type(v) is int and v >= 0}


class ProviderError(Exception):
    def __init__(self, code, request_id, *, retryable=False):
        super().__init__(code)
        self.code, self.request_id, self.retryable = code, request_id, retryable

    def public(self):
        return dict(status="unavailable", code=self.code, request_id=self.request_id)


class GroqAdapter:
    def __init__(self, *, key=None, model=None, timeout=12, retries=1,
                 opener=urlopen, sleep=time.sleep):
        self.key = key if key is not None else os.environ.get("GROQ_API_KEY")
        self.model = model if model is not None else os.environ.get("GROQ_MODEL")
        self.timeout = max(1, min(timeout, 20))
        self.retries = max(0, min(retries, 2))
        self.opener, self.sleep = opener, sleep

    def _request(self, path, payload=None):
        rid = str(uuid.uuid4())
        if not self.key:
            raise ProviderError("provider_credentials_missing", rid)
        body = json.dumps(payload).encode() if payload is not None else None
        request = Request(BASE + path, data=body, headers={
            "Authorization": "Bearer " + self.key, "Content-Type": "application/json",
            "X-Request-ID": rid})
        for attempt in range(self.retries + 1):
            try:
                with self.opener(request, timeout=self.timeout) as response:
                    raw = response.read(262145)
                    if len(raw) > 262144:
                        raise ValueError("response too large")
                    data = json.loads(raw)
                    if not isinstance(data, dict):
                        raise ValueError("invalid response")
                    upstream_id = response.headers.get("x-request-id", rid)
                LOG.info("groq request_id=%s attempt=%s usage=%s", rid, attempt,
                         safe_usage(data))
                return data, upstream_id
            except HTTPError as exc:
                status = exc.code
                retryable = status == 429 or status >= 500
                code = {401: "provider_auth_failed", 403: "provider_access_denied",
                        404: "provider_model_unavailable", 429: "provider_rate_limited"}.get(
                            status, "provider_http_error")
                exc.close()  # never print upstream error bodies or headers
            except (URLError, TimeoutError, socket.timeout):
                retryable, code = True, "provider_network_or_timeout"
            except (ValueError, TypeError, KeyError):
                raise ProviderError("provider_invalid_response", rid) from None
            if not retryable or attempt == self.retries:
                raise ProviderError(code, rid, retryable=retryable) from None
            self.sleep(min(2 ** attempt, 2))

    def models(self):
        data, _ = self._request("/models")
        try:
            return sorted(x["id"] for x in data["data"] if x.get("active", True))
        except (KeyError, TypeError):
            raise ProviderError("provider_invalid_response", str(uuid.uuid4())) from None

    def complete(self, messages, *, max_tokens=512):
        if not self.model:
            raise ProviderError("provider_model_not_configured", str(uuid.uuid4()))
        data, rid = self._request("/chat/completions", dict(
            model=self.model, messages=messages, temperature=0,
            max_completion_tokens=min(max(1, max_tokens), 1024)))
        try:
            value = data["choices"][0]["message"]["content"]
            if not isinstance(value, str) or not value.strip():
                raise ValueError()
            return dict(status="available", text=value, request_id=rid,
                        model=self.model, usage=safe_usage(data))
        except (KeyError, IndexError, TypeError, ValueError):
            raise ProviderError("provider_invalid_response", rid) from None

    def complete_tool(self, messages, tool, *, max_tokens=512):
        """One forced local function request; returns validated args, never executes.

        Application-supplied schema is the only tool exposed. No external tools,
        LLM-supplied authority or arbitrary mutation names are supported here.
        """
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import ValidationError
        if not self.model:
            raise ProviderError("provider_model_not_configured", str(uuid.uuid4()))
        name = tool["function"]["name"]
        schema = tool["function"]["parameters"]
        data, rid = self._request("/chat/completions", dict(model=self.model, messages=messages,
            temperature=0, max_completion_tokens=min(max(1, max_tokens), 1024), tools=[tool],
            tool_choice={"type": "function", "function": {"name": name}}, parallel_tool_calls=False))
        try:
            calls = data["choices"][0]["message"]["tool_calls"]
            if not isinstance(calls, list) or len(calls) != 1:
                raise ValueError()
            call = calls[0]
            if call["type"] != "function" or call["function"]["name"] != name:
                raise ValueError()
            args = json.loads(call["function"]["arguments"])
            Draft202012Validator(schema).validate(args)
            if not isinstance(call["id"], str) or not call["id"] or len(call["id"]) > 256:
                raise ValueError()
            return dict(status="available", text=json.dumps(args), request_id=rid,
                        model=self.model, usage=safe_usage(data),
                        tool_call={"name": name, "id": call["id"], "arguments_validated": True})
        except (KeyError, IndexError, TypeError, ValueError, ValidationError):
            raise ProviderError("provider_tool_response_invalid", rid) from None

    def probe(self):
        """Bounded real-access check. Outputs metadata only, never response text."""
        try:
            models = self.models()
            if not self.model or self.model not in models:
                return dict(status="limited", code="select_GROQ_MODEL_from_discovery",
                            available_models=models)
            result = self.complete([{"role": "user", "content": "Reply only OK."}], max_tokens=8)
            return {k: result[k] for k in ("status", "model", "request_id", "usage")}
        except ProviderError as exc:
            return exc.public()


if __name__ == "__main__":
    print(json.dumps(GroqAdapter().probe(), sort_keys=True))
