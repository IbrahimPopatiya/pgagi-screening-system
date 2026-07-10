from app.models.schemas import ResumeProfile


def build_retrieval_queries(role: str, resume: ResumeProfile) -> list[str]:
    role_readable = role.replace("_", " ")
    # skills tend to use textbook-style ML vocabulary (e.g. "Deep Learning", "Fine-Tuning");
    # domains describe what the candidate applied ML to (e.g. "Recruitment Technology") and
    # rarely match a foundational textbook's language, so they're deprioritized here.
    topics = (resume.skills + resume.domains)[:6]
    return [f"{role_readable} interview question about {topic}" for topic in topics]
