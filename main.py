import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import io
import uuid
import json

# =========================
# SAFE APP INIT
# =========================
app = FastAPI(title="NAVI Resume Analyzer", version="SAFE-V1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

progress_store = {}

REQUIRED_SKILLS = [
    "Python",
    "FastAPI",
    "REST API",
    "Machine Learning",
    "Data Processing",
]

# =========================
# SAFE MODEL LOADING
# =========================
model = None
util = None
client = None

try:
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print("⚠️ Model failed to load:", e)

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print("⚠️ OpenAI failed to load:", e)

# =========================
# REQUEST MODELS
# =========================
class AnalysisRequest(BaseModel):
    resume: str
    job_descriptions: List[str]

class ResumeResult(BaseModel):
    resume_name: str
    semantic_score: float
    missing_skills: List[str]

class AnalysisResponse(BaseModel):
    results: List[ResumeResult]

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

# =========================
# SAFE SCORING FUNCTION
# =========================
def calculate_score_and_skills(resume_text: str, job_descriptions: List[str]):
    # fallback mode if model fails
    if model is None or util is None:
        missing = [skill for skill in REQUIRED_SKILLS if skill.lower() not in resume_text.lower()]
        return 50.0, missing

    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    job_embs = model.encode(job_descriptions, convert_to_tensor=True)

    similarities = util.pytorch_cos_sim(resume_emb, job_embs)[0]
    score = float(similarities.mean().item()) * 100

    missing = [skill for skill in REQUIRED_SKILLS if skill.lower() not in resume_text.lower()]

    return round(score, 2), missing

# =========================
# HEALTH CHECK (IMPORTANT)
# =========================
@app.get("/")
def root():
    return {"message": "NAVI API Running 🚀"}

# =========================
# ANALYZE ENDPOINT
# =========================
@app.post("/analyze", response_model=AnalysisResponse)
def analyze(req: AnalysisRequest):
    score, missing = calculate_score_and_skills(req.resume, req.job_descriptions)

    return AnalysisResponse(results=[
        ResumeResult(
            resume_name="Pasted Resume",
            semantic_score=score,
            missing_skills=missing
        )
    ])

# =========================
# CSV UPLOAD
# =========================
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), job_descriptions: str = ""):
    jobs = [j.strip() for j in job_descriptions.split("\n") if j.strip()]

    if not jobs:
        raise HTTPException(status_code=400, detail="Job description required")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    if "resume" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'resume' column")

    results = []
    task_id = str(uuid.uuid4())
    progress_store[task_id] = 0

    for i, row in df.iterrows():
        resume_text = str(row["resume"])
        score, missing = calculate_score_and_skills(resume_text, jobs)

        results.append({
            "resume_name": f"Resume {i+1}",
            "semantic_score": score,
            "missing_skills": ", ".join(missing)
        })

        progress_store[task_id] = int(((i + 1) / len(df)) * 100)

    progress_store[task_id] = 100

    return {"task_id": task_id, "results": results}

# =========================
# FIX RESUME (SAFE MODE)
# =========================
@app.post("/fix-resume", response_model=FixResumeResponse)
def fix_resume(req: FixResumeRequest):

    score, missing = calculate_score_and_skills(req.resume_text, [req.job_description])

    bullets = [b.strip("- ").strip() for b in req.resume_text.split("\n") if b.strip()]

    improved = []

    # -------------------------
    # IF OPENAI NOT AVAILABLE
    # -------------------------
    if client is None:
        for b in bullets:
            improved.append(
                ImprovedBullet(
                    original=b,
                    improved=b + " (improved with impact + clarity)",
                    keywords_added=[]
                )
            )

        return FixResumeResponse(
            similarity_score=score,
            missing_skills=missing,
            improved_bullets=improved
        )

    # -------------------------
    # OPENAI MODE
    # -------------------------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a resume expert. Improve bullets with impact and clarity. Return JSON only."
                },
                {
                    "role": "user",
                    "content": json.dumps({
                        "bullets": bullets,
                        "job": req.job_description,
                        "missing": missing
                    })
                }
            ],
            temperature=0.3
        )

        try:
            data = json.loads(response.choices[0].message.content)
        except:
            data = []

        for i, b in enumerate(bullets):
            improved.append(
                ImprovedBullet(
                    original=b,
                    improved=data[i]["improved"] if i < len(data) else b,
                    keywords_added=[]
                )
            )

    except Exception as e:
        print("OpenAI error:", e)

        for b in bullets:
            improved.append(
                ImprovedBullet(
                    original=b,
                    improved=b + " (safe fallback)",
                    keywords_added=[]
                )
            )

    return FixResumeResponse(
        similarity_score=score,
        missing_skills=missing,
        improved_bullets=improved
    )