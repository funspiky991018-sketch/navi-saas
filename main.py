from fastapi import FastAPI
from pydantic import BaseModel
import re
import os

app = FastAPI(title="NAVI SaaS V5 - Offline AI Engine", version="5.0.0")

# ----------------------------
# MODELS
# ----------------------------
class AnalyzeRequest(BaseModel):
    resume: str
    job: str


class FixRequest(BaseModel):
    resume: str


# ----------------------------
# SKILLS DB
# ----------------------------
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


# ----------------------------
# HOME
# ----------------------------
@app.get("/")
def home():
    return {
        "status": "NAVI V5 running (Offline AI)",
        "ai_mode": "offline",
        "openai": False
    }


# ----------------------------
# ANALYZE
# ----------------------------
@app.post("/analyze")
def analyze(req: AnalyzeRequest):

    resume_skills = extract_skills(req.resume)
    job_skills = extract_skills(req.job)

    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))

    if len(job_skills) == 0:
        score = 50
    else:
        score = int((len(matched) / len(job_skills)) * 100)

    if "project" in req.resume.lower():
        score += 5
    if "experience" in req.resume.lower():
        score += 5

    score = min(score, 100)

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing
    }


# ----------------------------
# FIX RESUME
# ----------------------------
@app.post("/fix-resume")
def fix_resume(req: FixRequest):

    lines = [l.strip() for l in req.resume.split("\n") if l.strip()]
    improved = []

    for line in lines:
        improved_line = improve_line(line)
        improved.append({
            "original": line,
            "improved": improved_line
        })

    return {
        "ai_mode": "offline",
        "improved": improved
    }


def improve_line(line: str):

    text = line.strip()

    if not re.match(r"^(built|developed|created|designed|implemented|led|managed|optimized)", text.lower()):
        text = "Developed " + text

    replacements = {
        "worked on": "contributed to",
        "helped": "assisted in improving",
        "made": "developed",
        "did": "executed"
    }

    for k, v in replacements.items():
        text = re.sub(k, v, text, flags=re.IGNORECASE)

    if not re.search(r"\d+%", text):
        text += " with improved efficiency and performance"

    if "api" in text.lower():
        text += " using RESTful API architecture"
    if "data" in text.lower():
        text += " handling structured datasets"

    return text


# ----------------------------
# DEBUG
# ----------------------------
@app.get("/debug")
def debug():
    return {
        "mode": "offline-ai-v5",
        "skills_db": list(SKILLS_DB.keys())
    }


# ----------------------------
# RENDER SAFE START
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)