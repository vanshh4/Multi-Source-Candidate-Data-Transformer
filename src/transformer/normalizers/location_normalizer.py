"""Location normalization for Phase 4."""

from __future__ import annotations

from typing import Dict

from transformer.normalizers.base import STATUS_OK, STATUS_PARTIAL, build_normalization_result, collapse_spaces, empty_result, is_empty_value

COUNTRY_MAP = {
    "india": "IN",
    "in": "IN",
    "usa": "US",
    "united states": "US",
    "united states of america": "US",
    "uk": "GB",
    "united kingdom": "GB",
}

INDIA_REGION_HINTS = {
    "delhi": "Delhi",
    "gurgaon": "Haryana",
    "gurugram": "Haryana",
    "mumbai": "Maharashtra",
    "pune": "Maharashtra",
    "bangalore": "Karnataka",
    "bengaluru": "Karnataka",
    "hyderabad": "Telangana",
    "chennai": "Tamil Nadu",
    "kolkata": "West Bengal",
}


def _title(value: str | None) -> str | None:
    if not value:
        return None
    return " ".join(part.capitalize() for part in value.split())


def normalize_location_candidate(candidate: Dict) -> Dict:
    method = "location_simple_parse"
    value = candidate.get("normalized_value", candidate.get("raw_value"))
    if is_empty_value(value):
        return empty_result(candidate, method=method)

    raw = collapse_spaces(str(value))
    parts = [collapse_spaces(part) for part in raw.split(",") if collapse_spaces(part)]

    city = parts[0] if parts else raw
    region = None
    country = None

    if len(parts) >= 3:
        region = parts[1]
        country = COUNTRY_MAP.get(parts[-1].lower(), parts[-1].upper() if len(parts[-1]) == 2 else None)
    elif len(parts) == 2:
        second = parts[1].lower()
        if second in COUNTRY_MAP:
            country = COUNTRY_MAP[second]
            region = INDIA_REGION_HINTS.get(city.lower()) if country == "IN" else None
        else:
            region = parts[1]
    elif len(parts) == 1:
        region = INDIA_REGION_HINTS.get(city.lower())
        country = "IN" if region else None

    normalized = {
        "city": _title(city),
        "region": _title(region),
        "country": country,
        "raw": raw,
    }

    status = STATUS_OK if normalized["country"] else STATUS_PARTIAL
    warnings = [] if status == STATUS_OK else ["Could not confidently infer country code."]

    return build_normalization_result(candidate, normalized_value=normalized, normalization_method=method, normalization_status=status, warnings=warnings)
