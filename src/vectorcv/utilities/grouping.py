import re


def segment_resume_sections(raw_text: str) -> dict:
    """
    Splits continuous resume text into logical dictionary sections based on headers.
    """
    # Common header titles found in resumes
    headers = [
        "WORK EXPERIENCE",
        "EXPERIENCE",
        "EMPLOYMENT HISTORY",
        "EDUCATION",
        "ACADEMIC BACKGROUND",
        "QUALIFICATIONS",
        "SKILLS",
        "TECHNICAL SKILLS",
        "COMPETENCIES",
        "PROJECTS",
        "PERSONAL PROJECTS",
        "CERTIFICATIONS",
        "LANGUAGES",
        "INTERESTS",
        "HOBBIES",
        "REFERENCES",
        "CONTACT INFORMATION",
        "ADDRESS",
        "ACTIVITIES",
        "CO-CURRICULAR ACTIVITIES",
        "NON-TECHNICAL ACTIVITIES",
        "OTHER INFORMATION",
    ]

    # Create regex regex pattern matching any uppercase header on a new line
    header_pattern = r"\n(?=(" + "|".join(headers) + r"))"

    # Split text by sections
    splits = re.split(header_pattern, raw_text, flags=re.IGNORECASE)

    sections = {}
    current_header = "HEADER_INFO"

    for block in splits:
        if not block:
            continue
        cleaned_block = block.strip()
        if cleaned_block.upper() in headers:
            current_header = cleaned_block.upper()
        else:
            sections[current_header] = cleaned_block

    return sections
