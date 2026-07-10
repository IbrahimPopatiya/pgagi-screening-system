import json
from sqlalchemy.orm import Session as DBSession
from app.models.db_models import InterviewSession, Question, Answer
from app.models.schemas import ResumeProfile
from app.core.roles import ROLE_COLLECTIONS, ROLE_CORE_TOPICS
from app.services.resume_parser import extract_text_from_resume, parse_resume
from app.services.query_builder import build_retrieval_queries
from app.services.retriever import retrieve_chunks
from app.services.question_generator import generate_question
from app.services.answer_scorer import score_answer


def create_session(db: DBSession, role: str) -> InterviewSession:
    if role not in ROLE_COLLECTIONS:
        raise ValueError(f"Unknown role '{role}'. Available roles: {list(ROLE_COLLECTIONS)}")

    session = InterviewSession(role=role, status="created")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def attach_resume(db: DBSession, session_id: int, file_bytes: bytes) -> ResumeProfile:
    session = _get_session_or_raise(db, session_id)

    resume_text = extract_text_from_resume(file_bytes)
    profile = parse_resume(resume_text)

    session.resume_profile_json = profile.model_dump_json()
    session.status = "resume_uploaded"
    db.commit()

    return profile


def generate_next_question(db: DBSession, session_id: int) -> Question:
    session = _get_session_or_raise(db, session_id)

    if not session.resume_profile_json:
        raise ValueError("Cannot generate a question before a resume is attached to this session")

    profile = ResumeProfile.model_validate_json(session.resume_profile_json)

    queries = build_retrieval_queries(session.role, profile)
    chunks = retrieve_chunks(session.role, queries)

    if not chunks:
        raise ValueError("No relevant knowledge base content found for this candidate/role combination")

    top_chunk = chunks[0]
    generated = generate_question(session.role, top_chunk, profile)

    next_order = len(session.questions)
    question = Question(
        session_id=session.id,
        text=generated.question_text,
        rationale=generated.rationale,
        difficulty=generated.difficulty,
        source_chunks_json=json.dumps({"page": top_chunk["page"], "source_query": top_chunk["source_query"]}),
        order=next_order,
    )
    db.add(question)
    session.status = "in_progress"
    db.commit()
    db.refresh(question)

    return question


def submit_answer(db: DBSession, question_id: int, text: str) -> Answer:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise ValueError(f"Question {question_id} not found")
    if question.answer:
        raise ValueError(f"Question {question_id} already has an answer")

    answer = Answer(question_id=question_id, text=text)
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


def get_summary(db: DBSession, session_id: int) -> dict:
    session = _get_session_or_raise(db, session_id)

    qa_pairs = []
    topics = set()
    for q in session.questions:
        source = json.loads(q.source_chunks_json) if q.source_chunks_json else {}

        score, justification = None, None
        if q.answer and q.answer.text.strip():
            try:
                result = score_answer(q.text, q.answer.text)
                score, justification = result.score, result.justification
            except Exception:
                pass  # scoring is a best-effort enhancement (LLM call) — never block the summary on it

        qa_pairs.append({
            "question": q.text,
            "answer": q.answer.text if q.answer else None,
            "rationale": q.rationale,
            "difficulty": q.difficulty,
            "source_page": source.get("page"),
            "score": score,
            "score_justification": justification,
        })
        if source.get("source_query"):
            topics.add(source["source_query"].split("about ")[-1])

    core_topics = ROLE_CORE_TOPICS.get(session.role, [])
    covered_lower = " ".join(topics).lower()
    matched = sum(1 for t in core_topics if t.lower() in covered_lower)
    coverage_percent = round((matched / len(core_topics)) * 100) if core_topics else 0

    session.status = "completed"
    db.commit()

    return {
        "session_id": session.id,
        "role": session.role,
        "qa_pairs": qa_pairs,
        "topics_covered": sorted(topics),
        "coverage_percent": coverage_percent,
    }


def _get_session_or_raise(db: DBSession, session_id: int) -> InterviewSession:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ValueError(f"Session {session_id} not found")
    return session
