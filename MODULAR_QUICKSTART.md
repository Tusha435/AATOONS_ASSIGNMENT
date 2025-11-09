# 🚀 Modular Codebase - Quick Start Guide

This guide shows you how to work with the **new modular structure** of the Proof-of-Work Hiring Platform.

---

## 📂 What Changed?

### Before (Monolithic)
```
hiring-platform/
├── models.py          # 600 lines, ALL models
├── schemas.py         # 400 lines, ALL schemas
├── main.py            # 500 lines, ALL routes
├── git_service.py
├── ai_service.py
└── database.py
```

### After (Modular)
```
hiring-platform/
├── app/
│   ├── core/          # Config & database
│   ├── models/        # Split by domain (5 files)
│   ├── schemas/       # Split by resource (coming)
│   ├── routers/       # Split by endpoint (coming)
│   └── services/      # Business logic
└── main.py            # Entry point
```

---

## 🎯 Quick Reference

### Import Models
```python
# ✅ NEW WAY (clean)
from app.models import Candidate, ProjectSubmission, Evaluation

# ❌ OLD WAY (still works but verbose)
from app.models.candidate import Candidate
from app.models.project import ProjectSubmission
```

### Import Configuration
```python
# ✅ NEW WAY
from app.core import settings, get_db

# Access settings
api_key = settings.OPENAI_API_KEY
db_url = settings.DATABASE_URL

# Use database dependency
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(Candidate).all()
```

### Import Services
```python
# ✅ NEW WAY
from app.services import GitAnalysisService, AICodeAnalysisService

# Use services
git_service = GitAnalysisService()
result = git_service.analyze_submission(submission_id)
```

---

## 📁 Where to Find Things

| What You Want | Where to Look |
|---------------|---------------|
| **Configuration** | `app/core/config.py` |
| **Database setup** | `app/core/database.py` |
| **Candidate model** | `app/models/candidate.py` |
| **HR model** | `app/models/hr_manager.py` |
| **Project models** | `app/models/project.py` |
| **Analysis models** | `app/models/analysis.py` |
| **Evaluation models** | `app/models/evaluation.py` |
| **All enums** | `app/models/common.py` |
| **Git analysis** | `app/services/git_service.py` |
| **AI code review** | `app/services/ai_service.py` |

---

## 🛠️ Common Tasks

### 1. Add a New Field to a Model

**Example**: Add `linkedin_url` to Candidate

```python
# File: app/models/candidate.py

class Candidate(Base):
    # ... existing fields ...

    linkedin_url = Column(String(500), nullable=True)  # ADD THIS
```

Then create migration:
```bash
alembic revision --autogenerate -m "Add linkedin_url to candidates"
alembic upgrade head
```

### 2. Access Settings in Your Code

```python
from app.core import settings

# All environment variables available via settings
print(f"API Key: {settings.OPENAI_API_KEY}")
print(f"Environment: {settings.ENVIRONMENT}")
print(f"Max submissions: {settings.MAX_SUBMISSIONS_PER_MONTH}")

# Check environment
if settings.is_production:
    # Production logic
elif settings.is_development:
    # Dev logic
```

### 3. Use Database Sessions

```python
from app.core import get_db, get_db_context
from app.models import Candidate
from fastapi import Depends
from sqlalchemy.orm import Session

# In FastAPI routes (automatic cleanup)
@app.get("/candidates")
def list_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).all()

# In standalone scripts (manual cleanup)
from app.core import get_db_context

with get_db_context() as db:
    candidates = db.query(Candidate).all()
    # db.commit() called automatically on success
```

### 4. Use the Git Service

```python
from app.services import GitAnalysisService

service = GitAnalysisService()

# Analyze a submission
result = service.analyze_submission(submission_id)

print(f"Authenticity Score: {result['pattern_analysis']['authenticity_score']}")
print(f"Commits: {result['commits_analyzed']}")

# Or analyze a repo directly
commits = service.analyze_commits("/path/to/repo")
pattern_score = service.calculate_commit_pattern_score(commits)
```

### 5. Use the AI Service

```python
from app.services import AICodeAnalysisService

service = AICodeAnalysisService()

# Analyze code quality
result = service.analyze_submission_full(
    submission_id=uuid,
    code_files={"main.py": code_content},
    project_description="Build a REST API"
)

print(f"Architecture Score: {result['architecture_analysis']['architecture_score']}")
print(f"AI Generated: {result['architecture_analysis']['ai_generated_probability']}%")

# Score HR's evaluation
hr_score = service.score_hr_evaluation(evaluation_id)
print(f"HR Quality: {hr_score['hr_quality_score']}/100")
```

