"""
Common reader response utilities for Phase 2 input readers.

This module defines a consistent result shape for every source reader.
Readers should never crash the pipeline for missing, empty, malformed, or
unreadable sources. Instead, they should return a structured result with
status, metadata, warnings, and errors.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional


ReaderStatus = Literal["ok", "missing", "empty", "malformed", "unreadable", "partial"]
ContentType = Literal["text", "tabular", "binary", "none"]


STATUS_OK: ReaderStatus = "ok"
STATUS_MISSING: ReaderStatus = "missing"
STATUS_EMPTY: ReaderStatus = "empty"
STATUS_MALFORMED: ReaderStatus = "malformed"
STATUS_UNREADABLE: ReaderStatus = "unreadable"
STATUS_PARTIAL: ReaderStatus = "partial"


@dataclass
class SourceResult:
    """
    Standard output contract for all Phase 2 readers.

    Attributes:
        source_id: Stable logical identifier for the source, e.g. recruiter_csv.
        source_type: Source type, e.g. recruiter_csv, resume_docx, resume_pdf, resume_txt.
        source_name: File name or logical source name.
        path: Local source path used by the reader.
        required: Whether this source is mandatory for the run.
        status: Reader status. Must be one of: ok, missing, empty, malformed, unreadable, partial.
        content_type: Type of returned content: text, tabular, binary, or none.
        content: Parsed content. For CSV this can be list[dict]; for resumes this can be text.
        metadata: Reader-specific metadata such as rows, columns, paragraph count, page count.
        warnings: Non-fatal issues.
        errors: Fatal/non-fatal errors captured without crashing the pipeline.
    """

    source_id: str
    source_type: str
    source_name: Optional[str]
    path: str
    required: bool = False
    status: ReaderStatus = STATUS_OK
    content_type: ContentType = "none"
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self, include_content: bool = True) -> Dict[str, Any]:
        """
        Convert result to dictionary.

        Args:
            include_content: If False, remove full content and keep only metadata.
                             Useful for privacy-safe logs and output summaries.
        """
        result = asdict(self)
        if not include_content:
            result.pop("content", None)
        return result


def build_reader_result(
    *,
    source_id: str,
    source_type: str,
    path: str,
    required: bool = False,
    status: ReaderStatus = STATUS_OK,
    content_type: ContentType = "none",
    content: Any = None,
    metadata: Optional[Dict[str, Any]] = None,
    warnings: Optional[List[str]] = None,
    errors: Optional[List[str]] = None,
    source_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a standardized reader result dictionary.

    Use this helper in csv_reader.py, text_reader.py, docx_reader.py, and pdf_reader.py.
    """
    resolved_source_name = source_name if source_name is not None else Path(path).name

    return SourceResult(
        source_id=source_id,
        source_type=source_type,
        source_name=resolved_source_name,
        path=path,
        required=required,
        status=status,
        content_type=content_type,
        content=content,
        metadata=metadata or {},
        warnings=warnings or [],
        errors=errors or [],
    ).to_dict(include_content=True)


def summarize_reader_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a privacy-safe summary of a reader result.

    This removes the full source content and keeps status, metadata, warnings, and errors.
    Useful for writing data/outputs/source_reading_output.json.
    """
    summary = dict(result)
    summary.pop("content", None)
    return summary


def combine_overall_status(results: List[Dict[str, Any]]) -> str:
    """
    Derive an overall reader-layer status from individual source statuses.

    Returns:
        completed: all sources are ok.
        completed_with_warnings: at least one optional source has a non-ok status.
        failed: at least one required source is missing, empty, malformed, or unreadable.
    """
    if not results:
        return "completed_with_warnings"

    for result in results:
        if result.get("required") and result.get("status") != STATUS_OK:
            return "failed"

    if any(result.get("status") != STATUS_OK for result in results):
        return "completed_with_warnings"

    return "completed"
