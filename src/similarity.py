
from typing import Dict, List
import math


def _safe_text(text: str) -> str:
    return text if text and text.strip() else "empty"


class SimilarityEngine:
    """Sentence-transformer similarity with automatic TF-IDF fallback."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.backend = "tfidf"
        self.model = None
        self.util = None
        try:
            from sentence_transformers import SentenceTransformer, util
            self.model = SentenceTransformer(model_name)
            self.util = util
            self.backend = "sentence-transformers"
        except Exception:
            self.model = None
            self.util = None
            self.backend = "tfidf"

    def similarity(self, text_a: str, text_b: str) -> float:
        text_a = _safe_text(text_a)
        text_b = _safe_text(text_b)
        if self.backend == "sentence-transformers" and self.model is not None:
            emb = self.model.encode([text_a, text_b], convert_to_tensor=True, normalize_embeddings=True)
            score = float(self.util.cos_sim(emb[0], emb[1]).item())
            return round(max(min(score, 1.0), 0.0), 4)
        return self._tfidf_similarity(text_a, text_b)

    @staticmethod
    def _tfidf_similarity(text_a: str, text_b: str) -> float:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", min_df=1)
            matrix = vectorizer.fit_transform([text_a, text_b])
            score = float(cosine_similarity(matrix[0], matrix[1])[0][0])
            return round(max(min(score, 1.0), 0.0), 4)
        except Exception:
            # Last-resort token overlap fallback.
            a = set(text_a.lower().split())
            b = set(text_b.lower().split())
            if not a or not b:
                return 0.0
            return round(len(a & b) / len(a | b), 4)

    def batch_pairwise(self, pairs: List[tuple]) -> List[float]:
        return [self.similarity(a, b) for a, b in pairs]
