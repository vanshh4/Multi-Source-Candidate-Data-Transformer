"""
Phase 2 command-line interface.

This CLI loads a sample input manifest, routes input files to the appropriate
readers, and writes a privacy-safe source-reading summary to JSON.

Example:
    PYTHONPATH=src python -m transformer.cli --manifest configs/sample_input_manifest.yaml
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import yaml

from transformer.readers.base import combine_overall_status, summarize_reader_result
from transformer.readers.reader_router import read_sources_from_manifest
from transformer.utils.file_utils import ensure_parent_dir


DEFAULT_SOURCE_READING_OUTPUT = "data/outputs/source_reading_output.json"


def load_manifest(manifest_path: str) -> Dict[str, Any]:
    """Load YAML manifest from disk."""
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f) or {}
    return manifest


def build_source_reading_output(
    *,
    manifest_path: str,
    manifest: Dict[str, Any],
    include_content: bool = False,
) -> Dict[str, Any]:
    """
    Read all sources from manifest and build Phase 2 output payload.

    Args:
        manifest_path: Path to manifest YAML.
        manifest: Loaded manifest dictionary.
        include_content: If True, include full source content in output JSON.
                         Default False is safer for privacy and smaller files.
    """
    results = read_sources_from_manifest(manifest)

    if include_content:
        output_sources = results
    else:
        output_sources = [summarize_reader_result(result) for result in results]

    overall_warnings = []
    overall_errors = []
    for result in results:
        for warning in result.get("warnings", []):
            overall_warnings.append(f"{result.get('source_id')}: {warning}")
        for error in result.get("errors", []):
            overall_errors.append(f"{result.get('source_id')}: {error}")

    return {
        "run_id": manifest.get("run", {}).get("run_id", "source_reading_run"),
        "description": "Phase 2 source-reading output. Extraction, normalization, merge, and projection are not performed here.",
        "manifest_path": manifest_path,
        "sources": output_sources,
        "overall_status": combine_overall_status(results),
        "warnings": overall_warnings,
        "errors": overall_errors,
    }


def resolve_output_path(manifest: Dict[str, Any], cli_output_path: str | None = None) -> str:
    """
    Resolve output path for source-reading JSON.

    CLI --output takes priority. If not supplied, use a Phase 2-specific default.
    This intentionally does not use manifest.output.path because that path is reserved
    for the final transformed candidate output in later phases.
    """
    if cli_output_path:
        return cli_output_path
    return DEFAULT_SOURCE_READING_OUTPUT


def write_json_output(payload: Dict[str, Any], output_path: str, pretty: bool = True) -> None:
    """Write output payload to JSON file."""
    ensure_parent_dir(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        else:
            json.dump(payload, f, ensure_ascii=False)
        f.write("\n")


def print_summary(payload: Dict[str, Any], output_path: str) -> None:
    """Print a short source-reading summary to terminal."""
    print("Source reading completed.")
    print(f"Overall status: {payload.get('overall_status')}")
    print("\nSources:")
    for source in payload.get("sources", []):
        print(f"- {source.get('source_id')} ({source.get('source_type')}): {source.get('status')}")
    print(f"\nOutput written to: {output_path}")

    warnings = payload.get("warnings", [])
    errors = payload.get("errors", [])
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"- {error}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Phase 2 source reader CLI for candidate transformer.")
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to input manifest YAML, e.g. configs/sample_input_manifest.yaml",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=f"Path for source-reading output JSON. Default: {DEFAULT_SOURCE_READING_OUTPUT}",
    )
    parser.add_argument(
        "--include-content",
        action="store_true",
        help="Include full parsed source content in output JSON. Default is metadata-only for privacy.",
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

    output_path = resolve_output_path(manifest, args.output)
    payload = build_source_reading_output(
        manifest_path=manifest_path,
        manifest=manifest,
        include_content=args.include_content,
    )
    write_json_output(payload, output_path, pretty=not args.compact)
    print_summary(payload, output_path)


if __name__ == "__main__":
    main()
