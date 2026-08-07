# src/vectorcv/services/jd_parser.py

import re
import spacy
from spacy.matcher import PhraseMatcher

class JobDescriptionParser:
    """
    Parses unstructured Job Description text to extract technical skills,
    soft skills, years of experience, and educational requirements.
    """

    def __init__(self, custom_skill_db: list[str] = None):
        # Load lightweight spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Default taxonomy of technical & analytical skills
        default_skills = [
            "Python", "Java", "C++", "SQL", "PostgreSQL", "SQLite", "MongoDB",
            "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Git", "CI/CD",
            "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch",
            "scikit-learn", "spaCy", "Pandas", "NumPy", "FastAPI", "Streamlit",
            "Flask", "REST API", "Microservices", "Data Structures", "Algorithms",
            "System Design", "Agile", "Scrum", "MLOps", "Linux", "Bash"
        ]
        
        skill_list = custom_skill_db if custom_skill_db else default_skills
        
        # Initialize PhraseMatcher with case-insensitive lower attribute
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = [self.nlp.make_doc(skill) for skill in skill_list]
        self.matcher.add("TECH_SKILLS", patterns)

    def extract_skills(self, jd_text: str) -> list[str]:
        """
        Tokenizes text and extracts matching technical skills using spaCy PhraseMatcher.
        """
        doc = self.nlp(jd_text)
        matches = self.matcher(doc)
        
        extracted_skills = set()
        for _, start, end in matches:
            span = doc[start:end]
            extracted_skills.add(span.text.strip())
            
        return sorted(list(extracted_skills))

    def extract_experience_years(self, jd_text: str) -> list[str]:
        """
        Extracts required years of experience using regular expressions.
        Handles formats like: '3+ years', '5-7 yrs', '10 years of experience'.
        """
        # Corrected pattern fixing the unescaped '+' quantifier
        pattern = r'\b\d{1,2}(?:\+|\s*-\s*\d{1,2})?\s*(?:years?|yrs?)(?:\s*of\s*experience)?'
        matches = re.findall(pattern, jd_text, re.IGNORECASE)
        return sorted(list(set(matches)))

    def extract_education_requirements(self, jd_text: str) -> list[str]:
        """
        Extracts common degree keywords (Bachelor, Master, PhD, B.S., M.S., Computer Science).
        """
        education_keywords = [
            r"\bB\.?S\.?\b", r"\bM\.?S\.?\b", r"\bPh\.?D\.?\b",
            r"Bachelor(?:'s)?", r"Master(?:'s)?", r"Doctorate",
            r"Computer Science", r"Software Engineering", r"Data Science", r"STEM"
        ]
        
        found = set()
        for pattern in education_keywords:
            if re.search(pattern, jd_text, re.IGNORECASE):
                # Clean regex symbols for tidy output presentation
                clean_name = pattern.replace(r"\b", "").replace(r"\.?", ".").replace("(?:'s)?", "")
                found.add(clean_name)
                
        return sorted(list(found))

    def parse(self, jd_text: str) -> dict:
        """
        Unified method returning structured details extracted from the Job Description.
        """
        if not jd_text.strip():
            return {
                "skills": [],
                "experience": [],
                "education": []
            }

        return {
            "skills": self.extract_skills(jd_text),
            "experience": self.extract_experience_years(jd_text),
            "education": self.extract_education_requirements(jd_text)
        }