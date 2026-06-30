"""Skill normalization for Phase 4."""

from __future__ import annotations

from typing import Dict

from transformer.normalizers.base import STATUS_OK, build_normalization_result, collapse_spaces, empty_result, is_empty_value

SKILL_ALIASES = {
    "powerbi": "Power BI",
    "power bi": "Power BI",
    "ms excel": "Excel",
    "excel": "Excel",
    "python": "Python",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "github": "GitHub",
    "git": "Git",
    "nlp": "NLP",
    "etl": "ETL",
    "html": "HTML",
    "css": "CSS",
    "aws": "AWS",
    "azure": "Azure",
    "machine learning": "Machine Learning",
    "data visualization": "Data Visualization",
    "data analysis": "Data Analysis",
}


def normalize_skill_candidate(candidate: Dict) -> Dict:
    method = "skill_alias_canonical"
    value = candidate.get("normalized_value", candidate.get("raw_value"))
    if is_empty_value(value):
        return empty_result(candidate, method=method)

    cleaned = collapse_spaces(str(value)).strip(".,;:()[]{}")
    key = cleaned.lower()
    normalized = SKILL_ALIASES.get(key)
    if not normalized:
        normalized = " ".join(part.capitalize() for part in key.split())

    return build_normalization_result(candidate, normalized_value=normalized, normalization_method=method, normalization_status=STATUS_OK)
