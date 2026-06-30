"""Canonical dot-path resolver for Phase 6."""

from __future__ import annotations

from typing import Any, Tuple


def get_by_path(data: dict, path: str, default: Any = None) -> Tuple[bool, Any]:
    """
    Resolve a dot path from a nested dictionary.

    Returns:
        (True, value) if the full path exists, even when value is None.
        (False, default) if any path segment is missing or not traversable.
    """
    if not path:
        return False, default
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, default
        current = current[part]
    return True, current


def path_exists(data: dict, path: str) -> bool:
    exists, _ = get_by_path(data, path)
    return exists


def is_missing_value(value: Any) -> bool:
    """Treat None, empty strings, empty lists, and empty dicts as missing for projection."""
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False
