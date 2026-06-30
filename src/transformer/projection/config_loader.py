"""Projection config loader and validator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml
from jsonschema import Draft202012Validator

from transformer.projection.errors import CONFIG_MISSING, INVALID_CONFIG, ProjectionConfigError

DEFAULT_PROJECTION_CONFIG_SCHEMA_PATH = "schemas/projection_config.schema.json"


def _resolve_path(path: str) -> Path:
    p = Path(path)
    if p.exists():
        return p
    cwd_p = Path.cwd() / path
    if cwd_p.exists():
        return cwd_p
    project_root = Path(__file__).resolve().parents[3]
    root_p = project_root / path
    if root_p.exists():
        return root_p
    return p


def load_yaml(path: str) -> Dict[str, Any]:
    resolved = _resolve_path(path)
    if not resolved.exists():
        raise ProjectionConfigError(f"{CONFIG_MISSING} Path: {path}")
    with open(resolved, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_projection_config(config: Dict[str, Any], schema_path: str | None = DEFAULT_PROJECTION_CONFIG_SCHEMA_PATH) -> List[str]:
    if schema_path is None:
        return []
    resolved = _resolve_path(schema_path)
    if not resolved.exists():
        # Keep validation optional in environments where only projection files are being tested.
        return []
    with open(resolved, "r", encoding="utf-8") as f:
        schema = json.load(f)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(config), key=lambda e: list(e.path))
    return [f"{'/'.join(str(p) for p in error.path) or '<root>'}: {error.message}" for error in errors]


def load_projection_config(config_path: str, schema_path: str | None = DEFAULT_PROJECTION_CONFIG_SCHEMA_PATH) -> Dict[str, Any]:
    config = load_yaml(config_path)
    errors = validate_projection_config(config, schema_path=schema_path)
    if errors:
        raise ProjectionConfigError(f"{INVALID_CONFIG} " + "; ".join(errors))
    return config
