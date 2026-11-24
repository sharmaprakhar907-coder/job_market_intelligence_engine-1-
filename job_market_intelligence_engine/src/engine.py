from pathlib import Path
import re
import pandas as pd

ALIASES = {
    "postgres": "postgresql", "powerbi": "power bi", "scikit learn": "scikit-learn",
    "ml": "machine learning", "dl": "deep learning", "ms excel": "excel",
    "natural language processing": "nlp", "amazon web services": "aws"
}
SKILL_LIBRARY = [
    "python", "sql", "excel", "power bi", "tableau", "statistics", "pandas", "numpy",
    "matplotlib", "seaborn", "data cleaning", "data visualization", "machine learning",
    "scikit-learn", "deep learning", "tensorflow", "pytorch", "nlp", "llm", "generative ai",
    "feature engineering", "model evaluation", "time series", "git", "github", "linux",
    "docker", "aws", "azure", "gcp", "flask", "fastapi", "streamlit", "mysql",
    "postgresql", "communication", " problem solving"
]

def normalize_skills(value):
    if isinstance(value, list):
        raw = value
    else:
        raw = re.split(r"[,;|\n]", str(value or ""))
    cleaned = []
    for item in raw:
        s = re.sub(r"\s+", " ", str(item).strip().lower())
        s = ALIASES.get(s, s)
        if s and s not in cleaned:
            cleaned.append(s)
    return cleaned

def load_jobs(path):
    df = pd.read_csv(path)
    required = {"title", "company", "location", "description", "skills"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {', '.join(sorted(missing))}")
    for col in ["experience", "salary_min", "salary_max"]:
        if col not in df.columns:
            df[col] = None
    return df.fillna({"title": "", "company": "", "location": "", "description": "", "skills": ""})

def save_upload(uploaded_file):
    df = pd.read_csv(uploaded_file)
    required = {"title", "company", "location", "description", "skills"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/uploaded_jobs.csv", index=False)
    return df.fillna("")

def skill_demand(jobs):
    counts = {}
    for skills in jobs["skills"].fillna("").apply(normalize_skills):
        for skill in set(skills):
            counts[skill] = counts.get(skill, 0) + 1
    out = pd.DataFrame([{"skill": k, "postings": v, "share": v / max(len(jobs), 1)} for k, v in counts.items()])
    return out.sort_values("postings", ascending=False) if not out.empty else out

def relevant_jobs(jobs, target):
    if target == "All roles":
        return jobs.copy()
    terms = {
        "Data Analyst": ["data analyst", "business analyst", "analytics"],
        "Machine Learning Engineer": ["machine learning", "ml engineer", "ai engineer"],
        "Data Scientist": ["data scientist", "machine learning", "research"],
        "Business Analyst": ["business analyst", "business intelligence"],
        "Python Developer": ["python developer", "backend", "software engineer"]
    }.get(target, [target.lower()])
    pattern = "|".join(re.escape(x) for x in terms)
    selected = jobs[jobs["title"].str.lower().str.contains(pattern, na=False)]
    return selected if not selected.empty else jobs.copy()

def analyze_candidate(jobs, candidate_skills, target, min_share=0.10):
    subset = relevant_jobs(jobs, target)
    if subset.empty:
        subset = jobs
    counts = {}
    for skills in subset["skills"].fillna("").apply(normalize_skills):
        for skill in set(skills):
            counts[skill] = counts.get(skill, 0) + 1
    denominator = max(len(subset), 1)
    priority = [(s, n, n / denominator) for s, n in counts.items() if n / denominator >= min_share]
    priority.sort(key=lambda x: (-x[2], x[0]))
    candidate = set(normalize_skills(candidate_skills))
    matched = [s for s, _, _ in priority if s in candidate]
    gaps = [{"skill": s, "postings": n, "demand_share": round(share * 100, 1),
             "priority": "High" if share >= .35 else "Medium"} for s, n, share in priority if s not in candidate]
    roadmap = []
    for i, gap in enumerate(gaps[:4], start=1):
        roadmap.append({"week": i, "skill": gap["skill"], "task": learning_task(gap["skill"])})
    total = len(priority)
    return {"matched_count": len(matched), "gaps": gaps, "relevant_jobs": len(subset),
            "match_ratio": len(matched) / total if total else 0.0, "roadmap": roadmap}

def learning_task(skill):
    tasks = {
        "sql": "Practice SELECT, JOIN, GROUP BY, window functions, and solve 10 business questions.",
        "python": "Write small scripts and practice functions, collections, file handling, and debugging.",
        "excel": "Practice lookups, pivot tables, conditional formatting, and cleaning a messy spreadsheet.",
        "power bi": "Build a one-page dashboard with measures, filters, and a clear business narrative.",
        "machine learning": "Train a baseline model, split data correctly, and compare evaluation metrics.",
        "pandas": "Load a CSV, handle missing values, group data, and produce a concise analysis.",
        "statistics": "Review distributions, sampling, confidence intervals, correlation, and hypothesis testing.",
        "git": "Create a repository, commit changes, branch, merge, and write a useful README.",
        "docker": "Containerize a small Python app and run it locally with a Dockerfile.",
        "generative ai": "Build a small retrieval or prompting demo and evaluate output quality and failure cases."
    }
    return tasks.get(skill, f"Learn the fundamentals of {skill}, complete a guided exercise, then add it to a small portfolio project.")
