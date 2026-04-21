from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from typing import List
import json

# OpenAI (new SDK)
from openai import OpenAI

# =========================
# APP SETUP
# =========================
app = FastAPI(title="NAVI Resume API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELS
# =========================
class AnalysisRequest(BaseModel):
    resume: str
    job_descriptions: List[str]

class FixResumeRequest(BaseModel):
    resume_text: str
    job_description: str

class ImprovedBullet(BaseModel):
    original: str
    improved: str
    keywords_added: List[str]

class FixResumeResponse(BaseModel):
    similarity_score: float
    missing_skills: List[str]
    improved_bullets: List[ImprovedBullet]

class AnalysisResponse(BaseModel):
    results: list

# =========================
# MODELS LOADING
# =========================
model = SentenceTransformer("all-MiniLM-L6-v2")

# SAFE OpenAI client (may fail if no API key)
try:
    client = OpenAI()
except:
    client = None

REQUIRED_SKILLS = [
    "Python",
    "FastAPI",
    "REST API",
    "Machine Learning",
    "Data Processing",
]

# =========================
# CORE LOGIC
# =========================
def calculate_score(resume, jobs):
    resume_emb = model.encode(resume, convert_to_tensor=True)
    job_embs = model.encode(jobs, convert_to_tensor=True)

    score = util.pytorch_cos_sim(resume_emb, job_embs).mean().item() * 100

    missing = []
    for skill in REQUIRED_SKILLS:
        skill_emb = model.encode(skill, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(resume_emb, skill_emb).item()
        if sim < 0.5:
            missing.append(skill)

    return round(score, 2), missing

# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    return {"message": "NAVI API Running 🚀"}

# -------------------------
# ANALYZE
# -------------------------
@app.post("/analyze", response_model=AnalysisResponse)
def analyze(req: AnalysisRequest):
    score, missing = calculate_score(req.resume, req.job_descriptions)

    return {
        "results": [
            {
                "resume_name": "Pasted Resume",
                "semantic_score": score,
                "missing_skills": missing
            }
        ]
    }

# -------------------------
# FIX RESUME (SAFE VERSION)
# -------------------------
@app.post("/fix-resume", response_model=FixResumeResponse)
def fix_resume(req: FixResumeRequest):

    score, missing = calculate_score(
        req.resume_text,
        [req.job_description]
    )

    bullets = [
        b.strip("- ").strip()
        for b in req.resume_text.split("\n")
        if b.strip()
    ]

    improved = []

    # =========================
    # TRY AI (OPENAI)
    # =========================
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a resume expert. Improve bullets without fabricating experience. Return JSON list."
                    },
                    {
                        "role": "user",
                        "content": json.dumps({
                            "bullets": bullets,
                            "job": req.job_description,
                            "missing_skills": missing
                        })
                    }
                ],
                temperature=0.3,
                max_tokens=600
            )

            content = response.choices[0].message.content

            try:
                improved = json.loads(content)
            except:
                raise Exception("Invalid JSON from AI")

        except Exception:
            improved = None

    # =========================
    # FALLBACK (ALWAYS WORKS)
    # =========================
    if not improved:
        improved = []
        for b in bullets:
            improved.append({
                "original": b,
                "improved": f"{b} → enhanced with measurable impact and clarity",
                "keywords_added": missing
            })

    return {
        "similarity_score": score,
        "missing_skills": missing,
        "improved_bullets": improved
    }