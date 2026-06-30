import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.canonical.id_generator import generate_candidate_id


def test_same_email_same_id():
    assert generate_candidate_id(emails=["a@example.com"]) == generate_candidate_id(emails=["A@example.com"])


def test_different_email_different_id():
    assert generate_candidate_id(emails=["a@example.com"]) != generate_candidate_id(emails=["b@example.com"])


def test_phone_fallback_works():
    cid = generate_candidate_id(phones=["+919999999999"])
    assert cid.startswith("cand_")
    assert "+919" not in cid


def test_uuid_fallback_works():
    assert generate_candidate_id().startswith("cand_")
