"""Projection metadata mapper for provenance and confidence."""

from __future__ import annotations

from typing import Any, Dict, List


def provenance_for_path(canonical_candidate: Dict[str, Any], canonical_path: str) -> List[Dict[str, Any]]:
    provenance = canonical_candidate.get("provenance", []) or []
    return [p for p in provenance if p.get("field") == canonical_path or str(p.get("field", "")).startswith(f"{canonical_path}.")]


def confidence_for_path(canonical_candidate: Dict[str, Any], canonical_path: str) -> float | None:
    items = [p for p in provenance_for_path(canonical_candidate, canonical_path) if p.get("selected")]
    if not items:
        if canonical_path == "overall_confidence":
            return canonical_candidate.get("overall_confidence")
        return None
    return round(sum(float(p.get("confidence", 0.0)) for p in items) / len(items), 4)


def build_projection_metadata(canonical_candidate: Dict[str, Any], field_configs: List[Dict[str, Any]], *, include_provenance: bool, include_confidence: bool) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    if include_provenance:
        metadata["_provenance"] = {}
    if include_confidence:
        metadata["_confidence"] = {}

    for field in field_configs:
        output_name = field["output_name"]
        path = field["path"]
        field_include_prov = field.get("include_provenance", include_provenance)
        field_include_conf = field.get("include_confidence", include_confidence)
        if include_provenance and field_include_prov:
            metadata["_provenance"][output_name] = provenance_for_path(canonical_candidate, path)
        if include_confidence and field_include_conf:
            metadata["_confidence"][output_name] = confidence_for_path(canonical_candidate, path)
    return metadata


def attach_projection_metadata(projected: Dict[str, Any], canonical_candidate: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    options = config.get("options", {}) or {}
    include_provenance = bool(options.get("include_provenance", True))
    include_confidence = bool(options.get("include_confidence", True))
    metadata = build_projection_metadata(
        canonical_candidate,
        config.get("output", {}).get("fields", []),
        include_provenance=include_provenance,
        include_confidence=include_confidence,
    )
    result = dict(projected)
    result.update(metadata)
    return result
