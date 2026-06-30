"""
PDF resume reader for Phase 2.

Uses pdfplumber for layout-aware PDF text extraction. Scanned/image-based PDFs
may not contain extractable text; those are reported as unreadable with a clear
warning instead of crashing the pipeline.
"""

from __future__ import annotations

from typing import Dict, List

import pdfplumber

from transformer.readers.base import (
    STATUS_EMPTY,
    STATUS_MISSING,
    STATUS_OK,
    STATUS_UNREADABLE,
    build_reader_result,
)
from transformer.utils.errors import (
    PDF_NO_TEXT,
    SOURCE_UNREADABLE,
    empty_source_warning,
    format_exception_message,
    missing_source_warning,
)
from transformer.utils.file_utils import file_exists, get_file_name, is_empty_file


def read_pdf_source(
    path: str,
    *,
    source_id: str = "resume_pdf",
    source_type: str = "resume_pdf",
    required: bool = False,
    layout: bool = True,
) -> Dict:
    """Safely extract text from a PDF resume using pdfplumber."""
    source_name = get_file_name(path)
    extraction_method = "pdfplumber_extract_text_layout" if layout else "pdfplumber_extract_text"

    base_metadata = {
        "page_count": 0,
        "character_count": 0,
        "has_extractable_text": False,
        "extraction_method": extraction_method,
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

    page_texts: List[str] = []
    page_count = 0

    try:
        with pdfplumber.open(path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                try:
                    extracted = page.extract_text(layout=layout) or ""
                except TypeError:
                    extracted = page.extract_text() or ""
                if extracted.strip():
                    page_texts.append(extracted.strip())
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
            metadata={**base_metadata, "page_count": page_count},
            warnings=[],
            errors=[format_exception_message(SOURCE_UNREADABLE, exc)],
        )

    text = "\n\n".join(page_texts).strip()

    if not text:
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_UNREADABLE,
            content_type="text",
            content="",
            metadata={**base_metadata, "page_count": page_count},
            warnings=[PDF_NO_TEXT],
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
            "page_count": page_count,
            "character_count": len(text),
            "has_extractable_text": True,
            "extraction_method": extraction_method,
        },
        warnings=[],
        errors=[],
    )


def read(path: str, **kwargs) -> Dict:
    """Friendly alias used by router/CLI."""
    return read_pdf_source(path, **kwargs)
