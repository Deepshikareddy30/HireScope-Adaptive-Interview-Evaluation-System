"""
HireScope Backend — services/interview_service.py
"""

import uuid

from ai_module.question_generator import (
    generate_resume_questions,
    generate_technical_questions,
    generate_hr_questions,
)
from ai_module.evaluator import evaluate_pipeline
from ai_module.probability import calculate_question_score, evaluate_interview

from backend.database import get_session, set_session
from backend.services.resume_service import extract_resume_data


MAX_FOLLOWUPS_PER_QUESTION = 1
ROUNDS_ORDER = ["resume", "technical", "hr"]


def _new_session(role: str, level: str, questions: dict) -> dict:
    return {
        "session_id": str(uuid.uuid4()),
        "role": role,
        "level": level,
        "current_round": "resume",
        "question_index": 0,
        "followup_count": 0,
        "questions": questions,
        "scores": {"resume": [], "technical": [], "hr": []},
        "current_question": None,
    }


# ── CREATE SESSION ─────────────────────────────────────

def create_interview_session(role: str, level: str, round: str, resume_text: str) -> dict:
    try:
        resume_data  = extract_resume_data(resume_text) if resume_text else {}
        resume_qs    = generate_resume_questions(resume_data or {"role": role})
        technical_qs = generate_technical_questions(role, resume_data.get("skills", [role]))
        hr_qs        = generate_hr_questions()

        questions = {"resume": resume_qs, "technical": technical_qs, "hr": hr_qs}
        session   = _new_session(role, level, questions)
        first_q   = resume_qs[0] if resume_qs else f"Tell me about yourself as a {role}."

        session["current_question"] = first_q
        set_session(session["session_id"], session)

        return {"session_id": session["session_id"], "question": first_q}

    except Exception as e:
        print(f"[create_interview_session] Error: {e}")
        sid     = str(uuid.uuid4())
        first_q = f"Tell me about yourself as a {role}."
        session = _new_session(role, level, {
            "resume":    [first_q],
            "technical": ["Explain a challenging technical problem you solved."],
            "hr":        ["Tell me about a time something didn't go as planned."],
        })
        session["session_id"]       = sid
        session["current_question"] = first_q
        set_session(sid, session)
        return {"session_id": sid, "question": first_q}


# ── PROCESS ANSWER ─────────────────────────────────────

def process_answer(session_id: str, answer: str, question_index: int,
                   followup_count: int, current_round: str, role: str) -> dict:
    try:
        session = get_session(session_id)
    except Exception:
        return {"error": "Session not found"}

    question  = session.get("current_question", "")
    round_key = current_round

    # Evaluate
    try:
        eval_result = evaluate_pipeline(question, answer)
    except Exception as e:
        print(f"[evaluate_pipeline] Error: {e}")
        eval_result = {}

    evaluation = eval_result.get("evaluation", {})
    followup_q = eval_result.get("followup_question")
    claim_data = eval_result.get("claim_validation")

    try:
        score = calculate_question_score(evaluation, claim_data)
    except Exception:
        score = 0

    if round_key in session["scores"]:
        session["scores"][round_key].append(score)

    questions = session["questions"].get(round_key, [])

    # ── FOLLOW-UP
    if followup_q and followup_count < MAX_FOLLOWUPS_PER_QUESTION:
        session["followup_count"] += 1
        set_session(session_id, session)
        return {"response": followup_q, "is_followup": True}

    # ── NEXT QUESTION in same round
    next_index = question_index + 1
    if next_index < len(questions):
        next_q = questions[next_index]
        session["question_index"]   = next_index
        session["followup_count"]   = 0
        session["current_question"] = next_q
        set_session(session_id, session)
        return {"response": next_q, "is_followup": False}

    # ── NEXT ROUND — return first question directly (no "Moving to X" message)
    next_round = _next_round(round_key)
    if next_round:
        next_q = session["questions"][next_round][0]
        session["current_round"]    = next_round
        session["question_index"]   = 0
        session["followup_count"]   = 0
        session["current_question"] = next_q
        set_session(session_id, session)
        return {"response": next_q, "is_followup": False, "next_round": next_round}

    # ── ALL DONE
    return {"response": "Interview complete.", "is_followup": False, "all_done": True}


# ── RESULT ─────────────────────────────────────────────

def get_interview_result(session_id: str) -> dict:
    try:
        session = get_session(session_id)
    except Exception:
        return {"error": "Session not found"}

    scores = session.get("scores", {})
    try:
        return evaluate_interview(
            resume_scores=scores.get("resume", []),
            tech_scores=scores.get("technical", []),
            hr_scores=scores.get("hr", []),
        )
    except Exception as e:
        print(f"[get_interview_result] Error: {e}")
        return {"error": "Result calculation failed"}


def _next_round(current: str):
    if current not in ROUNDS_ORDER:
        return None
    idx = ROUNDS_ORDER.index(current)
    return ROUNDS_ORDER[idx + 1] if idx < len(ROUNDS_ORDER) - 1 else None