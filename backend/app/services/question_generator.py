import json
import google.generativeai as genai
from app.core.config import settings
from app.models.schemas import GeneratedQuestion, ResumeProfile

genai.configure(api_key=settings.gemini_api_key)

QUESTION_PROMPT = """You are a technical interviewer for a {role} position.

Below is a passage from the role's reference textbook, and a summary of the candidate's background.
Generate ONE interview question that:
- Requires APPLYING the concept in the passage, not just recalling its definition
- Is meaningfully connected to the candidate's specific listed skills/experience where possible
- Is NOT a generic or template question — it must clearly depend on the passage content below

Return ONLY valid JSON, no markdown, matching exactly:
{{
  "question_text": "...",
  "rationale": "one sentence: why this question, referencing the passage and the candidate's background",
  "difficulty": "easy" | "medium" | "hard"
}}

Textbook passage (source: page {page}):
---
{passage}
---

Candidate background:
- Skills: {skills}
- Technologies: {technologies}
- Experience level: {experience_level}
"""


def generate_question(role: str, chunk: dict, resume: ResumeProfile) -> GeneratedQuestion:
    model = genai.GenerativeModel(settings.gemini_model)
    prompt = QUESTION_PROMPT.format(
        role=role.replace("_", " "),
        page=chunk["page"],
        passage=chunk["text"],
        skills=", ".join(resume.skills[:8]),
        technologies=", ".join(resume.technologies[:8]),
        experience_level=resume.experience_level,
    )

    response = model.generate_content(prompt)
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json\n", "", 1) if raw.startswith("json\n") else raw

    data = json.loads(raw)
    return GeneratedQuestion(**data)
