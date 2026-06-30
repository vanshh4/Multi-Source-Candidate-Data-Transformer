"""
Unstructured resume extractor for Phase 3.

Extracts deterministic field candidates from text produced by TXT/DOCX/PDF
readers. This module avoids inventing values: if a pattern is not present, no
candidate is emitted for that field.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from transformer.models.field_candidate import make_field_candidate
from transformer.extractors.patterns import (
    CONTACT_WORDS,
    DATE_RANGE_PATTERN,
    EMAIL_PATTERN,
    GITHUB_PATTERN,
    KNOWN_SKILLS,
    LINKEDIN_PATTERN,
    PHONE_PATTERN,
    SECTION_HEADINGS,
    URL_PATTERN,
    canonical_skill_name,
    clean_whitespace,
    normalize_url,
)

RESUME_SOURCE_TYPES = {"resume_txt", "resume_docx", "resume_pdf", "sample_resume_text"}


def _source_info(reader_result: Dict) -> Tuple[str, str, str | None]:
    return (
        reader_result.get("source_id", "resume_source"),
        reader_result.get("source_type", "resume_txt"),
        reader_result.get("source_name"),
    )


def _non_empty_lines(text: str) -> List[str]:
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def _looks_like_contact_line(line: str) -> bool:
    lower = line.lower()
    return (
        bool(EMAIL_PATTERN.search(line))
        or bool(PHONE_PATTERN.search(line))
        or bool(URL_PATTERN.search(line))
        or any(word in lower for word in CONTACT_WORDS)
    )


def _looks_like_section_heading(line: str) -> bool:
    return clean_whitespace(line).lower() in SECTION_HEADINGS


def _extract_name_candidate(lines: List[str], source_id: str, source_type: str, source_name: str | None) -> List[Dict]:
    """Use first clean non-contact, non-section line as a conservative name candidate."""
    for index, line in enumerate(lines[:8]):
        cleaned = clean_whitespace(line)
        if not cleaned or len(cleaned) > 80:
            continue
        if _looks_like_contact_line(cleaned) or _looks_like_section_heading(cleaned):
            continue
        if sum(ch.isdigit() for ch in cleaned) > 0:
            continue
        return [
            make_field_candidate(
                field_path="full_name",
                raw_value=line,
                normalized_value=cleaned,
                source_id=source_id,
                source_type=source_type,
                source_name=source_name,
                method="resume_header_name_heuristic",
                confidence=0.70,
                metadata={"line_index": index},
            )
        ]
    return []


def _extract_headline_candidate(lines: List[str], source_id: str, source_type: str, source_name: str | None) -> List[Dict]:
    """Extract a short headline from early resume lines or summary heading."""
    for index, line in enumerate(lines[:12]):
        lower = clean_whitespace(line).lower()
        if lower in {"summary", "professional summary", "profile", "career objective", "objective"}:
            if index + 1 < len(lines):
                next_line = clean_whitespace(lines[index + 1])
                if next_line and not _looks_like_section_heading(next_line):
                    return [
                        make_field_candidate(
                            field_path="headline",
                            raw_value=lines[index + 1],
                            normalized_value=next_line,
                            source_id=source_id,
                            source_type=source_type,
                            source_name=source_name,
                            method="resume_summary_heading_next_line",
                            confidence=0.75,
                            metadata={"line_index": index + 1},
                        )
                    ]

    # Fallback: second/third clean line after likely name if it is not contact information.
    for index, line in enumerate(lines[1:5], start=1):
        cleaned = clean_whitespace(line)
        if cleaned and not _looks_like_contact_line(cleaned) and not _looks_like_section_heading(cleaned):
            return [
                make_field_candidate(
                    field_path="headline",
                    raw_value=line,
                    normalized_value=cleaned,
                    source_id=source_id,
                    source_type=source_type,
                    source_name=source_name,
                    method="resume_early_line_headline_heuristic",
                    confidence=0.60,
                    metadata={"line_index": index},
                )
            ]
    return []


def _unique_matches(pattern, text: str) -> List[str]:
    seen = set()
    values = []
    for match in pattern.findall(text or ""):
        value = match if isinstance(match, str) else match[0]
        cleaned = clean_whitespace(value).strip(".,;:()[]{}")
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            values.append(cleaned)
    return values


def _extract_section(text: str, headings: Iterable[str]) -> str:
    """Extract rough text block after a heading until next known heading."""
    lines = _non_empty_lines(text)
    heading_set = {h.lower() for h in headings}
    collecting = False
    collected: List[str] = []
    for line in lines:
        lower = clean_whitespace(line).lower()
        if lower in heading_set:
            collecting = True
            continue
        if collecting and lower in SECTION_HEADINGS:
            break
        if collecting:
            collected.append(line)
    return "\n".join(collected).strip()


def _extract_skills(text: str) -> List[str]:
    """Extract skills using section text plus known-skill vocabulary matching."""
    skill_text = _extract_section(text, ["skills", "technical skills"])
    search_text = f"{skill_text}\n{text}".lower()
    found = set()
    for skill in KNOWN_SKILLS:
        if skill in search_text:
            found.add(canonical_skill_name(skill))
    return sorted(found)


def extract_resume_candidates(reader_result: Dict) -> List[Dict]:
    """Extract field candidates from text-based resume reader output."""
    if reader_result.get("source_type") not in RESUME_SOURCE_TYPES:
        return []
    if reader_result.get("status") != "ok":
        return []

    text = reader_result.get("content") or ""
    if not isinstance(text, str) or not text.strip():
        return []

    source_id, source_type, source_name = _source_info(reader_result)
    lines = _non_empty_lines(text)
    candidates: List[Dict] = []

    candidates.extend(_extract_name_candidate(lines, source_id, source_type, source_name))
    candidates.extend(_extract_headline_candidate(lines, source_id, source_type, source_name))

    for email in _unique_matches(EMAIL_PATTERN, text):
        candidates.append(
            make_field_candidate(
                field_path="emails",
                raw_value=email,
                normalized_value=email.lower(),
                source_id=source_id,
                source_type=source_type,
                source_name=source_name,
                method="email_regex",
                confidence=0.95,
                metadata={"pattern": "EMAIL_PATTERN"},
            )
        )

    for phone in _unique_matches(PHONE_PATTERN, text):
        digits = "".join(ch for ch in phone if ch.isdigit())
        # Avoid extracting years or short numeric fragments as phones.
        if len(digits) < 10 or len(digits) > 15:
            continue
        candidates.append(
            make_field_candidate(
                field_path="phones",
                raw_value=phone,
                normalized_value=clean_whitespace(phone),
                source_id=source_id,
                source_type=source_type,
                source_name=source_name,
                method="phone_regex",
                confidence=0.85,
                metadata={"pattern": "PHONE_PATTERN"},
            )
        )

    for link in _unique_matches(LINKEDIN_PATTERN, text):
        candidates.append(
            make_field_candidate(
                field_path="links.linkedin",
                raw_value=link,
                normalized_value=normalize_url(link),
                source_id=source_id,
                source_type=source_type,
                source_name=source_name,
                method="linkedin_regex",
                confidence=0.90,
            )
        )

    for link in _unique_matches(GITHUB_PATTERN, text):
        candidates.append(
            make_field_candidate(
                field_path="links.github",
                raw_value=link,
                normalized_value=normalize_url(link),
                source_id=source_id,
                source_type=source_type,
                source_name=source_name,
                method="github_regex",
                confidence=0.90,
            )
        )

    # Other URLs excluding LinkedIn/GitHub duplicates.
    known_urls = {c["normalized_value"].lower() for c in candidates if str(c.get("field_path", "")).startswith("links.")}
    for url in _unique_matches(URL_PATTERN, text):
        normalized = normalize_url(url)
        lower = normalized.lower()
        if "linkedin.com/in/" in lower or "github.com/" in lower or lower in known_urls:
            continue
        candidates.append(
            make_field_candidate(
                field_path="links.other",
                raw_value=url,
                normalized_value=normalized,
                source_id=source_id,
                source_type=source_type,
                source_name=source_name,
                method="url_regex",
                confidence=0.75,
            )
        )

    for skill in _extract_skills(text):
        candidates.append(
            make_field_candidate(
                field_path="skills",
                raw_value=skill,
                normalized_value=skill,
                source_id=source_id,
                source_type=source_type,
                source_name=source_name,
                method="known_skill_dictionary_match",
                confidence=0.75,
                metadata={"dictionary": "KNOWN_SKILLS"},
            )
        )

    experience_block = _extract_section(text, ["experience", "work experience", "professional experience", "employment"])
    if experience_block:
        candidates.append(
            make_field_candidate(
                field_path="experience",
                raw_value=experience_block,
                normalized_value=experience_block,
                source_id=source_id,
                source_type=source_type,
                source_name=source_name,
                method="resume_experience_section",
                confidence=0.65,
                metadata={"date_ranges_found": _unique_matches(DATE_RANGE_PATTERN, experience_block)},
            )
        )

    education_block = _extract_section(text, ["education", "academic background"])
    if education_block:
        candidates.append(
            make_field_candidate(
                field_path="education",
                raw_value=education_block,
                normalized_value=education_block,
                source_id=source_id,
                source_type=source_type,
                source_name=source_name,
                method="resume_education_section",
                confidence=0.65,
            )
        )

    return candidates
