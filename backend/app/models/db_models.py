from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class InterviewSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    status = Column(String, default="created")  # created -> resume_uploaded -> in_progress -> completed
    resume_profile_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="session", order_by="Question.order")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    text = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    difficulty = Column(String, nullable=True)
    source_chunks_json = Column(Text, nullable=True)  # traceability: which chunks produced this
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False)


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, unique=True)
    text = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("Question", back_populates="answer")
