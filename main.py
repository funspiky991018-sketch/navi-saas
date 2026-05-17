from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import analyze, auth, resume, user

app = FastAPI(
    title="NAVI SaaS V4",
    version="4.0.0"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ROUTERS
app.include_router(analyze.router)
app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(user.router)


# HOME
@app.get("/")
def home():
    return {
        "status": "NAVI SaaS V4 running",
        "architecture": "modular",
        "ai_mode": "offline"
    }


# DEBUG
@app.get("/debug")
def debug():
    return {
        "version": "4.0.0",
        "routers": [
            "analyze",
            "auth",
            "resume",
            "user"
        ]
    }