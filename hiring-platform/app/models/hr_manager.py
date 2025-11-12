"""
HR Manager model - Hiring managers who evaluate candidates.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.common import Base, SubscriptionTier


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


class HRPerformanceDashboard(Base):
    """
    Materialized view of HR manager performance metrics.
    Refreshed periodically for performance.
    """
    __tablename__ = "hr_performance_dashboard"

    hr_id = Column(UUID(as_uuid=True), primary_key=True)
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
