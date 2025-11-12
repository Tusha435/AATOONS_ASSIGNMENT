"""
Proof-of-Work Hiring Platform - Database Models

This module defines the complete SQLAlchemy ORM models for the platform.
Both candidates and HR are scored based on actual work, not theater.
"""

from datetime import datetime, date
from typing import Optional, List
import enum
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text,
    ForeignKey, JSON, Enum, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.sql import func, select

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class ExperienceLevel(str, enum.Enum):
    """Candidate experience levels"""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"


class SubscriptionTier(str, enum.Enum):
    """HR subscription tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class DifficultyLevel(str, enum.Enum):
    """Project difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class SubmissionStatus(str, enum.Enum):
    """Project submission statuses"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    EVALUATED = "evaluated"


class HireRecommendation(str, enum.Enum):
    """Hiring recommendation levels"""
    REJECT = "reject"
    MAYBE = "maybe"
    HIRE = "hire"
    STRONG_HIRE = "strong_hire"


class CheckInStatus(str, enum.Enum):
    """90-day check-in outcomes"""
    SUCCESS = "success"
    STRUGGLING = "struggling"
    LEFT = "left"


class AgreementLevel(str, enum.Enum):
    """HR vs AI agreement"""
    SAME = "same"
    SIMILAR = "similar"
    DIFFERENT = "different"


class OutcomeType(str, enum.Enum):
    """Actual hiring outcome"""
    HIRED_SUCCESS = "hired_success"
    HIRED_FAIL = "hired_fail"
    REJECTED = "rejected"


class ComparisonWinner(str, enum.Enum):
    """Who predicted better: HR or AI"""
    HR = "hr"
    AI = "ai"
    TIE = "tie"


class ProficiencyLevel(str, enum.Enum):
    """Skill badge proficiency"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# ============================================================================
# CORE MODELS
# ============================================================================

class Candidate(Base):
    """
    Developers seeking employment through proof-of-work.
    Scored based on actual project output and hiring outcomes.
    """
    __tablename__ = "candidates"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    github_username = Column(String(100), unique=True, nullable=True, index=True)
    portfolio_url = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Profile data
    skill_tags = Column(JSON, default=list, nullable=False)
    experience_level = Column(Enum(ExperienceLevel), nullable=False)

    # Computed metrics (updated via triggers/events)
    hire_success_rate = Column(Float, nullable=True)  # % of successful placements
    avg_project_score = Column(Float, nullable=True)  # Average submission score
    total_submissions = Column(Integer, default=0, nullable=False)

    # Platform status
    is_verified = Column(Boolean, default=False, nullable=False)
    reputation_score = Column(Float, default=50.0, nullable=False)

    # Relationships
    project_submissions = relationship("ProjectSubmission", back_populates="candidate", cascade="all, delete-orphan")
    skill_badges = relationship("SkillBadge", back_populates="candidate", cascade="all, delete-orphan")
    hiring_decisions = relationship("HiringDecision", back_populates="candidate")
    ai_interview_sessions = relationship("AIInterviewSession", back_populates="candidate")

    # Indexes
    __table_args__ = (
        Index('idx_candidate_reputation', 'reputation_score'),
        Index('idx_candidate_experience', 'experience_level'),
    )

    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.full_name}', reputation={self.reputation_score})>"


