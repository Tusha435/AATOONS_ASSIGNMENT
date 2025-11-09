# Proof-of-Work Hiring Platform

## 🔥 The Breakthrough Idea

**A platform where both candidates and HR prove themselves through actual work, not theater.**

Traditional hiring is mutual deception:
- Candidates fake "passion" and memorize LeetCode
- HR runs 30-minute behavioral interviews and calls it "thorough evaluation"
- Both sides gamble and blame each other when it fails

**This platform makes lying impossible for both sides.**

---

## 🎯 How It Works

### **For Candidates:**

1. **Choose a Real Project** (not a coding quiz)
   - Browse challenges like "Build a chat system with E2E encryption"
   - Pick one that matches your skills (3-7 days to complete)

2. **Build It For Real**
   - Work in your own GitHub repo
   - Make iterative commits (we analyze your work pattern!)
   - Document your architecture decisions
   - Explain what you'd improve with more time

3. **Submit for Evaluation**
   - GitHub repo + demo (optional)
   - 2-3 min video walkthrough
   - System automatically analyzes:
     - Commit patterns (bulk vs iterative)
     - Code quality metrics
     - AI detection (did you just copy-paste from ChatGPT?)

4. **Get Matched with Companies**
   - HR managers review your work
   - You see their evaluation quality score too!
   - No more black-box rejections

### **For HR Managers:**

1. **Review Candidate Projects**
   - See full GitHub repo, commits, documentation
   - Get AI analysis insights (after you evaluate!)

2. **Submit Your Evaluation** (HERE'S THE CATCH)
   - You must explain what's good/bad technically
   - List strengths, weaknesses, interview questions
   - Predict: Will this candidate succeed?

3. **Get Scored by the System**
   - Did you catch what the AI caught?
   - Did you miss critical red flags?
   - Did you add insights AI couldn't?
   - **Your evaluation quality becomes your platform reputation**

4. **Track Outcomes**
   - System follows up at 90 days
   - Did your hire succeed?
   - **Your prediction accuracy is public**

---

## 🚀 Quick Start

### **Prerequisites**

- Python 3.11+
- PostgreSQL 15+
- Redis (for background jobs)
- OpenAI API key (for AI analysis)
- GitHub token (for repo analysis)

### **Installation**

```bash
# Clone repository
git clone <repo-url>
cd hiring-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-platform.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from database import init_database; init_database()"

# Run migrations (if using Alembic)
alembic upgrade head

# Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Using Docker (Recommended)**

```bash
# Start all services (API + PostgreSQL + Redis)
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Stop services
docker-compose down
```

---

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **Key Endpoints**

#### **Candidates**

```http
POST /api/candidates
GET  /api/candidates
GET  /api/candidates/{id}
PATCH /api/candidates/{id}
```

#### **Project Submissions**

```http
POST /api/submissions
GET  /api/submissions
GET  /api/submissions/{id}
GET  /api/submissions/{id}/commits  # See commit analysis
```

#### **Evaluations**

```http
POST /api/evaluations
GET  /api/evaluations/{id}
GET  /api/submissions/{id}/evaluations
```

#### **Hiring Decisions**

```http
POST /api/hiring-decisions
GET  /api/hiring-decisions/{id}
```

#### **Leaderboards & Stats**

```http
GET /api/leaderboard/candidates
GET /api/stats
```

---

## 🗄️ Database Schema

See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for complete schema documentation.

**Core Entities:**

- **Candidate**: Developers seeking employment
- **HRManager**: Hiring managers evaluating candidates
- **ProjectSubmission**: Candidate's completed work
- **Evaluation**: HR's assessment (gets scored!)
- **CommitAnalysis**: Git commit pattern analysis
- **AIAnalysis**: AI's code review
- **HiringDecision**: Actual hire outcomes (ground truth)

**Key Insight**: Everything is tracked, scored, and validated against 90-day outcomes.

---

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

```
Frontend (Next.js) → FastAPI Backend → PostgreSQL + Redis
                         ↓
                   Background Jobs (Celery)
                         ↓
              ┌──────────┴──────────┐
              ▼                     ▼
        Git Analysis           AI Analysis
     (commit patterns)      (code quality)
```

---

## 🔧 Services

### **1. Git Analysis Service** (`git_service.py`)

Analyzes GitHub repositories to detect work authenticity:

```python
from git_service import GitAnalysisService

service = GitAnalysisService()
result = service.analyze_submission(submission_id)

print(f"Authenticity Score: {result['pattern_analysis']['authenticity_score']}/100")
```

**What it detects:**
- Bulk commits (AI red flag)
- Commit message quality
- Iterative development patterns
- Time gaps between commits

### **2. AI Analysis Service** (`ai_service.py`)

Uses GPT-4 to evaluate code and compare HR assessments:

```python
from ai_service import AICodeAnalysisService

service = AICodeAnalysisService()

# Analyze candidate's code
result = service.analyze_submission_full(
    submission_id=submission_id,
    code_files={"main.py": code_content},
    project_description="Build a REST API"
)

# Score HR's evaluation
hr_score = service.score_hr_evaluation(evaluation_id)
print(f"HR Quality: {hr_score['hr_quality_score']}/100")
```

**What it evaluates:**
- Architecture quality (0-100)
- Production readiness (0-100)
- AI-generated probability (0-100)
- Strengths/weaknesses
- HR evaluation quality (by comparison)

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Test specific service
pytest tests/test_git_service.py -v
```

---

## 🚀 Deployment

### **Environment Variables**

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/hiring_platform

# API Keys
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# Environment
ENVIRONMENT=production
SQL_ECHO=false
```

### **Production Checklist**

- [ ] Set strong `SECRET_KEY`
- [ ] Configure CORS for your domain
- [ ] Enable HTTPS
- [ ] Setup database backups
- [ ] Configure rate limiting
- [ ] Setup monitoring (Sentry, Prometheus)
- [ ] Enable API key authentication
- [ ] Review security settings

---

## 📊 Example Workflow

### **Complete Candidate Journey**

```bash
# 1. Candidate registers
curl -X POST http://localhost:8000/api/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dev@example.com",
    "full_name": "Jane Developer",
    "github_username": "janedev",
    "experience_level": "mid",
    "skill_tags": ["Python", "FastAPI", "PostgreSQL"]
  }'

