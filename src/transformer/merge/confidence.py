"""Confidence scoring utilities for Phase 5."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

FIELD_WEIGHTS = {
    "full_name": 0.15,
    "emails": 0.15,
    "phones": 0.10,
    "location": 0.08,
    "links": 0.07,
    "headline": 0.07,
    "years_experience": 0.10,
    "skills": 0.12,
    "experience": 0.10,
    "education": 0.06,
}


def clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def candidate_confidence(candidate: Dict[str, Any]) -> float:
    status = candidate.get("normalization_status", "ok")
    base = clamp_confidence(candidate.get("confidence", 0.0))
    if status == "invalid":
        return min(base, 0.20)
    if status == "empty":
        return min(base, 0.10)
    if status == "partial":
        return min(base, 0.65)
    return base


def average_confidence(candidates: Iterable[Dict[str, Any]]) -> float:
    values = [candidate_confidence(c) for c in candidates]
    return round(sum(values) / len(values), 4) if values else 0.0


def field_presence_confidence(value: Any, provenance_items: List[Dict[str, Any]]) -> float:
    if value is None or value == [] or value == {}:
        return 0.0
    selected = [p for p in provenance_items if p.get("selected")]
    if selected:
        return round(sum(float(p.get("confidence", 0.0)) for p in selected) / len(selected), 4)
    return 0.0


def calculate_overall_confidence(candidate: Dict[str, Any]) -> float:
    provenance = candidate.get("provenance", [])
    weighted_total = 0.0
    total_weight = 0.0
    for field, weight in FIELD_WEIGHTS.items():
        value = candidate.get(field)
        field_prov = [p for p in provenance if p.get("field") == field or str(p.get("field", "")).startswith(f"{field}.")]
        score = field_presence_confidence(value, field_prov)
        weighted_total += score * weight
        total_weight += weight
    if total_weight == 0:
        return 0.0
    return round(clamp_confidence(weighted_total / total_weight), 4)
