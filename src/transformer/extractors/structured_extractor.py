"""
Structured source extractor for Phase 3.

Converts recruiter CSV reader output into field candidates. This module performs
only light cleanup. Full normalization and merge/conflict resolution happen in
later phases.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from transformer.models.field_candidate import is_meaningful_value, make_field_candidate
from transformer.extractors.patterns import clean_whitespace, normalize_url, canonical_skill_name


CSV_COLUMN_MAPPING = {
    "candidate_name": "full_name",
    "full_name": "full_name",
    "name": "full_name",
    "email": "emails",
    "email_address": "emails",
    "phone": "phones",
    "mobile": "phones",
    "current_location": "location.raw",
    "location": "location.raw",
    "linkedin": "links.linkedin",
    "github": "links.github",
    "portfolio": "links.portfolio",
    "headline": "headline",
    "current_role": "headline",
    "years_experience": "years_experience",
    "experience_years": "years_experience",
    "skills": "skills",
}

FIELD_CONFIDENCE = {
    "full_name": 0.95,
    "emails": 0.95,
    "phones": 0.90,
    "location.raw": 0.85,
    "links.linkedin": 0.90,
    "links.github": 0.90,
    "links.portfolio": 0.85,
    "headline": 0.80,
    "years_experience": 0.90,
    "skills": 0.85,
}


def _normalized_column_name(column: str) -> str:
    """Normalize CSV column name for matching."""
    return clean_whitespace(str(column)).lower().replace(" ", "_").replace("-", "_")


def _split_skills(value: str) -> List[str]:
    """Split skills from comma/semicolon/pipe/slash separated CSV text."""
    if not value:
        return []
    separators = [",", ";", "|", "/"]
    parts = [value]
    for sep in separators:
        new_parts: List[str] = []
        for part in parts:
            new_parts.extend(part.split(sep))
        parts = new_parts
    return [canonical_skill_name(part) for part in parts if clean_whitespace(part)]


def _light_normalize(field_path: str, value: Any) -> Any:
    """Apply light extraction-stage cleanup only."""
    if value is None:
        return None
    if not isinstance(value, str):
        return value

    cleaned = clean_whitespace(value)
    if field_path == "emails":
        return cleaned.lower()
    if field_path.startswith("links."):
        return normalize_url(cleaned)
    if field_path == "skills":
        return _split_skills(cleaned)
    if field_path == "years_experience":
        try:
            return float(cleaned.replace("years", "").replace("year", "").strip())
        except ValueError:
            return cleaned
    return cleaned


def extract_from_row(row: Dict[str, Any], *, row_index: int, source: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract field candidates from one recruiter CSV row."""
    candidates: List[Dict[str, Any]] = []
    source_id = source.get("source_id", "recruiter_csv")
    source_type = source.get("source_type", "recruiter_csv")
    source_name = source.get("source_name")

    for column, value in row.items():
        normalized_column = _normalized_column_name(column)
        field_path = CSV_COLUMN_MAPPING.get(normalized_column)
        if not field_path:
            continue
        if not is_meaningful_value(value):
            continue

        normalized_value = _light_normalize(field_path, value)
        if not is_meaningful_value(normalized_value):
            continue

        # Emit one candidate per skill so later merge can union/deduplicate skills cleanly.
        if field_path == "skills" and isinstance(normalized_value, list):
            for skill in normalized_value:
                candidates.append(
                    make_field_candidate(
                        field_path="skills",
                        raw_value=value,
                        normalized_value=skill,
                        source_id=source_id,
                        source_type=source_type,
                        source_name=source_name,
                        method="csv_column_mapping",
                        confidence=FIELD_CONFIDENCE["skills"],
                        metadata={"column": column, "row_index": row_index},
                    )
                )
            continue

        candidates.append(
            make_field_candidate(
                field_path=field_path,
                raw_value=value,
                normalized_value=normalized_value,
                source_id=source_id,
                source_type=source_type,
                source_name=source_name,
                method="csv_column_mapping",
                confidence=FIELD_CONFIDENCE.get(field_path, 0.80),
                metadata={"column": column, "row_index": row_index},
            )
        )

    return candidates


def extract_structured_candidates(reader_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract field candidates from recruiter CSV reader result.

    Non-ok/empty/unreadable reader results return an empty candidate list.
    """
    if reader_result.get("source_type") != "recruiter_csv":
        return []
    if reader_result.get("status") not in {"ok", "partial"}:
        return []

    rows = reader_result.get("content") or []
    if not isinstance(rows, list):
        return []

    candidates: List[Dict[str, Any]] = []
    for row_index, row in enumerate(rows):
        if isinstance(row, dict):
            candidates.extend(extract_from_row(row, row_index=row_index, source=reader_result))
    return candidates
