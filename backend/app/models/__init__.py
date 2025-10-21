"""
Models package initialization.
Imports all models for easy access and ensures they're registered with SQLAlchemy.
"""
from app.models.user import User
from app.models.requirement import (
    Requirement,
    RequirementType,
    RequirementStatus,
    RequirementPriority,
    VerificationMethod
)
from app.models.test_case import (
    TestCase,
    TestCaseStatus,
    TestCasePriority
)
from app.models.traceability import (
    TraceabilityLink,
    TraceLinkType
)
from app.models.test_suggestion import (
    TestCaseSuggestion,
    SuggestionFeedback,
    FailurePattern
)
from app.models.impact_analysis import (
    ImpactAnalysisReport,
    ChangeRequest,
    RiskLevel,
    ChangeRequestStatus
)
from app.models.coverage import CoverageSnapshot

__all__ = [
    "User",
    "Requirement",
    "RequirementType",
    "RequirementStatus",
    "RequirementPriority",
    "VerificationMethod",
    "TestCase",
    "TestCaseStatus",
    "TestCasePriority",
    "TraceabilityLink",
    "TraceLinkType",
    "TestCaseSuggestion",
    "SuggestionFeedback",
    "FailurePattern",
    "ImpactAnalysisReport",
    "ChangeRequest",
    "RiskLevel",
    "ChangeRequestStatus",
    "CoverageSnapshot",
]
