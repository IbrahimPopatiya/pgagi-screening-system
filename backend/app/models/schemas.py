from pydantic import BaseModel
from typing import Literal


class ResumeProfile(BaseModel):
    skills: list[str]
    technologies: list[str]
    domains: list[str]
    experience_level: Literal["entry", "mid", "senior"]


class GeneratedQuestion(BaseModel):
    question_text: str
    rationale: str
    difficulty: Literal["easy", "medium", "hard"]


class AnswerScore(BaseModel):
    score: Literal[1, 2, 3, 4, 5]
    justification: str


class CreateSessionRequest(BaseModel):
    role: str


class CreateSessionResponse(BaseModel):
    session_id: int
    role: str
    status: str


class QuestionResponse(BaseModel):
    id: int
    text: str
    rationale: str | None
    difficulty: str | None
    order: int


class SubmitAnswerRequest(BaseModel):
    question_id: int
    text: str


class QASummaryItem(BaseModel):
    question: str
    answer: str | None
    rationale: str | None
    difficulty: str | None
    source_page: int | None
    score: int | None
    score_justification: str | None


class SessionSummaryResponse(BaseModel):
    session_id: int
    role: str
    qa_pairs: list[QASummaryItem]
    topics_covered: list[str]
    coverage_percent: int
