# App Package Structure

This is the main application package containing all modular components.

## 📁 Structure

```
app/
├── core/          # Configuration & database
├── models/        # Database models (SQLAlchemy)
├── schemas/       # Request/response schemas (Pydantic)
├── routers/       # API endpoints (FastAPI)
├── services/      # Business logic
└── main.py        # FastAPI app initialization
```

## 🚀 Quick Import Examples

```python
# Import models
from app.models import Candidate, ProjectSubmission, Evaluation

# Import configuration
from app.core import settings, get_db

# Import services
from app.services.git_service import GitAnalysisService
from app.services.ai_service import AICodeAnalysisService
```

## 📖 Full Documentation

See [CODEBASE_STRUCTURE.md](../CODEBASE_STRUCTURE.md) for complete documentation.
