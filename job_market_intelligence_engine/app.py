import streamlit as st
import pandas as pd
from pathlib import Path
from src.engine import analyze_candidate, load_jobs, normalize_skills, skill_demand, save_upload
from src.ingestion import parse_resume_text

st.set_page_config(page_title="Job Market Intelligence & Skill Gap Engine", page_icon="📊", layout="wide")
st.title("📊 Job Market Intelligence & Skill Gap Engine")
st.caption("Explore hiring demand, compare your skills with real job descriptions, and build a focused learning roadmap.")

DATA_PATH = Path("data/jobs.csv")
jobs = load_jobs(DATA_PATH)

with st.sidebar:
    st.header("Data source")
    uploaded_jobs = st.file_uploader("Upload a job dataset (CSV)", type=["csv"])
    if uploaded_jobs:
        try:
            jobs = save_upload(uploaded_jobs)
            st.success(f"Loaded {len(jobs)} job records.")
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
    st.divider()
    st.markdown("**Expected CSV columns**")
    st.code("title, company, location, description, skills, experience, salary_min, salary_max")
    st.caption("The included sample dataset is illustrative. Replace it with current job-posting data before making market claims.")

if jobs.empty:
    st.warning("No jobs found. Add a CSV using the sidebar uploader.")
    st.stop()

jobs = jobs.copy()
jobs["skills_list"] = jobs["skills"].fillna("").apply(normalize_skills)
all_skills = sorted({s for row in jobs["skills_list"] for s in row})

tab1, tab2, tab3 = st.tabs(["Market dashboard", "My skill-gap analysis", "Explore jobs"])

with tab1:
    st.subheader("What employers are asking for")
    c1, c2, c3 = st.columns(3)
    c1.metric("Job postings", f"{len(jobs):,}")
    c2.metric("Unique skills", f"{len(all_skills):,}")
    c3.metric("Locations", f"{jobs['location'].nunique():,}")
    demand = skill_demand(jobs)
    left, right = st.columns(2)
    with left:
        st.markdown("#### Most requested skills")
        st.bar_chart(demand.head(15).set_index("skill")["postings"])
    with right:
        st.markdown("#### Postings by location")
        loc = jobs["location"].fillna("Not specified").value_counts().head(12)
        st.bar_chart(loc)
    st.markdown("#### Job titles in the dataset")
    st.dataframe(jobs["title"].value_counts().rename_axis("title").reset_index(name="postings"), use_container_width=True)

with tab2:
    st.subheader("Compare your profile with the job market")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        candidate_skills_text = st.text_area(
            "Your current skills (comma-separated)",
            placeholder="Python, SQL, Excel, Pandas, Power BI, Statistics",
            height=110
        )
        target = st.selectbox("Target role", ["Data Analyst", "Machine Learning Engineer", "Data Scientist", "Business Analyst", "Python Developer", "All roles"])
        resume_file = st.file_uploader("Optional: upload your resume (.txt)", type=["txt"], key="resume")
        if resume_file:
            resume_text = resume_file.getvalue().decode("utf-8", errors="ignore")
            extracted = parse_resume_text(resume_text)
            st.info("Skills detected from resume: " + (", ".join(extracted) if extracted else "No known skills detected. Add skills manually."))
            if not candidate_skills_text.strip():
                candidate_skills_text = ", ".join(extracted)
    with col_b:
        st.markdown("#### How the engine scores skills")
        st.write("It counts how many postings mention each skill, filters postings by your target role, then compares your skills against the most demanded skills. This is a transparent baseline—not an AI hiring score.")
        min_demand = st.slider("Minimum job-posting share for a priority skill", 1, 80, 10)
    if st.button("Analyze my skill gap", type="primary"):
        candidate_skills = normalize_skills(candidate_skills_text)
        result = analyze_candidate(jobs, candidate_skills, target, min_demand / 100)
        st.session_state["analysis"] = result
    if "analysis" in st.session_state:
        result = st.session_state["analysis"]
        a, b, c = st.columns(3)
        a.metric("Matched skills", result["matched_count"])
        b.metric("Priority gaps", len(result["gaps"]))
        c.metric("Relevant postings", result["relevant_jobs"])
        st.markdown("#### Your skill match")
        st.progress(result["match_ratio"], text=f"{result['match_ratio']:.0%} of priority skills already present")
        st.markdown("#### Highest-priority skills to learn")
        if result["gaps"]:
            gap_df = pd.DataFrame(result["gaps"])
            st.dataframe(gap_df, use_container_width=True, hide_index=True)
        else:
            st.success("No priority gaps were found for this selection. Consider broadening your target role.")
        st.markdown("#### Suggested 30-day learning roadmap")
        for item in result["roadmap"]:
            st.markdown(f"- **Week {item['week']} — {item['skill']}**: {item['task']}")
        st.download_button("Download skill-gap report (CSV)", pd.DataFrame(result["gaps"]).to_csv(index=False), "skill_gap_report.csv", "text/csv")

with tab3:
    st.subheader("Search the included job dataset")
    q = st.text_input("Search title, company, location or description")
    locations = ["All"] + sorted(jobs["location"].dropna().unique().tolist())
    selected_location = st.selectbox("Location", locations)
    filtered = jobs.copy()
    if q:
        mask = filtered.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
        filtered = filtered[mask]
    if selected_location != "All":
        filtered = filtered[filtered["location"] == selected_location]
    st.write(f"{len(filtered)} postings")
    show_cols = [c for c in ["title", "company", "location", "experience", "salary_min", "salary_max", "skills"] if c in filtered.columns]
    st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)
