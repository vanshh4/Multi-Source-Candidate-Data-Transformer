import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from transformer.extractors.resume_extractor import extract_resume_candidates


def _resume_reader_result(text, status="ok", source_type="resume_docx"):
    return {
        "source_id": source_type,
        "source_type": source_type,
        "source_name": "vansh_resume.docx" if source_type == "resume_docx" else "sample_resume_text.txt",
        "status": status,
        "content_type": "text",
        "content": text,
        "metadata": {},
        "warnings": [],
        "errors": [],
    }


def test_resume_extractor_extracts_core_contact_fields():
    text = """
Sample Candidate
Data Analyst Intern
Email: sample@example.com | Phone: +91 99999 99999
LinkedIn: https://linkedin.com/in/samplecandidate
GitHub: github.com/samplecandidate
Skills
Python, SQL, Power BI, Excel
Education
B.Tech Computer Science
XYZ University
2025
"""
    candidates = extract_resume_candidates(_resume_reader_result(text))
    field_paths = [candidate["field_path"] for candidate in candidates]

    assert "full_name" in field_paths
    assert "headline" in field_paths
    assert "emails" in field_paths
    assert "phones" in field_paths
    assert "links.linkedin" in field_paths
    assert "links.github" in field_paths
    assert "education" in field_paths
    assert field_paths.count("skills") >= 4


def test_resume_extractor_empty_text_returns_empty():
    candidates = extract_resume_candidates(_resume_reader_result(""))

    assert candidates == []


def test_resume_extractor_non_ok_status_returns_empty():
    candidates = extract_resume_candidates(_resume_reader_result("Sample Candidate", status="unreadable"))

    assert candidates == []


def test_resume_extractor_includes_source_details():
    text = "Sample Candidate\nsample@example.com\nSkills\nPython"

    candidates = extract_resume_candidates(_resume_reader_result(text))

    assert candidates
    assert all(candidate["source_id"] == "resume_docx" for candidate in candidates)
    assert all(candidate["source_type"] == "resume_docx" for candidate in candidates)
    assert all(candidate["source_name"] == "vansh_resume.docx" for candidate in candidates)
    assert all("method" in candidate for candidate in candidates)
    assert all("confidence" in candidate for candidate in candidates)
