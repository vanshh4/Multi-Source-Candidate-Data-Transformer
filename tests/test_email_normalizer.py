import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.normalizers.email_normalizer import normalize_email_candidate


def c(value):
    return {"field_path":"emails","raw_value":value,"normalized_value":value,"source_id":"s","source_type":"t","source_name":"n","method":"m","confidence":0.9,"warnings":[],"metadata":{}}


def test_email_lowercase_and_trim():
    r = normalize_email_candidate(c(" SAMPLE@Example.COM "))
    assert r["normalization_status"] == "ok"
    assert r["normalized_value"] == "sample@example.com"


def test_invalid_email():
    r = normalize_email_candidate(c("not-an-email"))
    assert r["normalization_status"] == "invalid"
    assert r["normalized_value"] is None


def test_empty_email():
    r = normalize_email_candidate(c(""))
    assert r["normalization_status"] == "empty"
