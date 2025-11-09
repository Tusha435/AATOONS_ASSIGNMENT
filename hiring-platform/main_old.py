"""
Proof-of-Work Hiring Platform - Main FastAPI Application

A platform where both candidates and HR prove themselves through actual work.
No theater. No deception. Just real output and accountability.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import get_db, init_database
from models import (
    Candidate, HRManager, ProjectTemplate, ProjectSubmission,
    Evaluation, CodeQualityMetric, AIAnalysis, CommitAnalysis,
    HiringDecision, CandidateLeaderboard
)
from schemas import (
    CandidateCreate, CandidateUpdate, CandidateResponse,
    HRManagerCreate, HRManagerResponse,
    ProjectTemplateCreate, ProjectTemplateResponse,
    ProjectSubmissionCreate, ProjectSubmissionUpdate, ProjectSubmissionResponse,
    EvaluationCreate, EvaluationResponse,
    CodeQualityMetricResponse, AIAnalysisResponse, CommitAnalysisResponse,
    HiringDecisionCreate, HiringDecisionResponse,
    LeaderboardEntry, PlatformStats, ErrorResponse
)

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Proof-of-Work Hiring Platform",
    description="A platform where both candidates and HR prove competence through real work",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Proof-of-Work Hiring Platform API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check with database connectivity test
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


# ============================================================================
# CANDIDATE ENDPOINTS
# ============================================================================

@app.post("/api/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(candidate_data: CandidateCreate, db: Session = Depends(get_db)):
    """
    Register a new candidate on the platform.

    Candidates prove their skills through project submissions.
    """
    # Check if email already exists
    existing = db.query(Candidate).filter(Candidate.email == candidate_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create candidate
    candidate = Candidate(
        email=candidate_data.email,
        full_name=candidate_data.full_name,
        github_username=candidate_data.github_username,
        portfolio_url=str(candidate_data.portfolio_url) if candidate_data.portfolio_url else None,
        skill_tags=candidate_data.skill_tags,
        experience_level=candidate_data.experience_level
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@app.get("/api/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Get candidate profile by ID"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@app.get("/api/candidates", response_model=List[CandidateResponse])
def list_candidates(
    skip: int = 0,
    limit: int = 50,
    experience_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all candidates with optional filtering.

    Supports pagination and filtering by experience level.
    """
    query = db.query(Candidate)

    if experience_level:
        query = query.filter(Candidate.experience_level == experience_level)

    candidates = query.order_by(Candidate.reputation_score.desc()).offset(skip).limit(limit).all()
    return candidates


@app.patch("/api/candidates/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: str,
    update_data: CandidateUpdate,
    db: Session = Depends(get_db)
):
    """Update candidate profile"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Update fields
    for field, value in update_data.model_dump(exclude_unset=True).items():
        if field == "portfolio_url" and value:
            value = str(value)
        setattr(candidate, field, value)

    db.commit()
    db.refresh(candidate)
    return candidate


# ============================================================================
# HR MANAGER ENDPOINTS
# ============================================================================

@app.post("/api/hr-managers", response_model=HRManagerResponse, status_code=status.HTTP_201_CREATED)
def create_hr_manager(hr_data: HRManagerCreate, db: Session = Depends(get_db)):
    """
    Register a new HR manager.

    HR managers are scored based on evaluation quality and prediction accuracy.
    """
    # Check if email already exists
    existing = db.query(HRManager).filter(HRManager.email == hr_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hr_manager = HRManager(
        email=hr_data.email,
        full_name=hr_data.full_name,
        company_name=hr_data.company_name,
        job_title=hr_data.job_title
    )

    db.add(hr_manager)
    db.commit()
    db.refresh(hr_manager)
    return hr_manager


@app.get("/api/hr-managers/{hr_id}", response_model=HRManagerResponse)
def get_hr_manager(hr_id: str, db: Session = Depends(get_db)):
    """Get HR manager profile by ID"""
    hr_manager = db.query(HRManager).filter(HRManager.id == hr_id).first()
    if not hr_manager:
        raise HTTPException(status_code=404, detail="HR manager not found")
    return hr_manager


@app.get("/api/hr-managers", response_model=List[HRManagerResponse])
def list_hr_managers(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all HR managers, ordered by evaluation quality"""
    hr_managers = db.query(HRManager).order_by(
        HRManager.evaluation_quality_score.desc()
    ).offset(skip).limit(limit).all()
    return hr_managers


# ============================================================================
# PROJECT TEMPLATE ENDPOINTS
# ============================================================================

