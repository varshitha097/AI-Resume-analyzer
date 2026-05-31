
from pathlib import Path
from typing import Dict, List, Union
from .parser import extract_text_from_file
from .taxonomy import load_skills_taxonomy
from .extractor import extract_resume_info, extract_jd_info
from .domain import load_domain_profiles, detect_domain
from .similarity import SimilarityEngine
from .scorer import final_score_breakdown, recommendation


def _section_text(info: Dict, section: str, fallback: str = "") -> str:
    return info.get("sections", {}).get(section, fallback) or fallback or ""


class ResumeAnalyzer:
    def __init__(
        self,
        taxonomy_path: str = "config/skills_taxonomy.json",
        domain_profiles_path: str = "config/domain_profiles.json",
    ):
        self.taxonomy = load_skills_taxonomy(taxonomy_path)
        self.domain_profiles = load_domain_profiles(domain_profiles_path)
        self.similarity_engine = SimilarityEngine()

    def analyze_text(self, resume_text: str, jd_text: str, file_name: str = "resume.txt") -> Dict[str, object]:
        resume_info = extract_resume_info(resume_text, self.taxonomy)
        jd_info = extract_jd_info(jd_text, self.taxonomy)

        resume_domain = detect_domain(resume_text, resume_info.get("skills", []), self.domain_profiles)
        jd_domain = detect_domain(jd_text, jd_info.get("required_skills", []), self.domain_profiles)

        similarities = {
            "overall": self.similarity_engine.similarity(resume_text, jd_text),
            "skills": self.similarity_engine.similarity(
                ", ".join(resume_info.get("skills", [])), ", ".join(jd_info.get("required_skills", []))
            ),
            "experience": self.similarity_engine.similarity(
                _section_text(resume_info, "experience"), _section_text(jd_info, "experience", jd_text)
            ),
            "projects": self.similarity_engine.similarity(
                _section_text(resume_info, "projects"), jd_text
            ),
            "education": self.similarity_engine.similarity(
                _section_text(resume_info, "education"), jd_text
            ),
            "certifications": self.similarity_engine.similarity(
                _section_text(resume_info, "certifications"), jd_text
            ),
        }

        scoring = final_score_breakdown(resume_info, jd_info, similarities)
        scoring["recommendation"] = recommendation(scoring["final_score"])

        return {
            "file_name": file_name,
            "score": scoring["final_score"],
            "recommendation": scoring["recommendation"],
            "scoring": scoring,
            "similarities": {k: int(round(v * 100)) for k, v in similarities.items()},
            "resume_domain": resume_domain,
            "jd_domain": jd_domain,
            "resume_info": resume_info,
            "jd_info": jd_info,
            "engine": self.similarity_engine.backend,
        }

    def analyze_file(self, resume_file_path: Union[str, Path], jd_text: str) -> Dict[str, object]:
        text, meta = extract_text_from_file(str(resume_file_path))
        result = self.analyze_text(text, jd_text, file_name=Path(resume_file_path).name)
        result["parser_meta"] = meta
        result["extracted_text_length"] = len(text)
        return result

    def analyze_many(self, resume_paths: List[Union[str, Path]], jd_text: str) -> Dict[str, object]:
        results = [self.analyze_file(path, jd_text) for path in resume_paths]
        results.sort(key=lambda x: x["score"], reverse=True)
        for idx, item in enumerate(results, start=1):
            item["rank"] = idx
        jd_info = extract_jd_info(jd_text, self.taxonomy)
        return {
            "ranking": results,
            "total_candidates": len(results),
            "jd_summary": {
                "required_skills": jd_info.get("required_skills", []),
                "min_experience_years": jd_info.get("min_experience_years", 0),
                "domain": detect_domain(jd_text, jd_info.get("required_skills", []), self.domain_profiles),
            },
            "engine": self.similarity_engine.backend,
        }
