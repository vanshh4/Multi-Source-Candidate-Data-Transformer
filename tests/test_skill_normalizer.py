import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.normalizers.skill_normalizer import normalize_skill_candidate


def c(value):
    return {"field_path":"skills","raw_value":value,"normalized_value":value,"source_id":"s","source_type":"t","source_name":"n","method":"m","confidence":0.9,"warnings":[],"metadata":{}}


def test_powerbi_alias():
    assert normalize_skill_candidate(c("powerbi"))["normalized_value"] == "Power BI"


def test_sql_alias():
    assert normalize_skill_candidate(c("sql"))["normalized_value"] == "SQL"


def test_sklearn_alias():
    assert normalize_skill_candidate(c("sklearn"))["normalized_value"] == "scikit-learn"
