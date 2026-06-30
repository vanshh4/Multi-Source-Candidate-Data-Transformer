"""Output-level normalization used by runtime projection.

These rules only shape the outgoing projected response. They do not replace the
Phase 4 normalization layer.
"""

from __future__ import annotations

import json
import re
from typing import Any, Iterable


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _as_rules(normalization: Any) -> list[str]:
    if normalization is None:
        return []
    if isinstance(normalization, str):
        return [normalization]
    return list(normalization)


def _unique_key(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False).lower()
    except TypeError:
        return str(value).lower()


def _sorted_unique(value: Any) -> Any:
    if not isinstance(value, list):
        return value
    seen = set()
    result = []
    for item in value:
        key = item.get("name", "").lower() if isinstance(item, dict) and "name" in item else _unique_key(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return sorted(result, key=lambda x: x.get("name", "") if isinstance(x, dict) else str(x).lower())


def _skill_canonical(value: Any) -> Any:
    aliases = {"powerbi": "Power BI", "power bi": "Power BI", "sql": "SQL", "python": "Python", "sklearn": "scikit-learn"}
    def norm_one(v: Any) -> Any:
        if isinstance(v, dict) and "name" in v:
            new = dict(v)
            key = _collapse_spaces(str(new["name"])).lower()
            new["name"] = aliases.get(key, " ".join(part.capitalize() for part in key.split()))
            return new
        key = _collapse_spaces(str(v)).lower()
        return aliases.get(key, " ".join(part.capitalize() for part in key.split()))
    if isinstance(value, list):
        return [norm_one(v) for v in value]
    return norm_one(value)


def _e164_phone(value: Any) -> Any:
    def norm_one(v: Any) -> Any:
        s = str(v).strip()
        digits = "".join(ch for ch in s if ch.isdigit())
        if s.startswith("+") and 8 <= len(digits) <= 15:
            return f"+{digits}"
        if len(digits) == 10:
            return f"+91{digits}"
        if digits.startswith("91") and len(digits) == 12:
            return f"+{digits}"
        return v
    if isinstance(value, list):
        return [norm_one(v) for v in value]
    return norm_one(value)


def _https_url(value: Any) -> Any:
    def norm_one(v: Any) -> Any:
        if v is None:
            return None
        s = _collapse_spaces(str(v)).strip(".,;:()[]{}\"'")
        if not s:
            return s
        if not s.lower().startswith(("http://", "https://")):
            s = f"https://{s}"
        return s.rstrip("/")
    if isinstance(value, list):
        return [norm_one(v) for v in value]
    if isinstance(value, dict):
        return {k: _https_url(v) if k != "other" else [_https_url(i) for i in v] for k, v in value.items()}
    return norm_one(value)


def apply_normalization_rule(value: Any, rule: str) -> Any:
    if rule in {"none", None}:
        return value
    if rule == "trim" and isinstance(value, str):
        return value.strip()
    if rule == "collapse_spaces" and isinstance(value, str):
        return _collapse_spaces(value)
    if rule == "lowercase" and isinstance(value, str):
        return value.lower()
    if rule == "uppercase" and isinstance(value, str):
        return value.upper()
    if rule == "title_case" and isinstance(value, str):
        return " ".join(part.capitalize() for part in _collapse_spaces(value).split())
    if rule == "email_lowercase":
        return [str(v).strip().lower() for v in value] if isinstance(value, list) else str(value).strip().lower()
    if rule == "e164_phone":
        return _e164_phone(value)
    if rule == "iso_country_alpha2" and isinstance(value, str):
        mapping = {"india": "IN", "in": "IN", "united states": "US", "usa": "US"}
        return mapping.get(value.strip().lower(), value.strip().upper())
    if rule == "https_url":
        return _https_url(value)
    if rule == "sorted_unique":
        return _sorted_unique(value)
    if rule == "skill_canonical":
        return _skill_canonical(value)
    if rule == "round_1_decimal" and isinstance(value, (int, float)):
        return round(float(value), 1)
    if rule == "round_2_decimal" and isinstance(value, (int, float)):
        return round(float(value), 2)
    return value


def apply_output_normalization(value: Any, normalization: Any) -> Any:
    normalized = value
    for rule in _as_rules(normalization):
        normalized = apply_normalization_rule(normalized, rule)
    return normalized
