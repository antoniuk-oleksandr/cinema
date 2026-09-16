"""Load layered YAML application configuration."""

import os
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import yaml


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():  # pyright: ignore[reportAny]
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)  # pyright: ignore[reportAny]
        else:
            result[key] = value
    return result


def load_config(base_dir: Path) -> dict[str, Any]:
    """Load common and profile-specific YAML configuration values."""
    config_dir = Path(os.getenv("APP_CONFIG_DIR", base_dir / "config"))
    config_file = os.getenv("APP_CONFIG_FILE")
    base_file = Path(config_file) if config_file else config_dir / "application.yaml"
    data = (
        cast(dict[str, Any], yaml.safe_load(base_file.read_text()) or {})
        if base_file.exists()
        else {}
    )
    profile = os.getenv("APP_PROFILE", "local")
    profile_file = config_dir / f"application.{profile}.yaml"
    if profile_file.exists() and profile_file.resolve() != base_file.resolve():
        data = _merge(data, yaml.safe_load(profile_file.read_text()) or {})
    return data or {}
