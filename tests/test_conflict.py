import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.merge.conflict import values_conflict


def test_same_values_no_conflict():
    assert values_conflict("A", "a") is False


def test_different_scalar_conflicts():
    assert values_conflict("Delhi", "Mumbai", field_path="location.raw") is True


def test_list_fields_do_not_conflict():
    assert values_conflict("a@example.com", "b@example.com", field_path="emails") is False


def test_years_difference_conflicts():
    assert values_conflict(1.0, 2.0, field_path="years_experience") is True