class HRManager(Base):
    """
    Hiring managers who evaluate candidates.
    Scored based on evaluation quality and hire prediction accuracy.
    """
    __tablename__ = "hr_managers"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False, index=True)
    job_title = Column(String(200), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Performance metrics (computed)
    evaluation_count = Column(Integer, default=0, nullable=False)
    evaluation_quality_score = Column(Float, default=50.0, nullable=False)
    prediction_accuracy = Column(Float, nullable=True)  # % correct predictions
    avg_time_to_evaluate = Column(Float, nullable=True)  # Hours

    # Platform status
    is_verified = Column(Boolean, default=False, nullable=False)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    hire_success_rate = Column(Float, nullable=True)  # % stayed 90+ days

    # Relationships
    evaluations = relationship("Evaluation", back_populates="hr_manager")
    hiring_decisions = relationship("HiringDecision", back_populates="hr_manager")
    created_templates = relationship("ProjectTemplate", back_populates="creator")

    # Indexes
    __table_args__ = (
        Index('idx_hr_quality', 'evaluation_quality_score'),
        Index('idx_hr_performance', 'evaluation_quality_score', 'prediction_accuracy'),
    )

    def __repr__(self):
        return f"<HRManager(id={self.id}, name='{self.full_name}', company='{self.company_name}')>"


class ProjectTemplate(Base):
    """
    Standardized project challenges for candidates.
    Can be public (available to all) or company-specific.
    """
    __tablename__ = "project_templates"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Project parameters
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False, index=True)
    tech_stack = Column(JSON, nullable=False)  # ["Python", "FastAPI", "PostgreSQL"]
    estimated_hours = Column(Integer, nullable=False)
    max_duration_days = Column(Integer, default=7, nullable=False)

    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey('hr_managers.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Visibility & usage
    is_public = Column(Boolean, default=True, nullable=False, index=True)
    usage_count = Column(Integer, default=0, nullable=False)
    avg_completion_rate = Column(Float, nullable=True)  # % who finish

    # Evaluation criteria
    evaluation_rubric = Column(JSON, nullable=False)  # Scoring criteria

    # Relationships
    creator = relationship("HRManager", back_populates="created_templates")
    submissions = relationship("ProjectSubmission", back_populates="template")

    __table_args__ = (
        Index('idx_project_difficulty', 'difficulty_level'),
    )

    def __repr__(self):
        return f"<ProjectTemplate(id={self.id}, title='{self.title}', difficulty={self.difficulty_level.value})>"


class ProjectSubmission(Base):
    """
    Candidate's completed project work.
    The core proof-of-work artifact that gets evaluated.
    """
    __tablename__ = "project_submissions"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('candidates.id'), nullable=False, index=True)
    project_template_id = Column(UUID(as_uuid=True), ForeignKey('project_templates.id'), nullable=True)

    # Submission data
    github_repo_url = Column(String(500), unique=True, nullable=False)
    demo_url = Column(String(500), nullable=True)
    video_explanation_url = Column(String(500), nullable=True)

    # Timeline
    started_at = Column(DateTime, nullable=False)
    submitted_at = Column(DateTime, nullable=False)
    time_spent_hours = Column(Float, nullable=False)

    # Documentation
    architecture_doc = Column(Text, nullable=False)
    trade_offs_doc = Column(Text, nullable=False)

    # Status & scores
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.DRAFT, nullable=False, index=True)
    code_quality_score = Column(Float, nullable=True)  # 0-100
    ai_likelihood_score = Column(Float, nullable=True)  # 0-100 (probability AI-generated)
    commit_count = Column(Integer, nullable=True)
    overall_score = Column(Float, nullable=True)  # Composite score

    # Relationships
    candidate = relationship("Candidate", back_populates="project_submissions")
    template = relationship("ProjectTemplate", back_populates="submissions")
    commit_analyses = relationship("CommitAnalysis", back_populates="submission", cascade="all, delete-orphan")
    code_quality_metrics = relationship("CodeQualityMetric", back_populates="submission", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="submission", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="submission")
    ai_interviews = relationship("AIInterviewSession", back_populates="submission")

    # Indexes
    __table_args__ = (
        Index('idx_submission_status_date', 'status', 'submitted_at'),
        Index('idx_submission_score', 'overall_score'),
    )

    def __repr__(self):
        return f"<ProjectSubmission(id={self.id}, candidate_id={self.candidate_id}, status={self.status.value})>"


