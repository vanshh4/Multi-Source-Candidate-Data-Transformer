"""Stable candidate ID generation for Phase 5."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, Dict, Iterable, Optional


def _hash(value: str) -> str:
    digest = hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()[:10]
    return f"cand_{digest}"


def generate_candidate_id(*, emails: Optional[Iterable[str]] = None, phones: Optional[Iterable[str]] = None, full_name: str | None = None, location: Dict[str, Any] | None = None) -> str:
    emails = [e for e in (emails or []) if e]
    phones = [p for p in (phones or []) if p]
    if emails:
        return _hash(f"email:{sorted(emails)[0]}")
    if phones:
        return _hash(f"phone:{sorted(phones)[0]}")
    loc_raw = (location or {}).get("raw") if isinstance(location, dict) else None
    if full_name and loc_raw:
        return _hash(f"name_location:{full_name}:{loc_raw}")
    return f"cand_{uuid.uuid4().hex[:10]}"
