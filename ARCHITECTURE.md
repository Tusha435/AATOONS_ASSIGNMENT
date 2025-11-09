# Proof-of-Work Hiring Platform - Architecture

## 🎯 Vision

**A platform where both candidates and HR prove themselves through actual work, not theater.**

Traditional hiring is mutual deception:
- Candidates memorize LeetCode and fake "passion"
- HR runs 30-minute behavioral interviews and calls it "thorough evaluation"
- Both gamble and blame each other when it fails

**This platform makes lying impossible for both sides.**

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Future)                           │
│                    Next.js + React + Tailwind                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ REST API
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                          FASTAPI BACKEND                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  API ROUTES                                                  │   │
│  │  - /api/candidates      - /api/hr-managers                  │   │
│  │  - /api/submissions     - /api/evaluations                  │   │
│  │  - /api/leaderboard     - /api/stats                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  BUSINESS LOGIC SERVICES                                     │   │
│  │  - Git Analysis Service     (commit pattern detection)      │   │
│  │  - AI Analysis Service      (code quality, architecture)    │   │
│  │  - Evaluation Service       (HR scoring & comparison)       │   │
│  │  - Matching Service         (candidate-company matching)    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                        DATA LAYER                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │   PostgreSQL     │  │   Redis Cache    │  │  ChromaDB/      │  │
│  │  (Core Data)     │  │  (Leaderboards)  │  │  (Embeddings)   │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                     EXTERNAL INTEGRATIONS                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │   GitHub     │  │   OpenAI     │  │   Background Jobs       │ │
│  │     API      │  │   GPT-4      │  │   (Celery + Redis)      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow: The Complete Journey

### **1. Candidate Journey**

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: Registration                                             │
│ POST /api/candidates                                             │
│ → Creates Candidate record                                       │
│ → Reputation starts at 50.0                                      │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Choose Project Challenge                                │
│ GET /api/project-templates?difficulty=medium                     │
│ → Browses available challenges                                   │
│ → Picks one that matches their skills                            │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: Build the Project (5-7 days)                            │
│ → Candidate works in their GitHub repo                           │
│ → Makes iterative commits (this is tracked!)                     │
│ → Writes architecture documentation                              │
│ → Records what they'd improve with more time                     │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: Submit Project                                           │
│ POST /api/submissions                                            │
│ → Provides GitHub repo URL                                       │
│ → Includes architecture doc, trade-offs doc                      │
│ → Optional: Demo URL, video explanation                          │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: Automated Analysis (Background Jobs)                    │
│                                                                   │
│ Job 1: Git Analysis                                              │
│ ├─ Clone repository                                              │
│ ├─ Analyze commit patterns                                       │
│ ├─ Detect bulk commits (AI red flag)                            │
│ ├─ Score commit message quality                                 │
│ └─ Calculate authenticity score                                 │
│                                                                   │
│ Job 2: Code Quality Analysis                                     │
│ ├─ Run static analysis (pylint, radon)                          │
│ ├─ Calculate cyclomatic complexity                              │
│ ├─ Security scan (bandit)                                        │
│ └─ Save metrics to database                                      │
│                                                                   │
│ Job 3: AI Code Review                                            │
│ ├─ GPT-4 reviews architecture                                    │
│ ├─ Evaluates production readiness                                │
│ ├─ Detects AI-generated probability                              │
│ ├─ Identifies strengths/weaknesses                               │
│ └─ Saves AI analysis to database                                 │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: Available for HR Evaluation                             │
│ → Submission appears in HR's review queue                        │
│ → Includes all analysis data                                     │
│ → HR can now evaluate                                            │
└──────────────────────────────────────────────────────────────────┘
```

### **2. HR Manager Journey**

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: Registration                                             │
│ POST /api/hr-managers                                            │
│ → Creates HRManager record                                       │
│ → Evaluation quality starts at 50.0                              │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Browse Candidate Submissions                            │
│ GET /api/submissions?status=submitted                            │
│ → See list of candidates who completed projects                 │
│ → Filter by tech stack, difficulty, etc.                         │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: Review Candidate's Work                                 │
│ GET /api/submissions/{id}                                        │
│ GET /api/submissions/{id}/commits                                │
│                                                                   │
│ HR sees:                                                          │
│ ├─ GitHub repo (can clone and review)                           │
│ ├─ Architecture documentation                                    │
│ ├─ Trade-offs explanation                                        │
│ ├─ Commit history analysis                                       │
│ ├─ Code quality metrics                                          │
│ └─ Demo/video (if provided)                                      │
│                                                                   │
│ HR does NOT see (yet):                                           │
│ └─ AI's evaluation (to avoid anchoring bias)                    │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: Submit Evaluation (The Critical Step!)                  │
│ POST /api/evaluations                                            │
│                                                                   │
│ HR MUST provide:                                                  │
│ ├─ Technical assessment (detailed write-up)                     │
│ ├─ Strengths identified (min 1)                                 │
│ ├─ Weaknesses identified (min 1)                                │
│ ├─ Interview questions they'd ask (min 3)                       │
│ ├─ Hire recommendation (reject/maybe/hire/strong_hire)          │
│ └─ Predicted success likelihood (0-100)                          │
│                                                                   │
│ This is where HR proves they understand the code!               │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: HR Evaluation Gets Scored (Background Job)              │
│                                                                   │
│ System compares HR's assessment to AI's:                         │
│ ├─ Did HR catch the key strengths AI found?                     │
│ ├─ Did HR identify the same weaknesses?                         │
│ ├─ Did HR miss critical red flags?                              │
│ ├─ Was their technical depth adequate?                          │
│ └─ Calculate HR quality score (0-100)                            │
│                                                                   │
│ Updates HR manager's metrics:                                    │
│ ├─ evaluation_quality_score (rolling average)                   │
│ ├─ evaluation_count++                                            │
│ └─ Time to evaluate (for efficiency tracking)                   │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: HR Sees Comparison Results                              │
│ GET /api/evaluations/{id}                                        │
│                                                                   │
│ Now HR can see:                                                   │
│ ├─ Their quality score for this evaluation                      │
│ ├─ What they caught that AI missed (credit!)                    │
│ ├─ What AI caught that they missed (learning!)                  │
│ └─ Suggestions for improvement                                   │
│                                                                   │
│ This is the accountability + learning loop.                      │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 7: Make Hiring Decision (Optional)                         │
│ POST /api/hiring-decisions                                       │
│ → Records the hire (job title, start date, etc.)                │
│ → System will follow up at 90 days for outcome                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 The Accountability Loop

### **90-Day Follow-Up (The Ground Truth)**

```
┌──────────────────────────────────────────────────────────────────┐
│ When a hire happens, system tracks:                             │
│                                                                   │
│ T+30 days:  Automated email "How's {candidate} doing?"          │
│ T+60 days:  Second check-in                                      │
│ T+90 days:  Final assessment (THE GROUND TRUTH)                 │
│                                                                   │
│ Questions asked:                                                  │
│ ├─ Is candidate still employed? (retention metric)              │
│ ├─ Performance rating (0-100)                                    │
│ ├─ Would you hire them again?                                    │
│ └─ What surprised you (good or bad)?                             │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ System uses this data to:                                        │
│                                                                   │
│ 1. Update HR's prediction accuracy                              │
│    └─ "HR predicted 85% success, actual was 90%" → High score   │
│                                                                   │
│ 2. Update Candidate's hire success rate                         │
│    └─ "3 out of 4 hires stayed 90+ days" → Strong signal        │
│                                                                   │
│ 3. Refine AI models                                              │
│    └─ "When AI flags X, it predicts Y outcome" → Learn          │
│                                                                   │
│ 4. Platform reputation scores                                    │
│    └─ Both HR and candidates get adjusted based on outcomes     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI vs HR Competition

