"""Conflict detection helpers for Phase 5."""

from __future__ import annotations

from typing import Any


def _norm(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def values_conflict(left: Any, right: Any, *, field_path: str = "") -> bool:
    if left is None or right is None:
        return False
    if field_path in {"emails", "phones", "skills", "links.other"}:
        return False
    if field_path == "years_experience":
        try:
            return abs(float(left) - float(right)) >= 0.5
        except (TypeError, ValueError):
            return _norm(left) != _norm(right)
    if isinstance(left, dict) and isinstance(right, dict):
        return _norm(left.get("raw") or left) != _norm(right.get("raw") or right)
    return _norm(left) != _norm(right)


def conflict_ids_for_candidates(candidates: list[dict], *, field_path: str) -> set[int]:
    conflicts: set[int] = set()
    for i, left in enumerate(candidates):
        for right in candidates[i + 1:]:
            if values_conflict(left.get("normalized_value"), right.get("normalized_value"), field_path=field_path):
                conflicts.add(id(left))
                conflicts.add(id(right))
    return conflicts
