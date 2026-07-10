from app.services.resume_parser import extract_text_from_resume, parse_resume

with open("data/ibrahim_resume.pdf", "rb") as f:
    file_bytes = f.read()

resume_text = extract_text_from_resume(file_bytes)
print(f"Extracted {len(resume_text)} characters of text\n")

profile = parse_resume(resume_text)
print("Parsed profile:")
print(profile.model_dump_json(indent=2))
