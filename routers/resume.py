from fastapi import APIRouter
from pydantic import BaseModel

from services.resume_service import improve_resume_lines

router = APIRouter(prefix="", tags=["Resume"])


class ResumeFixRequest(BaseModel):
    resume: str


@router.post("/fix-resume")
def fix_resume(req: ResumeFixRequest):
    return improve_resume_lines(req.resume)