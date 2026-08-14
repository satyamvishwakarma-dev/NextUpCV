from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from NextUpCV.config import SPACY_MODEL


class MatchEngine:
    """
    Vector Space Matching Engine utilizing TF-IDF and Cosine Similarity.
    """

    def __init__(self):
        self.nlp = spacy.load(SPACY_MODEL)

    def compute_similarity(self, resume_text: str, job_desc_text: str) -> float:
        if not resume_text.strip() or not job_desc_text.strip():
            return 0.0

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        try:
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_desc_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]  # type: ignore
            return round(float(similarity) * 100, 2)
        except ValueError:
            return 0.0

    def extract_missing_keywords(
        self, resume_text: str, job_desc_text: str, top_n: int = 8
    ) -> list[str]:
        res_doc = self.nlp(resume_text.lower())
        jd_doc = self.nlp(job_desc_text.lower())

        resume_lemmas = {
            token.lemma_
            for token in res_doc
            if not token.is_stop and not token.is_punct and token.is_alpha
        }

        jd_keywords = []
        for token in jd_doc:
            if (
                not token.is_stop
                and not token.is_punct
                and token.is_alpha
                and len(token.text) > 2
                and token.pos_ in ("NOUN", "PROPN")
            ):
                if token.lemma_ not in resume_lemmas:
                    jd_keywords.append(token.text.lower())

        counts = Counter(jd_keywords)
        return [kw for kw, _ in counts.most_common(top_n)]
