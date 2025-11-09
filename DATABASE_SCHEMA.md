# Proof-of-Work Hiring Platform - Database Schema

## Core Philosophy
Both candidates and HR managers are scored based on **actual work output**, not theater. The database tracks every action, decision, and outcome to build an accountability system.

---

## Entity Relationship Overview

```
Candidate (1) ──── (M) ProjectSubmission ──── (M) Evaluation ──── (M) HRManager
                         │                          │
                         │                          └──── (1) HiringDecision
                         │
                         └──── (M) CommitAnalysis
                         └──── (M) CodeQualityMetric
                         └──── (M) AIAnalysis
```

---

## 📊 Core Entities

### 1. **Candidate**

**Purpose**: Developers seeking employment through proof-of-work

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `email` | String(255) | Contact email | Unique, NOT NULL |
| `full_name` | String(255) | Full name | NOT NULL |
| `github_username` | String(100) | GitHub handle | Unique, Indexed |
| `portfolio_url` | String(500) | Personal website | Nullable |
| `created_at` | DateTime | Registration date | Default: NOW() |
| `last_active` | DateTime | Last platform activity | Auto-updated |
| `skill_tags` | JSON | Skills array | Default: [] |
| `experience_level` | Enum | junior/mid/senior | NOT NULL |
| `hire_success_rate` | Float | % of successful placements | Default: NULL |
| `avg_project_score` | Float | Average across submissions | Computed |
| `total_submissions` | Integer | Count of projects | Default: 0 |
| `is_verified` | Boolean | Email + GitHub verified | Default: False |
| `reputation_score` | Float | Platform reputation (0-100) | Default: 50.0 |

**Indexes**:
- `idx_candidate_email` (email)
- `idx_candidate_github` (github_username)
- `idx_candidate_reputation` (reputation_score DESC)

---

### 2. **HRManager**

**Purpose**: Hiring managers who evaluate candidates

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `email` | String(255) | Contact email | Unique, NOT NULL |
| `full_name` | String(255) | Full name | NOT NULL |
| `company_name` | String(255) | Employer | NOT NULL |
| `job_title` | String(200) | Role title | NOT NULL |
| `created_at` | DateTime | Registration date | Default: NOW() |
| `evaluation_count` | Integer | Total evaluations done | Default: 0 |
| `evaluation_quality_score` | Float | Assessment accuracy (0-100) | Default: 50.0 |
| `prediction_accuracy` | Float | Hire success prediction % | Computed |
| `avg_time_to_evaluate` | Float | Average hours to evaluate | Computed |
| `is_verified` | Boolean | Company email verified | Default: False |
| `subscription_tier` | Enum | free/pro/enterprise | Default: free |
| `hire_success_rate` | Float | % of hires that stayed 90+ days | Computed |

**Indexes**:
- `idx_hr_email` (email)
- `idx_hr_quality` (evaluation_quality_score DESC)
- `idx_hr_company` (company_name)

---

### 3. **ProjectTemplate**

**Purpose**: Standardized challenges for candidates

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `title` | String(255) | Project name | NOT NULL |
| `description` | Text | Full requirements | NOT NULL |
| `difficulty_level` | Enum | easy/medium/hard/expert | NOT NULL |
| `tech_stack` | JSON | Required technologies | NOT NULL |
| `estimated_hours` | Integer | Expected time to complete | NOT NULL |
| `max_duration_days` | Integer | Deadline (days) | Default: 7 |
| `created_by` | UUID | Author (HR or admin) | FK: hr_managers.id |
| `is_public` | Boolean | Available to all candidates | Default: True |
| `usage_count` | Integer | Times used | Default: 0 |
| `avg_completion_rate` | Float | % who finish | Computed |
| `evaluation_rubric` | JSON | Scoring criteria | NOT NULL |
| `created_at` | DateTime | Creation date | Default: NOW() |

**Indexes**:
- `idx_project_difficulty` (difficulty_level)
- `idx_project_public` (is_public)

---

### 4. **ProjectSubmission**

