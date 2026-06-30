import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.normalizers.experience_normalizer import normalize_years_experience_candidate, normalize_experience_candidate


def c(field, value):
    return {"field_path":field,"raw_value":value,"normalized_value":value,"source_id":"s","source_type":"t","source_name":"n","method":"m","confidence":0.9,"warnings":[],"metadata":{}}


def test_years_only():
    assert normalize_years_experience_candidate(c("years_experience", "2 years"))["normalized_value"] == 2.0


def test_years_months():
    assert normalize_years_experience_candidate(c("years_experience", "2 years 6 months"))["normalized_value"] == 2.5


def test_numeric_years():
    assert normalize_years_experience_candidate(c("years_experience", "1.5"))["normalized_value"] == 1.5


def test_experience_text_cleanup():
    r = normalize_experience_candidate(c("experience", "  Role at Company  "))
    assert r["normalized_value"] == "Role at Company"
