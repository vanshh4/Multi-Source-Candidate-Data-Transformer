"""Minimal Streamlit UI for the candidate transformer.

Run from project root:

    PYTHONPATH=src streamlit run ui/streamlit_app.py

On Windows PowerShell:

    $env:PYTHONPATH="src"
    streamlit run ui/streamlit_app.py
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Dict

# Allow running without manually setting PYTHONPATH in some local setups.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import streamlit as st
import yaml

from transformer.pipeline import run_full_pipeline
from transformer.ui_helpers.manifest_builder import (
    build_ui_manifest,
    detect_resume_type,
    generate_run_id,
    sanitize_filename,
    save_manifest,
)


PROJECTION_OPTIONS: Dict[str, str] = {
    "Default Projection": "configs/default_projection.yaml",
    "Minimal Recruiter View": "configs/minimal_recruiter_view.yaml",
    "Client Custom Schema": "configs/client_custom_schema.yaml",
}

UPLOAD_ROOT = Path("data/ui_uploads")
RUN_ROOT = Path("data/ui_runs")
OUTPUT_ROOT = Path("data/outputs/ui")


def _save_uploaded_file(uploaded_file, destination: Path) -> Path:
    """Save Streamlit UploadedFile to destination path."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as f:
        f.write(uploaded_file.getbuffer())
    return destination


def _display_json_download(label: str, payload: dict, file_name: str) -> None:
    data = json.dumps(payload, indent=2, ensure_ascii=False)
    st.download_button(
        label=label,
        data=data,
        file_name=file_name,
        mime="application/json",
    )


def main() -> None:
    st.set_page_config(page_title="Candidate Transformer", layout="wide")

    st.title("Candidate Transformer")
    st.caption("Thin UI for upload → transform → projected JSON output")

    with st.sidebar:
        st.header("Run Settings")
        projection_label = st.selectbox("Projection config", list(PROJECTION_OPTIONS.keys()))
        projection_config_path = PROJECTION_OPTIONS[projection_label]
        include_intermediate = st.checkbox("Include intermediate debug data", value=False)
        skip_canonical_validation = st.checkbox("Skip canonical validation", value=False)
        skip_projection_validation = st.checkbox("Skip projection validation", value=False)

        st.divider()
        st.write("Selected config:")
        st.code(projection_config_path)

    st.subheader("Inputs")
    col1, col2 = st.columns(2)

    with col1:
        recruiter_file = st.file_uploader("Upload recruiter CSV", type=["csv"])

    with col2:
        resume_file = st.file_uploader("Upload resume", type=["docx", "pdf", "txt"])

    run_clicked = st.button("Run Transformer", type="primary", use_container_width=True)

    if run_clicked:
        if recruiter_file is None:
            st.error("Please upload a recruiter CSV file.")
            return
        if resume_file is None:
            st.error("Please upload a resume file: DOCX, PDF, or TXT.")
            return

        run_id = generate_run_id()
        upload_dir = UPLOAD_ROOT / run_id
        run_dir = RUN_ROOT / run_id
        output_path = OUTPUT_ROOT / f"{run_id}_projected_output.json"
        manifest_path = run_dir / "manifest.yaml"

        recruiter_path = upload_dir / "recruiter.csv"
        resume_filename = sanitize_filename(resume_file.name)
        resume_path = upload_dir / resume_filename

        try:
            detect_resume_type(resume_path)
            _save_uploaded_file(recruiter_file, recruiter_path)
            _save_uploaded_file(resume_file, resume_path)

            manifest = build_ui_manifest(
                run_id=run_id,
                recruiter_csv_path=recruiter_path,
                resume_path=resume_path,
                projection_config_path=projection_config_path,
                output_path=output_path,
            )
            save_manifest(manifest, manifest_path)

            with st.spinner("Running transformer pipeline..."):
                result = run_full_pipeline(
                    manifest,
                    projection_config_path=projection_config_path,
                    include_intermediate=include_intermediate,
                    validate_canonical=not skip_canonical_validation,
                    validate_projection=not skip_projection_validation,
                )
                payload = result.to_dict(include_intermediate=include_intermediate)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

            if payload.get("status") == "completed":
                st.success("Pipeline completed successfully.")
            elif payload.get("status") == "completed_with_warnings":
                st.warning("Pipeline completed with warnings.")
            else:
                st.error("Pipeline failed. Check errors below.")

            st.subheader("Projected Output")
            st.json(payload.get("projected_output", {}))

            with st.expander("Run metadata"):
                st.write("Run ID:")
                st.code(run_id)
                st.write("Manifest path:")
                st.code(str(manifest_path.as_posix()))
                st.write("Output path:")
                st.code(str(output_path.as_posix()))

            if payload.get("warnings"):
                with st.expander("Warnings"):
                    for warning in payload["warnings"]:
                        st.warning(warning)

            if payload.get("errors"):
                with st.expander("Errors"):
                    for error in payload["errors"]:
                        st.error(error)

            if include_intermediate:
                with st.expander("Full debug payload"):
                    st.json(payload)

            _display_json_download(
                "Download output JSON",
                payload,
                file_name=f"{run_id}_projected_output.json",
            )

            with st.expander("Generated manifest"):
                st.code(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), language="yaml")

        except Exception as exc:
            st.exception(exc)


if __name__ == "__main__":
    main()
