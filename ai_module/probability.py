# 🎯 Constants
MAX_SCORE_PER_QUESTION = 12

WEIGHTS = {
    "resume": 0.30,
    "technical": 0.50,
    "hr": 0.20
}


# 🔥 1️⃣ Score per question (with claim adjustment)
def calculate_question_score(eval_data, claim_data=None):
    """
    eval_data = {clarity, correctness, depth}
    claim_data = {claim_status, confidence}
    """

    # Base score
    score = (
        eval_data.get("clarity", 0) +
        eval_data.get("correctness", 0) +
        eval_data.get("depth", 0)
    )

    # 🔍 Claim validation adjustment
    if claim_data:
        status = claim_data.get("claim_status")
        confidence = claim_data.get("confidence", "low")

        if status == "bluff":
            score -= 2 if confidence == "high" else 1
        elif status == "weak":
            score -= 1
        # valid → no change
        # not_applicable → no change

    return max(score, 0)


# 🔥 2️⃣ Round probability
def calculate_round_probability(question_scores):
    """
    question_scores = list of scores (each out of 12)
    """
    if not question_scores:
        return 0.0

    avg_score = sum(question_scores) / len(question_scores)

    probability = (avg_score / MAX_SCORE_PER_QUESTION) * 100

    return round(probability, 2)


# 🔥 3️⃣ Overall probability (weighted)
def calculate_overall_probability(round_probs):
    """
    round_probs = {
        "resume": float,
        "technical": float,
        "hr": float
    }
    """

    total = 0.0

    for round_name, weight in WEIGHTS.items():
        total += round_probs.get(round_name, 0) * weight

    return round(total, 2)


# 🔥 4️⃣ Full pipeline (BEST FUNCTION TO USE)
def evaluate_interview(resume_scores, tech_scores, hr_scores):
    """
    Takes all scores and returns final structured result
    """

    # Round probabilities
    resume_prob = calculate_round_probability(resume_scores)
    tech_prob = calculate_round_probability(tech_scores)
    hr_prob = calculate_round_probability(hr_scores)

    # Overall probability
    overall_prob = calculate_overall_probability({
        "resume": resume_prob,
        "technical": tech_prob,
        "hr": hr_prob
    })

    return {
        "resume_probability": resume_prob,
        "technical_probability": tech_prob,
        "hr_probability": hr_prob,
        "overall_probability": overall_prob
    }