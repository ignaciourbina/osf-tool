"""Config and auth resolution for the OSF SDK and CLI."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import OSFConfigError

DEFAULT_API_BASE = "https://api.osf.io/v2/"
DEFAULT_TIMEOUT = 30.0
DEFAULT_PROFILE = "default"
TOKEN_ENV_VAR = "OSF_TOKEN"
PROFILE_ENV_VAR = "OSF_PROFILE"
CONFIG_ENV_VAR = "OSF_CONFIG"
API_BASE_ENV_VAR = "OSF_API_BASE"
TIMEOUT_ENV_VAR = "OSF_TIMEOUT"
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "osf-tool" / "config.toml"
LEGACY_CREDENTIALS_FILE = Path(__file__).resolve().parents[1] / "osf-credentials.txt"


@dataclass(slots=True)
class ResolvedSettings:
    token: str
    profile: str
    base_url: str
    timeout: float
    config_path: Path
    token_source: str


def load_legacy_token(path: Path = LEGACY_CREDENTIALS_FILE) -> str:
    """Read a TOKEN entry from the legacy credentials file."""
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip().lower() == "token":
            token = value.strip()
            if token:
                return token
    raise OSFConfigError(f"No TOKEN found in {path}")


def _load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text())


def _profile_data(config: dict[str, Any], profile: str) -> dict[str, Any]:
    profiles = config.get("profiles", {})
    if isinstance(profiles, dict):
        data = profiles.get(profile, {})
        if isinstance(data, dict):
            return data
    return {}


def resolve_settings(
    *,
    token: str | None = None,
    profile: str | None = None,
    config_path: str | Path | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
    legacy_credentials_path: str | Path | None = None,
) -> ResolvedSettings:
    """Resolve auth/config using explicit args, env vars, then config profiles."""
    resolved_config_path = Path(
        config_path or os.getenv(CONFIG_ENV_VAR, "") or DEFAULT_CONFIG_PATH
    ).expanduser()
    config = _load_config(resolved_config_path)

    resolved_profile = (
        profile
        or os.getenv(PROFILE_ENV_VAR, "").strip()
        or config.get("default_profile")
        or DEFAULT_PROFILE
    )
    profile_data = _profile_data(config, resolved_profile)

    token_source = "explicit"
    resolved_token = token
    if not resolved_token:
        resolved_token = os.getenv(TOKEN_ENV_VAR, "").strip() or None
        if resolved_token:
            token_source = "env"
    if not resolved_token:
        profile_token = profile_data.get("token")
        if isinstance(profile_token, str) and profile_token.strip():
            resolved_token = profile_token.strip()
            token_source = f"profile:{resolved_profile}"
    if not resolved_token:
        legacy_path = Path(legacy_credentials_path) if legacy_credentials_path else LEGACY_CREDENTIALS_FILE
        if legacy_path.exists():
            resolved_token = load_legacy_token(legacy_path)
            token_source = f"legacy:{legacy_path}"
    if not resolved_token:
        raise OSFConfigError(
            "No OSF token found. Set --token, OSF_TOKEN, or a config profile token."
        )

    resolved_base_url = (
        base_url
        or os.getenv(API_BASE_ENV_VAR, "").strip()
        or profile_data.get("api_base")
        or DEFAULT_API_BASE
    )

    timeout_value: float
    if timeout is not None:
        timeout_value = float(timeout)
    else:
        env_timeout = os.getenv(TIMEOUT_ENV_VAR, "").strip()
        if env_timeout:
            timeout_value = float(env_timeout)
        elif profile_data.get("timeout") is not None:
            timeout_value = float(profile_data["timeout"])
        else:
            timeout_value = DEFAULT_TIMEOUT

    return ResolvedSettings(
        token=resolved_token,
        profile=resolved_profile,
        base_url=resolved_base_url,
        timeout=timeout_value,
        config_path=resolved_config_path,
        token_source=token_source,
    )
