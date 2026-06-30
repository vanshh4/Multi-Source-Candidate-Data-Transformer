"""
Reader router for Phase 2.

This module chooses the correct input reader based on source_type or file
extension. It keeps CLI logic thin and centralizes source routing rules.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from transformer.readers import csv_reader, docx_reader, pdf_reader, text_reader
from transformer.readers.base import STATUS_UNREADABLE, build_reader_result
from transformer.utils.errors import unsupported_type_error
from transformer.utils.file_utils import get_extension, get_file_name


SOURCE_TYPE_TO_READER = {
    "recruiter_csv": csv_reader.read_csv_source,
    "resume_txt": text_reader.read_text_source,
    "sample_resume_text": text_reader.read_text_source,
    "resume_docx": docx_reader.read_docx_source,
    "resume_pdf": pdf_reader.read_pdf_source,
}

EXTENSION_TO_SOURCE_TYPE = {
    "csv": "recruiter_csv",
    "txt": "resume_txt",
    "docx": "resume_docx",
    "pdf": "resume_pdf",
}


def infer_source_type(path: str, source_type: Optional[str] = None) -> Optional[str]:
    """
    Infer source type from explicit source_type or file extension.

    Args:
        path: Source file path.
        source_type: Optional source type from manifest.

    Returns:
        A normalized source type string if supported, otherwise None.
    """
    if source_type and source_type in SOURCE_TYPE_TO_READER:
        return source_type

    extension = get_extension(path)
    return EXTENSION_TO_SOURCE_TYPE.get(extension)


def read_source(source_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route one manifest source config to the correct reader.

    Expected source_config shape:
        {
            "path": "data/samples/resume.docx",
            "source_id": "resume_docx",
            "source_type": "resume_docx",
            "required": false,
            "type": "docx"  # optional legacy/helper field
        }

    Returns:
        Standard reader result dictionary.
    """
    path = source_config.get("path", "")
    required = bool(source_config.get("required", False))
    source_id = source_config.get("source_id")
    source_type = source_config.get("source_type")

    # Some manifests may provide type: docx/pdf/csv/txt instead of source_type.
    if not source_type and source_config.get("type"):
        source_type = EXTENSION_TO_SOURCE_TYPE.get(str(source_config["type"]).lower().lstrip("."))

    inferred_source_type = infer_source_type(path, source_type)

    if not inferred_source_type:
        return build_reader_result(
            source_id=source_id or "unknown_source",
            source_type=source_type or "unknown",
            source_name=get_file_name(path),
            path=path,
            required=required,
            status=STATUS_UNREADABLE,
            content_type="none",
            content=None,
            metadata={},
            warnings=[],
            errors=[unsupported_type_error(path, source_type)],
        )

    reader = SOURCE_TYPE_TO_READER[inferred_source_type]
    final_source_id = source_id or inferred_source_type

    return reader(
        path,
        source_id=final_source_id,
        source_type=inferred_source_type,
        required=required,
    )


def read_sources_from_manifest(manifest: Dict[str, Any]) -> list[Dict[str, Any]]:
    """
    Read all supported sources from a loaded manifest dictionary.

    The current Phase 2 manifest supports:
        inputs.recruiter_csv
        inputs.resume

    It may also optionally support:
        inputs.sample_resume_text
        inputs.resume_text
        inputs.resume_pdf
        inputs.resume_docx
    """
    inputs = manifest.get("inputs", {}) or {}
    source_results: list[Dict[str, Any]] = []

    # Read recruiter CSV if provided.
    recruiter_csv_config = inputs.get("recruiter_csv")
    if recruiter_csv_config:
        source_results.append(read_source(recruiter_csv_config))

    # Read primary resume if provided. This can be docx/pdf/txt depending on manifest path/type.
    resume_config = inputs.get("resume")
    if resume_config:
        source_results.append(read_source(resume_config))

    # Optional additional direct source keys for local testing.
    for optional_key in ["sample_resume_text", "resume_text", "resume_docx", "resume_pdf"]:
        optional_config = inputs.get(optional_key)
        if optional_config:
            source_results.append(read_source(optional_config))

    return source_results