class CommitAnalysis(Base):
    """
    Git commit pattern analysis to detect authenticity.
    Real developers show iterative refinement; AI shows bulk commits.
    """
    __tablename__ = "commit_analyses"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey('project_submissions.id'), nullable=False, index=True)

    # Git data
    commit_hash = Column(String(40), nullable=False)
    commit_message = Column(Text, nullable=False)
    commit_timestamp = Column(DateTime, nullable=False, index=True)

    # Commit metrics
    files_changed = Column(Integer, nullable=False)
    lines_added = Column(Integer, nullable=False)
    lines_deleted = Column(Integer, nullable=False)

    # Analysis flags
    is_bulk_commit = Column(Boolean, default=False, nullable=False)  # Suspicious pattern
    time_gap_hours = Column(Float, nullable=True)  # Hours since previous commit
    message_quality_score = Column(Float, nullable=True)  # 0-10

    # Relationships
    submission = relationship("ProjectSubmission", back_populates="commit_analyses")

    def __repr__(self):
        return f"<CommitAnalysis(hash={self.commit_hash[:7]}, timestamp={self.commit_timestamp})>"


class CodeQualityMetric(Base):
    """
    Automated code analysis results (static analysis, security, complexity).
    """
    __tablename__ = "code_quality_metrics"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey('project_submissions.id'), nullable=False, index=True)

    # Static analysis metrics
    cyclomatic_complexity = Column(Float, nullable=True)
    test_coverage = Column(Float, nullable=True)  # %
    linting_errors = Column(Integer, default=0, nullable=False)
    security_vulnerabilities = Column(Integer, default=0, nullable=False)

    # Quality scores
    documentation_score = Column(Float, nullable=True)  # 0-100
    code_duplication = Column(Float, nullable=True)  # %
    maintainability_index = Column(Float, nullable=True)  # 0-100
    architecture_score = Column(Float, nullable=True)  # 0-100 (AI-scored)

    # Metadata
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submission = relationship("ProjectSubmission", back_populates="code_quality_metrics")

    def __repr__(self):
        return f"<CodeQualityMetric(submission_id={self.submission_id}, score={self.maintainability_index})>"


class AIAnalysis(Base):
    """
    GPT-4 evaluation of code, architecture, and documentation.
    Provides deep technical review that HR gets compared against.
    """
    __tablename__ = "ai_analyses"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey('project_submissions.id'), nullable=False, index=True)

    # Model info
    model_used = Column(String(100), nullable=False)  # "gpt-4-turbo", etc.

    # Reviews
    architecture_review = Column(Text, nullable=False)
    code_review = Column(Text, nullable=False)
    documentation_review = Column(Text, nullable=False)

    # Scores
    creativity_score = Column(Float, nullable=False)  # 0-100
    production_readiness = Column(Float, nullable=False)  # 0-100
    ai_generated_probability = Column(Float, nullable=False)  # 0-100

    # Highlights
    key_strengths = Column(JSON, nullable=False)  # ["Good error handling", ...]
    key_weaknesses = Column(JSON, nullable=False)  # ["No input validation", ...]

    # Metadata
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submission = relationship("ProjectSubmission", back_populates="ai_analyses")

    def __repr__(self):
        return f"<AIAnalysis(submission_id={self.submission_id}, model={self.model_used})>"


