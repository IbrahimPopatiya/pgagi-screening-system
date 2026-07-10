from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session as DBSession
from app.db.database import get_db
from app.services import session_service
from app.models.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    QuestionResponse,
    SubmitAnswerRequest,
    SessionSummaryResponse,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=CreateSessionResponse)
def create_session(payload: CreateSessionRequest, db: DBSession = Depends(get_db)):
    try:
        session = session_service.create_session(db, payload.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return CreateSessionResponse(session_id=session.id, role=session.role, status=session.status)


@router.post("/{session_id}/resume")
def upload_resume(session_id: int, file: UploadFile = File(...), db: DBSession = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Resume must be a PDF file")

    file_bytes = file.file.read()
    try:
        profile = session_service.attach_resume(db, session_id, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return profile


@router.post("/{session_id}/next-question", response_model=QuestionResponse)
def next_question(session_id: int, db: DBSession = Depends(get_db)):
    try:
        question = session_service.generate_next_question(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return question


@router.post("/{session_id}/answer")
def answer_question(session_id: int, payload: SubmitAnswerRequest, db: DBSession = Depends(get_db)):
    try:
        answer = session_service.submit_answer(db, payload.question_id, payload.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"answer_id": answer.id, "status": "stored"}


@router.get("/{session_id}/summary", response_model=SessionSummaryResponse)
def summary(session_id: int, db: DBSession = Depends(get_db)):
    try:
        return session_service.get_summary(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
