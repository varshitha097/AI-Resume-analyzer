
import re
from typing import Dict, List
from .cleaner import lines

SECTION_ALIASES = {
    "summary": ["summary", "profile", "objective", "career objective", "professional summary", "about me"],
    "skills": ["skills", "technical skills", "core skills", "key skills", "technologies", "tools", "programming skills"],
    "experience": ["experience", "work experience", "professional experience", "employment", "internship", "internships"],
    "education": ["education", "academic background", "academics", "qualification", "qualifications"],
    "projects": ["projects", "academic projects", "personal projects", "project experience", "major projects"],
    "certifications": ["certifications", "certificates", "licenses", "achievements", "awards"],
    "contact": ["contact", "personal details"],
}

ALIAS_TO_SECTION = {alias: sec for sec, aliases in SECTION_ALIASES.items() for alias in aliases}


def _canonical_heading(line: str) -> str:
    clean = re.sub(r"[^a-zA-Z ]", " ", line).lower()
    clean = re.sub(r"\s+", " ", clean).strip()
    if clean in ALIAS_TO_SECTION:
        return ALIAS_TO_SECTION[clean]
    # Allow heading with colon, e.g. "Technical Skills: Python, SQL"
    before_colon = re.sub(r"[^a-zA-Z ]", " ", line.split(":", 1)[0]).lower()
    before_colon = re.sub(r"\s+", " ", before_colon).strip()
    return ALIAS_TO_SECTION.get(before_colon, "")


def detect_sections(text: str) -> Dict[str, str]:
    """Split resume/JD text into named sections using common heading aliases."""
    result: Dict[str, List[str]] = {k: [] for k in SECTION_ALIASES}
    result["other"] = []
    current = "other"

    for raw_line in lines(text):
        heading = _canonical_heading(raw_line)
        if heading:
            current = heading
            # Keep text after colon as content if available.
            if ":" in raw_line and len(raw_line.split(":", 1)[1].strip()) > 0:
                result[current].append(raw_line.split(":", 1)[1].strip())
            continue
        result[current].append(raw_line)

    return {k: "\n".join(v).strip() for k, v in result.items() if "\n".join(v).strip()}
