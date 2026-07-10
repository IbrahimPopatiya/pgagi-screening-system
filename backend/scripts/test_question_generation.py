from app.services.resume_parser import extract_text_from_resume, parse_resume
from app.services.query_builder import build_retrieval_queries
from app.services.retriever import retrieve_chunks
from app.services.question_generator import generate_question

with open("data/Ibrahim_resume.pdf", "rb") as f:
    file_bytes = f.read()

resume_text = extract_text_from_resume(file_bytes)
profile = parse_resume(resume_text)

queries = build_retrieval_queries("ai_ml_engineer", profile)
chunks = retrieve_chunks("ai_ml_engineer", queries)

print(f"Using top chunk (page {chunks[0]['page']}) to generate a question:\n")
print(chunks[0]["text"][:200], "\n")

question = generate_question("ai_ml_engineer", chunks[0], profile)
print("Generated question:")
print(question.model_dump_json(indent=2))
