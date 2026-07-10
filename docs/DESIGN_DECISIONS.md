# Design Decisions Log

Format: **Decision** — reasoning, alternatives considered.

---

- **Git workflow: Git Flow (develop + feature branches)** — chosen to demonstrate a real team workflow rather than committing directly to main; every phase of work is isolated in its own feature branch and merged into develop once working.


- **Resume upload endpoint deferred to Phase 6** — parsing logic is built and tested standalone first (service layer independent of API layer, per separation-of-concerns), then wired into the session lifecycle once InterviewSession exists, avoiding rework.


- **LLM provider: Google Gemini (gemini-1.5-flash)** — chosen for free-tier access; resume extraction uses a strict JSON-only prompt with Pydantic validation at the boundary to catch malformed LLM output before it propagates downstream.
