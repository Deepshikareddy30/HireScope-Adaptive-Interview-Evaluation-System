"""
HireScope Backend — routes/interview.py
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.interview_service import (
    create_interview_session,
    process_answer,
    get_interview_result,
)

router = APIRouter()


class StartRequest(BaseModel):
    role: str
    level: str = "mid"
    round: str = "resume"
    resume_text: Optional[str] = None


class AnswerRequest(BaseModel):
    session_id: str
    answer: str
    question_index: int = 0
    followup_count: int = 0
    round: str = "resume"
    role: str = ""


@router.post("/start")
def start_interview(body: StartRequest):
    try:
        return create_interview_session(
            role=body.role,
            level=body.level,
            round=body.round,
            resume_text=body.resume_text or "",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer")
def answer_question(body: AnswerRequest):
    try:
        result = process_answer(
            session_id=body.session_id,
            answer=body.answer,
            question_index=body.question_index,
            followup_count=body.followup_count,
            current_round=body.round,
            role=body.role,
        )
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{session_id}")
def interview_result(session_id: str):
    try:
        result = get_interview_result(session_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))