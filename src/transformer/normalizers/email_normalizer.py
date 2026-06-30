"""Email normalization for Phase 4."""

from __future__ import annotations

import re
from typing import Dict

from transformer.normalizers.base import STATUS_OK, build_normalization_result, collapse_spaces, empty_result, invalid_result, is_empty_value

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def normalize_email_candidate(candidate: Dict) -> Dict:
    method = "email_lowercase_validate"
    value = candidate.get("normalized_value", candidate.get("raw_value"))
    if is_empty_value(value):
        return empty_result(candidate, method=method)

    email = collapse_spaces(str(value)).strip("<>.,;:()[]{}\"'").lower()
    if not EMAIL_RE.match(email):
        return invalid_result(candidate, method=method, warning=f"Invalid email format: {value}")

    return build_normalization_result(candidate, normalized_value=email, normalization_method=method, normalization_status=STATUS_OK)
