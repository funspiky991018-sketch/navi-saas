import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NAVI SaaS API")

# =========================
# CORS (ALLOW FRONTEND)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# FLAGS
# =========================
OPENAI_OK = False
client = None

# =========================
# LOAD OPENAI SAFELY
# =========================
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        client = OpenAI(api_key=api_key)
        OPENAI_OK = True
    else:
        print("❌ OPENAI_API_KEY not found")

except Exception as e:
    print("❌ OpenAI load error:", e)

# =========================
# ROOT ENDPOINT
# =========================
@app.get("/")
def home():
    return {
        "status": "NAVI running",
        "model": False,
        "openai": OPENAI_OK
    }

# =========================
# DEBUG ENV (IMPORTANT)
# =========================
@app.get("/debug-env")
def debug_env():
    return {
        "has_key": os.getenv("OPENAI_API_KEY") is not None,
        "key_preview": str(os.getenv("OPENAI_API_KEY"))[:10] if os.getenv("OPENAI_API_KEY") else None
    }

# =========================
# ANALYZE (LIGHTWEIGHT)
# =========================
@app.post("/analyze")
def analyze(data: dict):
    resume = data.get("resume", "")
    job = data.get("job", "")

    keywords = ["python", "fastapi", "machine learning", "api", "data"]

    missing = [k for k in keywords if k not in resume.lower()]

    score = 70 - (len(missing) * 5)

    return {
        "score": max(score, 30),
        "missing_skills": missing
    }

# =========================
# FIX RESUME
# =========================
@app.post("/fix-resume")
def fix_resume(data: dict):
    resume = data.get("resume", "")
    lines = [l.strip() for l in resume.split("\n") if l.strip()]

    improved = []

    # -------- OpenAI MODE --------
    if OPENAI_OK:
        try:
            prompt = f"""
Improve these resume bullet points with impact and measurable results:

{lines}

Return as JSON list:
[{{"improved": "..."}}, ...]
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            import json
            data_out = json.loads(response.choices[0].message.content)

            for i, line in enumerate(lines):
                improved.append({
                    "original": line,
                    "improved": data_out[i]["improved"] if i < len(data_out) else line
                })

        except Exception as e:
            print("OpenAI error:", e)

    # -------- FALLBACK MODE --------
    if not improved:
        for line in lines:
            improved.append({
                "original": line,
                "improved": line + " (improved with impact + clarity)"
            })

    return {
        "openai_used": OPENAI_OK,
        "improved": improved
    }