# Response: {"id": "uuid-here", "reputation_score": 50.0, ...}

# 2. Browse project templates
curl http://localhost:8000/api/project-templates?difficulty=medium

# 3. Candidate builds project in GitHub repo
# ... (5-7 days of work)

# 4. Submit project
curl -X POST http://localhost:8000/api/submissions?candidate_id=<candidate-id> \
  -H "Content-Type: application/json" \
  -d '{
    "github_repo_url": "https://github.com/janedev/my-project",
    "demo_url": "https://my-project-demo.herokuapp.com",
    "time_spent_hours": 35,
    "architecture_doc": "I built this using...",
    "trade_offs_doc": "I chose X over Y because..."
  }'

# 5. System automatically runs analysis (background jobs)
# - Git commit analysis
# - Code quality metrics
# - AI review

# 6. HR reviews and evaluates
curl -X POST http://localhost:8000/api/evaluations?hr_manager_id=<hr-id> \
  -H "Content-Type: application/json" \
  -d '{
    "submission_id": "<submission-id>",
    "technical_assessment": "Solid architecture, good error handling...",
    "strengths_identified": ["Clean code", "Good tests"],
    "weaknesses_identified": ["No input validation"],
    "interview_questions": ["How would you scale this?"],
    "hire_recommendation": "hire",
    "predicted_success_likelihood": 85
  }'

# 7. System scores HR's evaluation
# HR gets quality score based on how well they understood the code

# 8. If hired, system follows up at 90 days
# Outcome validates both candidate and HR predictions
```

---

## 🎯 Key Metrics Dashboard

The platform tracks these critical metrics:

### **Candidate Metrics**
- `reputation_score`: Overall platform reputation (0-100)
- `avg_project_score`: Quality of submissions
- `hire_success_rate`: % of hires that succeeded (90+ days)
- `total_submissions`: Work ethic indicator

### **HR Metrics**
- `evaluation_quality_score`: How well they assess code (0-100)
- `prediction_accuracy`: % of predictions that came true
- `avg_time_to_evaluate`: Efficiency metric
- `hire_success_rate`: % of their hires that succeeded

### **Platform Metrics**
- Total submissions this week
- Average candidate score trend
- Average HR quality trend
- Hire retention rate (90-day)

---

## 🔮 Roadmap

### **Phase 1: MVP** ✅ (You Are Here)
- [x] Database schema
- [x] FastAPI backend
- [x] Git analysis service
- [x] AI code review
- [x] HR evaluation system
- [ ] Basic frontend (Next.js)

### **Phase 2: Intelligence**
- [ ] AI interview bot
- [ ] Real-time HR vs AI comparison
- [ ] Skill badge system
- [ ] Candidate-company matching algorithm
- [ ] 90-day outcome tracking

### **Phase 3: Scale**
- [ ] Multi-language support
- [ ] ATS integrations
- [ ] White-label for enterprises
- [ ] Mobile app
- [ ] Video code walkthrough analysis

---

## 🤝 Contributing

We welcome contributions! See areas to improve:

1. **AI Models**: Improve code quality detection
2. **Commit Analysis**: Better AI-generated code detection
3. **HR Scoring**: Refine evaluation quality algorithms
4. **Frontend**: Build the UI (Next.js + React)
5. **Testing**: Increase test coverage

---

## 📜 License

[MIT License](LICENSE)

---

## 🙏 Acknowledgments

This platform is built on the insight that **both candidates and HR should be accountable for their claims through actual output.**

Inspired by the frustration of:
- Talented developers rejected after 4-hour whiteboard coding
- HR managers hiring based on "culture fit" gut feelings
- Both sides lying and then blaming each other

**Let's make hiring honest.**

---

## 📞 Support

- **Documentation**: See `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Email**: support@hiring-platform.com (future)

---

## 🎤 Final Thought

**Traditional hiring asks:**
- "Can you reverse a linked list in 15 minutes?"
- "Tell me about a time when..."

**This platform asks:**
- "Can you build something real in a week?"
- "Can you explain why you made these technical decisions?"
- "Did your prediction about this candidate come true?"

**That's the difference between theater and truth.**

---

Built with ❤️ and accountability