**Purpose**: Candidate's completed work

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `candidate_id` | UUID | Submitter | FK: candidates.id, NOT NULL |
| `project_template_id` | UUID | Challenge chosen | FK: project_templates.id |
| `github_repo_url` | String(500) | Repository link | NOT NULL, Unique |
| `demo_url` | String(500) | Live demo (optional) | Nullable |
| `video_explanation_url` | String(500) | Walkthrough video | Nullable |
| `started_at` | DateTime | Project start time | NOT NULL |
| `submitted_at` | DateTime | Submission time | NOT NULL |
| `time_spent_hours` | Float | Self-reported hours | NOT NULL |
| `architecture_doc` | Text | Technical decisions | NOT NULL |
| `trade_offs_doc` | Text | What I'd improve | NOT NULL |
| `status` | Enum | draft/submitted/evaluated | Default: draft |
| `code_quality_score` | Float | Automated score (0-100) | Computed |
| `ai_likelihood_score` | Float | AI-generated probability | Computed |
| `commit_count` | Integer | Git commits | Extracted from repo |
| `overall_score` | Float | Final composite score | Computed |

**Indexes**:
- `idx_submission_candidate` (candidate_id)
- `idx_submission_status` (status)
- `idx_submission_date` (submitted_at DESC)

---

### 5. **CommitAnalysis**

**Purpose**: Git commit pattern analysis to detect authenticity

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `submission_id` | UUID | Project reference | FK: project_submissions.id |
| `commit_hash` | String(40) | Git SHA | NOT NULL |
| `commit_message` | Text | Message content | NOT NULL |
| `commit_timestamp` | DateTime | When committed | NOT NULL |
| `files_changed` | Integer | Files modified | NOT NULL |
| `lines_added` | Integer | LOC added | NOT NULL |
| `lines_deleted` | Integer | LOC deleted | NOT NULL |
| `is_bulk_commit` | Boolean | Suspicious pattern flag | Computed |
| `time_gap_hours` | Float | Hours since last commit | Computed |
| `message_quality_score` | Float | Commit msg quality (0-10) | AI-scored |

**Indexes**:
- `idx_commit_submission` (submission_id)
- `idx_commit_timestamp` (commit_timestamp)

---

### 6. **CodeQualityMetric**

**Purpose**: Automated code analysis results

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `submission_id` | UUID | Project reference | FK: project_submissions.id |
| `cyclomatic_complexity` | Float | Code complexity | Nullable |
| `test_coverage` | Float | % coverage | Nullable |
| `linting_errors` | Integer | Linter violations | Default: 0 |
| `security_vulnerabilities` | Integer | Security issues found | Default: 0 |
| `documentation_score` | Float | Comment/doc quality (0-100) | Computed |
| `code_duplication` | Float | % duplicated code | Computed |
| `maintainability_index` | Float | Maintainability (0-100) | Computed |
| `architecture_score` | Float | Design patterns (0-100) | AI-scored |
| `analyzed_at` | DateTime | Analysis timestamp | Default: NOW() |

**Indexes**:
- `idx_quality_submission` (submission_id)

---

### 7. **AIAnalysis**

**Purpose**: GPT-4 evaluation of code and documentation

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `submission_id` | UUID | Project reference | FK: project_submissions.id |
| `model_used` | String(100) | AI model name | NOT NULL |
| `architecture_review` | Text | Design assessment | NOT NULL |
| `code_review` | Text | Code quality review | NOT NULL |
| `documentation_review` | Text | Docs assessment | NOT NULL |
| `creativity_score` | Float | Innovation rating (0-100) | NOT NULL |
| `production_readiness` | Float | Deployability (0-100) | NOT NULL |
| `ai_generated_probability` | Float | Likelihood AI-written (0-100) | NOT NULL |
| `key_strengths` | JSON | Positive highlights | NOT NULL |
| `key_weaknesses` | JSON | Areas to improve | NOT NULL |
| `analyzed_at` | DateTime | Analysis timestamp | Default: NOW() |

**Indexes**:
- `idx_ai_submission` (submission_id)

---

### 8. **Evaluation**

**Purpose**: HR manager's assessment of a candidate's project

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `submission_id` | UUID | Project evaluated | FK: project_submissions.id |
| `hr_manager_id` | UUID | Evaluator | FK: hr_managers.id |
| `started_at` | DateTime | When evaluation began | NOT NULL |
| `completed_at` | DateTime | When submitted | NOT NULL |
| `time_spent_minutes` | Float | Evaluation duration | Computed |
| `technical_assessment` | Text | What HR thinks technically | NOT NULL |
| `strengths_identified` | JSON | What they saw as strong | NOT NULL |
| `weaknesses_identified` | JSON | Red flags noticed | NOT NULL |
| `interview_questions` | JSON | Questions they'd ask | NOT NULL |
| `hire_recommendation` | Enum | reject/maybe/hire/strong_hire | NOT NULL |
| `predicted_success_likelihood` | Float | Will they succeed? (0-100) | NOT NULL |
| `hr_quality_score` | Float | How good was this eval? (0-100) | Computed |
| `delta_from_ai` | Float | Difference from AI assessment | Computed |
| `evaluation_depth_score` | Float | Thoroughness (0-100) | Computed |

