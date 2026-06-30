"""Generic text normalization for Phase 4."""

from __future__ import annotations

from typing import Dict

from transformer.normalizers.base import STATUS_OK, build_normalization_result, collapse_spaces, empty_result, is_empty_value


def _title_name(value: str) -> str:
    return " ".join(part.capitalize() if not part.isupper() else part for part in value.split())


def normalize_text_candidate(candidate: Dict) -> Dict:
    method = "generic_text_cleanup"
    field_path = candidate.get("field_path")
    value = candidate.get("normalized_value", candidate.get("raw_value"))
    if is_empty_value(value):
        return empty_result(candidate, method=method)

    text = str(value).strip()
    if field_path in {"full_name", "headline"}:
        text = collapse_spaces(text)
    if field_path == "full_name":
        text = _title_name(text)
        method = "name_text_cleanup"
    elif field_path == "headline":
        method = "headline_text_cleanup"

    return build_normalization_result(candidate, normalized_value=text, normalization_method=method, normalization_status=STATUS_OK)