@app.post("/api/project-templates", response_model=ProjectTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_project_template(
    template_data: ProjectTemplateCreate,
    hr_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Create a new project template.

    Can be public (available to all) or company-specific.
    """
    template = ProjectTemplate(
        title=template_data.title,
        description=template_data.description,
        difficulty_level=template_data.difficulty_level,
        tech_stack=template_data.tech_stack,
        estimated_hours=template_data.estimated_hours,
        max_duration_days=template_data.max_duration_days,
        is_public=template_data.is_public,
        evaluation_rubric=template_data.evaluation_rubric,
        created_by=hr_id
    )

    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@app.get("/api/project-templates/{template_id}", response_model=ProjectTemplateResponse)
def get_project_template(template_id: str, db: Session = Depends(get_db)):
    """Get project template by ID"""
    template = db.query(ProjectTemplate).filter(ProjectTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Project template not found")
    return template


@app.get("/api/project-templates", response_model=List[ProjectTemplateResponse])
def list_project_templates(
    skip: int = 0,
    limit: int = 50,
    difficulty: Optional[str] = None,
    is_public: bool = True,
    db: Session = Depends(get_db)
):
    """
    List available project templates.

    Candidates browse these to choose what to build.
    """
    query = db.query(ProjectTemplate).filter(ProjectTemplate.is_public == is_public)

    if difficulty:
        query = query.filter(ProjectTemplate.difficulty_level == difficulty)

    templates = query.order_by(ProjectTemplate.usage_count.desc()).offset(skip).limit(limit).all()
    return templates


# ============================================================================
# PROJECT SUBMISSION ENDPOINTS
# ============================================================================

@app.post("/api/submissions", response_model=ProjectSubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_submission(
    submission_data: ProjectSubmissionCreate,
    candidate_id: str,
    db: Session = Depends(get_db)
):
    """
    Submit a completed project for evaluation.

    This is the candidate's proof-of-work.
    """
    from datetime import datetime

    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Create submission
    submission = ProjectSubmission(
        candidate_id=candidate_id,
        project_template_id=submission_data.project_template_id,
        github_repo_url=str(submission_data.github_repo_url),
        demo_url=str(submission_data.demo_url) if submission_data.demo_url else None,
        video_explanation_url=str(submission_data.video_explanation_url) if submission_data.video_explanation_url else None,
        started_at=datetime.utcnow(),  # Should be provided by client in real implementation
        submitted_at=datetime.utcnow(),
        time_spent_hours=submission_data.time_spent_hours,
        architecture_doc=submission_data.architecture_doc,
        trade_offs_doc=submission_data.trade_offs_doc,
        status="submitted"
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Update candidate's total submissions
    candidate.total_submissions += 1
    db.commit()

    return submission


@app.get("/api/submissions/{submission_id}", response_model=ProjectSubmissionResponse)
def get_submission(submission_id: str, db: Session = Depends(get_db)):
    """Get project submission by ID"""
    submission = db.query(ProjectSubmission).filter(ProjectSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@app.get("/api/submissions", response_model=List[ProjectSubmissionResponse])
def list_submissions(
    skip: int = 0,
    limit: int = 50,
    candidate_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List project submissions with filtering.

    HR managers use this to find candidates to evaluate.
    """
    query = db.query(ProjectSubmission)

    if candidate_id:
        query = query.filter(ProjectSubmission.candidate_id == candidate_id)

    if status_filter:
        query = query.filter(ProjectSubmission.status == status_filter)

    submissions = query.order_by(ProjectSubmission.submitted_at.desc()).offset(skip).limit(limit).all()
    return submissions


@app.get("/api/submissions/{submission_id}/commits", response_model=List[CommitAnalysisResponse])
def get_submission_commits(submission_id: str, db: Session = Depends(get_db)):
    """
    Get commit analysis for a submission.

    Shows the candidate's work pattern - real developers iterate, AI does bulk commits.
    """
    commits = db.query(CommitAnalysis).filter(
        CommitAnalysis.submission_id == submission_id
    ).order_by(CommitAnalysis.commit_timestamp.asc()).all()

    return commits


# ============================================================================
# EVALUATION ENDPOINTS
# ============================================================================

@app.post("/api/evaluations", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_evaluation(
    evaluation_data: EvaluationCreate,
    hr_manager_id: str,
    db: Session = Depends(get_db)
):
    """
    Submit an evaluation of a candidate's project.

    This is where HR proves they understand what they're evaluating.
    The system will score this evaluation against AI analysis.
    """
    from datetime import datetime

    # Verify HR manager exists
    hr_manager = db.query(HRManager).filter(HRManager.id == hr_manager_id).first()
    if not hr_manager:
        raise HTTPException(status_code=404, detail="HR manager not found")

    # Verify submission exists
    submission = db.query(ProjectSubmission).filter(
        ProjectSubmission.id == evaluation_data.submission_id
    ).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Create evaluation
    evaluation = Evaluation(
        submission_id=evaluation_data.submission_id,
        hr_manager_id=hr_manager_id,
        started_at=datetime.utcnow(),  # Should track from when they started viewing
        completed_at=datetime.utcnow(),
        technical_assessment=evaluation_data.technical_assessment,
        strengths_identified=evaluation_data.strengths_identified,
        weaknesses_identified=evaluation_data.weaknesses_identified,
        interview_questions=evaluation_data.interview_questions,
        hire_recommendation=evaluation_data.hire_recommendation,
        predicted_success_likelihood=evaluation_data.predicted_success_likelihood
    )

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    # Update HR manager's evaluation count
    hr_manager.evaluation_count += 1
    db.commit()

    # TODO: Trigger async job to compare with AI analysis and score the evaluation

    return evaluation


@app.get("/api/evaluations/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    """Get evaluation by ID"""
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation


@app.get("/api/submissions/{submission_id}/evaluations", response_model=List[EvaluationResponse])
def get_submission_evaluations(submission_id: str, db: Session = Depends(get_db)):
    """Get all evaluations for a specific submission"""
    evaluations = db.query(Evaluation).filter(
        Evaluation.submission_id == submission_id
    ).all()
    return evaluations


# ============================================================================
# HIRING DECISION ENDPOINTS
# ============================================================================

@app.post("/api/hiring-decisions", response_model=HiringDecisionResponse, status_code=status.HTTP_201_CREATED)
def create_hiring_decision(
    decision_data: HiringDecisionCreate,
    db: Session = Depends(get_db)
):
    """
    Record a hiring decision.

    This is the ground truth that will be used to measure both HR and AI prediction accuracy.
    """
    from datetime import datetime

    # Verify evaluation exists
    evaluation = db.query(Evaluation).filter(Evaluation.id == decision_data.evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    # Create hiring decision
    decision = HiringDecision(
        evaluation_id=decision_data.evaluation_id,
        candidate_id=evaluation.submission.candidate_id,
        hr_manager_id=evaluation.hr_manager_id,
        hired_at=datetime.utcnow(),
        job_title=decision_data.job_title,
        salary_range=decision_data.salary_range,
        start_date=decision_data.start_date
    )

    db.add(decision)
    db.commit()
    db.refresh(decision)

    return decision


# ============================================================================
# LEADERBOARD & STATS
# ============================================================================

@app.get("/api/leaderboard/candidates", response_model=List[LeaderboardEntry])
def get_candidate_leaderboard(limit: int = 100, db: Session = Depends(get_db)):
    """
    Get top-performing candidates ranked by reputation score.

    This shows who consistently delivers high-quality work.
    """
    entries = db.query(CandidateLeaderboard).order_by(
        CandidateLeaderboard.reputation_score.desc()
    ).limit(limit).all()

    return entries


@app.get("/api/stats", response_model=PlatformStats)
def get_platform_stats(db: Session = Depends(get_db)):
    """
    Get platform-wide statistics.

    Shows overall health and usage metrics.
    """
    from sqlalchemy import func

    total_candidates = db.query(func.count(Candidate.id)).scalar()
    total_hr_managers = db.query(func.count(HRManager.id)).scalar()
    total_submissions = db.query(func.count(ProjectSubmission.id)).scalar()
    total_evaluations = db.query(func.count(Evaluation.id)).scalar()
    total_hires = db.query(func.count(HiringDecision.id)).scalar()

    avg_candidate_score = db.query(func.avg(Candidate.reputation_score)).scalar() or 0.0
    avg_hr_quality = db.query(func.avg(HRManager.evaluation_quality_score)).scalar() or 0.0

    return PlatformStats(
        total_candidates=total_candidates,
        total_hr_managers=total_hr_managers,
        total_submissions=total_submissions,
        total_evaluations=total_evaluations,
        total_hires=total_hires,
        avg_candidate_score=round(avg_candidate_score, 2),
        avg_hr_quality=round(avg_hr_quality, 2)
    )


# ============================================================================
# STARTUP EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup (in production, use migrations)"""
    print("🚀 Starting Proof-of-Work Hiring Platform...")
    # init_database()  # Uncomment to auto-create tables on startup
    print("✅ API ready!")


# ============================================================================
# MAIN (for local development)
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
