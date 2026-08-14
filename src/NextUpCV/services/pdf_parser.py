import io
import re
from typing import Any, Dict
from pypdf import PdfReader


def extract_contact_info(raw_text: str) -> Dict[str, Any]:
    """Extracts email, phone number, and social profiles using regex."""
    if not raw_text:
        return {"email": None, "phone": None, "linkedin": None, "github": None}

    # Email
    email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
    emails = re.findall(email_pattern, raw_text)

    # Phone (handles international and standard formats)
    phone_pattern = r"(?:\+91[\-\s]?)?(?:[6-9]\d{4}[\-\s]?\d{5}|[6-9]\d{9})"
    phones = re.findall(phone_pattern, raw_text)
    clean_phone = re.sub(r"[^\d+]", "", phones[0]) if phones else None

    # LinkedIn & GitHub
    linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+"
    github_pattern = r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+"

    linkedin = re.findall(linkedin_pattern, raw_text, re.IGNORECASE)
    github = re.findall(github_pattern, raw_text, re.IGNORECASE)

    return {
        "email": emails[0] if emails else None,
        "phone": clean_phone,
        "linkedin": linkedin[0] if linkedin else None,
        "github": github[0] if github else None,
    }


class ResumeParserService:
    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes) -> str:
        """Extracts text content from PDF bytes using pypdf."""
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)
        return "\n".join(text_parts).strip()

    def parse_resume(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Parses PDF bytes and returns raw text + extracted contact information.
        """
        try:
            raw_text = self.extract_text_from_bytes(file_bytes)
            if not raw_text:
                return {"error": "Could not extract any readable text from the uploaded PDF."}

            contact_info = extract_contact_info(raw_text)

            return {
                "raw_text": raw_text,
                "contact_info": contact_info
            }
        except Exception as e:
            return {"error": f"PDF extraction error: {str(e)}"}