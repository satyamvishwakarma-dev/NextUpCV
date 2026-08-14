import streamlit as st

def render_sidebar_history(recent_scans: list[dict]):
    """Renders recent database scan records in the Streamlit sidebar."""
    st.sidebar.title("📊 Recent Scans")
    if recent_scans:
        for scan in recent_scans:
            st.sidebar.metric(
                label=scan["file_name"],
                value=f"{scan['match_score']}% Match",
                delta=f"{scan['missing_keyword_count']} missing terms"
            )
    else:
        st.sidebar.info("No prior scan logs found.")

def render_results(score: float, missing_keywords: list[str], bullets: list[str], email: str):
    """Renders metrics dashboard, keyword tags, and generated suggestions."""
    st.divider()
    st.header("Match Analysis Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("ATS Similarity Score", f"{score}%")
    col2.metric("Missing Keywords", len(missing_keywords))
    col3.metric("Extracted Email", email or "Not Found")

    st.subheader("Critical Keyword Gaps")
    if missing_keywords:
        st.write(" • ".join([f"`{kw}`" for kw in missing_keywords]))
    else:
        st.success("No significant keyword gaps identified.")

    st.subheader("Suggested Action Bullet Points (spaCy Driven)")
    for b in bullets:
        st.markdown(f"- {b}")