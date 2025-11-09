"""
Models module - All database models for the platform.
"""

from app.models.common import (
    Base,
    ExperienceLevel,
    SubscriptionTier,
    DifficultyLevel,
    SubmissionStatus,
    HireRecommendation,
    CheckInStatus,
    AgreementLevel,
    OutcomeType,
    ComparisonWinner,
    ProficiencyLevel,
)

from app.models.candidate import (
    Candidate,
    SkillBadge,
    CandidateLeaderboard,
)

from app.models.hr_manager import (
    HRManager,
    HRPerformanceDashboard,
)

from app.models.project import (
    ProjectTemplate,
    ProjectSubmission,
)

from app.models.analysis import (
    CommitAnalysis,
    CodeQualityMetric,
    AIAnalysis,
    AIInterviewSession,
)

from app.models.evaluation import (
    Evaluation,
    HiringDecision,
    HRvsAIComparison,
)

__all__ = [
    # Base
    "Base",

    # Enums
    "ExperienceLevel",
    "SubscriptionTier",
    "DifficultyLevel",
    "SubmissionStatus",
    "HireRecommendation",
    "CheckInStatus",
    "AgreementLevel",
    "OutcomeType",
    "ComparisonWinner",
    "ProficiencyLevel",

    # Candidate models
    "Candidate",
    "SkillBadge",
    "CandidateLeaderboard",

    # HR models
    "HRManager",
    "HRPerformanceDashboard",

    # Project models
    "ProjectTemplate",
    "ProjectSubmission",

    # Analysis models
    "CommitAnalysis",
    "CodeQualityMetric",
    "AIAnalysis",
    "AIInterviewSession",

    # Evaluation models
    "Evaluation",
    "HiringDecision",
    "HRvsAIComparison",
]
