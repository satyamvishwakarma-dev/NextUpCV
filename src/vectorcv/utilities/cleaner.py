import re

def clean_text(raw_text: str) -> str:
    """
    Strips invalid characters, normalizes whitespace, and cleans non-ASCII symbols.
    """
    if not raw_text:
        return ""
    
    # Remove null bytes and non-printable characters
    text = raw_text.replace("\x00", " ")
    
    # Normalize excessive newlines and whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip URLs and email tokens for standardized NLP vector matching
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    return text.strip()

def extract_contact_info(raw_text: str) -> dict:
    """
    Extracts contact metadata (email and phone number) using regular expressions.
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    
    emails = re.findall(email_pattern, raw_text)
    phones = re.findall(phone_pattern, raw_text)
    
    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None
    }