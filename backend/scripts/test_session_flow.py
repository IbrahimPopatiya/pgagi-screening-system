from app.db.database import SessionLocal, Base, engine
from app.models import db_models  # noqa: F401
from app.services import session_service

Base.metadata.create_all(bind=engine)
db = SessionLocal()

session = session_service.create_session(db, "ai_ml_engineer")
print(f"Created session {session.id}, status={session.status}")

with open("data/Ibrahim_resume.pdf", "rb") as f:
    file_bytes = f.read()
profile = session_service.attach_resume(db, session.id, file_bytes)
print(f"Resume attached, status={session.status}")

question = session_service.generate_next_question(db, session.id)
print(f"\nGenerated question: {question.text}")
print(f"Difficulty: {question.difficulty}")

answer = session_service.submit_answer(db, question.id, "This is my test answer explaining the concept.")
print(f"\nAnswer stored: {answer.text}")

summary = session_service.get_summary(db, session.id)
print(f"\nSummary:\n{summary}")

db.close()
