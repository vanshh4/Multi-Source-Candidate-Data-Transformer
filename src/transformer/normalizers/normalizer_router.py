"""Normalizer router for Phase 4."""

from __future__ import annotations

from typing import Dict, Iterable, List

from transformer.normalizers.email_normalizer import normalize_email_candidate
from transformer.normalizers.experience_normalizer import normalize_experience_candidate, normalize_years_experience_candidate
from transformer.normalizers.link_normalizer import normalize_link_candidate
from transformer.normalizers.location_normalizer import normalize_location_candidate
from transformer.normalizers.phone_normalizer import normalize_phone_candidate
from transformer.normalizers.skill_normalizer import normalize_skill_candidate
from transformer.normalizers.text_normalizer import normalize_text_candidate
from transformer.normalizers.base import STATUS_UNCHANGED, build_normalization_result


def normalize_field_candidate(candidate: Dict) -> Dict:
    field_path = candidate.get("field_path", "")

    if field_path == "emails":
        return normalize_email_candidate(candidate)
    if field_path == "phones":
        return normalize_phone_candidate(candidate)
    if field_path.startswith("links."):
        return normalize_link_candidate(candidate)
    if field_path == "skills":
        return normalize_skill_candidate(candidate)
    if field_path == "years_experience":
        return normalize_years_experience_candidate(candidate)
    if field_path == "experience":
        return normalize_experience_candidate(candidate)
    if field_path == "location.raw":
        return normalize_location_candidate(candidate)
    if field_path in {"full_name", "headline", "education"}:
        return normalize_text_candidate(candidate)

    return build_normalization_result(
        candidate,
        normalized_value=candidate.get("normalized_value", candidate.get("raw_value")),
        normalization_method="no_registered_normalizer",
        normalization_status=STATUS_UNCHANGED,
        warnings=[f"No registered normalizer for field_path: {field_path}"],
    )


def normalize_field_candidates(candidates: Iterable[Dict]) -> List[Dict]:
    return [normalize_field_candidate(candidate) for candidate in candidates]


def build_normalization_output(*, run_id: str, field_candidates: Iterable[Dict]) -> Dict:
    normalized = normalize_field_candidates(field_candidates)
    return {
        "run_id": run_id,
        "description": "Phase 4 normalization output. Merge, canonical building, and projection are not performed here.",
        "normalized_candidate_count": len(normalized),
        "normalized_candidates": normalized,
    }
