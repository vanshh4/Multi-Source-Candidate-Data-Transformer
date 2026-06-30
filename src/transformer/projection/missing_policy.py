"""Missing-value policy handling for Phase 6 projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from transformer.projection.errors import MISSING_VALUE_ERROR, ProjectionMissingValueError


@dataclass(frozen=True)
class OmitField:
    """Sentinel indicating that the projected field should be omitted."""
    reason: str


OMIT = OmitField(reason="omit")


def resolve_missing_policy(field_config: dict, options: dict | None = None) -> str:
    options = options or {}
    if field_config.get("required") and "missing" not in field_config:
        return "error"
    return field_config.get("missing") or options.get("missing_default") or "null"


def handle_missing_value(output_name: str, path: str, missing_policy: str) -> Any:
    """
    Apply missing-value policy.

    - null: returns None
    - omit: returns OMIT sentinel
    - error: raises ProjectionMissingValueError
    """
    if missing_policy == "null":
        return None
    if missing_policy == "omit":
        return OMIT
    if missing_policy == "error":
        raise ProjectionMissingValueError(f"{MISSING_VALUE_ERROR} output_name={output_name}, path={path}")
    raise ProjectionMissingValueError(f"Unsupported missing policy '{missing_policy}' for output_name={output_name}, path={path}")
