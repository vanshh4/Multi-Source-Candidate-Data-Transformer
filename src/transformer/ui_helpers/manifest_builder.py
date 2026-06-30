"""UI manifest builder helpers.

The Streamlit UI should remain a thin input/output layer. This module creates a
run-specific manifest for uploaded recruiter/resume files and selected runtime
projection config, then the existing transformer pipeline consumes that manifest.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import re
import shutil
import uuid

import yaml


SUPPORTED_RESUME_EXTENSIONS = {"docx", "pdf", "txt"}
RESUME_EXTENSION_TO_SOURCE = {
    "docx": ("resume_docx", "resume_docx"),
    "pdf": ("resume_pdf", "resume_pdf"),
    "txt": ("resume_txt", "resume_txt"),
}


@dataclass(frozen=True)
class UIManifestPaths:
    """Paths generated for one UI run."""

    run_id: str
    upload_dir: Path
    run_dir: Path
    manifest_path: Path
    output_path: Path


def sanitize_filename(filename: str) -> str:
    """Return a safe filename while preserving extension."""
    name = Path(filename or "uploaded_file").name
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return name or "uploaded_file"


def generate_run_id(prefix: str = "ui_run") -> str:
    """Generate a short timestamped UI run ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{suffix}"


def detect_resume_type(resume_path: str | Path) -> tuple[str, str, str]:
    """
    Detect resume extension, manifest type, and source_type.

    Returns:
        (extension, manifest_type, source_type)
    """
    ext = Path(resume_path).suffix.lower().lstrip(".")
    if ext not in SUPPORTED_RESUME_EXTENSIONS:
        raise ValueError(
            f"Unsupported resume extension '.{ext}'. Supported extensions: {sorted(SUPPORTED_RESUME_EXTENSIONS)}"
        )
    manifest_type, source_type = RESUME_EXTENSION_TO_SOURCE[ext]
    return ext, ext, source_type


def build_ui_manifest(
    *,
    run_id: str,
    recruiter_csv_path: str | Path,
    resume_path: str | Path,
    projection_config_path: str | Path,
    output_path: str | Path,
    description: str = "UI run for candidate transformer.",
) -> Dict[str, Any]:
    """Build a manifest dictionary for one UI pipeline run."""
    resume_ext, resume_type, resume_source_type = detect_resume_type(resume_path)

    return {
        "run": {
            "run_id": run_id,
            "description": description,
        },
        "inputs": {
            "recruiter_csv": {
                "path": str(Path(recruiter_csv_path).as_posix()),
                "required": False,
                "source_id": "recruiter_csv",
                "source_type": "recruiter_csv",
            },
            "resume": {
                "path": str(Path(resume_path).as_posix()),
                "type": resume_type,
                "required": False,
                "source_id": resume_source_type,
                "source_type": resume_source_type,
            },
        },
        "projection": {
            "config_path": str(Path(projection_config_path).as_posix()),
        },
        "output": {
            "path": str(Path(output_path).as_posix()),
            "pretty_print": True,
        },
        "runtime": {
            "fail_on_source_error": False,
            "unknown_value_policy": "null",
            "preserve_provenance": True,
            "preserve_confidence": True,
        },
    }


def save_manifest(manifest: Dict[str, Any], manifest_path: str | Path) -> Path:
    """Persist manifest YAML to disk."""
    path = Path(manifest_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(manifest, f, sort_keys=False, allow_unicode=True, width=100)
    return path


def make_ui_run_paths(
    *,
    run_id: Optional[str] = None,
    uploads_root: str | Path = "data/ui_uploads",
    runs_root: str | Path = "data/ui_runs",
    outputs_root: str | Path = "data/outputs/ui",
) -> UIManifestPaths:
    """Create and return standard folders/files for one UI run."""
    run_id = run_id or generate_run_id()
    upload_dir = Path(uploads_root) / run_id
    run_dir = Path(runs_root) / run_id
    output_path = Path(outputs_root) / f"{run_id}_projected_output.json"
    manifest_path = run_dir / "manifest.yaml"

    upload_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return UIManifestPaths(
        run_id=run_id,
        upload_dir=upload_dir,
        run_dir=run_dir,
        manifest_path=manifest_path,
        output_path=output_path,
    )


def copy_file_to_run_dir(source_path: str | Path, destination_dir: str | Path, *, filename: Optional[str] = None) -> Path:
    """Copy a local file into the UI run upload directory."""
    src = Path(source_path)
    if not src.exists():
        raise FileNotFoundError(f"Input file not found: {source_path}")
    dest_name = sanitize_filename(filename or src.name)
    dest = Path(destination_dir) / dest_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return dest


def create_manifest_for_uploaded_files(
    *,
    recruiter_csv_path: str | Path,
    resume_path: str | Path,
    projection_config_path: str | Path,
    run_id: Optional[str] = None,
    uploads_root: str | Path = "data/ui_uploads",
    runs_root: str | Path = "data/ui_runs",
    outputs_root: str | Path = "data/outputs/ui",
) -> tuple[Dict[str, Any], UIManifestPaths]:
    """
    Copy uploaded/local files into a run-specific folder and save manifest YAML.

    Returns:
        (manifest_dict, generated_paths)
    """
    paths = make_ui_run_paths(
        run_id=run_id,
        uploads_root=uploads_root,
        runs_root=runs_root,
        outputs_root=outputs_root,
    )

    recruiter_dest = copy_file_to_run_dir(recruiter_csv_path, paths.upload_dir, filename="recruiter.csv")
    resume_dest = copy_file_to_run_dir(resume_path, paths.upload_dir, filename=Path(resume_path).name)

    manifest = build_ui_manifest(
        run_id=paths.run_id,
        recruiter_csv_path=recruiter_dest,
        resume_path=resume_dest,
        projection_config_path=projection_config_path,
        output_path=paths.output_path,
    )
    save_manifest(manifest, paths.manifest_path)
    return manifest, paths
