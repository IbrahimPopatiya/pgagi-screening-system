# Architecture — Stage by Stage

This walks through exactly what happens, in order, from a resume upload to the final summary. Each stage names the file(s) responsible and what gets read/written.

## 1. Candidate entry

**Frontend:** `components/EntryStage.tsx` — candidate uploads a PDF resume and picks a role.
**Flow:** `POST /api/sessions` creates a row in `sessions` (status: `created`) before any AI work happens, so nothing about the candidate's progress lives only in memory. The returned `session_id` is persisted to `localStorage` (see Session Continuity below).

## 2. Resume processing

**File:** `app/services/resume_parser.py`
**Flow:** `POST /api/sessions/{id}/resume` extracts raw text from the uploaded PDF (`pypdf`), then sends it to Gemini with a strict JSON-only extraction prompt. The result is validated against the `ResumeProfile` Pydantic schema (skills, technologies, domains, experience level) and stored as JSON on the session row. Session status advances to `resume_uploaded`.

## 3. Context construction

**File:** `app/services/query_builder.py`
**Flow:** the candidate's skills and domains (skills prioritized — see Design Decisions) are combined with the role into up to 6 focused retrieval queries, one per topic (e.g. *"ai ml engineer interview question about Deep Learning"*). This is the fork where resume signal and role selection actually merge into one search intent.

## 4. Knowledge retrieval (RAG)

**File:** `app/services/retriever.py`
**Flow:** each query is embedded (`sentence-transformers`) and searched against the role's dedicated ChromaDB collection (built ahead of time by `scripts/ingest.py`). Results across all queries are merged, deduplicated by source page, filtered by a similarity distance threshold (tuned empirically to 1.35), and ranked. The single best-matching passage — with its page number — is passed forward.

## 5. Question generation

**File:** `app/services/question_generator.py`
**Flow:** `POST /api/sessions/{id}/next-question` sends the retrieved passage + the candidate's skills/experience level to Gemini, explicitly instructed to generate a question that requires *applying* the concept, not recalling its definition. The response includes the question text, a one-line rationale connecting the passage and the candidate's background, and a difficulty rating. Stored as a `Question` row with `source_chunks_json` (page + originating query) for traceability. Session status advances to `in_progress`.

## 6. Interactive interview

**Frontend:** `components/InterviewStage.tsx`
**Flow:** the candidate sees one question at a time (with a "Why this question?" collapsible revealing the rationale), types an answer, and submits. `POST /api/sessions/{id}/answer` stores it linked to the exact question. The frontend then immediately requests the next question (repeating steps 3–6), up to `MAX_QUESTIONS` (5).

## 7. Response handling

**File:** `app/models/db_models.py` — `Answer` table, one row per question, foreign-keyed.
Every answer is written immediately on submission — nothing is held in memory waiting for the interview to finish.

## 8. Final output

**File:** `app/services/session_service.py` → `get_summary()`
**Flow:** `GET /api/sessions/{id}/summary` compiles every question/answer pair, plus:
- **Answer scoring** (best-effort, lazy): each answer is scored 1–5 with a justification via one additional Gemini call per answer, run only at summary time so the live interview stays fast. Failures here never break the summary — score just comes back `null`.
- **Topic coverage %**: the topics actually retrieved during the interview are checked against a fixed per-role core-topics checklist (`ROLE_CORE_TOPICS`), producing a simple percentage — no extra LLM cost, purely derived from stored data.

The frontend's `SummaryStage.tsx` displays all of this, including the source page number per question — full traceability, visible in the product itself, not just in logs.

## Session continuity

The `InterviewSession.status` field (`created` → `resume_uploaded` → `in_progress` → `completed`) means the backend always knows what stage a session is in. On the frontend, Zustand's `persist` middleware mirrors the store to `localStorage`, so a page refresh mid-interview rehydrates `sessionId` and `currentQuestion` and resumes exactly where the candidate left off, rather than restarting. A `hasHydrated` flag prevents a flash of the wrong stage while `localStorage` is being read on first client render.

## Why this shape

The API layer (`app/api/sessions.py`) is intentionally thin — it only translates HTTP requests into calls on `session_service.py` and turns `ValueError`s into proper `HTTPException` responses. All actual business logic lives in the service layer, which is fully testable and was verified end-to-end via standalone scripts (`backend/scripts/test_*.py`) before any HTTP endpoint existed. This separation is what let each phase of the RAG pipeline (ingestion, retrieval, generation) be built and proven independently before being wired together.
