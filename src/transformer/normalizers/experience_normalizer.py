"""Experience and years-of-experience normalization for Phase 4."""

from __future__ import annotations

import re
from typing import Dict

from transformer.normalizers.base import STATUS_OK, STATUS_UNCHANGED, build_normalization_result, collapse_spaces, empty_result, invalid_result, is_empty_value

YEARS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", re.IGNORECASE)
MONTHS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:months?|mos?)", re.IGNORECASE)
NUMBER_RE = re.compile(r"^\d+(?:\.\d+)?$")


def normalize_years_experience_candidate(candidate: Dict) -> Dict:
    method = "years_experience_to_float"
    value = candidate.get("normalized_value", candidate.get("raw_value"))
    if is_empty_value(value):
        return empty_result(candidate, method=method)

    if isinstance(value, (int, float)):
        years = float(value)
    else:
        text = collapse_spaces(str(value)).lower()
        if NUMBER_RE.match(text):
            years = float(text)
        else:
            year_match = YEARS_RE.search(text)
            month_match = MONTHS_RE.search(text)
            years = 0.0
            if year_match:
                years += float(year_match.group(1))
            if month_match:
                years += float(month_match.group(1)) / 12.0
            if not year_match and not month_match:
                return invalid_result(candidate, method=method, warning=f"Could not parse years_experience: {value}")

    if years < 0 or years > 80:
        return invalid_result(candidate, method=method, warning=f"Unreasonable years_experience value: {value}")

    return build_normalization_result(candidate, normalized_value=round(years, 2), normalization_method=method, normalization_status=STATUS_OK)


def normalize_experience_candidate(candidate: Dict) -> Dict:
    """Keep raw experience blocks as cleaned text for later structured parsing."""
    method = "experience_text_cleanup"
    value = candidate.get("normalized_value", candidate.get("raw_value"))
    if is_empty_value(value):
        return empty_result(candidate, method=method)
    cleaned = str(value).strip()
    return build_normalization_result(candidate, normalized_value=cleaned, normalization_method=method, normalization_status=STATUS_UNCHANGED)
