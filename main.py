from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import io
import uuid
import os
import json

# ==============================
# SAFE IMPORTS (NO CRASH STARTUP)
# ==============================
try:
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print("SentenceTransformer failed:", e)
    model = None
    util = None

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print("OpenAI init failed:", e)
    client = None

# ==============================
# APP INIT
# ==============================
app = FastAPI(title="NAVI Resume Analyzer", version="4.0")

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

# ==============================
# MODELS
# ==============================
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

# ==============================
# SAFE SCORING FUNCTION
# ==============================
def calculate_score_and_skills(resume_text: str, job_descriptions: List[str]):
    if model is None or util is None:
        return 50.0, ["Model not loaded"]

    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    job_embs = model.encode(job_descriptions, convert_to_tensor=True)

    similarities = util.pytorch_cos_sim(resume_emb, job_embs)[0]
    semantic_score = float(similarities.mean().item()) * 100

    missing_skills = []
    for skill in REQUIRED_SKILLS:
        if skill.lower() not in resume_text.lower():
            missing_skills.append(skill)

    return round(semantic_score, 2), missing_skills

# ==============================
# ROUTES
# ==============================
@app.get("/")
def root():
    return {"message": "NAVI API Running 🚀"}

# --------------------------
# ANALYZE
# --------------------------
@app.post("/analyze", response_model=AnalysisResponse)
def analyze_resume(req: AnalysisRequest):
    score, missing = calculate_score_and_skills(
        req.resume,
        req.job_descriptions
    )

    result = ResumeResult(
        resume_name="Pasted Resume",
        semantic_score=score,
        missing_skills=missing
    )

    return AnalysisResponse(results=[result])

# --------------------------
# CSV UPLOAD
# --------------------------
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), job_descriptions: str = ""):
    job_list = [jd.strip() for jd in job_descriptions.split("\n") if jd.strip()]

    if not job_list:
        raise HTTPException(status_code=400, detail="Job description required.")

    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    if "resume" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'resume' column.")

    total = len(df)
    task_id = str(uuid.uuid4())
    progress_store[task_id] = 0

    results = []

    for index, row in df.iterrows():
        resume_text = str(row["resume"])
        score, missing = calculate_score_and_skills(resume_text, job_list)

        results.append({
            "resume_name": f"Resume {index + 1}",
            "semantic_score": score,
            "missing_skills": ", ".join(missing)
        })

        progress_store[task_id] = int(((index + 1) / total) * 100)

    progress_store[task_id] = 100

    return {
        "task_id": task_id,
        "results": results
    }

# --------------------------
# FIX RESUME (SAFE VERSION)
# --------------------------
@app.post("/fix-resume", response_model=FixResumeResponse)
def fix_resume(request: FixResumeRequest):

    resume_text = request.resume_text
    job_description = request.job_description

    score, missing_skills = calculate_score_and_skills(
        resume_text,
        [job_description]
    )

    bullets = [
        line.strip("- ").strip()
        for line in resume_text.split("\n")
        if line.strip()
    ]

    improved_bullets = []

    # ==========================
    # IF OPENAI NOT AVAILABLE → fallback
    # ==========================
    if client is None:
        for b in bullets:
            improved_bullets.append(
                ImprovedBullet(
                    original=b,
                    improved=f"{b} (improved with impact + clarity)",
                    keywords_added=[]
                )
            )

        return FixResumeResponse(
            similarity_score=score,
            missing_skills=missing_skills,
            improved_bullets=improved_bullets
        )

    # ==========================
    # OPENAI MODE (if available)
    # ==========================
    try:
        system_prompt = (
            "You are an expert resume optimizer. "
            "Rewrite bullet points with impact, clarity, and ATS optimization. "
            "Return ONLY JSON list."
        )

        user_prompt = {
            "resume_bullets": bullets,
            "job_description": job_description,
            "missing_skills": missing_skills
        }

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(user_prompt)}
            ],
            temperature=0.3,
            max_tokens=800
        )

        try:
            improved_bullets_json = json.loads(
                response.choices[0].message.content
            )
        except:
            improved_bullets_json = []

        for i, b in enumerate(bullets):
            improved_bullets.append(
                ImprovedBullet(
                    original=b,
                    improved=improved_bullets_json[i]["improved"]
                    if i < len(improved_bullets_json)
                    else b,
                    keywords_added=[]
                )
            )

    except Exception as e:
        print("OpenAI error:", e)

        for b in bullets:
            improved_bullets.append(
                ImprovedBullet(
                    original=b,
                    improved=f"{b} (safe fallback improvement)",
                    keywords_added=[]
                )
            )

    return FixResumeResponse(
        similarity_score=score,
        missing_skills=missing_skills,
        improved_bullets=improved_bullets
    )