import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.normalizers.location_normalizer import normalize_location_candidate


def c(value):
    return {"field_path":"location.raw","raw_value":value,"normalized_value":value,"source_id":"s","source_type":"t","source_name":"n","method":"m","confidence":0.9,"warnings":[],"metadata":{}}


def test_delhi_india():
    r = normalize_location_candidate(c("Delhi, India"))
    assert r["normalized_value"]["city"] == "Delhi"
    assert r["normalized_value"]["country"] == "IN"


def test_gurgaon_haryana_india():
    r = normalize_location_candidate(c("Gurgaon, Haryana, India"))
    assert r["normalized_value"]["region"] == "Haryana"
    assert r["normalized_value"]["country"] == "IN"


def test_unknown_location_partial():
    assert normalize_location_candidate(c("Unknown Place"))["normalization_status"] == "partial"
