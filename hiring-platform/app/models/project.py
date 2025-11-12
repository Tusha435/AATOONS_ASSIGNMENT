"""
Project models - Templates and submissions.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.common import Base, DifficultyLevel, SubmissionStatus


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
