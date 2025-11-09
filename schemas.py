"""
Pydantic schemas for request/response validation.
These define the API contract between frontend and backend.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator
from enum import Enum
import uuid


# ============================================================================
# ENUMS (matching models.py)
# ============================================================================

class ExperienceLevelEnum(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"


class DifficultyLevelEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class SubmissionStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    EVALUATED = "evaluated"


class HireRecommendationEnum(str, Enum):
    REJECT = "reject"
    MAYBE = "maybe"
    HIRE = "hire"
    STRONG_HIRE = "strong_hire"


# ============================================================================
# CANDIDATE SCHEMAS
# ============================================================================

class CandidateCreate(BaseModel):
    """Schema for creating a new candidate"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    github_username: Optional[str] = Field(None, max_length=100)
    portfolio_url: Optional[HttpUrl] = None
    skill_tags: List[str] = Field(default_factory=list)
    experience_level: ExperienceLevelEnum


class CandidateUpdate(BaseModel):
    """Schema for updating candidate profile"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    github_username: Optional[str] = None
    portfolio_url: Optional[HttpUrl] = None
    skill_tags: Optional[List[str]] = None
    experience_level: Optional[ExperienceLevelEnum] = None


class CandidateResponse(BaseModel):
    """Schema for candidate data in responses"""
    id: uuid.UUID
    email: str
    full_name: str
    github_username: Optional[str]
    portfolio_url: Optional[str]
    created_at: datetime
    skill_tags: List[str]
    experience_level: str
    reputation_score: float
    total_submissions: int
    avg_project_score: Optional[float]
    is_verified: bool

    class Config:
        from_attributes = True


# ============================================================================
# HR MANAGER SCHEMAS
# ============================================================================

class HRManagerCreate(BaseModel):
    """Schema for HR manager registration"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    company_name: str = Field(..., min_length=2, max_length=255)
    job_title: str = Field(..., min_length=2, max_length=200)


class HRManagerResponse(BaseModel):
    """Schema for HR manager data in responses"""
    id: uuid.UUID
    email: str
    full_name: str
    company_name: str
    job_title: str
    evaluation_count: int
    evaluation_quality_score: float
    prediction_accuracy: Optional[float]
    subscription_tier: str
    is_verified: bool

    class Config:
        from_attributes = True


# ============================================================================
# PROJECT TEMPLATE SCHEMAS
# ============================================================================

class ProjectTemplateCreate(BaseModel):
    """Schema for creating a project template"""
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=50)
    difficulty_level: DifficultyLevelEnum
    tech_stack: List[str] = Field(..., min_items=1)
    estimated_hours: int = Field(..., gt=0, le=200)
    max_duration_days: int = Field(default=7, gt=0, le=30)
    is_public: bool = Field(default=True)
    evaluation_rubric: Dict[str, Any]


class ProjectTemplateResponse(BaseModel):
    """Schema for project template in responses"""
    id: uuid.UUID
    title: str
    description: str
    difficulty_level: str
    tech_stack: List[str]
    estimated_hours: int
    max_duration_days: int
    is_public: bool
    usage_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PROJECT SUBMISSION SCHEMAS
# ============================================================================

class ProjectSubmissionCreate(BaseModel):
    """Schema for creating a project submission"""
    project_template_id: Optional[uuid.UUID] = None
    github_repo_url: HttpUrl
    demo_url: Optional[HttpUrl] = None
    video_explanation_url: Optional[HttpUrl] = None
    time_spent_hours: float = Field(..., gt=0)
    architecture_doc: str = Field(..., min_length=100)
    trade_offs_doc: str = Field(..., min_length=50)


class ProjectSubmissionUpdate(BaseModel):
    """Schema for updating a submission"""
    demo_url: Optional[HttpUrl] = None
    video_explanation_url: Optional[HttpUrl] = None
    architecture_doc: Optional[str] = None
    trade_offs_doc: Optional[str] = None
    status: Optional[SubmissionStatusEnum] = None


class ProjectSubmissionResponse(BaseModel):
    """Schema for project submission in responses"""
    id: uuid.UUID
    candidate_id: uuid.UUID
    project_template_id: Optional[uuid.UUID]
    github_repo_url: str
    demo_url: Optional[str]
    video_explanation_url: Optional[str]
    started_at: datetime
    submitted_at: datetime
    time_spent_hours: float
    status: str
    code_quality_score: Optional[float]
    ai_likelihood_score: Optional[float]
    overall_score: Optional[float]

    class Config:
        from_attributes = True


