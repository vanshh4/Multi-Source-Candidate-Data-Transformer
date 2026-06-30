"""
Recruiter CSV reader for Phase 2.

Reads structured recruiter CSV input safely and returns rows plus metadata.
This reader does not extract canonical candidate fields yet; extraction belongs
to a later phase.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

from transformer.readers.base import (
    STATUS_EMPTY,
    STATUS_MALFORMED,
    STATUS_MISSING,
    STATUS_OK,
    STATUS_PARTIAL,
    STATUS_UNREADABLE,
    build_reader_result,
)
from transformer.utils.errors import (
    CSV_NO_COLUMNS,
    CSV_NO_ROWS,
    ENCODING_ERROR,
    SOURCE_MALFORMED,
    SOURCE_UNREADABLE,
    empty_source_warning,
    format_exception_message,
    missing_source_warning,
)
from transformer.utils.file_utils import file_exists, get_file_name, is_empty_file


DEFAULT_EXPECTED_COLUMNS = [
    "candidate_name",
    "email",
    "phone",
    "current_location",
    "linkedin",
    "github",
    "portfolio",
    "headline",
    "years_experience",
    "skills",
]


def read_csv_source(
    path: str,
    *,
    source_id: str = "recruiter_csv",
    source_type: str = "recruiter_csv",
    required: bool = False,
    encoding: str = "utf-8",
    expected_columns: Optional[List[str]] = None,
) -> Dict:
    """Safely read recruiter CSV into row dictionaries."""
    source_name = get_file_name(path)
    expected_columns = expected_columns or DEFAULT_EXPECTED_COLUMNS

    if not file_exists(path):
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_MISSING,
            content_type="tabular",
            content=[],
            metadata={
                "encoding": encoding,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "missing_expected_columns": expected_columns,
            },
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
            content_type="tabular",
            content=[],
            metadata={
                "encoding": encoding,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "missing_expected_columns": expected_columns,
            },
            warnings=[empty_source_warning(path)],
            errors=[],
        )

    try:
        df = pd.read_csv(path, encoding=encoding, dtype=str, keep_default_na=False)
    except UnicodeDecodeError as exc:
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_UNREADABLE,
            content_type="tabular",
            content=[],
            metadata={"encoding": encoding, "row_count": 0, "column_count": 0, "columns": []},
            warnings=[ENCODING_ERROR],
            errors=[format_exception_message(SOURCE_UNREADABLE, exc)],
        )
    except pd.errors.EmptyDataError as exc:
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_EMPTY,
            content_type="tabular",
            content=[],
            metadata={"encoding": encoding, "row_count": 0, "column_count": 0, "columns": []},
            warnings=[empty_source_warning(path)],
            errors=[format_exception_message(SOURCE_MALFORMED, exc)],
        )
    except pd.errors.ParserError as exc:
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_MALFORMED,
            content_type="tabular",
            content=[],
            metadata={"encoding": encoding, "row_count": 0, "column_count": 0, "columns": []},
            warnings=[],
            errors=[format_exception_message(SOURCE_MALFORMED, exc)],
        )
    except Exception as exc:
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_UNREADABLE,
            content_type="tabular",
            content=[],
            metadata={"encoding": encoding, "row_count": 0, "column_count": 0, "columns": []},
            warnings=[],
            errors=[format_exception_message(SOURCE_UNREADABLE, exc)],
        )

    columns = [str(col).strip() for col in df.columns.tolist()]
    df.columns = columns

    if not columns:
        return build_reader_result(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            path=path,
            required=required,
            status=STATUS_MALFORMED,
            content_type="tabular",
            content=[],
            metadata={"encoding": encoding, "row_count": 0, "column_count": 0, "columns": []},
            warnings=[CSV_NO_COLUMNS],
            errors=[],
        )

    warnings: List[str] = []
    status = STATUS_OK

    if len(df) == 0:
        status = STATUS_EMPTY
        warnings.append(CSV_NO_ROWS)

    missing_expected_columns = [col for col in expected_columns if col not in columns]
    extra_columns = [col for col in columns if col not in expected_columns]

    if missing_expected_columns:
        status = STATUS_PARTIAL if status == STATUS_OK else status
        warnings.append(f"Missing expected CSV columns: {missing_expected_columns}")

    rows = df.to_dict(orient="records")

    return build_reader_result(
        source_id=source_id,
        source_type=source_type,
        source_name=source_name,
        path=path,
        required=required,
        status=status,
        content_type="tabular",
        content=rows,
        metadata={
            "encoding": encoding,
            "row_count": int(len(df)),
            "column_count": int(len(columns)),
            "columns": columns,
            "missing_expected_columns": missing_expected_columns,
            "extra_columns": extra_columns,
        },
        warnings=warnings,
        errors=[],
    )


def read(path: str, **kwargs) -> Dict:
    """Friendly alias used by router/CLI."""
    return read_csv_source(path, **kwargs)
