"""Canonical candidate builder for Phase 5."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from transformer.canonical.candidate_model import clone_empty_candidate
from transformer.canonical.id_generator import generate_candidate_id
from transformer.merge.confidence import calculate_overall_confidence
from transformer.merge.resolver import resolve_all


def build_canonical_candidate(normalized_candidates: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    candidate = clone_empty_candidate()
    resolved = resolve_all(list(normalized_candidates))

    for key in [
        "full_name", "emails", "phones", "location", "links", "headline",
        "years_experience", "skills", "experience", "education", "provenance"
    ]:
        if key in resolved:
            candidate[key] = resolved[key]

    candidate["candidate_id"] = generate_candidate_id(
        emails=candidate.get("emails"),
        phones=candidate.get("phones"),
        full_name=candidate.get("full_name"),
        location=candidate.get("location"),
    )
    candidate["overall_confidence"] = calculate_overall_confidence(candidate)
    return candidate