### **The Breakthrough Feature**

```
┌─────────────────────────────────────────────────────────────────┐
│                    For Each Submission:                          │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐                  ┌──────────────────┐
    │   AI Analysis    │                  │  HR Evaluation   │
    │   (Automated)    │                  │   (Manual)       │
    └────────┬─────────┘                  └────────┬─────────┘
             │                                      │
             │  - Architecture score                │  - Technical assessment
             │  - Production readiness              │  - Strengths identified
             │  - AI-generated probability          │  - Weaknesses identified
             │  - Key strengths/weaknesses          │  - Hire recommendation
             │                                      │
             └──────────────┬───────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   Comparison Engine   │
                │                       │
                │  Did HR catch what    │
                │  AI caught?           │
                │                       │
                │  Did HR miss critical │
                │  red flags?           │
                │                       │
                │  Did HR add human     │
                │  insights AI missed?  │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   HR Quality Score    │
                │      (0-100)          │
                │                       │
                │  This becomes HR's    │
                │  platform reputation  │
                └───────────────────────┘
```

**Example Comparison:**

| Aspect | AI Found | HR Found | Score Impact |
|--------|----------|----------|--------------|
| Missing error handling | ✅ Yes | ❌ No | -15 points (critical miss) |
| Good architecture | ✅ Yes | ✅ Yes | +10 points (agreement) |
| Security vulnerability | ❌ No | ✅ Yes | +20 points (HR adds value!) |
| Overly complex code | ✅ Yes | ❌ No | -5 points (minor miss) |

**Result**: HR gets scored on **both alignment and unique insights**.

---

## 🗄️ Database Design Principles

### **1. Everything is Tracked**

```sql
-- Example: Every evaluation gets timestamped
Evaluation:
  - started_at    → When HR began reviewing
  - completed_at  → When they submitted
  - time_spent_minutes → Computed (efficiency metric)
```

**Why?** We can detect if HR is rubber-stamping (2-minute evaluations) vs. actually reviewing code (45+ minutes).

