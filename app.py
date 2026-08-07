import streamlit as st
import pdfplumber
from src.vectorcv import (
    flash_success,
    flash_error,
    extract_contact_info,
    SkillExtractor,
    segment_resume_sections,
    word_count,
    JobDescriptionParser,
)

sample_jd = """
We are looking for a Senior Software Engineer with 3+ years of experience in building scalable web apps.
Requirements:
- Bachelor's degree in Computer Science or related field.
- Proficiency in Python, FastAPI, Docker, and PostgreSQL.
- Experience with MLOps pipelines and Machine Learning tools like PyTorch or scikit-learn.
"""

st.title("VectorCV")

st.write("Upload your resume here:")
resume_file = st.file_uploader("Upload your resume", type=["pdf"])
if st.button("Submit", key="submit_resume"):
    if resume_file is None:
        flash_error("Resume not uploaded!", 1)
    else:
        # flash_success("Resume uploaded successfully!", 1)
        with pdfplumber.open(resume_file) as pdf:
            num_of_pages = len(pdf.pages)
            pages = pdf.pages[num_of_pages - 1]
            text = pages.extract_text()
            # st.write(text)
            skills = SkillExtractor().extract_skills(text)
            with st.container(border=True):
                contact_info = extract_contact_info(text)
                # st.write(contact_info)
                st.subheader("Contact Info")
                for i in contact_info:
                    st.write(contact_info[i])
            with st.container(border=True):
                st.subheader("Skills")
                for i in skills:
                    st.write(i)
            with st.container(border=True):
                sections = segment_resume_sections(text)
                st.subheader("Sections")
                for i in sections:
                    st.write(sections[i])
            # st.write(sections)

st.write("paste the job description here:")
job_description = st.text_area("Job Description", value=None, key="job_description")
if st.button("Submit", key="submit_discription"):
    if job_description is None:
        flash_error("Job description not uploaded!", 1)
    elif word_count(job_description) < 10:
        flash_error("Job description too short!", 1)
    else:
        flash_success("Job description uploaded successfully!", 1)

        # Instantiate parser
        jd_parser = JobDescriptionParser()

        # Extract structured information
        parsed_data = jd_parser.parse(job_description)

        st.write("Extracted Skills:", parsed_data["skills"])
        # Output: ['Bachelor', 'Computer Science', 'Docker', 'FastAPI', 'MLOps', 'Machine Learning', 'PostgreSQL', 'PyTorch', 'Python', 'scikit-learn']

        st.write("Required Experience:", parsed_data["experience"])
        # Output: ['3+ years']

        st.write("Required Education:", parsed_data["education"])
        # Output: ['Bachelor', 'Computer Science']
