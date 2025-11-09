"""
Common models, base classes, and enums.
"""

import enum
from sqlalchemy.ext.declarative import declarative_base

# Base class for all models
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
