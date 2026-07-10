# Design Decisions Log

Format: **Decision** — reasoning, alternatives considered.

---

- **Git workflow: Git Flow (develop + feature branches)** — chosen to demonstrate a real team workflow rather than committing directly to main; every phase of work is isolated in its own feature branch and merged into develop once working.


- **Resume upload endpoint deferred to Phase 6** — parsing logic is built and tested standalone first (service layer independent of API layer, per separation-of-concerns), then wired into the session lifecycle once InterviewSession exists, avoiding rework.


- **LLM provider: Google Gemini (gemini-1.5-flash)** — chosen for free-tier access; resume extraction uses a strict JSON-only prompt with Pydantic validation at the boundary to catch malformed LLM output before it propagates downstream.


- **Query construction prioritizes resume skills over domains** — empirically, skills (e.g. "Deep Learning", "Fine-Tuning") use textbook-style vocabulary that embeds close to book content, while domains (e.g. "Recruitment Technology") describe application context that a foundational theory book doesn't cover, producing weak/irrelevant matches. Verified via distance comparison during testing (domains-first: best match 1.17 on an unrelated title page; skills-first: [update after retest]).
- **Retrieval switched from one combined query to multi-query retrieval** — one query per skill/domain, merged and deduplicated by page, ranked by distance. A single query combining many keywords ("Python, SQL, PyTorch, FastAPI...") embedded poorly since it mixes unrelated concepts; individual focused queries per topic retrieve far more relevant chunks.


- **Query construction prioritizes resume skills over domains** — empirically, skills (e.g. "Deep Learning", "Fine-Tuning") use textbook-style vocabulary that embeds close to book content, while domains (e.g. "Recruitment Technology") describe application context a foundational theory book doesn't cover. Verified: domains-first best match was distance 1.17 on an unrelated title page; skills-first best match was distance 1.12 on an actually relevant "deep learning" definition passage.
- **Retrieval switched from one combined query to multi-query retrieval** — one query per skill/domain (top 6), merged and deduplicated by page, ranked by distance. A single combined query mixing unrelated keywords embedded poorly; individual focused queries per topic retrieved 4/5 genuinely relevant chunks vs. 0/5 before the fix.
- **Similarity distance threshold set to 1.35** — tuned empirically against this book/embedding model combination; lower thresholds (1.2) rejected valid matches, this book's chunk-query distances for good matches run 1.1–1.3.