class Evaluation(Base):
    """
    HR manager's assessment of a candidate's project.
    This is where HR proves they understand what they're evaluating.
    """
    __tablename__ = "evaluations"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey('project_submissions.id'), nullable=False, index=True)
    hr_manager_id = Column(UUID(as_uuid=True), ForeignKey('hr_managers.id'), nullable=False, index=True)

    # Timeline
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=False)
    time_spent_minutes = Column(Float, nullable=True)  # Computed from timeline

    # HR's assessment
    technical_assessment = Column(Text, nullable=False)
    strengths_identified = Column(JSON, nullable=False)  # What HR saw as strong
    weaknesses_identified = Column(JSON, nullable=False)  # Red flags noticed
    interview_questions = Column(JSON, nullable=False)  # Questions they'd ask

    # HR's decision
    hire_recommendation = Column(Enum(HireRecommendation), nullable=False)
    predicted_success_likelihood = Column(Float, nullable=False)  # 0-100

    # Quality metrics (computed by comparing to AI)
    hr_quality_score = Column(Float, nullable=True)  # 0-100 (how good was this eval?)
    delta_from_ai = Column(Float, nullable=True)  # Difference from AI assessment
    evaluation_depth_score = Column(Float, nullable=True)  # 0-100 (thoroughness)

    # Relationships
    submission = relationship("ProjectSubmission", back_populates="evaluations")
    hr_manager = relationship("HRManager", back_populates="evaluations")
    hiring_decision = relationship("HiringDecision", back_populates="evaluation", uselist=False)

    # Indexes
    __table_args__ = (
        Index('idx_eval_quality', 'hr_quality_score'),
    )

    def __repr__(self):
        return f"<Evaluation(id={self.id}, recommendation={self.hire_recommendation.value})>"


class HiringDecision(Base):
    """
    Track actual hiring outcomes to measure prediction accuracy.
    This is the ultimate ground truth that validates both HR and AI assessments.
    """
    __tablename__ = "hiring_decisions"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey('evaluations.id'), nullable=False, unique=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('candidates.id'), nullable=False, index=True)
    hr_manager_id = Column(UUID(as_uuid=True), ForeignKey('hr_managers.id'), nullable=False, index=True)

    # Hiring details
    hired_at = Column(DateTime, nullable=False, index=True)
    job_title = Column(String(255), nullable=False)
    salary_range = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=False)

    # Outcome tracking (90-day check-in)
    ninety_day_check_in = Column(Enum(CheckInStatus), nullable=True)
    ninety_day_notes = Column(Text, nullable=True)
    still_employed_at_90 = Column(Boolean, nullable=True)
    actual_performance = Column(Float, nullable=True)  # Manager rating 0-100

    # Accuracy measurement
    prediction_accuracy = Column(Float, nullable=True)  # How accurate was the prediction?

    # Relationships
    evaluation = relationship("Evaluation", back_populates="hiring_decision")
    candidate = relationship("Candidate", back_populates="hiring_decisions")
    hr_manager = relationship("HRManager", back_populates="hiring_decisions")

    def __repr__(self):
        return f"<HiringDecision(candidate_id={self.candidate_id}, title='{self.job_title}')>"


class AIInterviewSession(Base):
    """
    AI bot interview of candidates (competing with HR).
    Asks probing questions about their code and design decisions.
    """
    __tablename__ = "ai_interview_sessions"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey('project_submissions.id'), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('candidates.id'), nullable=False, index=True)

    # Timeline
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Interview data
    total_questions_asked = Column(Integer, default=0, nullable=False)
    conversation_log = Column(JSON, nullable=False)  # Full Q&A history

    # AI's assessment
    technical_depth_score = Column(Float, nullable=True)  # 0-100
    communication_score = Column(Float, nullable=True)  # 0-100
    reasoning_score = Column(Float, nullable=True)  # 0-100
    adaptability_score = Column(Float, nullable=True)  # 0-100

    # AI's decision
    overall_ai_recommendation = Column(Enum(HireRecommendation), nullable=True)
    confidence_level = Column(Float, nullable=True)  # 0-100

    # Relationships
    submission = relationship("ProjectSubmission", back_populates="ai_interviews")
    candidate = relationship("Candidate", back_populates="ai_interview_sessions")

    def __repr__(self):
        return f"<AIInterviewSession(candidate_id={self.candidate_id}, questions={self.total_questions_asked})>"


