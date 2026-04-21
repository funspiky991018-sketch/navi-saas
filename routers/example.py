from fastapi import APIRouter
from pydantic import BaseModel
from services.analysis_service import clean_text, generate_suggestions

router = APIRouter()

# Request model for /example/analyze
class AnalysisRequest(BaseModel):
    resume: str
    job_description: str

@router.post("/analyze")
def analyze(data: AnalysisRequest):
    # Clean and normalize text
    resume_words = clean_text(data.resume)
    job_words = clean_text(data.job_description)

    # Compute matches and missing keywords
    matched = resume_words.intersection(job_words)
    missing = job_words - resume_words

    match_score = round((len(matched) / len(job_words)) * 100, 2) if job_words else 0

    # Generate improvement suggestions
    suggestions = generate_suggestions(missing)

    # Optional summary for quick display
    summary = "Focus on improving: " + ", ".join(list(missing)[:3]) if missing else "Good match!"

    # Return structured response
    return {
        "match_score": match_score,
        "matched_keywords": sorted(list(matched)),
        "missing_keywords": sorted(list(missing))[:15],
        "suggestions": suggestions,
        "summary": summary
    }

