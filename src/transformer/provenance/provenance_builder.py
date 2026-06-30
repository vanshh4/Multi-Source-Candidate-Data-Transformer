"""Provenance builder for Phase 5.

Each provenance entry explains where a candidate value came from, how it was
extracted/normalized, whether it was selected, and whether it conflicted.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def source_ref(candidate: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source_id": candidate.get("source_id", "unknown_source"),
        "source_type": candidate.get("source_type", "unknown"),
        "source_name": candidate.get("source_name"),
        "status": candidate.get("source_status", "ok"),
    }


def build_provenance_item(
    candidate: Dict[str, Any],
    *,
    field: Optional[str] = None,
    selected: bool = False,
    conflict: bool = False,
    extra_warnings: Optional[List[str]] = None,
) -> Dict[str, Any]:
    warnings = list(candidate.get("warnings") or [])
    if extra_warnings:
        warnings.extend(extra_warnings)

    method_parts = [candidate.get("method", "unknown_method")]
    if candidate.get("normalization_method"):
        method_parts.append(candidate["normalization_method"])

    return {
        "field": field or candidate.get("field_path", "unknown_field"),
        "source": source_ref(candidate),
        "method": " + ".join(method_parts),
        "raw_value": candidate.get("raw_value"),
        "normalized_value": candidate.get("normalized_value"),
        "confidence": float(candidate.get("confidence", 0.0)),
        "selected": bool(selected),
        "conflict": bool(conflict),
        "warnings": warnings,
    }


def build_provenance_for_candidates(
    candidates: Iterable[Dict[str, Any]],
    *,
    selected_ids: Optional[set[int]] = None,
    conflict_ids: Optional[set[int]] = None,
    field_override: Optional[str] = None,
) -> List[Dict[str, Any]]:
    selected_ids = selected_ids or set()
    conflict_ids = conflict_ids or set()
    items: List[Dict[str, Any]] = []
    for candidate in candidates:
        items.append(
            build_provenance_item(
                candidate,
                field=field_override,
                selected=id(candidate) in selected_ids,
                conflict=id(candidate) in conflict_ids,
            )
        )
    return items