class HRvsAIComparison(Base):
    """
    Direct comparison of HR vs AI assessments.
    Tracks who's better at predicting candidate success.
    """
    __tablename__ = "hr_vs_ai_comparisons"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey('project_submissions.id'), nullable=False, index=True)
    evaluation_id = Column(UUID(as_uuid=True), ForeignKey('evaluations.id'), nullable=False)
    ai_interview_id = Column(UUID(as_uuid=True), ForeignKey('ai_interview_sessions.id'), nullable=False)

    # Recommendations
    hr_recommendation = Column(Enum(HireRecommendation), nullable=False)
    ai_recommendation = Column(Enum(HireRecommendation), nullable=False)

    # Agreement analysis
    agreement_level = Column(Enum(AgreementLevel), nullable=True)  # Computed
    hr_caught_issues = Column(JSON, nullable=True)  # Issues only HR noticed
    ai_caught_issues = Column(JSON, nullable=True)  # Issues only AI noticed

    # Outcome tracking
    actual_outcome = Column(Enum(OutcomeType), nullable=True)  # Set after hire completes
    winner = Column(Enum(ComparisonWinner), nullable=True)  # Who was more accurate?

    # Indexes
    __table_args__ = (
        Index('idx_comparison_outcomes', 'actual_outcome', 'agreement_level'),
    )

    def __repr__(self):
        return f"<HRvsAIComparison(submission_id={self.submission_id}, winner={self.winner})>"


class SkillBadge(Base):
    """
    Verified skill credentials earned through completing projects.
    Platform-verified proof of competency.
    """
    __tablename__ = "skill_badges"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('candidates.id'), nullable=False, index=True)

    # Badge details
    skill_name = Column(String(100), nullable=False, index=True)
    proficiency_level = Column(Enum(ProficiencyLevel), nullable=False)

    # Proof
    earned_via_submission = Column(UUID(as_uuid=True), ForeignKey('project_submissions.id'), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiry_date = Column(DateTime, nullable=True)

    # Verification
    is_verified = Column(Boolean, default=True, nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="skill_badges")

    def __repr__(self):
        return f"<SkillBadge(skill='{self.skill_name}', level={self.proficiency_level.value})>"


# ============================================================================
# MATERIALIZED VIEWS (Defined as regular tables for now, refreshed via jobs)
# ============================================================================

class CandidateLeaderboard(Base):
    """
    Materialized view of top-performing candidates.
    Refreshed periodically for performance.
    """
    __tablename__ = "candidate_leaderboard"

    candidate_id = Column(UUID(as_uuid=True), ForeignKey('candidates.id'), primary_key=True)
    full_name = Column(String(255), nullable=False)
    reputation_score = Column(Float, nullable=False)
    total_projects = Column(Integer, default=0)
    avg_score = Column(Float, nullable=True)
    total_hires = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_leaderboard_rank', 'reputation_score'),
    )


class HRPerformanceDashboard(Base):
    """
    Materialized view of HR manager performance metrics.
    Refreshed periodically for performance.
    """
    __tablename__ = "hr_performance_dashboard"

    hr_id = Column(UUID(as_uuid=True), ForeignKey('hr_managers.id'), primary_key=True)
    full_name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    evaluation_quality_score = Column(Float, nullable=False)
    prediction_accuracy = Column(Float, nullable=True)
    total_evaluations = Column(Integer, default=0)
    total_hires = Column(Integer, default=0)
    avg_hire_quality = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_hr_dashboard_quality', 'evaluation_quality_score'),
    )


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db(engine):
    """
    Initialize all database tables.

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)
    print("✅ All database tables created successfully!")


def drop_all(engine):
    """
    Drop all database tables (use with caution!).

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(engine)
    print("⚠️ All database tables dropped!")


if __name__ == "__main__":
    print("This module defines the database models.")
    print("Import and use with SQLAlchemy engine to create tables.")
    print("\nExample:")
    print("  from sqlalchemy import create_engine")
    print("  from models import init_db")
    print("  engine = create_engine('postgresql://user:pass@localhost/dbname')")
    print("  init_db(engine)")
