"""
Plain-text reader for Phase 2.

Reads sample_resume_text.txt or any UTF-8-compatible plain text file safely and
returns a standardized reader result.
"""

from __future__ import annotations

from typing import Dict

from transformer.readers.base import (
    STATUS_EMPTY,
    STATUS_MISSING,
    STATUS_OK,
    STATUS_UNREADABLE,
    build_reader_result,
)
from transformer.utils.errors import (
    ENCODING_ERROR,
    SOURCE_UNREADABLE,
    empty_source_warning,
    format_exception_message,
    missing_source_warning,
)
from transformer.utils.file_utils import file_exists, get_file_name, is_empty_file, read_text_safely


def read_text_source(
    path: str,
    *,
    source_id: str = "sample_resume_text",
    source_type: str = "resume_txt",
    required: bool = False,
    encoding: str = "utf-8",
) -> Dict:
    """Safely read a plain text source and return a standard reader result."""
    source_name = get_file_name(path)

    base_metadata = {
        "encoding": encoding,
        "line_count": 0,
        "character_count": 0,
        "has_extractable_text": False,
    }

    if not file_exists(path):
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_MISSING,
            content_type="text",
            content="",
            metadata=base_metadata,
            warnings=[missing_source_warning(path)],
            errors=[],
        )

    if is_empty_file(path):
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_EMPTY,
            content_type="text",
            content="",
            metadata=base_metadata,
            warnings=[empty_source_warning(path)],
            errors=[],
        )

    try:
        text = read_text_safely(path, encoding=encoding)
    except UnicodeDecodeError as exc:
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_UNREADABLE,
            content_type="text",
            content="",
            metadata=base_metadata,
            warnings=[ENCODING_ERROR],
            errors=[format_exception_message(SOURCE_UNREADABLE, exc)],
        )
    except Exception as exc:
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_UNREADABLE,
            content_type="text",
            content="",
            metadata=base_metadata,
            warnings=[],
            errors=[format_exception_message(SOURCE_UNREADABLE, exc)],
        )

    if not text.strip():
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_EMPTY,
            content_type="text",
            content="",
            metadata=base_metadata,
            warnings=[empty_source_warning(path)],
            errors=[],
        )

    return build_reader_result(
        source_id=source_id,
        source_type=source_type,
        source_name=source_name,
        path=path,
        required=required,
        status=STATUS_OK,
        content_type="text",
        content=text,
        metadata={
            "encoding": encoding,
            "line_count": len(text.splitlines()),
            "character_count": len(text),
            "has_extractable_text": True,
        },
        warnings=[],
        errors=[],
    )


def read(path: str, **kwargs) -> Dict:
    """Friendly alias used by router/CLI."""
    return read_text_source(path, **kwargs)
