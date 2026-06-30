"""Canonical candidate model helpers for Phase 5.

This module defines the internal canonical record shape. It intentionally mirrors
schemas/canonical_candidate.schema.json and never invents unavailable values.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


def default_links() -> Dict[str, Any]:
    return {
        "linkedin": None,
        "github": None,
        "portfolio": None,
        "other": [],
    }


def default_location() -> None:
    # Canonical schema allows location to be null when unavailable.
    return None


def empty_canonical_candidate() -> Dict[str, Any]:
    """Return an empty canonical candidate with all required schema fields."""
    return {
        "candidate_id": "cand_unknown",
        "full_name": None,
        "emails": [],
        "phones": [],
        "location": default_location(),
        "links": default_links(),
        "headline": None,
        "years_experience": None,
        "skills": [],
        "experience": [],
        "education": [],
        "provenance": [],
        "overall_confidence": 0.0,
    }


def clone_empty_candidate() -> Dict[str, Any]:
    return deepcopy(empty_canonical_candidate())
