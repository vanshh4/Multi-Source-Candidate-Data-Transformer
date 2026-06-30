import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from transformer.extractors.extractor_router import build_extraction_output, extract_from_source, extract_from_sources


def test_extractor_router_routes_recruiter_csv():
    reader_result = {
        "source_id": "recruiter_csv",
        "source_type": "recruiter_csv",
        "source_name": "recruiter.csv",
        "status": "ok",
        "content_type": "tabular",
        "content": [{"candidate_name": "Sample Candidate", "email": "sample@example.com"}],
    }

    candidates = extract_from_source(reader_result)

    assert len(candidates) >= 2
    assert {candidate["field_path"] for candidate in candidates} >= {"full_name", "emails"}


def test_extractor_router_routes_resume_docx():
    reader_result = {
        "source_id": "resume_docx",
        "source_type": "resume_docx",
        "source_name": "vansh_resume.docx",
        "status": "ok",
        "content_type": "text",
        "content": "Sample Candidate\nsample@example.com\nSkills\nPython SQL",
    }

    candidates = extract_from_source(reader_result)

    assert len(candidates) >= 3
    assert "emails" in {candidate["field_path"] for candidate in candidates}


def test_extractor_router_unknown_source_returns_empty():
    reader_result = {"source_type": "unknown", "status": "ok", "content": "anything"}

    assert extract_from_source(reader_result) == []


def test_extract_from_sources_combines_candidates():
    reader_results = [
        {
            "source_id": "recruiter_csv",
            "source_type": "recruiter_csv",
            "source_name": "recruiter.csv",
            "status": "ok",
            "content_type": "tabular",
            "content": [{"candidate_name": "Sample Candidate", "email": "sample@example.com"}],
        },
        {
            "source_id": "resume_docx",
            "source_type": "resume_docx",
            "source_name": "vansh_resume.docx",
            "status": "ok",
            "content_type": "text",
            "content": "Sample Candidate\nsample@example.com\nSkills\nPython",
        },
    ]

    candidates = extract_from_sources(reader_results)

    assert len(candidates) >= 4


def test_build_extraction_output_shape():
    reader_results = [
        {
            "source_id": "resume_docx",
            "source_type": "resume_docx",
            "source_name": "vansh_resume.docx",
            "status": "ok",
            "content_type": "text",
            "content": "Sample Candidate\nsample@example.com",
        }
    ]

    output = build_extraction_output(run_id="run_001", reader_results=reader_results)

    assert output["run_id"] == "run_001"
    assert output["field_candidate_count"] == len(output["field_candidates"])
    assert output["field_candidate_count"] >= 2
