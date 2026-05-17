SKILLS = {
    "python": ["python"],
    "fastapi": ["fastapi", "api"],
    "ml": ["machine learning", "ml"],
    "data": ["data", "pandas"],
    "sql": ["sql"]
}

def extract_skills(text: str):
    text = text.lower()
    found = []

    for skill, keys in SKILLS.items():
        for k in keys:
            if k in text:
                found.append(skill)
                break

    return list(set(found))