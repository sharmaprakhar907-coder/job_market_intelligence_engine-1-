# Job Market Intelligence & Skill Gap Engine

A deployable Streamlit portfolio project that summarizes skill demand from job-posting data and compares it with a candidate's current skills.

## Features
- Job-market dashboard: postings, locations, role titles, and most requested skills.
- Candidate skill-gap analysis by target role.
- Demand-based skill priorities and a 30-day starter roadmap.
- Plain-text resume skill detection (dictionary-based baseline).
- CSV upload and CSV report export.
- Docker deployment support.

## Tech stack
Python, Pandas, Streamlit, rule-based text processing, CSV data.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Deploy on Streamlit Community Cloud
1. Push this project to a GitHub repository.
2. Open https://share.streamlit.io/ and sign in.
3. Create app, select repository, branch, and `app.py`.
4. Deploy. No secrets are required for the included demo.

## Deploy with Docker
```bash
docker build -t job-skill-engine .
docker run --rm -p 8501:8501 job-skill-engine
```

## Dataset format
Required columns: `title, company, location, description, skills`.
Optional columns: `experience, salary_min, salary_max`.
`skills` should be a comma-separated list. See `data/jobs.csv`.

## Important data note
The included data is synthetic and only demonstrates the workflow. Do not describe its charts as live labor-market statistics. For a real deployment, ingest job postings from a permitted API, licensed dataset, or employer-approved source; store the source URL and collection date; deduplicate postings; and refresh regularly. Respect each source's terms and privacy requirements.

## Method and limitations
1. Normalize skill names using a small alias dictionary.
2. Count each skill at most once per posting.
3. Filter postings by target-role title keywords.
4. Calculate demand share = postings mentioning skill / relevant postings.
5. Flag skills meeting the user's minimum demand-share threshold.
6. Compare the priority list against candidate skills.
7. Sort missing skills by observed demand and create a simple learning plan.

This is an explainable baseline, not a predictive hiring model. It does not estimate employability, infer proficiency, or guarantee job outcomes. Resume extraction is keyword matching and can miss synonyms or context.
