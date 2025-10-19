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
]
