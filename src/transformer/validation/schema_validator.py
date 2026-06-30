"""JSON schema validation helpers for Phase 5."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator, FormatChecker

DEFAULT_CANONICAL_SCHEMA_PATH = "schemas/canonical_candidate.schema.json"


def _resolve_schema_path(schema_path: str) -> Path:
    path = Path(schema_path)
    if path.exists():
        return path
    cwd_candidate = Path.cwd() / schema_path
    if cwd_candidate.exists():
        return cwd_candidate
    # src/transformer/validation/schema_validator.py -> project root is parents[3]
    project_root = Path(__file__).resolve().parents[3]
    project_candidate = project_root / schema_path
    if project_candidate.exists():
        return project_candidate
    raise FileNotFoundError(f"Schema file not found: {schema_path}")


def load_schema(schema_path: str) -> Dict[str, Any]:
    resolved = _resolve_schema_path(schema_path)
    with open(resolved, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_json(instance: Dict[str, Any], schema_path: str) -> List[str]:
    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    return [f"{'/'.join(str(p) for p in error.path) or '<root>'}: {error.message}" for error in errors]


def validate_canonical_candidate(candidate: Dict[str, Any], schema_path: str = DEFAULT_CANONICAL_SCHEMA_PATH) -> List[str]:
    return validate_json(candidate, schema_path)


def assert_valid_canonical_candidate(candidate: Dict[str, Any], schema_path: str = DEFAULT_CANONICAL_SCHEMA_PATH) -> None:
    errors = validate_canonical_candidate(candidate, schema_path)
    if errors:
        raise ValueError("Canonical candidate schema validation failed: " + "; ".join(errors))
