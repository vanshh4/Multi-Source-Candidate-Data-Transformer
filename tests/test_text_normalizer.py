import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.normalizers.text_normalizer import normalize_text_candidate


def c(field, value):
    return {"field_path":field,"raw_value":value,"normalized_value":value,"source_id":"s","source_type":"t","source_name":"n","method":"m","confidence":0.9,"warnings":[],"metadata":{}}


def test_name_cleanup():
    assert normalize_text_candidate(c("full_name", "  sample   candidate  "))["normalized_value"] == "Sample Candidate"


def test_headline_cleanup():
    assert normalize_text_candidate(c("headline", " Data   Analyst  Intern "))["normalized_value"] == "Data Analyst Intern"


def test_empty_text():
    assert normalize_text_candidate(c("headline", ""))["normalization_status"] == "empty"
