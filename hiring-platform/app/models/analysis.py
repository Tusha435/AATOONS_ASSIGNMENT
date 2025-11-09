"""
Analysis models - Git, code quality, and AI analysis.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.common import Base, HireRecommendation


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
