
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from transformer.readers.pdf_reader import read_pdf_source

pytest.importorskip("pdfplumber")


def test_pdf_reader_missing_file(tmp_path):
    missing_file = tmp_path / "missing_resume.pdf"

    result = read_pdf_source(str(missing_file))

    assert result["status"] == "missing"
    assert result["content"] == ""
    assert result["metadata"]["has_extractable_text"] is False
    assert result["warnings"]
    assert result["errors"] == []


def test_pdf_reader_empty_file(tmp_path):
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")

    result = read_pdf_source(str(empty_file))

    assert result["status"] == "empty"
    assert result["content"] == ""
    assert result["metadata"]["has_extractable_text"] is False
    assert result["warnings"]
    assert result["errors"] == []


def test_pdf_reader_corrupted_file_does_not_crash(tmp_path):
    corrupted_file = tmp_path / "corrupted.pdf"
    corrupted_file.write_text("This is not a real PDF file", encoding="utf-8")

    result = read_pdf_source(str(corrupted_file))

    assert result["status"] == "unreadable"
    assert result["content"] == ""
    assert result["metadata"]["has_extractable_text"] is False
    assert result["errors"]


def test_pdf_reader_valid_pdf_if_reportlab_available(tmp_path):
    reportlab = pytest.importorskip("reportlab")
    from reportlab.pdfgen import canvas

    pdf_file = tmp_path / "resume.pdf"
    c = canvas.Canvas(str(pdf_file))
    c.drawString(100, 750, "Sample Candidate")
    c.drawString(100, 730, "Email: sample@example.com")
    c.save()

    result = read_pdf_source(str(pdf_file))

    assert result["status"] == "ok"
    assert result["content_type"] == "text"
    assert "Sample Candidate" in result["content"]
    assert result["metadata"]["page_count"] >= 1
    assert result["metadata"]["has_extractable_text"] is True
