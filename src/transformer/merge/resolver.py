"""Merge/conflict resolver for Phase 5."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Tuple

from transformer.merge.confidence import candidate_confidence
from transformer.merge.conflict import conflict_ids_for_candidates
from transformer.provenance.provenance_builder import build_provenance_for_candidates

SOURCE_PRIORITY = {
    "recruiter_csv": 3,
    "resume_docx": 2,
    "resume_pdf": 2,
    "resume_txt": 2,
    "sample_resume_text": 2,
}


def is_valid_candidate(candidate: Dict[str, Any]) -> bool:
    if candidate.get("normalization_status") in {"invalid", "empty"}:
        return False
    value = candidate.get("normalized_value")
    return value is not None and value != "" and value != [] and value != {}


def group_by_field(candidates: Iterable[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        if is_valid_candidate(candidate):
            grouped[candidate.get("field_path", "")].append(candidate)
    return dict(grouped)


def candidate_sort_key(candidate: Dict[str, Any]) -> Tuple[float, int]:
    return (candidate_confidence(candidate), SOURCE_PRIORITY.get(candidate.get("source_type"), 0))


def choose_best(candidates: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    if not candidates:
        return None
    return sorted(candidates, key=candidate_sort_key, reverse=True)[0]


def dedupe_list(values: Iterable[Any]) -> List[Any]:
    seen = set()
    result = []
    for value in values:
        key = str(value).strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(value)
    return result


def resolve_scalar(field_path: str, candidates: List[Dict[str, Any]], output_field: str | None = None) -> tuple[Any, List[Dict[str, Any]]]:
    output_field = output_field or field_path
    best = choose_best(candidates)
    if not best:
        return None, []
    conflict_ids = conflict_ids_for_candidates(candidates, field_path=field_path)
    provenance = build_provenance_for_candidates(candidates, selected_ids={id(best)}, conflict_ids=conflict_ids, field_override=output_field)
    return best.get("normalized_value"), provenance


def resolve_union(field_path: str, candidates: List[Dict[str, Any]], output_field: str | None = None) -> tuple[List[Any], List[Dict[str, Any]]]:
    output_field = output_field or field_path
    values = dedupe_list(c.get("normalized_value") for c in candidates if is_valid_candidate(c))
    selected_ids = {id(c) for c in candidates if c.get("normalized_value") in values}
    provenance = build_provenance_for_candidates(candidates, selected_ids=selected_ids, conflict_ids=set(), field_override=output_field)
    return values, provenance


def resolve_location(candidates: List[Dict[str, Any]]) -> tuple[Any, List[Dict[str, Any]]]:
    return resolve_scalar("location.raw", candidates, output_field="location")


def resolve_links(grouped: Dict[str, List[Dict[str, Any]]]) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    links = {"linkedin": None, "github": None, "portfolio": None, "other": []}
    provenance: List[Dict[str, Any]] = []
    for sub in ["linkedin", "github", "portfolio"]:
        value, prov = resolve_scalar(f"links.{sub}", grouped.get(f"links.{sub}", []), output_field=f"links.{sub}")
        links[sub] = value
        provenance.extend(prov)
    other, prov = resolve_union("links.other", grouped.get("links.other", []), output_field="links.other")
    links["other"] = other
    provenance.extend(prov)
    return links, provenance


def resolve_skills(candidates: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    by_name: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for c in candidates:
        name = str(c.get("normalized_value", "")).strip()
        if name:
            by_name[name.lower()].append(c)
    skills = []
    selected_ids = set()
    for _, items in sorted(by_name.items()):
        best = choose_best(items)
        if not best:
            continue
        selected_ids.add(id(best))
        skills.append({
            "name": best.get("normalized_value"),
            "confidence": round(candidate_confidence(best), 4),
            "sources": sorted({i.get("source_id", "unknown_source") for i in items}),
        })
    provenance = build_provenance_for_candidates(candidates, selected_ids=selected_ids, conflict_ids=set(), field_override="skills")
    return skills, provenance


def resolve_experience_or_education(field_path: str, candidates: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    # Keep cleaned text blocks in schema-compatible summary objects for now.
    values = []
    selected_ids = set()
    for c in candidates:
        text = c.get("normalized_value")
        if not text:
            continue
        selected_ids.add(id(c))
        if field_path == "experience":
            values.append({"company": None, "title": None, "start": None, "end": None, "summary": str(text)})
        else:
            values.append({"institution": None, "degree": None, "field": str(text), "end_year": None})
    provenance = build_provenance_for_candidates(candidates, selected_ids=selected_ids, conflict_ids=set(), field_override=field_path)
    return values, provenance


def resolve_all(normalized_candidates: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    grouped = group_by_field(normalized_candidates)
    resolved: Dict[str, Any] = {"provenance": []}

    for field in ["full_name", "headline", "years_experience"]:
        value, prov = resolve_scalar(field, grouped.get(field, []), output_field=field)
        resolved[field] = value
        resolved["provenance"].extend(prov)

    for field in ["emails", "phones"]:
        value, prov = resolve_union(field, grouped.get(field, []), output_field=field)
        resolved[field] = value
        resolved["provenance"].extend(prov)

    location, prov = resolve_location(grouped.get("location.raw", []))
    resolved["location"] = location
    resolved["provenance"].extend(prov)

    links, prov = resolve_links(grouped)
    resolved["links"] = links
    resolved["provenance"].extend(prov)

    skills, prov = resolve_skills(grouped.get("skills", []))
    resolved["skills"] = skills
    resolved["provenance"].extend(prov)

    for field in ["experience", "education"]:
        value, prov = resolve_experience_or_education(field, grouped.get(field, []))
        resolved[field] = value
        resolved["provenance"].extend(prov)

    return resolved
