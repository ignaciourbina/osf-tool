"""Tests for auth/config precedence."""

from __future__ import annotations

from pathlib import Path

from osf_api_cli.config import resolve_settings


def test_explicit_token_beats_env_and_profile(monkeypatch, tmp_path):
    config = tmp_path / "config.toml"
    config.write_text("[profiles.default]\ntoken = 'profile-token'\n")
    monkeypatch.setenv("OSF_TOKEN", "env-token")
    settings = resolve_settings(
        token="explicit-token",
        config_path=config,
        legacy_credentials_path=tmp_path / "missing.txt",
    )
    assert settings.token == "explicit-token"
    assert settings.token_source == "explicit"


def test_profile_token_used_when_env_missing(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text(
        "[profiles.lab]\n"
        "token = 'lab-token'\n"
        "api_base = 'https://api.example/'\n"
        "timeout = 12\n"
    )
    settings = resolve_settings(
        profile="lab",
        config_path=config,
        legacy_credentials_path=tmp_path / "missing.txt",
    )
    assert settings.token == "lab-token"
    assert settings.profile == "lab"
    assert settings.base_url == "https://api.example/"
    assert settings.timeout == 12.0
    assert settings.token_source == "profile:lab"
