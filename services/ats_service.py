SKILLS_DB = {
    "python": ["python", "py"],
    "fastapi": ["fastapi", "api", "rest"],
    "machine learning": ["ml", "machine learning", "ai"],
    "data": ["data", "pandas", "numpy"],
    "sql": ["sql", "database", "db"]
}


def normalize(text: str):
    return text.lower()


def extract_skills(text: str):
    text = normalize(text)
    found = []

    for skill, keywords in SKILLS_DB.items():
        for kw in keywords:
            if kw in text:
                found.append(skill)
                break

    return list(set(found))


def analyze_resume(resume: str, job: str):

    resume_skills = extract_skills(resume)
    job_skills = extract_skills(job)

    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))

    if len(job_skills) == 0:
        score = 50
    else:
        score = int((len(matched) / len(job_skills)) * 100)

    if "project" in resume.lower():
        score += 5

    if "experience" in resume.lower():
        score += 5

    score = min(score, 100)

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing
    }