### **2. Scores are Computed, Not Declared**

```sql
-- Candidate reputation is NOT self-reported
Candidate.reputation_score = COMPUTED FROM:
  - avg_project_score (quality of work)
  - hire_success_rate (do they succeed in jobs?)
  - evaluation_count (how many HR reviewed them)
  - consistency (variance in scores)
```

### **3. Ground Truth Validates Everything**

```
HiringDecision.still_employed_at_90
  ↓
  Updates:
    - HR's prediction_accuracy
    - Candidate's hire_success_rate
    - AI model training data
```

**The 90-day outcome is the ultimate truth** that calibrates all predictions.

---

## 🔧 Technology Stack

### **Backend**
- **FastAPI** (Python 3.11+)
  - High performance, async support
  - Auto-generated OpenAPI docs
  - Type safety with Pydantic

### **Database**
- **PostgreSQL** (Core data)
  - ACID compliance
  - Complex queries, joins, aggregations
  - Full-text search

- **Redis** (Caching & Background Jobs)
  - Leaderboard caching
  - Celery task queue
  - Real-time data

### **AI/ML**
- **OpenAI GPT-4** (Code review, evaluation comparison)
- **CodeBERT** (Code similarity, plagiarism detection)
- **Custom ML** (Commit pattern analysis)

### **Git Integration**
- **GitPython** (Clone, analyze repos)
- **GitHub API** (Repo metadata)

### **Code Analysis**
- **Pylint** (Linting)
- **Radon** (Complexity metrics)
- **Bandit** (Security scanning)
- **Coverage.py** (Test coverage)

---

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         PRODUCTION                          │
└─────────────────────────────────────────────────────────────┘

Load Balancer (Nginx / AWS ALB)
    │
    ├─── FastAPI App (Docker, 4 replicas)
    │    └─── Gunicorn + Uvicorn workers
    │
    ├─── PostgreSQL (RDS / Managed DB)
    │    └─── Read replicas for analytics
    │
    ├─── Redis (ElastiCache / Managed Redis)
    │    └─── Clustering for HA
    │
    └─── Celery Workers (Docker, auto-scaling)
         ├─── Git analysis jobs
         ├─── AI analysis jobs
         └─── Notification jobs

Monitoring:
  - Prometheus (metrics)
  - Grafana (dashboards)
  - Sentry (error tracking)
  - CloudWatch (logs)
```

---

## 🔐 Security Considerations

### **Data Privacy**
- PII encryption at rest (email, names)
- GDPR compliance (right to deletion, export)
- Row-level security (multi-tenant isolation)

### **API Security**
- JWT authentication
- Rate limiting (prevent abuse)
- API key rotation
- CORS policies

### **Code Analysis Safety**
- Sandboxed code execution (never run user code directly)
- Malware scanning before analysis
- Resource limits (prevent DOS via huge repos)

---

## 📈 Scalability Strategy

### **Phase 1: MVP (0-1,000 users)**
- Single FastAPI server
- Managed PostgreSQL
- Synchronous processing

### **Phase 2: Growth (1K-10K users)**
- Add Celery for async jobs
- Redis caching
- Read replicas for DB

### **Phase 3: Scale (10K-100K users)**
- Kubernetes for auto-scaling
- CDN for static assets
- Database sharding by company
- Microservices split (if needed)

---

## 🎯 Key Metrics to Track

### **Platform Health**
- Total submissions / week
- Evaluation completion rate
- Average time from submission → hire
- User retention (candidates & HR)

### **Quality Metrics**
- Average candidate score trend
- Average HR quality score trend
- Hire success rate (90-day retention)
- AI vs HR agreement rate

### **Business Metrics**
- Revenue per hire
- Subscription conversion rate
- Churn rate
- LTV:CAC ratio

---

## 🔮 Future Enhancements

### **Phase 2 Features**
- Real-time AI interview bot
- Video code walkthrough analysis
- Skill badge system with expiry
- Company-specific templates

### **Phase 3 Features**
- Multi-language support
- Integration with ATS systems
- Candidate referral marketplace
- HR training program (improve low-scoring HR)

### **Advanced AI**
- Predict hire success before HR evaluates
- Detect interview coaching vs genuine skill
- Personalized project recommendations
- Auto-generate interview questions

---

## ✅ Why This Architecture Works

1. **Accountability is Built-In**
   - Every action is tracked and scored
   - Ground truth (90-day outcomes) validates predictions

2. **Scalable from Day 1**
   - Async background jobs
   - Caching layer ready
   - Database designed for growth

3. **AI Enhances, Not Replaces**
   - AI evaluates code objectively
   - HR adds human judgment
   - System learns which matters when

4. **Data-Driven Improvement**
   - Every hire teaches the system
   - HR gets better through feedback
   - Candidates see what good looks like

---

**This is not an HR platform. This is a truth engine for hiring.**
