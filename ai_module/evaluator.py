from groq import Groq
from ai_module.prompts import (
    evaluation_prompt,
    followup_prompt,
    claim_validation_prompt
)

import json

import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# 🧠 Common LLM call
def _generate(prompt):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("LLM Error:", e)
        return None


# 🔥 1️⃣ Evaluate Answer
def evaluate_answer(question, answer):
    prompt = evaluation_prompt(question, answer)
    raw = _generate(prompt)

    if raw is None:
        return None

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("Evaluation JSON Error:", raw)
        return None


# 🔍 2️⃣ Claim Validation
def validate_claim(claim, question, answer):
    prompt = claim_validation_prompt(claim, question, answer)
    raw = _generate(prompt)

    if raw is None:
        return None

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("Claim JSON Error:", raw)
        return None


# 🔁 3️⃣ Generate Follow-up Question
def generate_followup(question, answer, focus, justification):
    prompt = followup_prompt(question, answer, focus, justification)
    return _generate(prompt)


# 🧠 4️⃣ Decide Focus Area (core logic)
def get_focus(eval_data):
    if not eval_data:
        return "none"

    clarity = eval_data.get("clarity", 4)
    correctness = eval_data.get("correctness", 4)
    depth = eval_data.get("depth", 4)

    # Priority: correctness > depth > clarity
    if correctness <= 2:
        return "correctness"
    elif depth <= 2:
        return "depth"
    elif clarity <= 2:
        return "clarity"
    else:
        return "none"


# 💣 5️⃣ Full Evaluation Pipeline (VERY IMPORTANT)
def evaluate_pipeline(question, answer, claim=None):
    """
    This is the MAIN function backend will call.
    """

    # Step 1: Evaluate answer
    eval_data = evaluate_answer(question, answer)

    if not eval_data:
        return {"error": "Evaluation failed"}

    # Step 2: Get focus
    focus = get_focus(eval_data)

    # Step 3: Claim validation (only if claim exists)
    claim_data = None
    if claim:
        claim_data = validate_claim(claim, question, answer)

    # Step 4: Decide follow-up
    followup_question = None
    if focus != "none":
        followup_question = generate_followup(
            question,
            answer,
            focus,
            eval_data.get("justification", "")
        )

    return {
        "evaluation": eval_data,
        "focus": focus,
        "claim_validation": claim_data,
        "followup_question": followup_question
    }