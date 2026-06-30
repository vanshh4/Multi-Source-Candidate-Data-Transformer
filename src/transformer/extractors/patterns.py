"""
Reusable extraction patterns and constants for Phase 3.

The patterns are intentionally deterministic and explainable. They are not meant
to be perfect; they provide a robust baseline before normalization and merge.
"""

from __future__ import annotations

import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)

# General phone pattern for Indian/international resume formats.
# Examples: +91 98765 43210, 9876543210, +1-555-555-5555
PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?){2,5}\d{2,5}(?!\w)"
)

URL_PATTERN = re.compile(
    r"\b(?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[\w\-.~:/?#\[\]@!$&'()*+,;=%]*)?",
    re.IGNORECASE,
)

LINKEDIN_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_\-/%]+", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_\-/%]+", re.IGNORECASE)

SECTION_HEADING_PATTERN = re.compile(
    r"^(summary|profile|professional summary|career objective|objective|skills|technical skills|experience|work experience|professional experience|employment|education|academic background|projects|certifications)\s*$",
    re.IGNORECASE,
)

DATE_RANGE_PATTERN = re.compile(
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)?\s*\d{4}\s*(?:-|–|—|to)\s*(?:Present|Current|Now|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)?\s*\d{4})",
    re.IGNORECASE,
)

CONTACT_WORDS = {
    "email",
    "phone",
    "mobile",
    "linkedin",
    "github",
    "portfolio",
    "location",
    "address",
}

SECTION_HEADINGS = {
    "summary",
    "profile",
    "professional summary",
    "career objective",
    "objective",
    "skills",
    "technical skills",
    "experience",
    "work experience",
    "professional experience",
    "employment",
    "education",
    "academic background",
    "projects",
    "certifications",
}

# Baseline skill vocabulary. Later phases can replace this with a richer taxonomy.
KNOWN_SKILLS = {
    "python",
    "sql",
    "excel",
    "power bi",
    "powerbi",
    "tableau",
    "machine learning",
    "data analysis",
    "data visualization",
    "pandas",
    "numpy",
    "scikit-learn",
    "sklearn",
    "matplotlib",
    "seaborn",
    "statistics",
    "etl",
    "dashboards",
    "dashboarding",
    "java",
    "c++",
    "html",
    "css",
    "javascript",
    "git",
    "github",
    "azure",
    "aws",
    "mysql",
    "postgresql",
    "mongodb",
    "nlp",
    "deep learning",
}

SKILL_ALIASES = {
    "powerbi": "Power BI",
    "power bi": "Power BI",
    "sklearn": "scikit-learn",
    "github": "GitHub",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "nlp": "NLP",
    "etl": "ETL",
}


def clean_whitespace(value: str) -> str:
    """Collapse repeated whitespace and trim."""
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_url(url: str) -> str:
    """Add https:// to URLs if no scheme is present."""
    url = clean_whitespace(url)
    if url and not re.match(r"^https?://", url, re.IGNORECASE):
        return f"https://{url}"
    return url


def canonical_skill_name(skill: str) -> str:
    """Return display form for a skill using simple alias rules."""
    cleaned = clean_whitespace(skill).lower()
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]
    return " ".join(part.upper() if part in {"sql", "html", "css", "aws"} else part.capitalize() for part in cleaned.split())
