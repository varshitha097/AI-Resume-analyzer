
import json
from typing import Dict, List
from .taxonomy import extract_skills
from .cleaner import normalize_for_match


def load_domain_profiles(path: str = "config/domain_profiles.json") -> Dict[str, Dict[str, List[str]]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_domain(text: str, skills: List[str], profiles: Dict[str, Dict[str, List[str]]]) -> Dict[str, object]:
    norm = normalize_for_match(text)
    skill_set = set(skills)
    scores = []
    for domain, profile in profiles.items():
        core_skills = set(profile.get("core_skills", []))
        keywords = profile.get("keywords", [])
        skill_overlap = len(skill_set & core_skills)
        keyword_hits = sum(1 for k in keywords if normalize_for_match(k) in norm)
        score = skill_overlap * 2.0 + keyword_hits * 1.0
        max_possible = max(len(core_skills) * 2.0 + len(keywords), 1)
        confidence = min(score / max_possible, 1.0)
        scores.append({
            "domain": domain,
            "score": round(score, 2),
            "confidence": round(confidence, 3),
            "matched_core_skills": sorted(skill_set & core_skills),
        })
    scores.sort(key=lambda x: x["score"], reverse=True)
    best = scores[0] if scores else {"domain": "General", "confidence": 0}
    return {"best_domain": best["domain"], "confidence": best.get("confidence", 0), "domain_scores": scores[:5]}
