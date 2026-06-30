import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.projection.validator import validate_projected_output


def test_valid_output_passes():
    schema = {"type":"object","required":["name"],"properties":{"name":{"type":"string"}},"additionalProperties":False}
    assert validate_projected_output({"name":"A"}, schema) == []


def test_missing_required_fails():
    schema = {"type":"object","required":["name"],"properties":{"name":{"type":"string"}},"additionalProperties":False}
    assert validate_projected_output({}, schema)
