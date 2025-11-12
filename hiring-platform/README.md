# Proof-of-Work Hiring Platform

A platform where both candidates and HR prove themselves through actual work, not theater.

## 🎯 The Breakthrough Idea

**Traditional hiring is mutual deception:**
- Candidates fake "passion" and memorize LeetCode
- HR runs 30-minute interviews and calls it "thorough evaluation"
- Both gamble and blame each other when it fails

**This platform makes lying impossible for both sides.**

## 🚀 Quick Start

```bash
cd hiring-platform

# Option 1: Docker (Recommended)
docker-compose up -d

# Option 2: Manual
python -m venv venv
source venv/bin/activate
pip install -r requirements-platform.txt
export OPENAI_API_KEY='sk-...'
export DATABASE_URL='postgresql://...'
uvicorn main:app --reload
```

Access API docs: http://localhost:8000/docs

## 📁 Project Structure

```
hiring-platform/
├── app/                    # Modular application
│   ├── core/              # Config & database
│   ├── models/            # Database models (split by domain)
│   ├── services/          # Business logic
│   ├── schemas/           # Pydantic schemas (coming)
│   └── routers/           # API routes (coming)
│
├── docker-compose.yml     # Docker setup
├── Dockerfile
├── alembic.ini           # Database migrations
├── requirements-platform.txt
└── README.md             # This file
```

## 🔥 Key Features

1. **For Candidates**: Prove skills via real projects (5-7 days)
   - Git commit analysis detects AI-generated code
   - Architecture review by GPT-4

2. **For HR**: Prove competence via evaluation quality
   - Must deeply analyze code
   - Gets scored against AI analysis
   - Prediction accuracy tracked for 90 days

3. **90-Day Ground Truth**
   - System validates all predictions
   - Updates reputation scores for both sides

## 📚 Documentation

- **MODULAR_QUICKSTART.md** - How to use the modular structure
- **CODEBASE_STRUCTURE.md** - Complete architecture guide
- **DATABASE_SCHEMA.md** - Database design
- **ARCHITECTURE.md** - System architecture
- **PLATFORM_SUMMARY.md** - Implementation overview

## 🔧 Core Services

- **Git Analysis** (`app/services/git_service.py`) - Commit pattern detection
- **AI Code Review** (`app/services/ai_service.py`) - GPT-4 powered analysis

## 🎯 Import Examples

```python
# Models
from app.models import Candidate, ProjectSubmission, Evaluation

# Config & Database
from app.core import settings, get_db

# Services
from app.services import GitAnalysisService, AICodeAnalysisService
```

## ✅ Status

**Phase 1: Backend Complete** ✅
- Database models (12 entities)
- FastAPI endpoints
- Git analysis service
- AI code review service

**Phase 2: Coming Next**
- Frontend (Next.js)
- Background jobs (Celery)
- Authentication (JWT)

---

**This is not an HR platform. This is a truth engine for hiring.**
