import math
import re
from collections import Counter
from typing import List, Tuple

class MatchEngine:
    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can't", "cannot", "could", "did",
        "do", "does", "doing", "don't", "down", "during", "each", "few", "for", "from",
        "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
        "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it",
        "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
        "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
        "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
        "themselves", "then", "there", "these", "they", "this", "those", "through",
        "to", "too", "under", "until", "up", "very", "was", "we", "were", "what",
        "when", "where", "which", "while", "who", "whom", "why", "with", "would", "you", "your"
    }

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        return [w for w in words if w not in self.STOPWORDS]

    def calculate_score(self, resume_text: str, jd_text: str) -> Tuple[int, List[str]]:
        resume_tokens = self._tokenize(resume_text)
        jd_tokens = self._tokenize(jd_text)

        if not jd_tokens or not resume_tokens:
            return 0, []

        resume_counts = Counter(resume_tokens)
        jd_counts = Counter(jd_tokens)

        # 1. Cosine Similarity Calculation
        all_words = set(resume_counts.keys()).union(set(jd_counts.keys()))
        dot_product = sum(resume_counts[w] * jd_counts[w] for w in all_words)
        
        mag_resume = math.sqrt(sum(v ** 2 for v in resume_counts.values()))
        mag_jd = math.sqrt(sum(v ** 2 for v in jd_counts.values()))
        
        if mag_resume == 0 or mag_jd == 0:
            cosine_sim = 0.0
        else:
            cosine_sim = dot_product / (mag_resume * mag_jd)

        # Scale match score between 0 and 100
        score = int(min(max(cosine_sim * 100 * 1.5, 0), 100))

        # 2. Missing keywords: Top keywords in JD missing from resume
        missing_keywords = [
            word for word, _ in jd_counts.most_common(15)
            if word not in resume_counts
        ][:6]

        return score, missing_keywords