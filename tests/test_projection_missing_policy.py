import sys
from pathlib import Path
import pytest
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.projection.missing_policy import OMIT, handle_missing_value, resolve_missing_policy
from transformer.projection.errors import ProjectionMissingValueError


def test_null_policy():
    assert handle_missing_value("x", "y", "null") is None


def test_omit_policy():
    assert handle_missing_value("x", "y", "omit") == OMIT


def test_error_policy():
    with pytest.raises(ProjectionMissingValueError):
        handle_missing_value("x", "y", "error")


def test_required_defaults_to_error():
    assert resolve_missing_policy({"required": True}, {}) == "error"