**Indexes**:
- `idx_eval_submission` (submission_id)
- `idx_eval_hr` (hr_manager_id)
- `idx_eval_quality` (hr_quality_score DESC)

---

### 9. **HiringDecision**

**Purpose**: Track actual hiring outcomes

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `evaluation_id` | UUID | Evaluation that led to hire | FK: evaluations.id |
| `candidate_id` | UUID | Hired candidate | FK: candidates.id |
| `hr_manager_id` | UUID | Hiring manager | FK: hr_managers.id |
| `hired_at` | DateTime | Hire date | NOT NULL |
| `job_title` | String(255) | Position filled | NOT NULL |
| `salary_range` | String(100) | Compensation band | Nullable |
| `start_date` | Date | Employment start | NOT NULL |
| `90_day_check_in` | Enum | success/struggling/left | Nullable |
| `90_day_notes` | Text | Performance notes | Nullable |
| `still_employed_at_90` | Boolean | Retention success | Nullable |
| `actual_performance` | Float | Manager rating (0-100) | Nullable |
| `prediction_accuracy` | Float | How accurate was HR? | Computed |

**Indexes**:
- `idx_hire_candidate` (candidate_id)
- `idx_hire_hr` (hr_manager_id)
- `idx_hire_date` (hired_at DESC)

---

### 10. **AIInterviewSession**

**Purpose**: AI bot interview of candidates (competing with HR)

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `submission_id` | UUID | Project context | FK: project_submissions.id |
| `candidate_id` | UUID | Interviewee | FK: candidates.id |
| `started_at` | DateTime | Interview start | NOT NULL |
| `completed_at` | DateTime | Interview end | Nullable |
| `total_questions_asked` | Integer | Q&A count | Default: 0 |
| `conversation_log` | JSON | Full Q&A history | NOT NULL |
| `technical_depth_score` | Float | How deep AI went (0-100) | Computed |
| `communication_score` | Float | Candidate clarity (0-100) | AI-scored |
| `reasoning_score` | Float | Problem-solving (0-100) | AI-scored |
| `adaptability_score` | Float | Handles unknowns (0-100) | AI-scored |
| `overall_ai_recommendation` | Enum | reject/maybe/hire/strong_hire | NOT NULL |
| `confidence_level` | Float | AI's certainty (0-100) | NOT NULL |

**Indexes**:
- `idx_ai_interview_submission` (submission_id)
- `idx_ai_interview_candidate` (candidate_id)

---

### 11. **HRvsAIComparison**

**Purpose**: Track who's better at predicting success: HR or AI

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `submission_id` | UUID | Evaluated project | FK: project_submissions.id |
| `evaluation_id` | UUID | HR assessment | FK: evaluations.id |
| `ai_interview_id` | UUID | AI assessment | FK: ai_interview_sessions.id |
| `hr_recommendation` | Enum | HR decision | NOT NULL |
| `ai_recommendation` | Enum | AI decision | NOT NULL |
| `agreement_level` | Enum | same/similar/different | Computed |
| `hr_caught_issues` | JSON | Issues only HR saw | Nullable |
| `ai_caught_issues` | JSON | Issues only AI saw | Nullable |
| `actual_outcome` | Enum | hired_success/hired_fail/rejected | Nullable |
| `winner` | Enum | hr/ai/tie | Computed after hire |

**Indexes**:
- `idx_comparison_submission` (submission_id)

---

### 12. **SkillBadge**

**Purpose**: Verified skill credentials earned through projects

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | PK, Auto-generated |
| `candidate_id` | UUID | Badge earner | FK: candidates.id |
| `skill_name` | String(100) | Technology/skill | NOT NULL |
| `proficiency_level` | Enum | beginner/intermediate/advanced/expert | NOT NULL |
| `earned_via_submission` | UUID | Proof project | FK: project_submissions.id |
| `earned_at` | DateTime | Award date | Default: NOW() |
| `expiry_date` | DateTime | Badge expiration | Nullable |
| `is_verified` | Boolean | Platform verified | Default: True |

