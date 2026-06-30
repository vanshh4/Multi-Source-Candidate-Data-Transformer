import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.normalizers.link_normalizer import normalize_link_candidate


def c(value):
    return {"field_path":"links.linkedin","raw_value":value,"normalized_value":value,"source_id":"s","source_type":"t","source_name":"n","method":"m","confidence":0.9,"warnings":[],"metadata":{}}


def test_adds_https():
    assert normalize_link_candidate(c("linkedin.com/in/sample/"))["normalized_value"] == "https://linkedin.com/in/sample"


def test_keeps_https():
    assert normalize_link_candidate(c("https://github.com/sample"))["normalized_value"] == "https://github.com/sample"


def test_invalid_url():
    assert normalize_link_candidate(c("not-a-url"))["normalization_status"] == "invalid"
