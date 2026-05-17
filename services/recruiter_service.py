from typing import List
from fastapi import UploadFile
from PyPDF2 import PdfReader
from docx import Document
import io

from app.services.analysis_service import analyze_resume  # your existing function


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])


async def process_batch(job_description: str, files: List[UploadFile]):

    results = []

    for file in files:
        contents = await file.read()

        if file.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(contents)

        elif file.filename.endswith(".docx"):
            resume_text = extract_text_from_docx(contents)

        else:
            continue  # skip unsupported formats

        analysis = analyze_resume(resume_text, job_description)

        results.append({
            "filename": file.filename,
            "match_score": analysis["match_score"],
            "matched_keywords": analysis["matched_keywords"],
            "missing_keywords": analysis["missing_keywords"],
            "summary": analysis["summary"]
        })

    # Sort descending by score
    results.sort(key=lambda x: x["match_score"], reverse=True)

    # Add rank
    for index, item in enumerate(results):
        item["rank"] = index + 1

    return results
