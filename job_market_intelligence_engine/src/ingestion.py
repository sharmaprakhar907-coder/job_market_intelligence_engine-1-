import re
from .engine import SKILL_LIBRARY, normalize_skills

def parse_resume_text(text):
    """Simple dictionary-based skill extraction from plain text; not an ATS parser."""
    normalized = re.sub(r"\s+", " ", str(text).lower())
    found = []
    for skill in SKILL_LIBRARY:
        term = skill.strip()
        if term and re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", normalized):
            found.append(term)
    return normalize_skills(found)
