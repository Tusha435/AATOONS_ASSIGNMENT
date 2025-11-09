# 📁 Codebase Structure - Modular Organization

This document explains the **new modular structure** of the Proof-of-Work Hiring Platform codebase.

## 🎯 Why We Reorganized

**Before**: Everything was in single files (`main.py`, `models.py`, `schemas.py`)
- Hard to find specific code
- Difficult to maintain
- Challenging to test individual components
- Not scalable

**After**: Clean, modular structure
- Easy to locate any feature
- Simple to update specific components
- Clear separation of concerns
- Ready to scale

---

## 📂 Directory Structure

```
hiring-platform/
│
├── app/                            # Main application package
│   │
│   ├── core/                       # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py              # Settings (from .env)
│   │   └── database.py            # DB connection & sessions
│   │
│   ├── models/                     # Database models (SQLAlchemy)
│   │   ├── __init__.py            # Exports all models
│   │   ├── common.py              # Base & enums
│   │   ├── candidate.py           # Candidate, SkillBadge, Leaderboard
│   │   ├── hr_manager.py          # HRManager, HRDashboard
│   │   ├── project.py             # ProjectTemplate, ProjectSubmission
│   │   ├── analysis.py            # CommitAnalysis, CodeQuality, AIAnalysis
│   │   └── evaluation.py          # Evaluation, HiringDecision, Comparison
│   │
│   ├── schemas/                    # Pydantic schemas (coming next)
│   │   ├── __init__.py
│   │   ├── candidate.py           # Candidate request/response schemas
│   │   ├── hr_manager.py          # HR schemas
│   │   ├── project.py             # Project schemas
│   │   └── evaluation.py          # Evaluation schemas
│   │
│   ├── routers/                    # API routes (FastAPI)
│   │   ├── __init__.py
│   │   ├── candidates.py          # /api/candidates endpoints
│   │   ├── hr_managers.py         # /api/hr-managers endpoints
│   │   ├── submissions.py         # /api/submissions endpoints
│   │   ├── evaluations.py         # /api/evaluations endpoints
│   │   ├── hiring.py              # /api/hiring-decisions endpoints
│   │   └── stats.py               # /api/stats, /api/leaderboard
│   │
│   ├── services/                   # Business logic services
│   │   ├── __init__.py
│   │   ├── git_service.py         # Git analysis (commit patterns)
│   │   └── ai_service.py          # AI code review & HR scoring
│   │
│   └── main.py                     # FastAPI app initialization
│
├── main.py                         # Entry point (imports from app/)
├── docker-compose.yml              # Docker setup
├── Dockerfile                      # Container definition
├── alembic.ini                     # DB migrations config
├── requirements-platform.txt       # Dependencies
├── .env.platform.example           # Environment template
│
└── docs/                           # Documentation
    ├── DATABASE_SCHEMA.md
    ├── ARCHITECTURE.md
    ├── README-PLATFORM.md
    └── CODEBASE_STRUCTURE.md      # This file!
```

---

## 🗂️ Module Breakdown

### **1. `app/core/` - Core Configuration**

Central configuration and database setup.

**Files**:
- `config.py` - **Settings management**
  - Loads from `.env` file
  - Uses Pydantic for validation
  - Single source of truth for all config
  - Example: `settings.OPENAI_API_KEY`

- `database.py` - **Database setup**
  - SQLAlchemy engine
  - Session management
  - `get_db()` dependency for FastAPI
  - `init_database()` helper

**Usage**:
```python
from app.core import settings, get_db

# Access settings
api_key = settings.OPENAI_API_KEY

# Use in route
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

---

### **2. `app/models/` - Database Models**

SQLAlchemy ORM models organized by domain.

**File Structure**:

| File | Contains | Purpose |
|------|----------|---------|
| `common.py` | Base, Enums | Shared base class and all enums |
| `candidate.py` | Candidate, SkillBadge, CandidateLeaderboard | Candidate-related models |
| `hr_manager.py` | HRManager, HRPerformanceDashboard | HR-related models |
| `project.py` | ProjectTemplate, ProjectSubmission | Project-related models |
| `analysis.py` | CommitAnalysis, CodeQualityMetric, AIAnalysis, AIInterviewSession | All analysis models |
| `evaluation.py` | Evaluation, HiringDecision, HRvsAIComparison | Evaluation & hiring models |

**Why this split?**
- **Domain-driven**: Each file represents a logical domain
- **Manageable size**: No file over 200 lines
- **Easy to find**: Want candidate model? Check `candidate.py`
- **Clear dependencies**: Relationships are explicit

**Usage**:
```python
from app.models import Candidate, ProjectSubmission, Evaluation

