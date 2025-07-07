# sms


# 📚 School Management System – **Backend (FastAPI × Supabase)**
A modular, AI‑ready school platform that supports **Admin, Teacher, Student & Guardian** roles.  
Features include smart attendance, rich quiz/assessment engine, guardian dashboards, anti‑cheat proctoring and AI nudges.  
The backend is written in **FastAPI (Async SQLAlchemy)**, connects to a **Supabase (Postgres)** instance, and runs container‑first via **Docker + Compose**.

---

## 🏗️ Project Structure
```bash
school-management-backend/
├── app/
│   ├── main.py                # FastAPI entry‑point
│   ├── api/
│   │   ├── dependencies.py    # DB session + auth guards
│   │   └── routes/
│   │       ├── auth.py        # JWT login / register
│   │       ├── admin.py       # Admin CRUD & stats
│   │       ├── teacher.py     # Quiz creation & grading
│   │       ├── student.py     # Quiz attempt flow
│   │       └── guardian.py    # Child insights & alerts
│   ├── core/
│   │   ├── config.py          # Settings (pydantic‑BaseSettings)
│   │   └── security.py        # Bcrypt + JWT helpers
│   ├── db/
│   │   ├── database.py        # Async engine/session
│   │   ├── models.py          # SQLAlchemy models (mirror ERD)
│   │   ├── schemas.py         # Pydantic I/O models
│   │   └── crud.py            # Typed CRUD helpers
│   └── utils/
│       ├── quiz_logic.py      # Shuffle, scoring, adaptive diff.
│       └── proctoring.py      # Anti‑cheat utilities
├── tests/                     # Pytest (+ httpx.AsyncClient)
├── requirements.txt           # Locked deps
├── Dockerfile                 # Image for backend
├── docker-compose.yml         # Local orchestration
├── .dockerignore
├── .env.example               # Copy → .env
└── README.md (this file)
```

---

## ⚙️ Requirements
* Python 3.11+
* FastAPI · SQLAlchemy 2 (async) · asyncpg
* passlib[bcrypt] · python‑dotenv · pydantic
* Docker & Compose (dev/prod)

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment (.env)
```env
DB_HOST=<supabase-host>
DB_PORT=5432
DB_NAME=<supabase-db>
DB_USER=<supabase-user>
DB_PASSWORD=<supabase-pw>
SECRET_KEY=<jwt-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 🐳 Docker Quick‑Start
```bash
# Build & run
docker-compose up --build
# Hot‑reload dev server on http://localhost:8000/docs
```
`Dockerfile` uses `uvicorn --reload` for local DX; switch to `gunicorn -k uvicorn.workers.UvicornWorker` for production.

---

## 🚀 Running Locally (without Docker)
```bash
git clone https://github.com/sms.git
cd sms
cp .env.example .env  # ← add DB creds & secret
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🧑‍💼 Admin Endpoints
* CRUD: users / classes / payments
* Platform metrics & reports

## 👩‍🏫 Teacher Endpoints
* Create/update quizzes (Bolt‑style metadata)
* View submissions & leaderboards

## 👨‍🎓 Student Endpoints
* List assigned quizzes
* Start/pause/submit attempts (anti‑cheat)
* View grades & certificates

## 👨‍👩‍👧 Guardian Endpoints
* Real‑time child progress
* Attendance & AI nudges
* Sibling comparison leaderboard

---

## 📌 MVP Task‑List
- [ ] Wire async DB connection ➜ Supabase
- [ ] JWT auth (`/login`) + `role_required()` guards
- [ ] Core routes (admin/teacher/student/guardian)
- [ ] Quiz engine : create → attempt → results
- [ ] Guardian dashboard APIs
- [ ] Basic proctoring (device/IP logging)
- [ ] Docker CI build + deploy script

---

## ✨ Future Ideas
* AI quiz generation (OpenAI)
* Bland.ai voice alerts for attendance
* Redis + RQ/Celery workers for async tasks
* React/Next.js frontend (separate repo)
* Mobile app via Expo

---
### 📣 How to Contribute
Open a PR with clear commit messages; all code must pass `ruff` + `mypy` & have pytest coverage ≥ 80%.

Happy hacking! 🚀
