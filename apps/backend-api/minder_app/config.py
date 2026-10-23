"""Owner-only, allowlisted provider secrets. Never sources shell or logs values."""
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import stat

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SECRET_FILE = ROOT / ".env.groq.local"
ALLOWED = {"GROQ_API_KEY", "GROQ_MODEL", "MINDER_LLM_DAILY_LIMIT"}


class ConfigError(Exception):
    """Safe code only; do not attach file lines, values or underlying exceptions."""


@dataclass(frozen=True, repr=False)
class ProviderConfig:
    api_key: str = field(repr=False, default="")
    model: str = field(repr=False, default="")
    daily_limit: int = 20

    def __repr__(self):
        return "<ProviderConfig redacted>"

    def presence(self):
        return {"api_key_present": bool(self.api_key), "model_configured": bool(self.model)}


def _read_secret_file(path):
    """Refuse symlinks, other-owner files and group/world access before reading."""
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    except FileNotFoundError:
        return {}
    except OSError:
        raise ConfigError("secret_file_open_failed") from None
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) & 0o077):
            raise ConfigError("secret_file_requires_owner_only_regular_file")
        if info.st_size > 8192:
            raise ConfigError("secret_file_too_large")
        with os.fdopen(fd, "r", encoding="utf-8") as handle:
            fd = None
            content = handle.read(8193)
        if len(content.encode()) > 8192:
            raise ConfigError("secret_file_too_large")
        values = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ConfigError("secret_file_invalid_assignment")
            name, value = line.split("=", 1)
            name, value = name.strip(), value.strip()
            if name not in ALLOWED:
                raise ConfigError("secret_file_unknown_variable")
            if name in values:
                raise ConfigError("secret_file_duplicate_variable")
            if value.startswith(("'", '"')):
                if len(value) < 2 or value[-1] != value[0]:
                    raise ConfigError("secret_file_invalid_quotes")
                value = value[1:-1]
            if any(ord(c) < 32 or ord(c) == 127 for c in value):
                raise ConfigError("secret_file_invalid_value")
            # Literal values only: no interpolation, command substitution or eval.
            values[name] = value
        return values
    except (UnicodeError, OSError):
        raise ConfigError("secret_file_read_failed") from None
    finally:
        if fd is not None:
            os.close(fd)


def load_provider_config(*, path=None, environ=None):
    environ = os.environ if environ is None else environ
    selected = Path(path if path is not None else environ.get("MINDER_GROQ_SECRET_FILE", DEFAULT_SECRET_FILE))
    if not selected.is_absolute():
        raise ConfigError("secret_file_path_must_be_absolute")
    values = _read_secret_file(selected)
    for name in ALLOWED:
        if environ.get(name):
            values[name] = environ[name]  # inherited non-empty environment wins
    model = values.get("GROQ_MODEL", "")
    if model and not re.fullmatch(r"[A-Za-z0-9_./:-]+", model):
        raise ConfigError("provider_model_id_invalid")
    try:
        limit = int(values.get("MINDER_LLM_DAILY_LIMIT", "20"))
    except (ValueError, TypeError):
        raise ConfigError("provider_daily_limit_invalid") from None
    if not 1 <= limit <= 100:
        raise ConfigError("provider_daily_limit_invalid")
    return ProviderConfig(api_key=values.get("GROQ_API_KEY", ""), model=model, daily_limit=limit)


def configured_provider():
    from minder_ml.intelligence.groq_adapter import GroqAdapter
    config = load_provider_config()
    provider = GroqAdapter(key=config.api_key, model=config.model)
    provider.daily_limit = config.daily_limit
    return provider