# All models available from single import
candidate = db.query(Candidate).first()
```

---

### **3. `app/schemas/` - Pydantic Schemas** (Coming Next)

Request/response validation schemas.

**Planned Structure**:
```
schemas/
├── candidate.py       # CandidateCreate, CandidateResponse, etc.
├── hr_manager.py      # HRManagerCreate, HRManagerResponse
├── project.py         # ProjectTemplateCreate, SubmissionResponse
└── evaluation.py      # EvaluationCreate, EvaluationResponse
```

**Why schemas?**
- Validate incoming requests
- Define response structure
- Auto-generate API docs
- Type safety

---

### **4. `app/routers/` - API Routes** (Coming Next)

FastAPI routers organized by resource.

**Planned Structure**:
```
routers/
├── candidates.py      # All /api/candidates/* routes
├── hr_managers.py     # All /api/hr-managers/* routes
├── submissions.py     # All /api/submissions/* routes
├── evaluations.py     # All /api/evaluations/* routes
├── hiring.py          # All /api/hiring-decisions/* routes
└── stats.py           # All /api/stats, /api/leaderboard routes
```

**Why split routes?**
- **Separation of concerns**: Each router handles one resource
- **Easier testing**: Test each router independently
- **Team collaboration**: Different devs can work on different routers
- **Clear API structure**: Routes map to files

**Example** (`routers/candidates.py`):
```python
from fastapi import APIRouter, Depends
from app.models import Candidate
from app.schemas.candidate import CandidateCreate, CandidateResponse

router = APIRouter(prefix="/api/candidates", tags=["candidates"])

@router.post("/", response_model=CandidateResponse)
def create_candidate(data: CandidateCreate, db: Session = Depends(get_db)):
    # ...
    return candidate
```

Then in `main.py`:
```python
from app.routers import candidates, hr_managers, submissions

app.include_router(candidates.router)
app.include_router(hr_managers.router)
app.include_router(submissions.router)
```

---

### **5. `app/services/` - Business Logic**

Core business logic and external integrations.

**Files**:
- `git_service.py` - **Git analysis**
  - Clone repositories
  - Analyze commit patterns
  - Detect AI-generated code
  - Calculate authenticity scores

- `ai_service.py` - **AI code review**
  - GPT-4 powered code analysis
  - Architecture review
  - HR evaluation scoring
  - AI interview bot

**Why services?**
- **Reusable logic**: Use same code in API, CLI, background jobs
- **Testable**: Easy to mock and unit test
- **Single responsibility**: Each service has one job
- **Clean separation**: Routes call services, services contain logic

**Usage**:
```python
from app.services.git_service import GitAnalysisService
from app.services.ai_service import AICodeAnalysisService

git_service = GitAnalysisService()
result = git_service.analyze_submission(submission_id)
```

---

## 🚀 How to Navigate the Codebase

### **Finding Code by Task**

| Task | Where to Look |
|------|---------------|
| Add a new API endpoint | `app/routers/<resource>.py` |
| Modify database schema | `app/models/<domain>.py` |
| Change validation rules | `app/schemas/<domain>.py` |
| Update configuration | `app/core/config.py` or `.env` |
| Add business logic | `app/services/<service>.py` |
| Change Git analysis | `app/services/git_service.py` |
| Modify AI review | `app/services/ai_service.py` |

### **Common Workflows**

**1. Add a new field to Candidate**:
```
1. Edit app/models/candidate.py (add column)
2. Create migration: alembic revision --autogenerate
3. Run migration: alembic upgrade head
4. Update app/schemas/candidate.py (add field to schemas)
5. Done!
```

**2. Add a new API endpoint**:
```
1. Add route to appropriate app/routers/<resource>.py
2. Create schema if needed in app/schemas/<resource>.py
3. Test the endpoint via /docs
```

**3. Change application settings**:
```
1. Add setting to app/core/config.py
2. Add to .env.platform.example
3. Set in your .env file
4. Access via settings.<YOUR_SETTING>
```

---

## 🔧 Import Conventions

### **Clean Imports**

```python
# ✅ GOOD: Import from module root
from app.models import Candidate, ProjectSubmission
from app.core import settings, get_db
from app.services.git_service import GitAnalysisService

