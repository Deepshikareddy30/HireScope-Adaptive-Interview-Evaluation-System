def extract_resume_data_prompt(resume_text):
    return f"""
You are an expert resume analyzer.

Your task is to extract structured information from the resume.

Follow these rules STRICTLY:

1. Skills:
- Only include actual skills (e.g., Java, Python, Problem Solving)
- Do NOT include tools here

2. Technologies:
- Include frameworks, tools, libraries (e.g., React, Node.js, Django)

3. Projects:
- Extract project names or short descriptions

4. Claims:
- Extract strong action statements where the candidate claims work
  (e.g., "built a web app", "developed a REST API")

IMPORTANT:
- Do NOT hallucinate
- Do NOT add anything not present in resume
- Keep items short and precise
- Avoid duplicates
- If any category is missing, return an empty list.
-Only include strong action-based claims (built, developed, implemented). 
-Do NOT include generic statements like "know" or "familiar with".

Return ONLY valid JSON in this format:
{{
 "skills": [],
 "technologies": [],
 "projects": [],
 "claims": []
}}

Resume:
{resume_text}
"""

def resume_round_prompt(resume_data):
    return f"""
You are an experienced technical interviewer conducting a real interview.

Your goal is to verify whether the candidate truly understands and has actually worked on the things mentioned in their resume.

Generate exactly 3 interview questions.

Behavior guidelines:
- Ask questions like a real human interviewer
- Focus on the candidate's projects and claims
- Ask about implementation details, decisions, and challenges
- Use a conversational tone (not robotic)
- Questions should feel slightly probing, as if you are testing authenticity
- Avoid generic or textbook questions


Question style examples:
- "Can you walk me through how you built this?"
- "Why did you choose this approach?"
- "What challenges did you face and how did you handle them?"

IMPORTANT:
- Do NOT ask theory-based questions like "What is React?"
- Do NOT repeat questions
- Keep each question clear and natural
-Keep questions concise and natural. Avoid overly long sentences.

Return ONLY a numbered list of questions.

Resume Data:
{resume_data}
"""

def technical_round_prompt(role, skills):
    return f"""
You are a real technical interviewer conducting an interview for a {role} position.

You're speaking directly to the candidate. Ask 3 technical questions.

Your goal is to understand how well they actually know their subject, not just what they have memorized.

How you should behave:
- Ask questions in a natural, conversational tone
- Focus on how they think and solve problems
- Push them slightly to explain their reasoning
- Mix direct and scenario-based questions
-Vary the tone slightly between questions.

Avoid:
- Basic definition questions like "What is Java?"
- Overly long or complicated wording

Instead, ask things like:
- "How would you approach this in a real project?"
- "What would you do if this system started failing?"
- "Can you walk me through your thinking here?"

Difficulty:
- Vary the difficulty naturally across questions

IMPORTANT:
- Do NOT label or mention difficulty in the output

IMPORTANT:
- Do NOT repeat resume-based questions
- Do NOT ask generic textbook questions

Keep each question clear, realistic, and something an interviewer would genuinely ask.

Return ONLY a numbered list.

Skills to consider:
{skills}
"""

def hr_round_prompt():
    return """
You are a professional interviewer conducting the HR round.

Speak directly to the candidate and ask exactly 2 questions.

Your goal is to understand how the candidate thinks, communicates, and handles real situations.

How you should behave:
- Sound natural and conversational
- Ask open-ended questions
- Encourage the candidate to explain their thinking
- Keep questions clear and realistic

Question requirements:
- At least ONE question must be scenario-based (give a situation and ask what they would do)
- The other question can be experience-based or reflective

Avoid:
- Overused or cliché questions
- Questions like "What are your strengths/weaknesses?"
- Yes/No questions
- Long or complicated wording

Examples of good style:
- "Imagine your team is close to a deadline and something critical breaks — how would you handle it?"
- "Can you tell me about a time when something didn’t go as planned and what you learned from it?"

IMPORTANT:
- Do NOT explain anything
- Do NOT add extra text

Output format:
1. Question
2. Question
"""

def evaluation_prompt(question, answer):
    return f"""
You are a strict technical interviewer evaluating a candidate’s answer.

Evaluate the answer using the criteria below.

Clarity (structure & communication):
1 - very unclear or confusing
2 - somewhat unclear or poorly structured
3 - clear and understandable
4 - very clear, structured, and easy to follow

Correctness (technical accuracy):
1 - incorrect or misleading
2 - partially correct with mistakes
3 - mostly correct with minor gaps
4 - fully correct and accurate

Depth (understanding & explanation):
1 - very shallow or vague
2 - basic understanding without detail
3 - good explanation with some reasoning
4 - deep understanding with clear reasoning or examples

Evaluation rules:
- Be strict and realistic (do not overrate)
- Do NOT assume knowledge not shown
- Penalize vague or generic answers
- Reward specific, structured, and well-explained answers

IMPORTANT:
- Use only the scale 1–4
- Do NOT skip any field
- Keep justification concise (1–2 lines)
- Justification MUST clearly mention:
  • what is good
  • what is missing or weak
- Return ONLY valid JSON (no extra text)

Output format:
{{
 "clarity": 1-4,
 "correctness": 1-4,
 "depth": 1-4,
 "justification": "mention strength + weakness clearly"
}}

Question:
{question}

Answer:
{answer}
"""

def followup_prompt(question, answer, focus, evaluation):
    return f"""
You are a technical interviewer continuing an interview.

The candidate gave the following answer, and it has a weakness in: {focus}.

Evaluation summary:
{evaluation}

Your goal is to ask ONE follow-up question that directly targets what is missing or weak.

Guidelines:
- If correctness is weak → ask them to correct or justify their understanding
- If depth is weak → ask for detailed explanation or example
- If clarity is weak → ask them to explain more clearly step-by-step

Make the question SPECIFIC to the candidate’s answer and the issue identified.
Do NOT ask generic follow-up questions.

Behavior:
- Be natural and conversational
- Do NOT repeat the same question
- Do NOT give hints or answers
- Keep it short and focused

Previous Question:
{question}

Candidate Answer:
{answer}
"""

def claim_validation_prompt(claim, question, answer):
    return f"""
You are a strict interviewer verifying whether the candidate truly understands their resume claim.

Claim made by candidate:
{claim}

Question asked:
{question}

Candidate answer:
{answer}

Step 1: Determine if the question is actually related to the claim.

- If NOT related:
  → Return "not_applicable"
  → Do NOT evaluate the claim

- If related:
  → Evaluate whether the answer proves the claim

Step 2: If related, classify:

VALID:
- Answer clearly demonstrates real understanding of the claim
- Includes correct explanation, reasoning, or example

WEAK:
- Partial understanding but lacks depth or clarity

BLUFF:
- Vague, incorrect, or does not support the claim

Rules:
- Do NOT assume knowledge not shown
- Require evidence (steps, reasoning, or example)
- Be strict — do not mark "valid" without strong proof

IMPORTANT:
- Keep reason short and specific (1 line)
- Return ONLY valid JSON (no extra text)

Output format:
{{
 "claim_status": "valid | weak | bluff | not_applicable",
 "confidence": "high | medium | low",
 "reason": "short explanation"
}}
"""