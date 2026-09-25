from ai_module.probability import evaluate_interview

resume_scores = [8, 7, 6]
tech_scores = [9, 6, 7]
hr_scores = [10, 9]

result = evaluate_interview(resume_scores, tech_scores, hr_scores)

print(result)