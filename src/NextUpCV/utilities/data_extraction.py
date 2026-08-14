import re
import spacy
from spacy.matcher import PhraseMatcher

class SkillExtractor:
    def __init__(self, skill_database: list[str] = None):  # type: ignore
        # Load lightweight spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        
        # Default fallback tech skill taxonomy
        if not skill_database:
            skill_database = [
                "Python", "Java", "C++", "SQL", "Docker", "Kubernetes", "AWS",
                "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
                "FastAPI", "Streamlit", "React", "Node.js", "Git", "CI/CD",
                "Agile", "REST API", "Pandas", "NumPy", "scikit-learn", "spaCy",
                "NLP", "NLTK", "Flask", "Django", "PostgreSQL", "MySQL",
                "SQLite", "Redis", "RabbitMQ", "Celery", "RabbitMQ", "Kafka",
                "RabbitMQ"
            ]
            
        # Convert skill strings into spaCy Doc patterns
        patterns = [self.nlp.make_doc(skill) for skill in skill_database]
        self.matcher.add("SKILL", patterns)

    def extract_skills(self, raw_text: str) -> list[str]:
        """Tokenizes text and extracts matching skills from the taxonomy."""
        doc = self.nlp(raw_text)
        matches = self.matcher(doc)
        
        extracted = set()
        for match_id, start, end in matches:
            span = doc[start:end]
            extracted.add(span.text.strip())
            
        return list(extracted)


def extract_contact_info(raw_text: str) -> dict:
    """Extracts email, phone number, and social links using Regex."""

    # 1. Email Pattern
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, raw_text)

    # 2. Phone Number Pattern (Handles +91 1234567891)
    phone_pattern = r"(?:\+91[\-\s]?)?(?:0(?![1-9]{4}\s?\d{3}))?(?:[6-9]\d{9}|[1-9]\d{1,4}[\-\s]?\d{6,8}|1800[\-\s]?\d{3}[\-\s]?\d{4})"
    phones = re.findall(phone_pattern, raw_text)

    # 3. LinkedIn & GitHub URLs
    linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+"
    github_pattern = r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+"

    linkedin = re.findall(linkedin_pattern, raw_text, re.IGNORECASE)
    github = re.findall(github_pattern, raw_text, re.IGNORECASE)

    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "linkedin": linkedin[0] if linkedin else None,
        "github": github[0] if github else None,
    }
