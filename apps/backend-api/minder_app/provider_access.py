"""Explicit post-confirmation discovery/verification. Prints booleans only."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from minder_ml.intelligence.groq_adapter import GroqAdapter, ProviderError
from .config import ConfigError, ROOT, load_provider_config

# Preferences only, never assumed accessible. Intersect with this account's
# actual /models response, then verify chat AND native tool use before activation.
TOOL_MODELS = ("openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant")


def selection_path(environ=None):
    environ = os.environ if environ is None else environ
    base = Path(environ.get("MINDER_ARTIFACT_DIR", ROOT / "ml/artifacts/session-c"))
    return base / "runtime/groq-model-selection.json"


def selected_model(path=None):
    """Nonsecret verified model metadata; no credential is stored here."""
    target = Path(path) if path is not None else selection_path()
    if not target.exists():
        return ""
    if target.is_symlink() or target.stat().st_uid != os.getuid() or target.stat().st_size > 4096:
        raise ConfigError("provider_selection_file_invalid")
    try:
        data = json.loads(target.read_text())
        model = data["model"]
        if not (data.get("chat_verified") is True and data.get("tool_verified") is True and
                isinstance(model, str) and model and all(c.isalnum() or c in "_./:-" for c in model)):
            raise ValueError()
        return model
    except (ValueError, KeyError, TypeError, OSError):
        raise ConfigError("provider_selection_file_invalid") from None


def verify(config, *, provider=None, path=None):
    result = dict(api_key_present=bool(config.api_key), model_accessible=False,
        discovery_request_success=False, chat_request_success=False, tool_request_success=False,
        verified_selection_saved=False)
    if not config.api_key:
        return result
    provider = provider or GroqAdapter(key=config.api_key, model=config.model, retries=0)
    try:
        available = provider.models()
        result["discovery_request_success"] = True
        model = config.model or next((m for m in TOOL_MODELS if m in available), "")
        if not model or model not in available:
            return result
        provider.model = model
        result["model_accessible"] = True
        reply = provider.complete([dict(role="user", content="Reply only OK.")], max_tokens=128)
        result["chat_request_success"] = reply["status"] == "available"
        tool = {"type": "function", "function": {"name": "check_local_readiness",
            "description": "Report readiness only. No writes or external actions.",
            "parameters": {"type": "object", "additionalProperties": False,
                "properties": {"ready": {"const": True}}, "required": ["ready"]}}}
        reply = provider.complete_tool([dict(role="user", content="Call check_local_readiness with ready true.")],
                                       tool, max_tokens=256)
        result["tool_request_success"] = (reply["status"] == "available" and
            json.loads(reply["text"]) == {"ready": True} and reply.get("tool_call", {}).get("arguments_validated") is True)
        if not result["chat_request_success"] or not result["tool_request_success"]:
            return result
        target = Path(path) if path is not None else selection_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".groq-model-", dir=target.parent)
        try:
            with os.fdopen(fd, "w") as handle:
                json.dump(dict(model=model, chat_verified=True, tool_verified=True,
                    verified_at=datetime.now(timezone.utc).isoformat()), handle)
            os.replace(name, target)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        result["verified_selection_saved"] = True
    except (ProviderError, ConfigError, ValueError, TypeError, KeyError, OSError):
        pass  # no raw exception/provider bodies/values are printed or returned
    return result


def main():
    try:
        config = load_provider_config()
        result = verify(config)
    except ConfigError:
        result = dict(configuration_accepted=False, request_success=False)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
