
import re
from typing import List

BULLET_CHARS = "•▪●■□◆◇◦‣⁃–—*"


def normalize_whitespace(text: str) -> str:
    """Normalize spacing while keeping useful line breaks for section detection."""
    if not text:
        return ""
    text = text.replace("\r", "\n")
    text = re.sub(r"[\t\x0b\x0c]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    return text.strip()


def clean_line(line: str) -> str:
    line = line.strip()
    line = line.strip(BULLET_CHARS + " ")
    return re.sub(r"\s+", " ", line).strip()


def lines(text: str) -> List[str]:
    return [clean_line(l) for l in normalize_whitespace(text).splitlines() if clean_line(l)]


def normalize_for_match(text: str) -> str:
    """Lowercase and normalize punctuation for keyword matching."""
    text = (text or "").lower()
    replacements = {
        "react.js": "reactjs",
        "node.js": "nodejs",
        "next.js": "nextjs",
        "express.js": "expressjs",
        "vue.js": "vuejs",
        "c ++": "c++",
        "c #": "c#",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[/|,;()\[\]{}]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def sentence_split(text: str) -> List[str]:
    text = normalize_whitespace(text)
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip()) > 2]
