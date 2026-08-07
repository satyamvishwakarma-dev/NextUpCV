import streamlit as st
import pdfplumber
from src.ui import flash_success, flash_error
from src.utilities import extract_contact_info, SkillExtractor

st.title("VectorCV")

st.write("Upload your resume here:")
resume_file = st.file_uploader("Upload your resume", type=["pdf"])
if st.button("Submit"):
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
            
