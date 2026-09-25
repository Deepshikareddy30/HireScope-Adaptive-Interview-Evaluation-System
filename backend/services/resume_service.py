"""
HireScope Backend — services/resume_service.py
"""

import json

from ai_module.prompts import extract_resume_data_prompt

try:
    from ai_module.evaluator import _generate
except ImportError:
    _generate = None


def _empty():
    return {"skills": [], "technologies": [], "projects": [], "claims": []}


def extract_resume_data(resume_text: str) -> dict:
    if not resume_text or not resume_text.strip():
        return _empty()

    if _generate is None:
        print("[resume_service] AI generator not available")
        return _empty()

    try:
        prompt = extract_resume_data_prompt(resume_text)
        raw    = _generate(prompt)

        if not raw:
            return _empty()

        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.strip("`")
            if clean.startswith("json"):
                clean = clean[4:].strip()

        data = json.loads(clean)

        return {
            "skills":       data.get("skills", []),
            "technologies": data.get("technologies", []),
            "projects":     data.get("projects", []),
            "claims":       data.get("claims", []),
        }

    except Exception as e:
        print(f"[resume_service] Error: {e}")
        return _empty()