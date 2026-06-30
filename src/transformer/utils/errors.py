"""
Centralized warning and error messages for Phase 2 readers.

Keeping messages here makes reader outputs consistent and easier to test.
"""

from __future__ import annotations


SOURCE_MISSING = "Source file is missing."
SOURCE_EMPTY = "Source file is empty."
SOURCE_UNREADABLE = "Source file could not be read."
SOURCE_MALFORMED = "Source file is malformed."
SOURCE_PARTIAL = "Source file was read partially."
UNSUPPORTED_FILE_TYPE = "Unsupported file type."
NO_EXTRACTABLE_TEXT = "No extractable text found. Source may be scanned, image-based, empty, or unsupported."
CSV_NO_ROWS = "CSV file has headers but no data rows."
CSV_NO_COLUMNS = "CSV file has no readable columns."
DOCX_NO_TEXT = "DOCX file contains no readable paragraph or table text."
PDF_NO_TEXT = "PDF contains no extractable text. It may be scanned or image-based."
ENCODING_ERROR = "File encoding could not be decoded with the attempted encoding."


def format_exception_message(prefix: str, exc: Exception) -> str:
    """
    Build a concise and consistent exception message for reader errors.

    Args:
        prefix: Human-readable context, e.g. SOURCE_UNREADABLE.
        exc: Captured exception.
    """
    return f"{prefix} Details: {type(exc).__name__}: {exc}"


def missing_source_warning(path: str) -> str:
    """Return a standard missing-source warning with path context."""
    return f"{SOURCE_MISSING} Path: {path}"


def empty_source_warning(path: str) -> str:
    """Return a standard empty-source warning with path context."""
    return f"{SOURCE_EMPTY} Path: {path}"


def unsupported_type_error(path: str, source_type: str | None = None) -> str:
    """Return a standard unsupported-file/source-type error."""
    if source_type:
        return f"{UNSUPPORTED_FILE_TYPE} Path: {path}; source_type: {source_type}"
    return f"{UNSUPPORTED_FILE_TYPE} Path: {path}"
