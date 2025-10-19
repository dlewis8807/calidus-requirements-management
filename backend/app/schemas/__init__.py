"""
Pydantic Schemas Package
Exports all schemas for API request/response validation.
"""

# User schemas
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserInDB,
    Token, TokenData, UserLogin
)

# Requirement schemas
from app.schemas.requirement import (
    RequirementBase, RequirementCreate, RequirementUpdate,
    RequirementInDB, RequirementResponse, RequirementListResponse,
    RequirementWithRelations, RequirementFilter, RequirementStats
)

# Test Case schemas
from app.schemas.test_case import (
    TestCaseBase, TestCaseCreate, TestCaseUpdate,
    TestCaseInDB, TestCaseResponse, TestCaseListResponse,
    TestCaseWithRequirement, TestCaseExecutionUpdate,
    TestCaseFilter, TestCaseStats
)

# Traceability schemas
from app.schemas.traceability import (
    TraceabilityLinkBase, TraceabilityLinkCreate, TraceabilityLinkUpdate,
    TraceabilityLinkInDB, TraceabilityLinkResponse, TraceabilityLinkListResponse,
    TraceabilityLinkWithRequirements, RequirementTraceNode, RequirementTraceTree,
    TraceabilityMatrix, TraceabilityGap, TraceabilityReport,
    TraceabilityLinkFilter, BulkTraceabilityCreate, BulkTraceabilityResponse
)

__all__ = [
    # User
    "UserCreate", "UserUpdate", "UserResponse", "UserInDB",
    "Token", "TokenData", "UserLogin",

    # Requirement
    "RequirementBase", "RequirementCreate", "RequirementUpdate",
    "RequirementInDB", "RequirementResponse", "RequirementListResponse",
    "RequirementWithRelations", "RequirementFilter", "RequirementStats",

    # Test Case
    "TestCaseBase", "TestCaseCreate", "TestCaseUpdate",
    "TestCaseInDB", "TestCaseResponse", "TestCaseListResponse",
    "TestCaseWithRequirement", "TestCaseExecutionUpdate",
    "TestCaseFilter", "TestCaseStats",

    # Traceability
    "TraceabilityLinkBase", "TraceabilityLinkCreate", "TraceabilityLinkUpdate",
    "TraceabilityLinkInDB", "TraceabilityLinkResponse", "TraceabilityLinkListResponse",
    "TraceabilityLinkWithRequirements", "RequirementTraceNode", "RequirementTraceTree",
    "TraceabilityMatrix", "TraceabilityGap", "TraceabilityReport",
    "TraceabilityLinkFilter", "BulkTraceabilityCreate", "BulkTraceabilityResponse",
]
