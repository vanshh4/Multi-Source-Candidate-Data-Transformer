
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from transformer.readers.csv_reader import DEFAULT_EXPECTED_COLUMNS, read_csv_source


def test_csv_reader_valid_file(tmp_path):
    csv_file = tmp_path / "recruiter.csv"
    csv_file.write_text(
        "candidate_name,email,phone,current_location,linkedin,github,portfolio,headline,years_experience,skills\n"
        "Sample Candidate,sample@example.com,+919999999999,Delhi IN,https://linkedin.com/in/sample,,,,1.0,Python SQL\n",
        encoding="utf-8",
    )

    result = read_csv_source(str(csv_file))

    assert result["status"] == "ok"
    assert result["content_type"] == "tabular"
    assert result["metadata"]["row_count"] == 1
    assert result["metadata"]["column_count"] == len(DEFAULT_EXPECTED_COLUMNS)
    assert result["metadata"]["missing_expected_columns"] == []
    assert len(result["content"]) == 1
    assert result["content"][0]["candidate_name"] == "Sample Candidate"
    assert result["warnings"] == []
    assert result["errors"] == []


def test_csv_reader_missing_file(tmp_path):
    missing_file = tmp_path / "missing_recruiter.csv"

    result = read_csv_source(str(missing_file))

    assert result["status"] == "missing"
    assert result["content"] == []
    assert result["metadata"]["row_count"] == 0
    assert result["warnings"]
    assert result["errors"] == []


def test_csv_reader_empty_file(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")

    result = read_csv_source(str(empty_file))

    assert result["status"] == "empty"
    assert result["content"] == []
    assert result["metadata"]["row_count"] == 0
    assert result["warnings"]


def test_csv_reader_missing_expected_columns_returns_partial(tmp_path):
    csv_file = tmp_path / "partial_recruiter.csv"
    csv_file.write_text(
        "candidate_name,email\nSample Candidate,sample@example.com\n",
        encoding="utf-8",
    )

    result = read_csv_source(str(csv_file))

    assert result["status"] == "partial"
    assert result["metadata"]["row_count"] == 1
    assert "phone" in result["metadata"]["missing_expected_columns"]
    assert result["warnings"]
    assert result["errors"] == []
