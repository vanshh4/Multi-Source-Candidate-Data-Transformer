import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.canonical.builder import build_canonical_candidate

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


def test_builds_required_canonical_fields():
    candidate = build_canonical_candidate([
        c("full_name", "Sample Candidate"),
        c("emails", "sample@example.com"),
        c("phones", "+919999999999"),
        c("location.raw", {"city":"Delhi","region":"Delhi","country":"IN","raw":"Delhi, India"}),
        c("skills", "Python"),
    ])
    for key in ["candidate_id","full_name","emails","phones","location","links","headline","years_experience","skills","experience","education","provenance","overall_confidence"]:
        assert key in candidate
    assert candidate["candidate_id"].startswith("cand_")
    assert candidate["emails"] == ["sample@example.com"]
    assert candidate["skills"][0]["name"] == "Python"
    assert candidate["provenance"]
    assert 0 <= candidate["overall_confidence"] <= 1


def test_missing_values_not_invented():
    candidate = build_canonical_candidate([])
    assert candidate["full_name"] is None
    assert candidate["emails"] == []
    assert candidate["phones"] == []
