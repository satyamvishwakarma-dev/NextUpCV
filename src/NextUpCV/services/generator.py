import random
import spacy
from NextUpCV.config import SPACY_MODEL


class RuleBasedBulletGenerator:
    """
    Deterministic bullet point generator driven by spaCy Part-of-Speech analysis.
    """

    def __init__(self):
        self.nlp = spacy.load(SPACY_MODEL)

        self.noun_templates = [
            "Architected and optimized pipelines utilizing {keyword} to improve system processing throughput.",
            "Engineered core modules leveraging {keyword}, reducing overall operational overhead by 15%.",
            "Integrated {keyword} into existing workflows to ensure scalable and reliable delivery.",
        ]

        self.verb_templates = [
            "Demonstrated strong competency in {keyword} across cross-functional engineering initiatives.",
            "Led optimization strategies focused on {keyword} to boost project execution speed.",
        ]

    def _classify_keyword(self, keyword: str) -> str:
        doc = self.nlp(keyword.strip())
        for token in doc:
            if token.pos_ in ("VERB", "AUX") or token.tag_ == "VBG":
                return "verb"
        return "noun"

    def generate_tailored_bullets(
        self, missing_keywords: list[str], max_bullets: int = 4
    ) -> list[str]:
        if not missing_keywords:
            return [
                "Resume already demonstrates strong alignment with target job requirements!"
            ]

        bullets = []
        for kw in missing_keywords[:max_bullets]:
            category = self._classify_keyword(kw)
            template = random.choice(
                self.verb_templates if category == "verb" else self.noun_templates
            )

            formatted_kw = kw.title() if len(kw) > 3 else kw.upper()
            bullets.append(template.format(keyword=formatted_kw))

        return bullets
