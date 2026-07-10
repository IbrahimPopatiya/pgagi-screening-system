import json
import io
import google.generativeai as genai
from pypdf import PdfReader
from app.core.config import settings
from app.models.schemas import ResumeProfile

genai.configure(api_key=settings.gemini_api_key)

EXTRACTION_PROMPT = """You are extracting structured information from a candidate's resume.

Return ONLY valid JSON, no markdown formatting, no commentary, matching exactly this shape:
{{
  "skills": ["skill1", "skill2", ...],
  "technologies": ["tech1", "tech2", ...],
  "domains": ["domain1", "domain2", ...],
  "experience_level": "entry" | "mid" | "senior"
}}

Resume text:
---
{resume_text}
---
"""


def extract_text_from_resume(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_resume(resume_text: str) -> ResumeProfile:
    model = genai.GenerativeModel(settings.gemini_model)
    prompt = EXTRACTION_PROMPT.format(resume_text=resume_text)

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Gemini sometimes wraps JSON in ```json ... ``` — strip that if present
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json\n", "", 1) if raw.startswith("json\n") else raw

    data = json.loads(raw)
    return ResumeProfile(**data)
