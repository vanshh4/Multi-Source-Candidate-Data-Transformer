
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from transformer.readers.reader_router import infer_source_type, read_source, read_sources_from_manifest


def test_infer_source_type_from_extension():
    assert infer_source_type("data/samples/recruiter.csv") == "recruiter_csv"
    assert infer_source_type("data/samples/sample_resume_text.txt") == "resume_txt"
    assert infer_source_type("data/samples/vansh_resume.docx") == "resume_docx"
    assert infer_source_type("data/samples/resume.pdf") == "resume_pdf"


def test_infer_source_type_prefers_explicit_supported_source_type():
    assert infer_source_type("some/random/path", "resume_docx") == "resume_docx"
    assert infer_source_type("some/random/path", "recruiter_csv") == "recruiter_csv"


def test_read_source_routes_text_file(tmp_path):
    text_file = tmp_path / "sample_resume_text.txt"
    text_file.write_text("Sample Candidate\nEmail: sample@example.com", encoding="utf-8")

    result = read_source(
        {
            "path": str(text_file),
            "source_id": "sample_resume_text",
            "source_type": "resume_txt",
            "required": False,
        }
    )

    assert result["status"] == "ok"
    assert result["source_type"] == "resume_txt"
    assert result["content_type"] == "text"


def test_read_source_routes_csv_file(tmp_path):
    csv_file = tmp_path / "recruiter.csv"
    csv_file.write_text(
        "candidate_name,email,phone,current_location,linkedin,github,portfolio,headline,years_experience,skills\n"
        "Sample Candidate,sample@example.com,+919999999999,Delhi IN,,,,,1.0,Python\n",
        encoding="utf-8",
    )

    result = read_source(
        {
            "path": str(csv_file),
            "source_id": "recruiter_csv",
            "source_type": "recruiter_csv",
            "required": False,
        }
    )

    assert result["status"] == "ok"
    assert result["source_type"] == "recruiter_csv"
    assert result["content_type"] == "tabular"


def test_read_source_routes_docx_file(tmp_path):
    Document = pytest.importorskip("docx").Document

    docx_file = tmp_path / "vansh_resume.docx"
    document = Document()
    document.add_paragraph("Sample Candidate")
    document.save(str(docx_file))

    result = read_source(
        {
            "path": str(docx_file),
            "source_id": "resume_docx",
            "source_type": "resume_docx",
            "required": False,
        }
    )

    assert result["status"] == "ok"
    assert result["source_type"] == "resume_docx"
    assert result["content_type"] == "text"


def test_read_source_unsupported_extension_returns_unreadable(tmp_path):
    unknown_file = tmp_path / "resume.xyz"
    unknown_file.write_text("content", encoding="utf-8")

    result = read_source(
        {
            "path": str(unknown_file),
            "source_id": "unknown_resume",
            "required": False,
        }
    )

    assert result["status"] == "unreadable"
    assert result["source_type"] == "unknown"
    assert result["errors"]


def test_read_sources_from_manifest_reads_recruiter_and_resume(tmp_path):
    csv_file = tmp_path / "recruiter.csv"
    csv_file.write_text(
        "candidate_name,email,phone,current_location,linkedin,github,portfolio,headline,years_experience,skills\n"
        "Sample Candidate,sample@example.com,+919999999999,Delhi IN,,,,,1.0,Python\n",
        encoding="utf-8",
    )

    text_file = tmp_path / "sample_resume_text.txt"
    text_file.write_text("Sample Candidate\nEmail: sample@example.com", encoding="utf-8")

    manifest = {
        "inputs": {
            "recruiter_csv": {
                "path": str(csv_file),
                "required": False,
                "source_id": "recruiter_csv",
                "source_type": "recruiter_csv",
            },
            "resume": {
                "path": str(text_file),
                "required": False,
                "source_id": "sample_resume_text",
                "source_type": "resume_txt",
            },
        }
    }

    results = read_sources_from_manifest(manifest)

    assert len(results) == 2
    assert results[0]["source_id"] == "recruiter_csv"
    assert results[0]["status"] == "ok"
    assert results[1]["source_id"] == "sample_resume_text"
    assert results[1]["status"] == "ok"
