"""
Candidate model - Developers seeking employment through proof-of-work.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.common import Base, ExperienceLevel


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


class SkillBadge(Base):
    """
    Verified skill credentials earned through completing projects.
    Platform-verified proof of competency.
    """
    __tablename__ = "skill_badges"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Badge details
    skill_name = Column(String(100), nullable=False, index=True)
    proficiency_level = Column(Enum('beginner', 'intermediate', 'advanced', 'expert', name='proficiency_level'), nullable=False)

    # Proof
    earned_via_submission = Column(UUID(as_uuid=True), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expiry_date = Column(DateTime, nullable=True)

    # Verification
    is_verified = Column(Boolean, default=True, nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="skill_badges")

    def __repr__(self):
        return f"<SkillBadge(skill='{self.skill_name}', level={self.proficiency_level})>"


class CandidateLeaderboard(Base):
    """
    Materialized view of top-performing candidates.
    Refreshed periodically for performance.
    """
    __tablename__ = "candidate_leaderboard"

    candidate_id = Column(UUID(as_uuid=True), primary_key=True)
    full_name = Column(String(255), nullable=False)
    reputation_score = Column(Float, nullable=False)
    total_projects = Column(Integer, default=0)
    avg_score = Column(Float, nullable=True)
    total_hires = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_leaderboard_rank', 'reputation_score'),
    )
