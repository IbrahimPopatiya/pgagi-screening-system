from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.models import db_models  # noqa: F401 — import so tables register with Base
from app.api import sessions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Candidate Screening System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
