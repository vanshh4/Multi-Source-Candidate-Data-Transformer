import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.normalizers.phone_normalizer import normalize_phone_candidate


def c(value):
    return {"field_path":"phones","raw_value":value,"normalized_value":value,"source_id":"s","source_type":"t","source_name":"n","method":"m","confidence":0.9,"warnings":[],"metadata":{}}


def test_indian_phone_with_country_code():
    assert normalize_phone_candidate(c("+91 99999 99999"))["normalized_value"] == "+919999999999"


def test_indian_local_phone_defaults_to_91():
    assert normalize_phone_candidate(c("9999999999"))["normalized_value"] == "+919999999999"


def test_invalid_short_phone():
    assert normalize_phone_candidate(c("12345"))["normalization_status"] == "invalid"
