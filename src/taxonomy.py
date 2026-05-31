
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from .cleaner import normalize_for_match

SPECIAL_ALIASES = {"c++", "c#", ".net", "nodejs", "reactjs", "nextjs", "expressjs", "vuejs"}


def load_skills_taxonomy(path: str = "config/skills_taxonomy.json") -> Dict[str, Dict[str, List[str]]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_alias_map(taxonomy: Dict[str, Dict[str, List[str]]]) -> Dict[str, Tuple[str, str]]:
    """Return alias -> (canonical_skill, category)."""
    alias_map: Dict[str, Tuple[str, str]] = {}
    for category, skills in taxonomy.items():
        for canonical, aliases in skills.items():
            all_aliases = set([canonical] + aliases)
            for alias in all_aliases:
                normalized = normalize_for_match(alias)
                if normalized:
                    alias_map[normalized] = (canonical, category)
    return alias_map


def _pattern_for_alias(alias: str) -> re.Pattern:
    # For normal words use word boundaries. For c++/.net use loose non-word boundaries.
    escaped = re.escape(alias)
    if alias in SPECIAL_ALIASES or any(ch in alias for ch in "+#."):
        return re.compile(rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])", re.I)
    return re.compile(rf"\b{escaped}\b", re.I)


def extract_skills(text: str, taxonomy: Dict[str, Dict[str, List[str]]]) -> Dict[str, object]:
    norm_text = normalize_for_match(text)
    alias_map = build_alias_map(taxonomy)
    found: Set[str] = set()
    matched_aliases: Dict[str, List[str]] = {}
    categories: Dict[str, Set[str]] = {}

    # Match longer aliases first so "machine learning" is found before "learning" if added later.
    for alias in sorted(alias_map, key=len, reverse=True):
        canonical, category = alias_map[alias]
        if _pattern_for_alias(alias).search(norm_text):
            found.add(canonical)
            matched_aliases.setdefault(canonical, []).append(alias)
            categories.setdefault(category, set()).add(canonical)

    return {
        "skills": sorted(found),
        "matched_aliases": {k: sorted(v) for k, v in matched_aliases.items()},
        "categories": {k: sorted(v) for k, v in categories.items()},
    }


def skill_gap(required: List[str], available: List[str]) -> Dict[str, List[str]]:
    required_set = set(required)
    available_set = set(available)
    missing = sorted(required_set - available_set)
    matched = sorted(required_set & available_set)
    return {"matched_skills": matched, "missing_skills": missing}