---

## 🏗️ Project Structure Overview

```
app/
├── core/
│   ├── config.py       # Settings from .env
│   └── database.py     # DB engine, sessions
│
├── models/
│   ├── common.py       # Base class + all enums
│   ├── candidate.py    # Candidate, SkillBadge, Leaderboard
│   ├── hr_manager.py   # HRManager, Dashboard
│   ├── project.py      # ProjectTemplate, ProjectSubmission
│   ├── analysis.py     # CommitAnalysis, CodeQuality, AIAnalysis
│   └── evaluation.py   # Evaluation, HiringDecision, Comparison
│
├── schemas/            # Pydantic schemas (coming next)
│   └── ...
│
├── routers/            # API routes (coming next)
│   └── ...
│
└── services/
    ├── git_service.py  # Git commit analysis
    └── ai_service.py   # AI code review
```

---

## 🚀 Running the App

**Nothing changed!** The app still runs the same way:

```bash
# Docker
docker-compose up -d

# Manual
uvicorn main:app --reload

# Access docs
open http://localhost:8000/docs
```

---

## 🧪 Testing (Example)

```python
# tests/models/test_candidate.py

from app.models import Candidate
from app.core import get_db_context

def test_create_candidate():
    with get_db_context() as db:
        candidate = Candidate(
            email="test@example.com",
            full_name="Test User",
            experience_level="mid"
        )
        db.add(candidate)
        db.commit()

        assert candidate.id is not None
        assert candidate.reputation_score == 50.0
```

---

## 📝 Best Practices

### 1. Always Import from Module Root

```python
# ✅ GOOD
from app.models import Candidate, ProjectSubmission
from app.core import settings, get_db
from app.services import GitAnalysisService

# ❌ AVOID (verbose)
from app.models.candidate import Candidate
from app.core.config import Settings
```

### 2. Use Settings for Configuration

```python
# ✅ GOOD
from app.core import settings
api_key = settings.OPENAI_API_KEY

# ❌ BAD
import os
api_key = os.getenv("OPENAI_API_KEY")
```

### 3. Use Database Dependency in Routes

```python
# ✅ GOOD (FastAPI handles cleanup)
from app.core import get_db

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# ❌ BAD (manual session management)
from app.core.database import SessionLocal
db = SessionLocal()
try:
    users = db.query(User).all()
finally:
    db.close()
```

---

## 🔄 Migration from Old Code

If you have existing code using the old structure:

### Old Code
```python
from models import Candidate, ProjectSubmission
from database import get_db
from git_service import GitAnalysisService
```

### New Code (just add `app.`)
```python
from app.models import Candidate, ProjectSubmission
from app.core import get_db
from app.services import GitAnalysisService
```

**That's it!** Just add `app.` prefix.

---

## 📚 Full Documentation

For complete documentation:
- **[CODEBASE_STRUCTURE.md](CODEBASE_STRUCTURE.md)** - Detailed structure guide
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Database schema
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[README-PLATFORM.md](README-PLATFORM.md)** - Platform overview

---

## ✅ Checklist for New Features

When adding a new feature:

- [ ] Models in `app/models/<domain>.py`
- [ ] Export in `app/models/__init__.py`
- [ ] Schemas in `app/schemas/<domain>.py` (when ready)
- [ ] Routes in `app/routers/<resource>.py` (when ready)
- [ ] Business logic in `app/services/<name>_service.py` if needed
- [ ] Update configuration in `app/core/config.py` if needed
- [ ] Create migration: `alembic revision --autogenerate`
- [ ] Test the feature

---

## 🎯 Summary

**Key Changes**:
1. ✅ Models split into 5 domain files
2. ✅ Configuration centralized in `app/core/config.py`
3. ✅ Services moved to `app/services/`
4. ✅ Clean imports from module roots

**Benefits**:
- 📖 **Easier to read**: Find code in seconds
- 🔧 **Easier to update**: Change one file, not massive files
- 🚀 **Easier to scale**: Add new models/routes without conflicts
- 🧪 **Easier to test**: Test individual modules

**Next Steps** (Coming Soon):
- Split schemas into `app/schemas/`
- Split routes into `app/routers/`
- Add test structure

---

**Questions? Check [CODEBASE_STRUCTURE.md](CODEBASE_STRUCTURE.md) for detailed explanations!**
