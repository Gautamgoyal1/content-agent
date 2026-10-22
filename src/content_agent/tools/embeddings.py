"""In-memory text similarity and keyword overlap utilities."""

import math
import re
from collections import Counter


class TextSimilarity:
    """Lightweight in-memory vector and token similarity calculator."""

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", text)]

    @classmethod
    def cosine_similarity(cls, text_a: str, text_b: str) -> float:
        """Calculate cosine similarity between word frequency vectors of two texts."""
        tokens_a = cls._tokenize(text_a)
        tokens_b = cls._tokenize(text_b)

        if not tokens_a or not tokens_b:
            return 0.0

        vec_a = Counter(tokens_a)
        vec_b = Counter(tokens_b)

        intersection = set(vec_a.keys()) & set(vec_b.keys())
        numerator = sum([vec_a[x] * vec_b[x] for x in intersection])

        sum1 = sum([vec_a[x] ** 2 for x in vec_a.keys()])
        sum2 = sum([vec_b[x] ** 2 for x in vec_b.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

    @classmethod
    def overlap_ratio(cls, text_a: str, text_b: str) -> float:
        """Calculate Jaccard token overlap between two texts."""
        set_a = set(cls._tokenize(text_a))
        set_b = set(cls._tokenize(text_b))
        if not set_a or not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)
