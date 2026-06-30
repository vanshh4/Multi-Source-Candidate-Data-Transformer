import sys
from pathlib import Path
import pytest
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.projection.projector import project_candidate
from transformer.projection.errors import ProjectionMissingValueError


def candidate():
    return {
        "candidate_id":"cand_123",
        "full_name":"sample candidate",
        "emails":["A@B.COM"],
        "phones":["9999999999"],
        "location":{"city":"Delhi","region":"Delhi","country":"IN","raw":"Delhi, India"},
        "links":{"linkedin":"linkedin.com/in/sample/","github":None,"portfolio":None,"other":[]},
        "headline":" data   analyst ",
        "years_experience":1.234,
        "skills":[{"name":"powerbi","confidence":0.9,"sources":["s"]}],
        "experience":[],
        "education":[],
        "provenance":[{"field":"full_name","selected":True,"confidence":0.9,"source":{}}],
        "overall_confidence":0.876,
    }


def test_default_like_projection():
    cfg = {"output":{"fields":[{"output_name":"full_name","path":"full_name","type":"string","missing":"null","normalization":["trim","collapse_spaces","title_case"]},{"output_name":"overall_confidence","path":"overall_confidence","type":"number","normalization":"round_2_decimal"}]},"options":{"include_provenance":True,"include_confidence":True}}
    out = project_candidate(candidate(), cfg)
    assert out["full_name"] == "Sample Candidate"
    assert out["overall_confidence"] == 0.88
    assert "_provenance" in out


def test_minimal_projection_omit_missing():
    cfg = {"output":{"fields":[{"output_name":"name","path":"full_name","type":"string"},{"output_name":"github","path":"links.github","type":"string","missing":"omit"}]},"options":{"missing_default":"null","include_provenance":False,"include_confidence":False}}
    out = project_candidate(candidate(), cfg)
    assert "name" in out
    assert "github" not in out
    assert "_provenance" not in out


def test_client_projection_nested_paths():
    cfg = {"output":{"fields":[{"output_name":"external_candidate_key","path":"candidate_id","type":"string","missing":"error"},{"output_name":"current_city","path":"location.city","type":"string","missing":"null"},{"output_name":"linkedin_url","path":"links.linkedin","type":"string","normalization":"https_url"}]},"options":{"include_provenance":False,"include_confidence":False}}
    out = project_candidate(candidate(), cfg)
    assert out["external_candidate_key"] == "cand_123"
    assert out["current_city"] == "Delhi"
    assert out["linkedin_url"] == "https://linkedin.com/in/sample"


def test_missing_error_raises():
    cfg = {"output":{"fields":[{"output_name":"x","path":"missing.path","type":"string","missing":"error"}]},"options":{"include_provenance":False,"include_confidence":False}}
    with pytest.raises(ProjectionMissingValueError):
        project_candidate(candidate(), cfg)
