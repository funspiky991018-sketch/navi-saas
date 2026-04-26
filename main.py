import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

# OpenAI (new SDK style)
from openai import OpenAI

app = FastAPI(title="NAVI SaaS API", version="1.0.0")

# ----------------------------
# OpenAI INIT (SAFE)
# ----------------------------
client = None
openai_ready = False

try:
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        client = OpenAI(api_key=api_key)
        openai_ready = True
        print("✅ OpenAI connected")
    else:
        print("❌ No OpenAI key found")

except Exception as e:
    print("❌ OpenAI init failed:", str(e))


# ----------------------------
# REQUEST MODELS
# ----------------------------
class AnalyzeRequest(BaseModel):
    resume: str
    job: str


class FixRequest(BaseModel):
    resume: str


# ----------------------------
# HOME
# ----------------------------
@app.get("/")
def home():
    return {
        "status": "NAVI running",
        "model": openai_ready,
        "openai": openai_ready
    }


# ----------------------------
# ANALYZE RESUME
# ----------------------------
@app.post("/analyze")
def analyze(req: AnalyzeRequest):

    resume = req.resume.lower()
    job = req.job.lower()

    keywords = [
        "python", "fastapi", "machine learning",
        "data", "api", "rest"
    ]

    matched = []
    missing = []

    for k in keywords:
        if k in resume and k in job:
            matched.append(k)
        elif k in job:
            missing.append(k)

    score = int((len(matched) / len(keywords)) * 100)

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing
    }


# ----------------------------
# FIX RESUME (AI POWERED)
# ----------------------------
@app.post("/fix-resume")
def fix_resume(req: FixRequest):

    lines = req.resume.split("\n")

    # If OpenAI is NOT ready → fallback safe mode
    if not openai_ready:
        return {
            "openai_used": False,
            "improved": [
                {
                    "original": line,
                    "improved": line + " (improved with impact + clarity)"
                }
                for line in lines
            ]
        }

    try:
        prompt = f"""
You are a professional resume writer.

Rewrite each bullet point to:
- be strong and professional
- use action verbs
- add measurable impact where possible
- avoid repetition

Return ONLY JSON like:
[
  {{"improved": "text"}}
]

Resume:
{req.resume}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        content = response.choices[0].message.content

        # Try safe parsing
        import json

        try:
            improved = json.loads(content)
        except:
            improved = [
                {"original": line, "improved": line}
                for line in lines
            ]

        return {
            "openai_used": True,
            "improved": improved
        }

    except Exception as e:
        return {
            "openai_used": False,
            "error": str(e),
            "improved": [
                {
                    "original": line,
                    "improved": line
                }
                for line in lines
            ]
        }


# ----------------------------
# DEBUG ENV (OPTIONAL)
# ----------------------------
@app.get("/debug-env")
def debug_env():
    return {
        "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "openai_ready": openai_ready
    }