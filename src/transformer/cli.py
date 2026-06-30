"""Command-line interface for the candidate transformer.

Default behavior remains Phase 2 source reading for backward compatibility.
Use --project to run the full pipeline:

    PYTHONPATH=src python -m transformer.cli \
      --manifest configs/sample_input_manifest.yaml \
      --project \
      --output data/outputs/projected_candidate_output.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import yaml

from transformer.pipeline import run_full_pipeline, run_source_reading
from transformer.utils.file_utils import ensure_parent_dir


DEFAULT_SOURCE_READING_OUTPUT = "data/outputs/source_reading_output.json"
DEFAULT_PROJECTED_OUTPUT = "data/outputs/projected_candidate_output.json"


def load_manifest(manifest_path: str) -> Dict[str, Any]:
    """Load YAML manifest from disk."""
    with open(manifest_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_json_output(payload: Dict[str, Any], output_path: str, pretty: bool = True) -> None:
    """Write output payload to JSON file."""
    ensure_parent_dir(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        else:
            json.dump(payload, f, ensure_ascii=False)
        f.write("\n")


def print_source_summary(payload: Dict[str, Any], output_path: str) -> None:
    """Print Phase 2 source-reading summary."""
    print("Source reading completed.")
    print(f"Overall status: {payload.get('overall_status')}")
    print("\nSources:")
    for source in payload.get("sources", []):
        print(f"- {source.get('source_id')} ({source.get('source_type')}): {source.get('status')}")
    print(f"\nOutput written to: {output_path}")

    if payload.get("warnings"):
        print("\nWarnings:")
        for warning in payload["warnings"]:
            print(f"- {warning}")
    if payload.get("errors"):
        print("\nErrors:")
        for error in payload["errors"]:
            print(f"- {error}")


def print_pipeline_summary(payload: Dict[str, Any], output_path: str) -> None:
    """Print full-pipeline summary."""
    print("Candidate transformer pipeline completed.")
    print(f"Status: {payload.get('status')}")
    projected = payload.get("projected_output", {})
    if isinstance(projected, dict):
        print(f"Projected fields: {len([k for k in projected.keys() if not k.startswith('_')])}")
    print(f"\nOutput written to: {output_path}")

    if payload.get("warnings"):
        print("\nWarnings:")
        for warning in payload["warnings"]:
            print(f"- {warning}")
    if payload.get("errors"):
        print("\nErrors:")
        for error in payload["errors"]:
            print(f"- {error}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Candidate transformer CLI.")
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to input manifest YAML, e.g. configs/sample_input_manifest.yaml",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path. Defaults to source-reading or projected-output path depending on mode.",
    )
    parser.add_argument(
        "--project",
        action="store_true",
        help="Run the full pipeline and apply runtime projection config. Default mode only reads sources.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Projection config path override. If omitted, manifest.projection.config_path is used.",
    )
    parser.add_argument(
        "--include-content",
        action="store_true",
        help="Source-reading mode only: include full parsed source content in output JSON.",
    )
    parser.add_argument(
        "--include-intermediate",
        action="store_true",
        help="Full-pipeline mode only: include source results, field candidates, normalized candidates, and canonical candidate in output JSON.",
    )
    parser.add_argument(
        "--skip-canonical-validation",
        action="store_true",
        help="Full-pipeline mode only: skip canonical schema validation.",
    )
    parser.add_argument(
        "--skip-projection-validation",
        action="store_true",
        help="Full-pipeline mode only: skip projected output validation.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Write compact JSON instead of pretty-printed JSON.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    manifest_path = str(Path(args.manifest).as_posix())
    manifest = load_manifest(manifest_path)

    if args.project:
        output_path = args.output or DEFAULT_PROJECTED_OUTPUT
        result = run_full_pipeline(
            manifest,
            projection_config_path=args.config,
            include_intermediate=args.include_intermediate,
            validate_canonical=not args.skip_canonical_validation,
            validate_projection=not args.skip_projection_validation,
        )
        payload = result.to_dict(include_intermediate=args.include_intermediate)
        write_json_output(payload, output_path, pretty=not args.compact)
        print_pipeline_summary(payload, output_path)
    else:
        output_path = args.output or DEFAULT_SOURCE_READING_OUTPUT
        payload = run_source_reading(manifest, include_content=args.include_content)
        payload["manifest_path"] = manifest_path
        write_json_output(payload, output_path, pretty=not args.compact)
        print_source_summary(payload, output_path)


if __name__ == "__main__":
    main()
