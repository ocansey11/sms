# 📚 School Management System – **Backend (FastAPI × PostgreSQL)**

A modular school platform that supports **Admin, Teacher, Student & Guardian** roles.  
Core features include user management, class organization, basic quiz/assessment engine, and guardian dashboards.  
The backend is written in **FastAPI (Async SQLAlchemy)**, uses **PostgreSQL** (local dev / Supabase prod), and runs container‑first via **Docker + Compose**.

---

## 🏗️ Project Structure
```bash
school-management-backend/
├── app/
│   ├── main.py                # FastAPI entry‑point
│   ├── api/
│   │   ├── dependencies.py    # DB session + auth guards
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
│   ├── services/              # Business logic layer
│   │   ├── auth_service.py    # Authentication business logic
│   │   ├── quiz_service.py    # Quiz management logic
│   │   └── user_service.py    # User management logic
│   ├── middleware/            # Custom middleware
│   │   ├── auth_middleware.py # JWT validation
│   │   └── cors_middleware.py # CORS configuration
│   ├── exceptions/            # Custom exceptions
│   │   └── custom_exceptions.py
│   └── utils/
│       └── helpers.py         # Utility functions
├── alembic/                   # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/                     # Pytest (+ httpx.AsyncClient)
├── requirements.txt           # Locked deps
├── Dockerfile                 # Multi-stage image for backend
├── docker-compose.dev.yml     # Local development with PostgreSQL
├── docker-compose.prod.yml    # Production configuration
├── .dockerignore
├── .env.example               # Copy → .env
├── .env.dev                   # Development environment
├── .env.prod                  # Production environment
├── alembic.ini                # Alembic configuration
└── README.md (this file)
```

---

## ⚙️ Requirements
* Python 3.11+
* FastAPI · SQLAlchemy 2 (async) · asyncpg · alembic
* passlib[bcrypt] · python‑jose[cryptography] · python‑dotenv · pydantic
* Docker & Compose (dev/prod)
* PostgreSQL (local dev) / Supabase (prod)

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Configuration

### Development (.env.dev)
```env
# Database - Local PostgreSQL
DATABASE_URL=postgresql+asyncpg://sms_user:sms_password@localhost:5432/sms_dev
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sms_dev
DB_USER=sms_user
DB_PASSWORD=sms_password

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Environment
ENV=development
DEBUG=true
LOG_LEVEL=debug

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### Production (.env.prod)
```env
# Database - Supabase
DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
DB_HOST=<supabase-host>
DB_PORT=5432
DB_NAME=<supabase-db>
DB_USER=<supabase-user>
DB_PASSWORD=<supabase-password>

# JWT Configuration
SECRET_KEY=<secure-random-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENV=production
DEBUG=false
LOG_LEVEL=info

# Azure Configuration (if deploying to Azure)
AZURE_STORAGE_CONNECTION_STRING=<azure-storage-connection>
AZURE_CONTAINER_NAME=<container-name>
```

---

## 🐳 Docker Setup

### Development with Local PostgreSQL
```bash
# Build & run with local database
docker-compose -f docker-compose.dev.yml up --build

# Hot‑reload dev server + PostgreSQL on:
# - API: http://localhost:8000/docs
# - DB: localhost:5432
```

### Production Deployment
```bash
# Build for production (connects to Supabase)
docker-compose -f docker-compose.prod.yml up --build

# Or build production image only
docker build --target production -t sms-backend .
```

**Multi-stage Dockerfile:**
- `development` stage: uvicorn with --reload, includes dev dependencies
- `production` stage: gunicorn with multiple workers, optimized for Azure Container Instances

---

## 🚀 Running Locally (without Docker)
```bash
git clone https://github.com/yourusername/sms.git
cd sms

# Copy environment file
cp .env.example .env.dev

# Install dependencies
pip install -r requirements.txt

# Set up database migrations
alembic upgrade head

