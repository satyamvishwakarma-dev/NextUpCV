import re
from typing import Dict, List, Optional


class SkillExtractor:
    def __init__(self, skill_database: Optional[List[str]] = None):
        # Cleaned taxonomy (removed duplicates, added special symbol handling)
        if not skill_database:
            skill_database = [
                "Python", "Java", "C++", "C#", "SQL", "Docker", "Kubernetes", "AWS",
                "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
                "FastAPI", "Streamlit", "React", "Node.js", "Git", "CI/CD",
                "Agile", "REST API", "Pandas", "NumPy", "scikit-learn", "spaCy",
                "NLP", "NLTK", "Flask", "Django", "PostgreSQL", "MySQL",
                "SQLite", "Redis", "RabbitMQ", "Celery", "Kafka"
            ]
        
        # Sort skills by length descending so multi-word phrases match before substrings
        # (e.g., "REST API" before "API", "Deep Learning" before "Learning")
        self.skill_database = sorted(list(set(skill_database)), key=len, reverse=True)
        
        # Precompile regex patterns with word boundary awareness
        self._compiled_patterns = []
        for skill in self.skill_database:
            escaped = re.escape(skill)
            # Handle special symbols like C++, C#, .NET
            pattern = re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)
            self._compiled_patterns.append((skill, pattern))

    def extract_skills(self, raw_text: str) -> List[str]:
        """Extracts technical skills matching taxonomy in O(N) regex passes."""
        if not raw_text:
            return []

        matched_skills = []
        for canonical_name, pattern in self._compiled_patterns:
            if pattern.search(raw_text):
                matched_skills.append(canonical_name)

        return matched_skills


def extract_contact_info(raw_text: str) -> Dict[str, Optional[str]]:
    """Extracts email, phone number, and professional URLs using Regex."""
    if not raw_text:
        return {"email": None, "phone": None, "linkedin": None, "github": None}

    # 1. Email Pattern
    email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
    emails = re.findall(email_pattern, raw_text)

    # 2. Phone Number Pattern (Handles standard Indian mobile numbers & international format)
    phone_pattern = r"(?:\+91[\-\s]?)?(?:[6-9]\d{4}[\-\s]?\d{5}|[6-9]\d{9})"
    phones = re.findall(phone_pattern, raw_text)

    # 3. LinkedIn & GitHub Profile URLs
    linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+(?:/)?"
    github_pattern = r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+(?:/)?"

    linkedin = re.findall(linkedin_pattern, raw_text, re.IGNORECASE)
    github = re.findall(github_pattern, raw_text, re.IGNORECASE)

    # Clean extracted phone output
    clean_phone = None
    if phones:
        clean_phone = re.sub(r"[^\d+]", "", phones[0])

    return {
        "email": emails[0] if emails else None,
        "phone": clean_phone,
        "linkedin": linkedin[0].strip() if linkedin else None,
        "github": github[0].strip() if github else None,
    }