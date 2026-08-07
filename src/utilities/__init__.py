# contact info extraction gives a dict of email, phone, linkedin, github
from .data_extraction import extract_contact_info

# skill extraction gives a list of skills
from .data_extraction import SkillExtractor

# segment_resume_sections gives a dict of sections
from .grouping import segment_resume_sections