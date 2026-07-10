# Design Decisions Log

Format: **Decision** — reasoning, alternatives considered, evidence where available.

---

## Process

- **Git workflow: Git Flow (develop + feature branches)** — chosen to demonstrate a real team workflow rather than committing directly to main; every phase of work is isolated in its own feature branch, PR'd, and merged into `develop` once working. `main` is reserved for the final submission state.

## Knowledge Ingestion (RAG 7.1)

- **Chunking: 900 characters per chunk, 150 character overlap** — small enough for focused, precise retrieval; overlap prevents concepts split across a chunk boundary from being lost, satisfying the "context preservation" requirement. Verified empirically: retrieval for "overfitting and regularization" correctly returned the exact pages (63-64) where that topic is discussed in the source book.
- **Embeddings: sentence-transformers `all-MiniLM-L6-v2` (local)** — zero cost, no API key or network dependency for ingestion, fast enough to embed a 150-page book in ~12 seconds. Tradeoff: slightly lower retrieval quality than a hosted embedding API, acceptable given the 48-hour constraint and free-tier goal.
- **Vector DB: ChromaDB, one collection per role** — persists locally to disk, zero external infrastructure to run. Collection-per-role (e.g. `ml_engineer_kb`) is what makes retrieval genuinely role-specific rather than searching one mixed pool across all roles.
- **Role selection scoped to books actually provided (AI/ML Engineer), not the assignment's example roles** — section 3 mentions "Backend Engineer" as an example role, but section 9 (Knowledge Base Resources) only supplies books for AI/ML and Data Science roles. Since the assignment explicitly requires using the provided book as the primary source ("not generic internet queries"), role names were chosen to match available knowledge bases rather than inventing a role with no grounded source.

## Retrieval Mechanism (RAG 7.2, 7.4)

- **LLM provider: Google Gemini (`gemini-2.5-flash`)** — chosen for free-tier access, avoiding per-call cost during heavy testing/iteration. Model name pinned explicitly via `GEMINI_MODEL` env var after an earlier `gemini-1.5-flash` reference returned a 404 (deprecated on this API version) — confirmed the current valid model via the account's `list_models()` endpoint rather than relying on possibly-outdated documentation.
- **Query construction prioritizes resume skills over domains** — empirically, skills (e.g. "Deep Learning", "Fine-Tuning") use textbook-style vocabulary that embeds close to book content, while domains (e.g. "Recruitment Technology") describe application context a foundational theory book doesn't cover. Verified: domains-first best match was distance 1.17 on an unrelated title page; skills-first best match was distance 1.12 on an actually relevant "deep learning" definition passage.
- **Multi-query retrieval instead of one combined query** — one focused query per skill/domain (top 6), merged and deduplicated by page, ranked by distance. A single query combining many unrelated keywords ("Python, SQL, PyTorch, FastAPI...") embedded poorly and mixed unrelated concepts; individual focused queries per topic retrieved 4/5 genuinely relevant chunks vs. 0/5 before this fix.
- **Similarity distance threshold set to 1.35** — tuned empirically against this book/embedding model combination; a stricter threshold (1.2) rejected valid, on-topic matches. This book's chunk-query distances for genuinely relevant matches run roughly 1.1–1.3.

## Question Generation (RAG 7.3)

- **One retrieved chunk per generated question, not all chunks at once** — keeps every generated question traceable to exactly one source passage; feeding multiple chunks into one prompt would make it impossible to honestly say which one drove the question.
- **Prompt explicitly instructs "apply the concept, don't just recall its definition"** — directly targets the assignment's "avoid generic/template-driven outputs" requirement. Verified: a generated question required applying the book's formal supervised-learning notation `(xi, yi)` to a novel LLM fine-tuning scenario tied to the candidate's actual listed skills, not a definition-recall question.
- **Candidate's experience level (from resume) passed into the question prompt** — first mechanism for resume-driven difficulty calibration; the model frames application scenarios differently for entry vs. senior candidates.

## Resume Processing

- **LLM-based structured extraction over a hand-built parser** — resumes have no fixed format, making rule-based/regex extraction brittle and slow to build robustly within 48 hours. An LLM with a strict JSON-only prompt generalizes across formats immediately.
- **Pydantic validation at the LLM output boundary** — LLM output is untrusted input; validating it the moment it enters the system (rather than trusting `json.loads` blindly) catches malformed responses at the source instead of causing confusing failures downstream.
- **Resume upload endpoint deferred until session management existed (Phase 6)** — parsing logic was built and tested standalone first (service layer independent of the API layer), then wired into the session lifecycle once `InterviewSession` existed, avoiding rework from building a standalone endpoint that would need restructuring later.

## Backend & Session API

- **Thin API layer, thick service layer** — `session_service.py` holds all business logic and is fully testable/runnable without HTTP; `app/api/sessions.py` only translates HTTP requests into service calls and converts `ValueError`s into proper `HTTPException` status codes. The full pipeline was verified end-to-end via a standalone script before any HTTP endpoint existed, isolating integration bugs from HTTP-layer bugs.
- **SQLite via SQLAlchemy for persistence** — zero setup required (no separate DB server), while still being a real, persistent relational database. Tradeoff: no built-in JSON column type, so resume profiles and question source-chunk metadata are stored as serialized JSON text. A production system would likely use Postgres; the SQLAlchemy abstraction means that swap only changes one connection string.
- **Session status field (`created` → `resume_uploaded` → `in_progress` → `completed`)** — enables session continuity: the frontend can always query the current stage and resume correctly, rather than relying on in-memory state that a server restart or refresh would lose.
- **Traceability stored per-question (`source_chunks_json`)** — every question row records which book page and which resume-derived query produced it, satisfying the requirement to trace how each question was generated back to its source.

## Frontend

- **Single-page app with store-driven stage switching, not separate routes** — the interview is one continuous session (upload → interview → summary), not independent destinations; a Zustand store's `stage` field determines which component renders, keeping session data naturally in scope without passing it through URLs.
- **Zustand over React Context for state management** — no Provider boilerplate; components subscribe only to the specific state slice they use.
- **Session continuity via Zustand's `persist` middleware (localStorage)** — a page refresh mid-interview resumes on the exact same question instead of restarting. Required a `hasHydrated` flag to avoid a flash of the wrong stage before `localStorage` is read on the client, since Next.js renders once server-side (no `localStorage` access) before the browser hydrates.
- **Question rationale surfaced in the UI as a collapsible "Why this question?"** — makes RAG grounding visible and verifiable to the end user directly, not just in backend logs or a debug endpoint.
- **Interview capped at 5 questions (`MAX_QUESTIONS`)** — bounds the demo to a reasonable length; a production system would likely make this configurable per role/session.

## Creativity Extensions

- **Answer scoring runs lazily at summary time, not per-answer during the interview** — keeps the live interview flow fast (the candidate doesn't wait on an extra LLM call between questions); scoring only matters once, for the final report.
- **Answer scoring failures are swallowed silently (best-effort)** — a scoring LLM call failing should never break the whole summary; score/justification simply come back `null` for that item if the call fails.
- **Topic coverage % is a fixed per-role checklist matched against covered topics, not another LLM call** — zero additional cost or latency, derived entirely from data already being stored (`source_query` per question).
