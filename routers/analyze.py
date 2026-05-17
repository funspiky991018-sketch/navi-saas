from fastapi import APIRouter
from pydantic import BaseModel

from services.ats_service import analyze_resume

router = APIRouter(prefix="", tags=["Analyze"])


class AnalyzeRequest(BaseModel):
    resume: str
    job: str


@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    return analyze_resume(req.resume, req.job)