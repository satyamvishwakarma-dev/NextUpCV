import streamlit as st
from src. import ResumeParserService
from vectorcv.services.jd_parser import JobDescriptionParser
from vectorcv.services.match_engine import MatchEngine
from vectorcv.services.generator import RuleBasedBulletGenerator
from vectorcv.database.connection import init_db
from vectorcv.database.repository import save_scan_record, get_recent_scans

# 1. Page Configuration
st.set_page_config(
    page_title="VectorCV | Deterministic Resume Matcher",
    page_icon="🎯",
    layout="wide"
)

# 2. Initialize Database on Startup
init_db()

# 3. Instantiate Service Engines
@st.cache_resource
def load_engines():
    return (
        ResumeParserService(),
        JobDescriptionParser(),
        MatchEngine(),
        RuleBasedBulletGenerator()
    )

resume_parser, jd_parser, match_engine, bullet_generator = load_engines()

# 4. Sidebar - Past Scan History
st.sidebar.title("📊 Recent Scans")
recent_scans = get_recent_scans(limit=5)
if recent_scans:
    for scan in recent_scans:
        st.sidebar.metric(
            label=scan["file_name"],
            value=f"{scan['match_score']}% Match",
            delta=f"{scan['missing_keyword_count']} missing terms"
        )
else:
    st.sidebar.info("No scan history found.")

# 5. Main UI Header
st.title("🎯 VectorCV")
st.caption("Offline, deterministic ATS resume compatibility & NLP match engine.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

with col2:
    st.subheader("2. Target Job Description")
    job_description = st.text_area("Paste job requirements here", height=200)

# 6. Process & Analyze
if st.button("Run Match Analysis", type="primary"):
    if not uploaded_file or not job_description.strip():
        st.warning("Please upload a PDF resume and paste a job description.")
    else:
        with st.spinner("Analyzing document structure and vector space..."):
            # Step A: Parse PDF
            file_bytes = uploaded_file.read()
            parsed_resume = resume_parser.parse_resume(file_bytes)

            if "error" in parsed_resume:
                st.error(parsed_resume["error"])
            else:
                raw_resume = parsed_resume["raw_text"]

                # Step B: Match & Extract
                score = match_engine.compute_similarity(raw_resume, job_description)
                missing_keywords = match_engine.extract_missing_keywords(raw_resume, job_description)
                suggested_bullets = bullet_generator.generate_tailored_bullets(missing_keywords)

                # Step C: Log to SQLite
                save_scan_record(
                    file_name=uploaded_file.name,
                    raw_resume_text=raw_resume,
                    job_description=job_description,
                    match_score=score,
                    missing_keyword_count=len(missing_keywords)
                )

                # Step D: Display Results
                st.divider()
                st.header("Results Analysis")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("ATS Compatibility Score", f"{score}%")
                m2.metric("Missing Keywords Found", len(missing_keywords))
                m3.metric("Extracted Contact Email", parsed_resume["contact_info"]["email"] or "N/A")

                st.subheader("Missing Critical Keywords")
                if missing_keywords:
                    st.write(" • ".join([f"`{kw}`" for kw in missing_keywords]))
                else:
                    st.success("No critical keyword gaps identified!")

                st.subheader("Suggested Action Bullets (spaCy POS Generated)")
                for bullet in suggested_bullets:
                    st.markdown(f"- {bullet}")