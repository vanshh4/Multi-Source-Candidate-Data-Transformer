"""
Field candidate model for Phase 3 extraction.

A FieldCandidate is not the final canonical value. It is one extracted value
observed from one source, with traceability metadata and extraction confidence.
Normalization, merge/conflict resolution, and canonical record creation happen
in later phases.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FieldCandidate:
    """
    Standard structure for one extracted candidate value.

    Attributes:
        field_path: Canonical destination path, e.g. emails, phones, links.linkedin.
        raw_value: Value exactly or nearly as extracted from source.
        normalized_value: Lightly cleaned value. Deep normalization happens later.
        source_id: Logical source identifier, e.g. recruiter_csv or resume_docx.
        source_type: Source type, e.g. recruiter_csv, resume_docx, resume_pdf, resume_txt.
        source_name: File name or source display name.
        method: Extraction method, e.g. email_regex or csv_column_mapping.
        confidence: Extraction confidence between 0 and 1.
        warnings: Non-fatal extraction warnings.
        metadata: Extra details such as row_index, column, pattern, or section.
    """

    field_path: str
    raw_value: Any
    normalized_value: Any
    source_id: str
    source_type: str
    source_name: Optional[str]
    method: str
    confidence: float
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Clamp confidence and ensure required strings are present."""
        if not self.field_path:
            raise ValueError("field_path is required")
        if not self.source_id:
            raise ValueError("source_id is required")
        if not self.source_type:
            raise ValueError("source_type is required")
        if not self.method:
            raise ValueError("method is required")
        self.confidence = max(0.0, min(1.0, float(self.confidence)))

    def to_dict(self) -> Dict[str, Any]:
        """Return JSON-serializable dictionary."""
        return asdict(self)


def make_field_candidate(
    *,
    field_path: str,
    raw_value: Any,
    normalized_value: Any,
    source_id: str,
    source_type: str,
    source_name: Optional[str],
    method: str,
    confidence: float,
    warnings: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Convenience factory returning a dictionary FieldCandidate."""
    return FieldCandidate(
        field_path=field_path,
        raw_value=raw_value,
        normalized_value=normalized_value,
        source_id=source_id,
        source_type=source_type,
        source_name=source_name,
        method=method,
        confidence=confidence,
        warnings=warnings or [],
        metadata=metadata or {},
    ).to_dict()


def is_meaningful_value(value: Any) -> bool:
    """Return True when an extracted value should be emitted as a field candidate."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True
