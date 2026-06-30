import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.projection.output_normalizers import apply_output_normalization


def test_text_rules():
    assert apply_output_normalization("  hello   world ", ["trim", "collapse_spaces", "title_case"]) == "Hello World"


def test_email_lowercase():
    assert apply_output_normalization(["A@B.COM"], "email_lowercase") == ["a@b.com"]


def test_https_url():
    assert apply_output_normalization("github.com/user/", "https_url") == "https://github.com/user"


def test_sorted_unique_skills():
    v = [{"name":"SQL"}, {"name":"Python"}, {"name":"SQL"}]
    assert apply_output_normalization(v, "sorted_unique") == [{"name":"Python"}, {"name":"SQL"}]


def test_rounding():
    assert apply_output_normalization(1.234, "round_1_decimal") == 1.2
    assert apply_output_normalization(1.236, "round_2_decimal") == 1.24