# ❌ BAD: Don't import from nested modules
from app.models.candidate import Candidate  # Works but verbose
from app.core.config import Settings  # Use settings singleton instead
```

### **Circular Import Prevention**

The module structure is designed to avoid circular imports:

```
app/core/        # No dependencies (bottom layer)
    ↓
app/models/      # Depends on: core
    ↓
app/schemas/     # Depends on: models (for Pydantic from_attributes)
    ↓
app/services/    # Depends on: models, core
    ↓
app/routers/     # Depends on: models, schemas, services, core
    ↓
app/main.py      # Depends on: routers, core
```

**Rule**: Higher layers can import from lower layers, but not vice versa.

---

## 📝 File Naming Conventions

- **Models**: Singular noun (`candidate.py`, not `candidates.py`)
  - Contains: `Candidate` class

- **Routers**: Plural noun (`candidates.py`)
  - Contains: Routes for `/api/candidates`

- **Services**: Descriptive (`git_service.py`, `ai_service.py`)
  - Contains: `GitAnalysisService` class

- **Schemas**: Matches model (`candidate.py`)
  - Contains: `CandidateCreate`, `CandidateResponse`

---

## 🧪 Testing Structure (Future)

```
tests/
├── core/
│   └── test_config.py
├── models/
│   ├── test_candidate.py
│   ├── test_hr_manager.py
│   └── test_project.py
├── services/
│   ├── test_git_service.py
│   └── test_ai_service.py
└── routers/
    ├── test_candidates.py
    ├── test_submissions.py
    └── test_evaluations.py
```

**Convention**: Test file structure mirrors app structure.

---

## ✅ Benefits of This Structure

### **1. Scalability**
- Add new models without touching existing files
- New routes go in dedicated routers
- Services can be split further if needed

### **2. Maintainability**
- Find code in seconds (consistent structure)
- Change one thing without breaking others
- Clear dependencies

### **3. Team Collaboration**
- Multiple developers can work simultaneously
- Less merge conflicts
- Clear ownership of modules

### **4. Testing**
- Test individual components
- Mock dependencies easily
- Fast test suite (only test what changed)

### **5. Performance**
- Import only what you need
- Lazy loading possible
- Smaller module footprint

---

## 🔄 Migration from Old Structure

**Old → New Mapping**:

| Old File | New Location |
|----------|--------------|
| `models.py` | `app/models/*.py` (split by domain) |
| `schemas.py` | `app/schemas/*.py` (coming next) |
| `main.py` | `app/routers/*.py` + `app/main.py` |
| `database.py` | `app/core/database.py` |
| `git_service.py` | `app/services/git_service.py` |
| `ai_service.py` | `app/services/ai_service.py` |

---

## 📚 Next Steps

1. ✅ **Models**: Split into domain files
2. 🔜 **Schemas**: Split Pydantic schemas
3. 🔜 **Routers**: Split API routes
4. 🔜 **Services**: Move to app/services
5. 🔜 **Main**: Create new entry point
6. 🔜 **Tests**: Add test structure

---

## 💡 Quick Reference

**Starting the app**:
```bash
# Still works the same way!
docker-compose up -d
# OR
uvicorn main:app --reload
```

**Importing models**:
```python
from app.models import Candidate, ProjectSubmission, Evaluation
```

**Importing config**:
```python
from app.core import settings, get_db
```

**Adding a new model**:
1. Create in appropriate `app/models/<domain>.py`
2. Export in `app/models/__init__.py`
3. Create migration: `alembic revision --autogenerate`

**Adding a new route**:
1. Add to appropriate `app/routers/<resource>.py`
2. Include router in `app/main.py`

---

**This structure is designed for humans to easily read, understand, and update the codebase.**
