"""
Base normalization utilities for Phase 4.

Phase 4 receives Phase 3 FieldCandidate dictionaries and returns normalized
candidate dictionaries. It does not merge values, choose winners, or build the
canonical candidate record.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
import re

STATUS_OK = "ok"
STATUS_UNCHANGED = "unchanged"
STATUS_INVALID = "invalid"
STATUS_EMPTY = "empty"
STATUS_PARTIAL = "partial"


@dataclass
class NormalizationResult:
    field_path: str
    raw_value: Any
    normalized_value: Any
    source_id: str
    source_type: str
    source_name: Optional[str]
    method: str
    confidence: float
    normalization_method: str
    normalization_status: str
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.confidence = max(0.0, min(1.0, float(self.confidence)))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def collapse_spaces(value: str) -> str:
    """Trim and collapse repeated whitespace."""
    return re.sub(r"\s+", " ", value or "").strip()


def is_empty_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def build_normalization_result(
    candidate: Dict[str, Any],
    *,
    normalized_value: Any,
    normalization_method: str,
    normalization_status: str = STATUS_OK,
    warnings: Optional[List[str]] = None,
    metadata_updates: Optional[Dict[str, Any]] = None,
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """Create a normalized candidate dictionary while preserving provenance fields."""
    metadata = deepcopy(candidate.get("metadata") or {})
    if metadata_updates:
        metadata.update(metadata_updates)

    combined_warnings = list(candidate.get("warnings") or [])
    if warnings:
        combined_warnings.extend(warnings)

    return NormalizationResult(
        field_path=candidate.get("field_path", ""),
        raw_value=candidate.get("raw_value"),
        normalized_value=normalized_value,
        source_id=candidate.get("source_id", "unknown_source"),
        source_type=candidate.get("source_type", "unknown"),
        source_name=candidate.get("source_name"),
        method=candidate.get("method", "unknown_method"),
        confidence=candidate.get("confidence", 0.0) if confidence is None else confidence,
        normalization_method=normalization_method,
        normalization_status=normalization_status,
        warnings=combined_warnings,
        metadata=metadata,
    ).to_dict()


def invalid_result(candidate: Dict[str, Any], *, method: str, warning: str) -> Dict[str, Any]:
    return build_normalization_result(
        candidate,
        normalized_value=None,
        normalization_method=method,
        normalization_status=STATUS_INVALID,
        warnings=[warning],
        confidence=min(float(candidate.get("confidence", 0.0)), 0.30),
    )


def empty_result(candidate: Dict[str, Any], *, method: str, warning: str = "Value is empty.") -> Dict[str, Any]:
    return build_normalization_result(
        candidate,
        normalized_value=None,
        normalization_method=method,
        normalization_status=STATUS_EMPTY,
        warnings=[warning],
        confidence=min(float(candidate.get("confidence", 0.0)), 0.20),
    )