# ============================================================================
# EVALUATION SCHEMAS
# ============================================================================

class EvaluationCreate(BaseModel):
    """Schema for creating an evaluation"""
    submission_id: uuid.UUID
    technical_assessment: str = Field(..., min_length=100)
    strengths_identified: List[str] = Field(..., min_items=1)
    weaknesses_identified: List[str] = Field(..., min_items=1)
    interview_questions: List[str] = Field(..., min_items=3)
    hire_recommendation: HireRecommendationEnum
    predicted_success_likelihood: float = Field(..., ge=0, le=100)


class EvaluationResponse(BaseModel):
    """Schema for evaluation in responses"""
    id: uuid.UUID
    submission_id: uuid.UUID
    hr_manager_id: uuid.UUID
    started_at: datetime
    completed_at: datetime
    technical_assessment: str
    hire_recommendation: str
    predicted_success_likelihood: float
    hr_quality_score: Optional[float]
    delta_from_ai: Optional[float]

    class Config:
        from_attributes = True


# ============================================================================
# CODE QUALITY SCHEMAS
# ============================================================================

class CodeQualityMetricResponse(BaseModel):
    """Schema for code quality metrics"""
    id: uuid.UUID
    submission_id: uuid.UUID
    cyclomatic_complexity: Optional[float]
    test_coverage: Optional[float]
    linting_errors: int
    security_vulnerabilities: int
    documentation_score: Optional[float]
    maintainability_index: Optional[float]
    analyzed_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AI ANALYSIS SCHEMAS
# ============================================================================

class AIAnalysisResponse(BaseModel):
    """Schema for AI analysis results"""
    id: uuid.UUID
    submission_id: uuid.UUID
    model_used: str
    architecture_review: str
    code_review: str
    creativity_score: float
    production_readiness: float
    ai_generated_probability: float
    key_strengths: List[str]
    key_weaknesses: List[str]
    analyzed_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# COMMIT ANALYSIS SCHEMAS
# ============================================================================

class CommitAnalysisResponse(BaseModel):
    """Schema for commit analysis data"""
    commit_hash: str
    commit_message: str
    commit_timestamp: datetime
    files_changed: int
    lines_added: int
    lines_deleted: int
    is_bulk_commit: bool
    message_quality_score: Optional[float]

    class Config:
        from_attributes = True


# ============================================================================
# HIRING DECISION SCHEMAS
# ============================================================================

class HiringDecisionCreate(BaseModel):
    """Schema for recording a hiring decision"""
    evaluation_id: uuid.UUID
    job_title: str = Field(..., min_length=2)
    salary_range: Optional[str] = None
    start_date: date


class HiringDecisionResponse(BaseModel):
    """Schema for hiring decision in responses"""
    id: uuid.UUID
    evaluation_id: uuid.UUID
    candidate_id: uuid.UUID
    hired_at: datetime
    job_title: str
    start_date: date
    still_employed_at_90: Optional[bool]
    actual_performance: Optional[float]

    class Config:
        from_attributes = True


# ============================================================================
# LEADERBOARD SCHEMAS
# ============================================================================

class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entries"""
    candidate_id: uuid.UUID
    full_name: str
    reputation_score: float
    total_projects: int
    avg_score: Optional[float]
    total_hires: int

    class Config:
        from_attributes = True


# ============================================================================
# UTILITY SCHEMAS
# ============================================================================

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error_code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Schema for generic success responses"""
    message: str
    data: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """Schema for paginated responses"""
    total: int
    page: int
    page_size: int
    items: List[Any]


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class PlatformStats(BaseModel):
    """Platform-wide statistics"""
    total_candidates: int
    total_hr_managers: int
    total_submissions: int
    total_evaluations: int
    total_hires: int
    avg_candidate_score: float
    avg_hr_quality: float


class CandidateStats(BaseModel):
    """Detailed candidate statistics"""
    total_submissions: int
    avg_score: Optional[float]
    best_score: Optional[float]
    total_evaluations_received: int
    hire_success_rate: Optional[float]
    skill_badges_earned: int
