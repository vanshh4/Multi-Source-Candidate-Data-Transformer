import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.projection.path_resolver import get_by_path, path_exists, is_missing_value


def test_resolves_nested_path():
    data = {"location": {"city": "Delhi"}}
    assert get_by_path(data, "location.city") == (True, "Delhi")


def test_missing_path():
    assert get_by_path({"location": None}, "location.city")[0] is False


def test_missing_value_detection():
    assert is_missing_value(None)
    assert is_missing_value([])
    assert not is_missing_value("Delhi")
