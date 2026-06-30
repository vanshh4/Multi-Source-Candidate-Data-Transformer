"""Projection-layer errors and constants."""

from __future__ import annotations

CONFIG_MISSING = "Projection config file is missing."
INVALID_CONFIG = "Projection config is invalid."
CANONICAL_PATH_NOT_FOUND = "Canonical path was not found."
MISSING_VALUE_ERROR = "Required projected value is missing."
INVALID_OUTPUT_FIELD = "Projected output field is invalid."
PROJECTION_VALIDATION_FAILED = "Projected output validation failed."


class ProjectionError(Exception):
    """Base exception for projection errors."""


class ProjectionConfigError(ProjectionError):
    """Raised when projection config cannot be loaded or validated."""


class ProjectionMissingValueError(ProjectionError):
    """Raised when missing policy is error and a value is unavailable."""


class ProjectionValidationError(ProjectionError):
    """Raised when projected output does not satisfy projected schema."""
