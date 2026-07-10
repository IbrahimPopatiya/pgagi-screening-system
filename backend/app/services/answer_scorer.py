import json
import google.generativeai as genai
from app.core.config import settings
from app.models.schemas import AnswerScore

genai.configure(api_key=settings.gemini_api_key)

SCORING_PROMPT = """You are grading a candidate's answer in a technical interview.

Question: {question}
Candidate's answer: {answer}

Score the answer from 1 to 5 on correctness and depth (1 = incorrect/empty, 5 = thorough and accurate).
Return ONLY valid JSON, no markdown, matching exactly:
{{
  "score": 1 | 2 | 3 | 4 | 5,
  "justification": "one sentence explaining the score"
}}
"""


def score_answer(question_text: str, answer_text: str) -> AnswerScore:
    model = genai.GenerativeModel(settings.gemini_model)
    prompt = SCORING_PROMPT.format(question=question_text, answer=answer_text)

    response = model.generate_content(prompt)
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json\n", "", 1) if raw.startswith("json\n") else raw

    data = json.loads(raw)
    return AnswerScore(**data)
