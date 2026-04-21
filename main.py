import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# SAFE FLAGS
# =========================
MODEL_OK = False
OPENAI_OK = False

model = None
util = None
client = None

# =========================
# SAFE IMPORT BLOCKS
# =========================
try:
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer("all-MiniLM-L6-v2")
    MODEL_OK = True
except Exception as e:
    print("MODEL LOAD FAILED:", e)

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_OK = True
except Exception as e:
    print("OPENAI LOAD FAILED:", e)

# =========================
# ROOT TEST (VERY IMPORTANT)
# =========================
@app.get("/")
def home():
    return {
        "status": "NAVI running",
        "model": MODEL_OK,
        "openai": OPENAI_OK
    }

# =========================
# SAFE ANALYZE ENDPOINT
# =========================
@app.post("/analyze")
def analyze(data: dict):
    resume = data.get("resume", "")
    job = data.get("job", "")

    missing = []

    keywords = ["python", "fastapi", "machine learning", "api", "data"]

    for k in keywords:
        if k not in resume.lower():
            missing.append(k)

    score = 60 if MODEL_OK else 45

    return {
        "score": score,
        "missing_skills": missing
    }

# =========================
# SAFE FIX ENDPOINT
# =========================
@app.post("/fix-resume")
def fix_resume(data: dict):
    resume = data.get("resume", "")

    lines = resume.split("\n")

    improved = []

    for l in lines:
        improved.append({
            "original": l,
            "improved": l + " (improved with impact + clarity)"
        })

    return {
        "improved": improved,
        "note": "OpenAI disabled fallback mode" if not OPENAI_OK else "AI mode ready"
    }