import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.provenance.provenance_builder import build_provenance_item

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


def test_provenance_contains_required_source_and_methods():
    item = build_provenance_item(c("emails", "a@example.com"), selected=True)
    assert item["field"] == "emails"
    assert item["source"]["source_id"] == "s"
    assert item["source"]["source_type"] == "recruiter_csv"
    assert "test_method" in item["method"]
    assert "test_normalizer" in item["method"]
    assert item["selected"] is True
    assert item["conflict"] is False
