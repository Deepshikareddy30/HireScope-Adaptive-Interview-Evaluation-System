"""
HireScope Backend — routes/resume.py
"""

import base64
from fastapi import APIRouter
from pydantic import BaseModel

from backend.utils.pdf_parser import extract_text_from_pdf

router = APIRouter()


class ExtractRequest(BaseModel):
    pdf_base64: str


@router.post("/extract")
def extract_resume(body: ExtractRequest):
    try:
        pdf_bytes = base64.b64decode(body.pdf_base64)
        text = extract_text_from_pdf(pdf_bytes)
        return {"text": text, "length": len(text)}
    except Exception as e:
        return {"text": "", "error": str(e)}