import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.merge.confidence import calculate_overall_confidence, candidate_confidence


def test_candidate_confidence_clamped():
    assert candidate_confidence({"confidence": 5}) == 1.0


def test_invalid_status_reduces_confidence():
    assert candidate_confidence({"confidence": 0.9, "normalization_status": "invalid"}) <= 0.2


def test_overall_confidence_between_zero_and_one():
    candidate = {"full_name": "A", "emails": ["a@example.com"], "phones": [], "location": None, "links": {}, "headline": None, "years_experience": None, "skills": [], "experience": [], "education": [], "provenance": [{"field":"full_name","selected":True,"confidence":0.9},{"field":"emails","selected":True,"confidence":0.95}]}
    score = calculate_overall_confidence(candidate)
    assert 0 <= score <= 1
