# AI-Powered Role-Based Candidate Screening System

A system that simulates a structured technical interview: a candidate uploads their resume and picks a role, and the system dynamically generates interview questions grounded in a role-specific textbook (via Retrieval-Augmented Generation), influenced by what's actually on the candidate's resume — not a fixed question bank.

Built for the PGAGI AI/ML & Backend Intern Assignment.

## What this is

The candidate uploads a resume PDF and selects a target role. The system extracts their skills/technologies/domains, builds retrieval queries from that profile, searches a pre-ingested vector store of the role's reference textbook, and hands the most relevant passage to an LLM with an explicit instruction to generate a question that requires **applying** the concept — not recalling a definition — tied to the candidate's actual background. The candidate answers through a chat-style UI; every question is stored with its source book page and the reasoning behind it, so the whole pipeline is auditable end to end. At the end, the candidate sees a summary with per-answer scoring, the topics covered, and a coverage percentage against the role's core topic checklist.

## Architecture

```
┌─────────────┐      ┌──────────────────────────────────────────────┐      ┌───────────────┐
│   Next.js   │◄────►│                  FastAPI                      │◄────►│    SQLite      │
│  (frontend) │ HTTP │           app/api/sessions.py                 │ SQL  │ sessions       │
│             │      │                    │                          │      │ questions      │
│  Zustand    │      │                    ▼                          │      │ answers        │
│  store      │      │          app/services/session_service.py      │      └───────────────┘
└─────────────┘      │         (orchestration — the only place       │
                      │          that knows the full pipeline)        │
                      │        ┌──────────┼──────────┬─────────┐     │
                      │        ▼          ▼          ▼         ▼     │
                      │  resume_parser  query_    retriever  question_│
                      │  (Gemini LLM)   builder   (Chroma)   generator │
                      │                                     (Gemini)  │
                      └──────────────────────┬─────────────────────────┘
                                              ▼
                                     ┌─────────────────┐
                                     │    ChromaDB      │
                                     │ one collection    │
                                     │ per role, built    │
                                     │ from role's book   │
                                     │ (scripts/ingest.py) │
                                     └─────────────────┘
```

**Data flow per question:** resume → extracted skills (Gemini) → retrieval queries (per skill/domain) → vector search against the role's Chroma collection → best-matching book passage → question generated from that passage + resume context (Gemini) → stored with page number + rationale for traceability → candidate answers → stored → next question, or summary.

For a step-by-step walkthrough of every stage, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js (App Router) + TypeScript + Tailwind + Zustand | see [Design Decisions](docs/DESIGN_DECISIONS.md#frontend) |
| Backend | FastAPI | async, auto-generated docs, clean Pydantic validation |
| LLM | Google Gemini (`gemini-2.5-flash`) | free tier, sufficient for structured extraction/generation |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) | local, free, no network dependency for ingestion |
| Vector store | ChromaDB | zero external infra, persists to disk |
| Database | SQLite via SQLAlchemy | zero setup, still a real persistent relational DB |

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Google Gemini API key](https://aistudio.google.com) (free tier)

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

cp .env.example .env
# edit .env and set GEMINI_API_KEY=your_key_here
```

Ingest the knowledge base (one-time — builds the vector store from the role's textbook):
```bash
python -m scripts.ingest
```

Run the API:
```bash
uvicorn app.main:app --reload
```
Backend runs at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install

cp .env.local.example .env.local   # or create manually — see below
```

`.env.local` contents:
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

```bash
npm run dev
```
Frontend runs at `http://localhost:3000`.

### Adding another role

1. Drop the role's PDF into `backend/data/source_books/`
2. Add a `role_name: collection_name` entry to `ROLE_COLLECTIONS` in `backend/app/core/roles.py`
3. Add a core-topics checklist entry to `ROLE_CORE_TOPICS` in the same file (used for the coverage %)
4. Update `BOOK_PATH`/`COLLECTION_NAME` in `backend/scripts/ingest.py` and re-run it for the new role
5. Add the role to the `ROLES` array in `frontend/components/EntryStage.tsx`

## Key Design Decisions

The full reasoning log — every major choice, why it was made, and what alternatives were considered — lives in [`docs/DESIGN_DECISIONS.md`](docs/DESIGN_DECISIONS.md). Highlights:

- **Multi-query retrieval** (one focused query per resume skill/domain, not one combined query) — empirically improved retrieval from 0/5 to 4/5 genuinely relevant chunks. See the log for the actual distance measurements that drove this fix.
- **Resume skills prioritized over domains** in query construction — skills use textbook-style vocabulary; domains describe application context a theory book doesn't cover.
- **Thin API layer, thick service layer** — the entire pipeline (`session_service.py`) is testable and runnable without any HTTP framework involved, verified via standalone scripts before any endpoint was wired.
- **Session continuity via localStorage** — a page refresh mid-interview resumes on the same question rather than restarting.
- **Every question is traceable** to its exact source book page and the resume signal that triggered its retrieval query — visible in the UI, not just in the database.

## Project structure

```
screening-system/
├── backend/
│   ├── app/
│   │   ├── api/          # HTTP route handlers (thin)
│   │   ├── core/         # config, role/knowledge-base registry
│   │   ├── services/     # business logic — RAG pipeline, orchestration
│   │   ├── models/       # SQLAlchemy DB models + Pydantic API schemas
│   │   └── db/           # database engine setup
│   ├── data/              # source books, ingested vector store, sqlite db (gitignored)
│   └── scripts/           # ingestion + standalone test scripts
├── frontend/
│   ├── app/                # Next.js App Router entry
│   ├── components/         # EntryStage, InterviewStage, SummaryStage
│   ├── store/               # Zustand interview state
│   └── lib/                  # typed API client
└── docs/
    ├── ARCHITECTURE.md
    └── DESIGN_DECISIONS.md
```
