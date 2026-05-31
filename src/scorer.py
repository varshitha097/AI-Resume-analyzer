
from typing import Dict, List
from .taxonomy import skill_gap

DEFAULT_WEIGHTS = {
    "skills": 0.45,
    "experience": 0.20,
    "projects": 0.15,
    "semantic": 0.10,
    "education": 0.05,
    "certifications": 0.05,
}


def percentage(value: float) -> int:
    return int(round(max(min(value, 1.0), 0.0) * 100))


def skills_score(required: List[str], available: List[str]) -> float:
    if not required:
        return 0.7 if available else 0.0
    return len(set(required) & set(available)) / max(len(set(required)), 1)


def experience_score(candidate_years: float, required_years: float) -> float:
    if required_years <= 0:
        return 0.75 if candidate_years > 0 else 0.5
    return min(candidate_years / required_years, 1.0)


def text_presence_score(items: List[str], semantic_score: float = 0.0) -> float:
    # Presence plus semantic relevance. Useful for projects, education, certifications.
    presence = 1.0 if items else 0.0
    return max(presence * 0.7, semantic_score)


def final_score_breakdown(
    resume_info: Dict,
    jd_info: Dict,
    similarities: Dict[str, float],
    weights: Dict[str, float] = None,
) -> Dict[str, object]:
    weights = weights or DEFAULT_WEIGHTS
    required = jd_info.get("required_skills", [])
    available = resume_info.get("skills", [])
    gap = skill_gap(required, available)

    raw = {
        "skills": skills_score(required, available),
        "experience": experience_score(
            float(resume_info.get("experience", {}).get("years", 0.0)),
            float(jd_info.get("min_experience_years", 0.0)),
        ),
        "projects": text_presence_score(resume_info.get("projects", []), similarities.get("projects", 0.0)),
        "semantic": similarities.get("overall", 0.0),
        "education": text_presence_score(resume_info.get("education", []), similarities.get("education", 0.0)),
        "certifications": text_presence_score(resume_info.get("certifications", []), similarities.get("certifications", 0.0)),
    }

    weighted = {k: raw[k] * weights.get(k, 0) for k in raw}
    final = sum(weighted.values()) / max(sum(weights.values()), 0.001)

    return {
        "final_score": percentage(final),
        "component_scores": {k: percentage(v) for k, v in raw.items()},
        "weights": {k: int(v * 100) for k, v in weights.items()},
        "matched_skills": gap["matched_skills"],
        "missing_skills": gap["missing_skills"],
        "matched_skill_count": len(gap["matched_skills"]),
        "missing_skill_count": len(gap["missing_skills"]),
    }


def recommendation(score: int) -> str:
    if score >= 80:
        return "Strong match - shortlist recommended"
    if score >= 65:
        return "Good match - review projects and experience"
    if score >= 50:
        return "Average match - needs skill improvement"
    return "Low match - many JD gaps found"
