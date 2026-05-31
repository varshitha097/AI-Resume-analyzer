
import re
from datetime import datetime
from typing import Dict, List, Tuple
from .sectionizer import detect_sections
from .taxonomy import extract_skills
from .cleaner import lines, sentence_split

DEGREE_KEYWORDS = [
    "b.tech", "btech", "b.e", "be ", "bachelor", "m.tech", "mtech", "m.e", "master",
    "degree", "diploma", "intermediate", "ssc", "ece", "cse", "computer science",
    "electronics", "communication", "engineering", "university", "college"
]

CERT_KEYWORDS = ["certificate", "certification", "certified", "course", "training", "nptel", "coursera", "udemy", "aws", "azure"]

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3, "apr": 4, "april": 4,
    "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7, "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9, "oct": 10, "october": 10, "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def _month_year_to_float(token: str) -> float:
    token = token.lower().strip()
    now = datetime.now()
    if token in {"present", "current", "till date", "ongoing"}:
        return now.year + (now.month - 1) / 12
    year_match = re.search(r"(19|20)\d{2}", token)
    if not year_match:
        return 0.0
    year = int(year_match.group())
    month = 1
    for m, num in MONTHS.items():
        if re.search(rf"\b{m}\b", token):
            month = num
            break
    return year + (month - 1) / 12


def extract_experience_years(text: str) -> Dict[str, object]:
    """Extract explicit and date-range experience. Returns max estimate."""
    lower = text.lower()
    explicit_years = []
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)", lower):
        explicit_years.append(float(m.group(1)))
    for m in re.finditer(r"(?:experience|exp)\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", lower):
        explicit_years.append(float(m.group(1)))

    # Month/year ranges: Jan 2022 - Mar 2024, 2021 - Present
    range_years = []
    date_token = r"(?:(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)\s+)?(?:19|20)\d{2}|present|current|ongoing"
    pattern = re.compile(rf"({date_token})\s*(?:-|–|—|to)\s*({date_token})", re.I)
    for m in pattern.finditer(lower):
        start = _month_year_to_float(m.group(1))
        end = _month_year_to_float(m.group(2))
        if start and end and end >= start:
            years = round(end - start, 2)
            if 0 <= years <= 50:
                range_years.append(years)

    estimated = max(explicit_years + range_years + [0.0])
    return {
        "years": round(estimated, 2),
        "explicit_years": explicit_years,
        "date_range_years": range_years,
    }


def extract_min_experience_from_jd(text: str) -> float:
    lower = text.lower()
    candidates = []
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
        r"minimum\s+(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
        r"at least\s+(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
    ]
    for p in patterns:
        for m in re.finditer(p, lower):
            candidates.append(float(m.group(1)))
    return min(candidates) if candidates else 0.0


def _important_lines(text: str, keywords: List[str], limit: int = 12) -> List[str]:
    result = []
    for line in lines(text):
        low = line.lower()
        if any(k in low for k in keywords):
            result.append(line)
    return result[:limit]


def extract_projects(section_text: str) -> List[str]:
    if not section_text:
        return []
    project_lines = []
    for line in lines(section_text):
        if len(line) > 8:
            project_lines.append(line)
    return project_lines[:12]


def extract_certifications(full_text: str, cert_section: str = "") -> List[str]:
    text = cert_section or full_text
    return _important_lines(text, CERT_KEYWORDS, limit=10)


def extract_education(full_text: str, education_section: str = "") -> List[str]:
    text = education_section or full_text
    return _important_lines(text, DEGREE_KEYWORDS, limit=12)


def summarize_bullets(text: str, limit: int = 8) -> List[str]:
    return sentence_split(text)[:limit]


def extract_resume_info(text: str, taxonomy: Dict) -> Dict[str, object]:
    sections = detect_sections(text)
    skills_text = "\n".join([sections.get("skills", ""), sections.get("projects", ""), sections.get("experience", ""), text])
    skill_info = extract_skills(skills_text, taxonomy)
    exp_text = "\n".join([sections.get("experience", ""), sections.get("summary", ""), text])

    return {
        "sections": sections,
        "skills": skill_info["skills"],
        "skills_by_category": skill_info["categories"],
        "matched_aliases": skill_info["matched_aliases"],
        "experience": extract_experience_years(exp_text),
        "education": extract_education(text, sections.get("education", "")),
        "certifications": extract_certifications(text, sections.get("certifications", "")),
        "projects": extract_projects(sections.get("projects", "")),
        "summary_points": summarize_bullets(sections.get("summary", "") or text, limit=5),
    }


def extract_jd_info(text: str, taxonomy: Dict) -> Dict[str, object]:
    sections = detect_sections(text)
    skill_info = extract_skills(text, taxonomy)
    return {
        "sections": sections,
        "required_skills": skill_info["skills"],
        "skills_by_category": skill_info["categories"],
        "min_experience_years": extract_min_experience_from_jd(text),
        "responsibility_points": summarize_bullets(sections.get("experience", "") or sections.get("other", "") or text, limit=10),
    }
