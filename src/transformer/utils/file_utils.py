"""
File utility helpers shared by Phase 2 readers.

These helpers keep file safety checks consistent across CSV, TXT, DOCX, and PDF readers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union


PathLike = Union[str, Path]


def to_path(path: PathLike) -> Path:
    """Convert a string or Path-like value to a pathlib.Path object."""
    return Path(path)


def file_exists(path: PathLike) -> bool:
    """Return True if the path exists and is a file."""
    return to_path(path).is_file()


def get_file_size(path: PathLike) -> Optional[int]:
    """
    Return file size in bytes.

    Returns None if the file does not exist or cannot be accessed.
    """
    try:
        p = to_path(path)
        if not p.exists() or not p.is_file():
            return None
        return p.stat().st_size
    except OSError:
        return None


def is_empty_file(path: PathLike) -> bool:
    """
    Return True if a file exists and has zero bytes.

    Missing files are not treated as empty. Use file_exists() separately.
    """
    size = get_file_size(path)
    return size == 0


def get_file_name(path: PathLike) -> str:
    """Return file name from path, e.g. resume.docx."""
    return to_path(path).name


def get_extension(path: PathLike) -> str:
    """
    Return lowercase file extension without dot.

    Example:
        data/samples/resume.docx -> docx
    """
    suffix = to_path(path).suffix.lower()
    return suffix[1:] if suffix.startswith(".") else suffix


def ensure_parent_dir(path: PathLike) -> None:
    """Create parent directory for a file path if it does not already exist."""
    to_path(path).parent.mkdir(parents=True, exist_ok=True)


def ensure_dir(path: PathLike) -> None:
    """Create a directory if it does not already exist."""
    to_path(path).mkdir(parents=True, exist_ok=True)


def read_text_safely(path: PathLike, encoding: str = "utf-8") -> str:
    """
    Read text using the provided encoding.

    Let exceptions propagate to the reader so the reader can return a structured
    unreadable/malformed result with the exception message.
    """
    return to_path(path).read_text(encoding=encoding)


def make_relative_display_path(path: PathLike) -> str:
    """
    Return a readable path string for logs/results.

    This does not force paths to be relative because local development environments differ.
    """
    return str(to_path(path).as_posix())


def validate_extension(path: PathLike, allowed_extensions: set[str]) -> bool:
    """
    Return True if path extension is in allowed_extensions.

    allowed_extensions should not include dots, e.g. {"csv", "txt"}.
    """
    return get_extension(path) in {ext.lower().lstrip(".") for ext in allowed_extensions}
