"""Projected output JSON schema builder."""

from __future__ import annotations

from typing import Any, Dict

TYPE_MAP = {
    "string": {"type": "string"},
    "number": {"type": "number"},
    "integer": {"type": "integer"},
    "boolean": {"type": "boolean"},
    "array": {"type": "array"},
    "object": {"type": "object"},
    "null": {"type": "null"},
}


def field_config_to_schema(field_config: Dict[str, Any], *, missing_policy: str | None = None) -> Dict[str, Any]:
    expected_type = field_config.get("type") or "string"
    schema = dict(TYPE_MAP.get(expected_type, {"type": expected_type}))
    policy = missing_policy or field_config.get("missing") or "null"
    if policy == "null" and schema.get("type") != "null":
        schema["type"] = [schema["type"], "null"]
    if field_config.get("description"):
        schema["description"] = field_config["description"]
    return schema


def build_projected_schema(config: Dict[str, Any]) -> Dict[str, Any]:
    output = config.get("output", {})
    options = config.get("options", {}) or {}
    missing_default = options.get("missing_default", "null")
    properties: Dict[str, Any] = {}
    required = []

    for field in output.get("fields", []):
        output_name = field["output_name"]
        policy = field.get("missing") or ("error" if field.get("required") else missing_default)
        properties[output_name] = field_config_to_schema(field, missing_policy=policy)
        if policy == "error" or field.get("required"):
            required.append(output_name)

    if options.get("include_provenance", True):
        properties["_provenance"] = {"type": "object"}
    if options.get("include_confidence", True):
        properties["_confidence"] = {"type": "object"}

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": bool(options.get("additional_output_properties", False)),
        "properties": properties,
    }
    if required:
        schema["required"] = required
    return schema
