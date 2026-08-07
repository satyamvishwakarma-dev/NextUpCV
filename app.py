import streamlit as st
from src.vectorcv import *

# 1. Page Configuration
st.set_page_config(page_title="VectorCV", page_icon="🎯", layout="wide")

# 2. Database & Resource Initialization
init_db()

@st.cache_resource
def load_services():
    return ResumeParserService(), MatchEngine(), RuleBasedBulletGenerator()

parser, match_engine, generator = load_services()

# 3. Sidebar Render
render_sidebar_history(get_recent_scans(limit=5))

# 4. Main Interface Header
st.title("🎯 VectorCV")
st.caption("Offline, deterministic ATS resume compatibility & NLP match engine.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Select PDF file", type=["pdf"])

with col2:
    st.subheader("2. Target Job Description")
    job_description = st.text_area("Paste job requirements", height=200)

# 5. Pipeline Execution Trigger
if st.button("Analyze Alignment", type="primary"):
    if not uploaded_file or not job_description.strip():
        st.warning("Please upload a PDF resume and provide a job description.")
    else:
        with st.spinner("Processing PDF layout and vector space model..."):
            file_bytes = uploaded_file.read()
            parsed_resume = parser.parse_resume(file_bytes)

            if "error" in parsed_resume:
                st.error(parsed_resume["error"])
            else:
                raw_text = parsed_resume["raw_text"]
                score = match_engine.compute_similarity(raw_text, job_description)
                missing_kw = match_engine.extract_missing_keywords(raw_text, job_description)
                bullets = generator.generate_tailored_bullets(missing_kw)

                # Persist Metrics to SQLite
                save_scan_record(
                    file_name=uploaded_file.name,
                    raw_resume_text=raw_text,
                    job_description=job_description,
                    match_score=score,
                    missing_keyword_count=len(missing_kw)
                )

                # Render Results
                render_results(
                    score=score,
                    missing_keywords=missing_kw,
                    bullets=bullets,
                    email=parsed_resume["contact_info"]["email"]
                )