"""Main runtime projection engine."""

from __future__ import annotations

from typing import Any, Dict

from transformer.projection.metadata_projector import attach_projection_metadata
from transformer.projection.missing_policy import OMIT, OmitField, handle_missing_value, resolve_missing_policy
from transformer.projection.output_normalizers import apply_output_normalization
from transformer.projection.path_resolver import get_by_path, is_missing_value
from transformer.projection.schema_builder import build_projected_schema
from transformer.projection.validator import assert_valid_projected_output


def project_candidate(canonical_candidate: Dict[str, Any], projection_config: Dict[str, Any], *, validate: bool = True) -> Dict[str, Any]:
    output: Dict[str, Any] = {}
    fields = projection_config.get("output", {}).get("fields", [])
    options = projection_config.get("options", {}) or {}

    for field in fields:
        output_name = field["output_name"]
        canonical_path = field["path"]
        exists, value = get_by_path(canonical_candidate, canonical_path)
        missing = (not exists) or is_missing_value(value)

        if missing:
            policy = resolve_missing_policy(field, options)
            value = handle_missing_value(output_name, canonical_path, policy)
            if isinstance(value, OmitField):
                continue
        else:
            value = apply_output_normalization(value, field.get("normalization"))

        output[output_name] = value

    projected = attach_projection_metadata(output, canonical_candidate, projection_config)
    schema = build_projected_schema(projection_config)
    if validate:
        assert_valid_projected_output(projected, schema)
    return projected
