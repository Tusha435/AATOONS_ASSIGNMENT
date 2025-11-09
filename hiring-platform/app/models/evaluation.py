"""
Evaluation models - HR evaluations, hiring decisions, and comparisons.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Float, DateTime, Date, Text, ForeignKey, JSON, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.common import Base, HireRecommendation, CheckInStatus, AgreementLevel, OutcomeType, ComparisonWinner


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
