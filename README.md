# NoticeMate – prototype citizen‑friendly notice assistant

A **hackathon‑style** demo that turns a complex synthetic government notice into a
clear, step‑by‑step action plan.  The prototype is split into a **FastAPI** backend
and a **Next.js** frontend, both wired to an OpenAI‑driven AI extraction service.

---

## 📂 Repository layout

```
notice-mate/
├─ backend/                     # Python FastAPI server
│   ├─ app/
│   │   ├─ api/               # REST endpoints (notices, documents, responses, submissions)
│   │   ├─ core/                # Settings & config (pydantic‑settings)
│   │   ├─ db/                  # SQLModel DB session & engine
│   │   ├─ models/              # DB tables (Notice, Document, Response, Submission)
│   │   ├─ schemas/             # Pydantic request/response contracts
│   │   ├─ services/
│   │   │   ├─ ai/              # OpenAI extraction prompt & parsing
│   │   │   ├─ response/        # Response generation service
│   │   │   └─ workflow/        # State‑machine helpers
│   │   └─ main.py              # FastAPI app entry point
│   ├─ requirements.txt
│   └─ .env.example
│
├─ frontend/                    # Next.js 13+ app (app router)
│   ├─ app/
│   │   ├─ page.tsx                     # Home – “Understand your government notice”
│   │   ├─ upload/                      # File‑upload UI
│   │   ├─ notice/
│   │   │   ├─ [id]/                    # Catch‑all route for a notice
│   │   │   │   ├─ page.tsx               # Summary of analysis
│   │   │   │   ├─ explain/page.tsx       # “What does this mean?”
│   │   │   │   ├─ plan/page.tsx          # Action plan & deadline
│   │   │   │   ├─ documents/page.tsx     # Checklist UI
│   │   │   │   ├─ draft/page.tsx         # Edit AI‑generated response
│   │   │   │   ├─ review/page.tsx        # Final review
│   │   │   │   └─ submit/page.tsx        # Mock submission confirmation
│   │   │   └─ ... (other step pages)
│   │   ├─ global.css
│   │   ├─ tailwind.config.js
│   │   └─ next.config.js
│   ├─ package.json
│   └─ tsconfig.json
│
├─ demo/                        # Sample synthetic notices/documents for quick testing
│   ├─ notices/
│   └─ documents/
│
├─ docs/                        # Architecture & demo‑script documentation
│   ├─ architecture.md
│   ├─ api.md
│   └─ demo-script.md
│
├─ README.md
└─ .gitignore
```

---

## 🚀 Quick‑start (local development)

### 1️⃣ Clone & install

```bash
git clone <repo‑url> notice-mate
cd notice-mate

# Backend dependencies
cd backend
python -m venv .venv          # optional, but recommended
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# Frontend dependencies
cd ../frontend
npm install                   # or `pnpm i` / `yarn`
```

### 2️⃣ Environment variables

Copy the example files and fill in your local values:

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env – at minimum set OPENAI_API_KEY=sk-…

# Frontend
# The Next.js app reads NEXT_PUBLIC_API_BASE_URL from .env.local or the OS env.
# You can leave it as the default value in .env.example (http://localhost:8000)
```

> **NOTE** – The project uses **SQLite** for the MVP, so `DATABASE_URL`
> points to `sqlite:///./notice-mate.db`.  No external DB is required.

### 3️⃣ Run the servers

```bash
# Backend (defaults to http://localhost:8000)
cd ../backend
uvicorn app.main:app --reload
```

```bash
# Frontend (defaults to http://localhost:3000)
cd ../frontend
npm run dev
```

Open <http://localhost:3000> in a browser – you should see the **Welcome** screen
with the two CTA buttons (“I received a notice” and “Try demo notice”).

### 4️⃣ Using the demo data

The `demo/` folder contains a few synthetic notice PDFs (or image files) that you
can drag‑and‑drop onto the **Upload** page.  The backend will store the file,
run the AI extraction, and populate the workflow state automatically.  From there
the UI walks you through the plain‑language explanation, required documents,
response drafting, and a mock “government submission” that returns a synthetic
tracking number.

### 5️⃣ Running the test suite (optional)

```bash
# Backend tests (if you add any later)
pytest  # (install with `pip install pytest`)

# Frontend lint / type‑check
npm run lint
npm run typecheck
```

---

## 📐 Architecture highlights

| Layer | Responsibility | Tech |
|------|----------------|------|
| **Frontend** | Render UI, collect user input, call backend APIs, display step‑by‑step workflow | Next.js (App Router), TypeScript, Tailwind CSS, React hooks |
| **Backend** | Store notices/documents/responses, enforce deterministic workflow state, invoke OpenAI extraction, generate plain‑language drafts | FastAPI, Pydantic, SQLModel (SQLite), Async OpenAI client |
| **AI Service** | Structured extraction from synthetic notices, generate responses | OpenAI `gpt‑4o‑mini` (or any model you set in `.env`) |
| **Workflow** | Enforce `NOTICE_RECEIVED → NOTICE_ANALYZED → DOCUMENTS_PENDING → RESPONSE_READY → USER_REVIEWED → SUBMITTED` state transitions | Python helper (`workflow/state.py`) |
| **Data** | Persist all entities; primary key UUIDs; ensure referential integrity | SQLModel / SQLAlchemy ORM |
| **Deployment** | Stateless HTTP APIs, easy to containerise with Docker | `requirements.txt`, `Dockerfile` (not included yet) |

---

## 🔧 Next steps (if you want to keep building)

1. **Add real multilingual support** – swap the static English strings for i18n
   bundles and add Hindi/Telugu translation layers.
2. **Persist uploaded files to object storage** (e.g., S3) instead of `/tmp`.
3. **Replace the mock submission endpoint** with a more realistic “submission
   confirmation” page that stores a synthetic tracking ID in the DB.
4. **Write integration tests** that crawl the entire flow (notice → submit) and
   assert that each workflow transition occurs.
5. **Dockerise** both backend and frontend for one‑click deployment on a cloud
   sandbox (e.g., Railway, Render, or a local Docker Compose setup).
6. **Polish UI/UX** – refine Tailwind component library, add accessibility
   attributes, dark‑mode support, and responsive breakpoints for low‑end phones.

---

## 📚 Resources

- **FastAPI docs** – https://fastapi.tiangolo.com/
- **Next.js App Router** – https://nextjs.org/docs/app
- **Tailwind CSS** – https://tailwindcss.com/docs
- **OpenAI structured JSON extraction** – see `backend/app/services/ai.py`
- **SQLModel tutorial** – https://sqlmodel.tiangolo.com/

---

*Happy hacking!*  🎉