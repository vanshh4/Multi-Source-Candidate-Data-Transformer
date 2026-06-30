
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from transformer.readers.text_reader import read_text_source


def test_text_reader_valid_file(tmp_path):
    sample_file = tmp_path / "sample_resume_text.txt"
    sample_text = "Sample Candidate\nEmail: sample@example.com\nSkills: Python, SQL"
    sample_file.write_text(sample_text, encoding="utf-8")

    result = read_text_source(str(sample_file))

    assert result["status"] == "ok"
    assert result["content_type"] == "text"
    assert result["content"] == sample_text
    assert result["metadata"]["line_count"] == 3
    assert result["metadata"]["character_count"] == len(sample_text)
    assert result["metadata"]["has_extractable_text"] is True
    assert result["warnings"] == []
    assert result["errors"] == []


def test_text_reader_missing_file(tmp_path):
    missing_file = tmp_path / "missing_resume_text.txt"

    result = read_text_source(str(missing_file), required=False)

    assert result["status"] == "missing"
    assert result["content"] == ""
    assert result["metadata"]["has_extractable_text"] is False
    assert result["warnings"]
    assert result["errors"] == []


def test_text_reader_empty_file(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")

    result = read_text_source(str(empty_file))

    assert result["status"] == "empty"
    assert result["content"] == ""
    assert result["metadata"]["line_count"] == 0
    assert result["metadata"]["character_count"] == 0
    assert result["metadata"]["has_extractable_text"] is False
    assert result["warnings"]
    assert result["errors"] == []
