
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from transformer.readers.docx_reader import read_docx_source


def test_docx_reader_valid_file(tmp_path):
    Document = pytest.importorskip("docx").Document

    docx_file = tmp_path / "vansh_resume.docx"
    document = Document()
    document.add_paragraph("Sample Candidate")
    document.add_paragraph("Email: sample@example.com")
    document.add_paragraph("Skills: Python, SQL")
    document.save(str(docx_file))

    result = read_docx_source(str(docx_file))

    assert result["status"] == "ok"
    assert result["content_type"] == "text"
    assert "Sample Candidate" in result["content"]
    assert "sample@example.com" in result["content"]
    assert result["metadata"]["paragraph_count"] >= 3
    assert result["metadata"]["character_count"] > 0
    assert result["metadata"]["has_extractable_text"] is True
    assert result["warnings"] == []
    assert result["errors"] == []


def test_docx_reader_missing_file(tmp_path):
    missing_file = tmp_path / "missing_resume.docx"

    result = read_docx_source(str(missing_file))

    assert result["status"] == "missing"
    assert result["content"] == ""
    assert result["metadata"]["has_extractable_text"] is False
    assert result["warnings"]
    assert result["errors"] == []


def test_docx_reader_empty_file(tmp_path):
    empty_file = tmp_path / "empty.docx"
    empty_file.write_bytes(b"")

    result = read_docx_source(str(empty_file))

    assert result["status"] == "empty"
    assert result["content"] == ""
    assert result["metadata"]["has_extractable_text"] is False
    assert result["warnings"]
    assert result["errors"] == []


def test_docx_reader_corrupted_file_does_not_crash(tmp_path):
    corrupted_file = tmp_path / "corrupted.docx"
    corrupted_file.write_text("This is not a real DOCX file", encoding="utf-8")

    result = read_docx_source(str(corrupted_file))

    assert result["status"] == "unreadable"
    assert result["content"] == ""
    assert result["metadata"]["has_extractable_text"] is False
    assert result["errors"]