**Indexes**:
- `idx_badge_candidate` (candidate_id)
- `idx_badge_skill` (skill_name)

---

## 🔍 Key Computed Fields & Triggers

### Candidate Metrics (Updated on ProjectSubmission events)
```sql
avg_project_score = AVG(overall_score) FROM project_submissions WHERE candidate_id = X
hire_success_rate = COUNT(still_employed_at_90=True) / COUNT(*) FROM hiring_decisions WHERE candidate_id = X
```

### HR Metrics (Updated on Evaluation and HiringDecision events)
```sql
evaluation_quality_score = AVG(hr_quality_score) FROM evaluations WHERE hr_manager_id = X
prediction_accuracy = AVG(prediction_accuracy) FROM hiring_decisions WHERE hr_manager_id = X
avg_time_to_evaluate = AVG(time_spent_minutes) FROM evaluations WHERE hr_manager_id = X
```

### Submission Scoring (Computed after analysis completion)
```sql
overall_score = WEIGHTED_AVG(
  code_quality_score * 0.3,
  ai_analysis.production_readiness * 0.2,
  commit_pattern_score * 0.2,
  documentation_score * 0.15,
  creativity_score * 0.15
)
```

---

## 🎯 Critical Indexes for Performance

```sql
-- Candidate search/ranking
CREATE INDEX idx_candidate_reputation ON candidates(reputation_score DESC);
CREATE INDEX idx_candidate_experience ON candidates(experience_level);

-- Project submission queries
CREATE INDEX idx_submission_composite ON project_submissions(status, submitted_at DESC);
CREATE INDEX idx_submission_score ON project_submissions(overall_score DESC);

-- HR performance tracking
CREATE INDEX idx_hr_performance ON hr_managers(evaluation_quality_score DESC, prediction_accuracy DESC);

-- Hiring outcome analysis
CREATE INDEX idx_hiring_outcomes ON hiring_decisions(still_employed_at_90, hired_at DESC);

-- AI vs HR comparisons
CREATE INDEX idx_comparison_outcomes ON hr_vs_ai_comparisons(actual_outcome, agreement_level);
```

---

## 🔐 Security & Privacy Considerations

1. **PII Encryption**: Encrypt `email`, `full_name` at rest
2. **Access Control**: Row-level security for multi-tenant isolation
3. **Audit Logging**: Track all evaluation access (who viewed what when)
4. **GDPR Compliance**:
   - Right to deletion (cascade rules)
   - Data export functionality
   - Consent tracking for data usage
5. **Rate Limiting**: Prevent evaluation farming (max N evals/day per HR)

---

## 📈 Analytics Views (Materialized for Performance)

### `candidate_leaderboard`
```sql
CREATE MATERIALIZED VIEW candidate_leaderboard AS
SELECT
  c.id, c.full_name, c.reputation_score,
  COUNT(ps.id) as total_projects,
  AVG(ps.overall_score) as avg_score,
  COUNT(hd.id) as total_hires
FROM candidates c
LEFT JOIN project_submissions ps ON c.id = ps.candidate_id
LEFT JOIN hiring_decisions hd ON c.id = hd.candidate_id
GROUP BY c.id
ORDER BY reputation_score DESC;
```

### `hr_performance_dashboard`
```sql
CREATE MATERIALIZED VIEW hr_performance_dashboard AS
SELECT
  hr.id, hr.full_name, hr.company_name,
  hr.evaluation_quality_score,
  hr.prediction_accuracy,
  COUNT(e.id) as total_evaluations,
  COUNT(hd.id) as total_hires,
  AVG(hd.actual_performance) as avg_hire_quality
FROM hr_managers hr
LEFT JOIN evaluations e ON hr.id = e.hr_manager_id
LEFT JOIN hiring_decisions hd ON hr.id = hd.hr_manager_id
GROUP BY hr.id;
```

---

## 🚀 Next Steps

1. ✅ Implement this schema in **SQLAlchemy models**
2. ✅ Create **Alembic migrations**
3. ✅ Build **FastAPI endpoints** for CRUD operations
4. ✅ Implement **background jobs** (Celery) for code analysis
5. ✅ Add **PostgreSQL full-text search** for project discovery
6. ✅ Setup **Redis caching** for leaderboards

---

**This schema is the foundation for a platform where lying is impossible - both candidates and HR are judged by their actual output.**
