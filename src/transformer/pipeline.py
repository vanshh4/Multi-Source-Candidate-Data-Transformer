"""End-to-end pipeline orchestration.

This module connects all completed phases:

Phase 2: Source reading
Phase 3: Field extraction
Phase 4: Normalization
Phase 5: Canonical candidate building and validation
Phase 6: Runtime projection

The pipeline keeps the internal canonical candidate separate from the projection
layer. Runtime config changes only affect the projected output shape.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from transformer.readers.reader_router import read_sources_from_manifest
from transformer.readers.base import combine_overall_status, summarize_reader_result
from transformer.extractors.extractor_router import extract_from_sources
from transformer.normalizers.normalizer_router import normalize_field_candidates
from transformer.canonical.builder import build_canonical_candidate
from transformer.validation.schema_validator import validate_canonical_candidate
from transformer.projection.config_loader import load_projection_config
from transformer.projection.projector import project_candidate


@dataclass
class PipelineResult:
    """Structured output from a full pipeline run."""

    run_id: str
    status: str
    source_results: List[Dict[str, Any]]
    field_candidates: List[Dict[str, Any]]
    normalized_candidates: List[Dict[str, Any]]
    canonical_candidate: Dict[str, Any]
    projected_output: Dict[str, Any]
    warnings: List[str]
    errors: List[str]

    def to_dict(self, *, include_intermediate: bool = False) -> Dict[str, Any]:
        """Convert pipeline result into JSON-serializable dictionary."""
        payload: Dict[str, Any] = {
            "run_id": self.run_id,
            "status": self.status,
            "projected_output": self.projected_output,
            "warnings": self.warnings,
            "errors": self.errors,
        }
        if include_intermediate:
            payload["source_results"] = self.source_results
            payload["field_candidates"] = self.field_candidates
            payload["normalized_candidates"] = self.normalized_candidates
            payload["canonical_candidate"] = self.canonical_candidate
        return payload


def _collect_reader_messages(source_results: List[Dict[str, Any]]) -> tuple[List[str], List[str]]:
    warnings: List[str] = []
    errors: List[str] = []
    for result in source_results:
        source_id = result.get("source_id", "unknown_source")
        for warning in result.get("warnings", []) or []:
            warnings.append(f"{source_id}: {warning}")
        for error in result.get("errors", []) or []:
            errors.append(f"{source_id}: {error}")
    return warnings, errors


def _derive_pipeline_status(*, source_status: str, canonical_errors: List[str], projection_errors: List[str]) -> str:
    if canonical_errors or projection_errors or source_status == "failed":
        return "failed"
    if source_status == "completed_with_warnings":
        return "completed_with_warnings"
    return "completed"


def run_source_reading(manifest: Dict[str, Any], *, include_content: bool = False) -> Dict[str, Any]:
    """Run only Phase 2 source reading and return a source-reading payload."""
    run_id = manifest.get("run", {}).get("run_id", "source_reading_run")
    source_results = read_sources_from_manifest(manifest)
    warnings, errors = _collect_reader_messages(source_results)
    source_payload = source_results if include_content else [summarize_reader_result(r) for r in source_results]
    return {
        "run_id": run_id,
        "description": "Phase 2 source-reading output. Extraction, normalization, merge, and projection are not performed here.",
        "sources": source_payload,
        "overall_status": combine_overall_status(source_results),
        "warnings": warnings,
        "errors": errors,
    }


def run_full_pipeline(
    manifest: Dict[str, Any],
    *,
    projection_config_path: Optional[str] = None,
    include_intermediate: bool = False,
    validate_canonical: bool = True,
    validate_projection: bool = True,
) -> PipelineResult:
    """
    Execute the full candidate transformer pipeline.

    Args:
        manifest: Loaded sample input manifest dictionary.
        projection_config_path: Optional projection config path. If omitted,
            manifest["projection"]["config_path"] is used.
        include_intermediate: The returned PipelineResult always stores
            intermediates, but this flag is used by callers when serializing.
        validate_canonical: Whether to validate canonical candidate against the
            canonical JSON Schema.
        validate_projection: Whether to validate projected output against the
            generated projected schema.

    Returns:
        PipelineResult containing projected output and optional intermediates.
    """
    run_id = manifest.get("run", {}).get("run_id", "candidate_pipeline_run")

    source_results = read_sources_from_manifest(manifest)
    source_status = combine_overall_status(source_results)
    warnings, errors = _collect_reader_messages(source_results)

    field_candidates = extract_from_sources(source_results)
    normalized_candidates = normalize_field_candidates(field_candidates)
    canonical_candidate = build_canonical_candidate(normalized_candidates)

    canonical_errors: List[str] = []
    if validate_canonical:
        canonical_errors = validate_canonical_candidate(canonical_candidate)
        errors.extend([f"canonical_validation: {error}" for error in canonical_errors])

    config_path = projection_config_path or manifest.get("projection", {}).get("config_path")
    if not config_path:
        raise ValueError("Projection config path is missing. Provide --config or manifest.projection.config_path.")

    projected_output: Dict[str, Any] = {}
    projection_errors: List[str] = []
    try:
        projection_config = load_projection_config(config_path)
        projected_output = project_candidate(canonical_candidate, projection_config, validate=validate_projection)
    except Exception as exc:  # Keep CLI-friendly structured output.
        projection_errors.append(f"{type(exc).__name__}: {exc}")
        errors.extend([f"projection: {error}" for error in projection_errors])

    status = _derive_pipeline_status(
        source_status=source_status,
        canonical_errors=canonical_errors,
        projection_errors=projection_errors,
    )

    return PipelineResult(
        run_id=run_id,
        status=status,
        source_results=source_results,
        field_candidates=field_candidates,
        normalized_candidates=normalized_candidates,
        canonical_candidate=canonical_candidate,
        projected_output=projected_output,
        warnings=warnings,
        errors=errors,
    )
