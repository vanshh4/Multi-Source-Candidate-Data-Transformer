import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.normalizers.normalizer_router import normalize_field_candidate, normalize_field_candidates, build_normalization_output


def c(field, value):
    return {"field_path":field,"raw_value":value,"normalized_value":value,"source_id":"s","source_type":"t","source_name":"n","method":"m","confidence":0.9,"warnings":[],"metadata":{}}


def test_router_routes_email():
    assert normalize_field_candidate(c("emails", "A@B.COM"))["normalized_value"] == "a@b.com"


def test_router_routes_phone():
    assert normalize_field_candidate(c("phones", "9999999999"))["normalized_value"] == "+919999999999"


def test_router_routes_link():
    assert normalize_field_candidate(c("links.github", "github.com/user"))["normalized_value"] == "https://github.com/user"


def test_router_routes_location():
    assert normalize_field_candidate(c("location.raw", "Delhi, India"))["normalized_value"]["country"] == "IN"


def test_batch_output_shape():
    items = [c("emails", "A@B.COM"), c("skills", "powerbi")]
    output = build_normalization_output(run_id="run_001", field_candidates=items)
    assert output["run_id"] == "run_001"
    assert output["normalized_candidate_count"] == 2
    assert output["normalized_candidates"][1]["normalized_value"] == "Power BI"


def test_unknown_field_does_not_crash():
    r = normalize_field_candidate(c("unknown.field", "value"))
    assert r["normalization_status"] == "unchanged"
    assert r["warnings"]
