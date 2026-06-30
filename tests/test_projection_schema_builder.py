import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.projection.schema_builder import build_projected_schema


def test_required_and_nullable_schema():
    cfg = {"output":{"fields":[{"output_name":"name","path":"full_name","type":"string","missing":"error"},{"output_name":"city","path":"location.city","type":"string","missing":"null"}]},"options":{"include_provenance":False,"include_confidence":False}}
    schema = build_projected_schema(cfg)
    assert "name" in schema["required"]
    assert schema["properties"]["city"]["type"] == ["string", "null"]


def test_metadata_properties_when_enabled():
    cfg = {"output":{"fields":[]},"options":{"include_provenance":True,"include_confidence":True}}
    schema = build_projected_schema(cfg)
    assert "_provenance" in schema["properties"]
    assert "_confidence" in schema["properties"]
