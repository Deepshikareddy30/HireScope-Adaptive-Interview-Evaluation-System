from groq import Groq
from ai_module.prompts import (
    resume_round_prompt,
    technical_round_prompt,
    hr_round_prompt
)


import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def _generate(prompt):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


#  Resume Round Questions
def generate_resume_questions(resume_data):
    """
    Input: structured resume_data (dict)
    Output: list of 3 questions
    """
    prompt = resume_round_prompt(resume_data)
    raw_output = _generate(prompt)

    return _parse_numbered_list(raw_output)


#  Technical Round Questions
def generate_technical_questions(role, skills):
    """
    Input: role (str), skills (list)
    Output: list of 3 questions
    """
    prompt = technical_round_prompt(role, skills)
    raw_output = _generate(prompt)

    return _parse_numbered_list(raw_output)


#  HR Round Questions
def generate_hr_questions():
    """
    Output: list of 2 questions
    """
    prompt = hr_round_prompt()
    raw_output = _generate(prompt)

    return _parse_numbered_list(raw_output)



def _parse_numbered_list(text):
    """
    Converts:
    '1. Question\n2. Question\n3. Question'
    → ['Question', 'Question', 'Question']
    """
    lines = text.split("\n")
    questions = []

    for line in lines:
        line = line.strip()

        if line and (line[0].isdigit()):
            # Remove "1. " or "2. "
            question = line.split(".", 1)[-1].strip()
            questions.append(question)

    return questions