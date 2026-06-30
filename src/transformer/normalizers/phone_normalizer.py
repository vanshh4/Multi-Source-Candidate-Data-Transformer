"""Phone normalization for Phase 4."""

from __future__ import annotations

from typing import Dict

from transformer.normalizers.base import STATUS_OK, build_normalization_result, collapse_spaces, empty_result, invalid_result, is_empty_value


def normalize_phone_candidate(candidate: Dict, *, default_country: str = "IN", default_dial_code: str = "+91") -> Dict:
    method = "phone_e164_basic"
    value = candidate.get("normalized_value", candidate.get("raw_value"))
    if is_empty_value(value):
        return empty_result(candidate, method=method)

    raw = collapse_spaces(str(value))
    has_plus = raw.strip().startswith("+")
    digits = "".join(ch for ch in raw if ch.isdigit())

    if not digits:
        return invalid_result(candidate, method=method, warning=f"Phone contains no digits: {value}")

    # Indian local 10-digit number -> +91XXXXXXXXXX
    if not has_plus and default_country.upper() == "IN" and len(digits) == 10:
        normalized = f"{default_dial_code}{digits}"
    elif has_plus and 8 <= len(digits) <= 15:
        normalized = f"+{digits}"
    elif not has_plus and digits.startswith("91") and len(digits) == 12:
        normalized = f"+{digits}"
    elif not has_plus and 10 < len(digits) <= 15:
        normalized = f"+{digits}"
    else:
        return invalid_result(candidate, method=method, warning=f"Invalid or unsupported phone length: {value}")

    return build_normalization_result(
        candidate,
        normalized_value=normalized,
        normalization_method=method,
        normalization_status=STATUS_OK,
        metadata_updates={"default_country": default_country},
    )
