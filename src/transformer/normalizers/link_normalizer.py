"""URL/link normalization for Phase 4."""

from __future__ import annotations

from urllib.parse import urlparse, urlunparse
from typing import Dict

from transformer.normalizers.base import STATUS_OK, build_normalization_result, collapse_spaces, empty_result, invalid_result, is_empty_value


def normalize_link_candidate(candidate: Dict) -> Dict:
    method = "url_https_normalize"
    value = candidate.get("normalized_value", candidate.get("raw_value"))
    if is_empty_value(value):
        return empty_result(candidate, method=method)

    url = collapse_spaces(str(value)).strip(".,;:()[]{}\"'")
    if not url.lower().startswith(("http://", "https://")):
        url = f"https://{url}"

    parsed = urlparse(url)
    if not parsed.netloc or "." not in parsed.netloc:
        return invalid_result(candidate, method=method, warning=f"Invalid URL format: {value}")

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    normalized = urlunparse((scheme, netloc, path, "", parsed.query, ""))

    return build_normalization_result(candidate, normalized_value=normalized, normalization_method=method, normalization_status=STATUS_OK)
