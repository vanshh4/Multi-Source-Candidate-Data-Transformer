import copy
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.canonical.builder import build_canonical_candidate
from transformer.validation.schema_validator import validate_canonical_candidate

def c(field, value, source_id="s", source_type="recruiter_csv", confidence=0.9):
    return {
        "field_path": field,
        "raw_value": value,
        "normalized_value": value,
        "source_id": source_id,
        "source_type": source_type,
        "source_name": "recruiter.csv" if source_type == "recruiter_csv" else "vansh_resume.docx",
        "method": "test_method",
        "confidence": confidence,
        "normalization_method": "test_normalizer",
        "normalization_status": "ok",
        "warnings": [],
        "metadata": {},
    }


def valid_candidate():
    return build_canonical_candidate([
        c("full_name", "Sample Candidate"),
        c("emails", "sample@example.com"),
        c("phones", "+919999999999"),
        c("location.raw", {"city":"Delhi","region":"Delhi","country":"IN","raw":"Delhi, India"}),
        c("skills", "Python"),
    ])


def test_valid_canonical_passes_schema():
    errors = validate_canonical_candidate(valid_candidate())
    assert errors == []


def test_missing_required_field_fails():
    candidate = valid_candidate()
    candidate.pop("candidate_id")
    assert validate_canonical_candidate(candidate)


def test_invalid_phone_fails():
    candidate = valid_candidate()
    candidate["phones"] = ["99999"]
    assert validate_canonical_candidate(candidate)


def test_invalid_confidence_fails():
    candidate = valid_candidate()
    candidate["overall_confidence"] = 2
    assert validate_canonical_candidate(candidate)
