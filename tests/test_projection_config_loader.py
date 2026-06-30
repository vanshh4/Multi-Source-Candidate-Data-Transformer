import sys
from pathlib import Path
import pytest
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.projection.config_loader import load_projection_config, validate_projection_config
from transformer.projection.errors import ProjectionConfigError


def test_valid_yaml_loads_without_schema(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("version: '1.0'\noutput:\n  fields:\n    - output_name: name\n      path: full_name\n", encoding="utf-8")
    cfg = load_projection_config(str(p), schema_path=None)
    assert cfg["version"] == "1.0"


def test_missing_config_raises():
    with pytest.raises(ProjectionConfigError):
        load_projection_config("missing.yaml", schema_path=None)


def test_invalid_config_with_schema_reports_error(tmp_path):
    schema = tmp_path / "schema.json"
    schema.write_text('{"type":"object","required":["version"]}', encoding="utf-8")
    errors = validate_projection_config({"output": {}}, schema_path=str(schema))
    assert errors
