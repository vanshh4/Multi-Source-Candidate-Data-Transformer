import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from transformer.extractors.structured_extractor import extract_structured_candidates


def _reader_result(rows, status="ok"):
    return {
        "source_id": "recruiter_csv",
        "source_type": "recruiter_csv",
        "source_name": "recruiter.csv",
        "status": status,
        "content_type": "tabular",
        "content": rows,
        "metadata": {},
        "warnings": [],
        "errors": [],
    }


def test_structured_extractor_valid_row_produces_candidates():
    result = _reader_result([
        {
            "candidate_name": "Sample Candidate",
            "email": "SAMPLE@EXAMPLE.COM",
            "phone": "+91 99999 99999",
            "current_location": "Delhi, India",
            "linkedin": "linkedin.com/in/samplecandidate",
            "years_experience": "1.5",
            "skills": "Python, SQL, Power BI",
        }
    ])

    candidates = extract_structured_candidates(result)
    field_paths = [candidate["field_path"] for candidate in candidates]

    assert "full_name" in field_paths
    assert "emails" in field_paths
    assert "phones" in field_paths
    assert "location.raw" in field_paths
    assert "links.linkedin" in field_paths
    assert "years_experience" in field_paths
    assert field_paths.count("skills") == 3
    assert all(candidate["source_id"] == "recruiter_csv" for candidate in candidates)
    assert all("confidence" in candidate for candidate in candidates)


def test_structured_extractor_skips_empty_values():
    result = _reader_result([{"candidate_name": "", "email": "sample@example.com", "phone": ""}])

    candidates = extract_structured_candidates(result)

    assert len(candidates) == 1
    assert candidates[0]["field_path"] == "emails"


def test_structured_extractor_non_ok_status_returns_empty():
    result = _reader_result([], status="missing")

    assert extract_structured_candidates(result) == []


def test_structured_extractor_ignores_unknown_columns():
    result = _reader_result([{"unknown_column": "value", "email": "sample@example.com"}])

    candidates = extract_structured_candidates(result)

    assert len(candidates) == 1
    assert candidates[0]["field_path"] == "emails"
