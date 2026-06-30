import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path: sys.path.insert(0, str(SRC_PATH))
from transformer.projection.metadata_projector import attach_projection_metadata, confidence_for_path, provenance_for_path


def candidate():
    return {"full_name":"A","provenance":[{"field":"full_name","selected":True,"confidence":0.9,"source":{}}],"overall_confidence":0.8}


def test_provenance_for_path():
    assert len(provenance_for_path(candidate(), "full_name")) == 1


def test_confidence_for_path():
    assert confidence_for_path(candidate(), "full_name") == 0.9


def test_attach_metadata_enabled():
    cfg = {"output":{"fields":[{"output_name":"name","path":"full_name"}]},"options":{"include_provenance":True,"include_confidence":True}}
    out = attach_projection_metadata({"name":"A"}, candidate(), cfg)
    assert "_provenance" in out and "_confidence" in out


def test_attach_metadata_disabled():
    cfg = {"output":{"fields":[{"output_name":"name","path":"full_name"}]},"options":{"include_provenance":False,"include_confidence":False}}
    out = attach_projection_metadata({"name":"A"}, candidate(), cfg)
    assert "_provenance" not in out and "_confidence" not in out
