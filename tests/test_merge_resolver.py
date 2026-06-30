import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.merge.resolver import resolve_all

def c(field, value, source_id="s", source_type="recruiter_csv", confidence=0.9):
    return {
        "field_path": field,
        "raw_value": value,
        "normalized_value": value,
        "source_id": source_id,
        "source_type": source_type,
        "source_name": "recruiter.csv" if source_type == "recruiter_csv" else "vansh_resume.docx",
        "method": "test_method",
        "confidence": confidence,
        "normalization_method": "test_normalizer",
        "normalization_status": "ok",
        "warnings": [],
        "metadata": {},
    }


def test_emails_union_dedupe():
    r = resolve_all([c("emails", "a@example.com"), c("emails", "a@example.com"), c("emails", "b@example.com")])
    assert r["emails"] == ["a@example.com", "b@example.com"]


def test_full_name_selects_high_confidence():
    r = resolve_all([c("full_name", "Low", confidence=0.5), c("full_name", "High", confidence=0.95)])
    assert r["full_name"] == "High"


def test_links_merge():
    r = resolve_all([c("links.linkedin", "https://linkedin.com/in/a"), c("links.github", "https://github.com/a")])
    assert r["links"]["linkedin"] == "https://linkedin.com/in/a"
    assert r["links"]["github"] == "https://github.com/a"


def test_skills_objects():
    r = resolve_all([c("skills", "Python"), c("skills", "SQL")])
    assert {s["name"] for s in r["skills"]} == {"Python", "SQL"}