# Run development server
uvicorn app.main:app --reload
```

### Database Management
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## 🧑‍💼 Admin Endpoints
* User management and role assignment
* Class creation and management
* Payment tracking and reports
* System analytics and metrics

## 👩‍🏫 Teacher Endpoints
* Create and manage quizzes
* Grade student submissions
* View class performance analytics
* Manage class roster

## 👨‍🎓 Student Endpoints
* View assigned quizzes
* Take quizzes with basic validation
* View grades and feedback
* Track personal progress

## 👨‍👩‍👧 Guardian Endpoints
* View children's progress
* Receive attendance notifications
* Access payment information
* Monitor academic performance

---

## 📌 MVP Task‑List

### Phase 1: Core Infrastructure
- [ ] Set up project structure with services and middleware layers
- [ ] Configure Alembic for database migrations
- [ ] Create simplified database schema (core tables only)
- [ ] Set up Docker development environment with PostgreSQL
- [ ] Implement basic error handling and logging

### Phase 2: Authentication & User Management
- [ ] JWT authentication system with refresh tokens
- [ ] User registration and login endpoints
- [ ] Role-based access control (RBAC)
- [ ] Password reset functionality
- [ ] Basic user profile management

### Phase 3: Core Features
- [ ] Admin: User and class management
- [ ] Teacher: Basic quiz creation and grading
- [ ] Student: Quiz taking and grade viewing
- [ ] Guardian: Child progress monitoring
- [ ] Basic attendance tracking

### Phase 4: Production Deployment
- [ ] Azure Container Instances deployment
- [ ] Supabase production database setup
- [ ] CI/CD pipeline configuration
- [ ] Basic monitoring and health checks

---

## 🎯 Simplified Database Schema (MVP)

### Core Tables
```sql
-- Users (simplified)
Table users {
  id uuid [pk]
  first_name text
  last_name text
  email text [unique]
  password_hash text
  phone_number text
  role text [note: 'student, teacher, admin, guardian']
  is_verified boolean
  last_login timestamp
  created_at timestamp
  updated_at timestamp
}

-- Classes
Table classes {
  id uuid [pk]
  teacher_id uuid [ref: > users.id]
  name text
  academic_year text
  grade text
  subject text
  created_at timestamp
  updated_at timestamp
}

-- Students-Classes relationship
Table student_classes {
  id uuid [pk]
  student_id uuid [ref: > users.id]
  class_id uuid [ref: > classes.id]
  enrolled_at timestamp
}

-- Guardian-Student relationship
Table guardian_students {
  id uuid [pk]
  guardian_id uuid [ref: > users.id]
  student_id uuid [ref: > users.id]
  relationship text
  created_at timestamp
}

-- Basic Quiz System
Table quizzes {
  id uuid [pk]
  title text
  description text
  class_id uuid [ref: > classes.id]
  created_by uuid [ref: > users.id]
  time_limit int
  max_attempts int
  status text [note: 'draft, published, archived']
  created_at timestamp
  updated_at timestamp
}

Table quiz_questions {
  id uuid [pk]
  quiz_id uuid [ref: > quizzes.id]
  text text
  options json
  correct_answer int
  points int
  created_at timestamp
  updated_at timestamp
}

Table quiz_attempts {
  id uuid [pk]
  quiz_id uuid [ref: > quizzes.id]
  student_id uuid [ref: > users.id]
  start_time timestamp
  end_time timestamp
  score numeric
  percentage numeric
  answers json
  status text [note: 'in_progress, completed, abandoned']
  created_at timestamp
  updated_at timestamp
}

-- Basic Attendance
Table attendance_records {
  id uuid [pk]
  student_id uuid [ref: > users.id]
  class_id uuid [ref: > classes.id]
  date date
  status text [note: 'present, absent, late']
  created_at timestamp
}
```

---

## 🚀 Future Enhancements
* AI quiz generation (OpenAI)
* Advanced proctoring features
* Mobile app via Expo
* Real-time notifications
* Advanced analytics and reporting

---

## 📣 How to Contribute
Open a PR with clear commit messages; all code must pass `ruff` + `mypy` & have pytest coverage ≥ 80%.

Happy hacking! 🚀
