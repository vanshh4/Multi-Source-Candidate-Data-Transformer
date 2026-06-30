"""
Extractor router for Phase 3.

Routes Phase 2 reader results to the correct Phase 3 extractor and returns a
single list of field candidates.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from transformer.extractors.resume_extractor import RESUME_SOURCE_TYPES, extract_resume_candidates
from transformer.extractors.structured_extractor import extract_structured_candidates


def extract_from_source(reader_result: Dict) -> List[Dict]:
    """Extract field candidates from one reader result."""
    source_type = reader_result.get("source_type")
    if source_type == "recruiter_csv":
        return extract_structured_candidates(reader_result)
    if source_type in RESUME_SOURCE_TYPES:
        return extract_resume_candidates(reader_result)
    return []


def extract_from_sources(reader_results: Iterable[Dict]) -> List[Dict]:
    """Extract field candidates from multiple reader results."""
    candidates: List[Dict] = []
    for result in reader_results:
        candidates.extend(extract_from_source(result))
    return candidates


def build_extraction_output(*, run_id: str, reader_results: Iterable[Dict]) -> Dict:
    """Build a standard Phase 3 extraction output payload."""
    candidates = extract_from_sources(reader_results)
    return {
        "run_id": run_id,
        "description": "Phase 3 extraction output. Normalization, merge, canonical building, and projection are not performed here.",
        "field_candidate_count": len(candidates),
        "field_candidates": candidates,
    }
