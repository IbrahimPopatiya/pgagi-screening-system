from app.services.resume_parser import extract_text_from_resume, parse_resume
from app.services.query_builder import build_retrieval_queries
from app.services.retriever import retrieve_chunks

with open("data/Ibrahim_resume.pdf", "rb") as f:
    file_bytes = f.read()

resume_text = extract_text_from_resume(file_bytes)
profile = parse_resume(resume_text)

queries = build_retrieval_queries("ai_ml_engineer", profile)
print("Generated queries:")
for q in queries:
    print(" -", q)
print()

chunks = retrieve_chunks("ai_ml_engineer", queries)
print(f"Retrieved {len(chunks)} chunks:\n")
for c in chunks:
    print(f"--- page {c['page']} | distance {c['distance']:.4f} | from query: \"{c['source_query']}\" ---")
    print(c["text"][:150], "\n")
