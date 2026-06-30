"""Projected output validator."""

from __future__ import annotations

from typing import Any, Dict, List

from jsonschema import Draft202012Validator, FormatChecker

from transformer.projection.errors import ProjectionValidationError


def validate_projected_output(output: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(output), key=lambda e: list(e.path))
    return [f"{'/'.join(str(p) for p in error.path) or '<root>'}: {error.message}" for error in errors]


def assert_valid_projected_output(output: Dict[str, Any], schema: Dict[str, Any]) -> None:
    errors = validate_projected_output(output, schema)
    if errors:
        raise ProjectionValidationError("; ".join(errors))
