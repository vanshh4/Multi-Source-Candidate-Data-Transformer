import sys
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from transformer.ui_helpers.manifest_builder import (
    build_ui_manifest,
    create_manifest_for_uploaded_files,
    detect_resume_type,
    sanitize_filename,
)


def test_detect_resume_type_docx():
    ext, manifest_type, source_type = detect_resume_type("vansh_resume.docx")
    assert ext == "docx"
    assert manifest_type == "docx"
    assert source_type == "resume_docx"


def test_detect_resume_type_pdf():
    ext, manifest_type, source_type = detect_resume_type("resume.pdf")
    assert ext == "pdf"
    assert manifest_type == "pdf"
    assert source_type == "resume_pdf"


def test_detect_resume_type_txt():
    ext, manifest_type, source_type = detect_resume_type("sample_resume_text.txt")
    assert ext == "txt"
    assert manifest_type == "txt"
    assert source_type == "resume_txt"


def test_detect_resume_type_unsupported():
    with pytest.raises(ValueError):
        detect_resume_type("resume.xlsx")


def test_build_ui_manifest_contains_correct_paths():
    manifest = build_ui_manifest(
        run_id="ui_run_test",
        recruiter_csv_path="data/ui_uploads/ui_run_test/recruiter.csv",
        resume_path="data/ui_uploads/ui_run_test/vansh_resume.docx",
        projection_config_path="configs/default_projection.yaml",
        output_path="data/outputs/ui/ui_run_test_projected_output.json",
    )

    assert manifest["run"]["run_id"] == "ui_run_test"
    assert manifest["inputs"]["recruiter_csv"]["path"] == "data/ui_uploads/ui_run_test/recruiter.csv"
    assert manifest["inputs"]["resume"]["path"] == "data/ui_uploads/ui_run_test/vansh_resume.docx"
    assert manifest["inputs"]["resume"]["type"] == "docx"
    assert manifest["inputs"]["resume"]["source_type"] == "resume_docx"
    assert manifest["projection"]["config_path"] == "configs/default_projection.yaml"
    assert manifest["output"]["path"] == "data/outputs/ui/ui_run_test_projected_output.json"


def test_sanitize_filename_removes_unsafe_characters():
    assert sanitize_filename("my resume (final).docx") == "my_resume_final_.docx"


def test_create_manifest_for_uploaded_files_copies_and_saves_manifest(tmp_path):
    recruiter = tmp_path / "recruiter.csv"
    recruiter.write_text("candidate_name,email\nSample Candidate,sample@example.com\n", encoding="utf-8")

    resume = tmp_path / "vansh_resume.docx"
    resume.write_bytes(b"fake docx content for copy test")

    uploads_root = tmp_path / "ui_uploads"
    runs_root = tmp_path / "ui_runs"
    outputs_root = tmp_path / "outputs"

    manifest, paths = create_manifest_for_uploaded_files(
        recruiter_csv_path=recruiter,
        resume_path=resume,
        projection_config_path="configs/default_projection.yaml",
        run_id="ui_run_test",
        uploads_root=uploads_root,
        runs_root=runs_root,
        outputs_root=outputs_root,
    )

    assert paths.manifest_path.exists()
    assert (paths.upload_dir / "recruiter.csv").exists()
    assert (paths.upload_dir / "vansh_resume.docx").exists()

    loaded = yaml.safe_load(paths.manifest_path.read_text(encoding="utf-8"))
    assert loaded["run"]["run_id"] == "ui_run_test"
    assert loaded["inputs"]["resume"]["source_type"] == "resume_docx"
    assert manifest["output"]["path"].endswith("ui_run_test_projected_output.json")
