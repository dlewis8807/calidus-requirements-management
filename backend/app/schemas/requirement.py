"""
Requirement Pydantic Schemas
Schema definitions for Requirement CRUD operations.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.requirement import (
    RequirementType, RequirementStatus,
    RequirementPriority, VerificationMethod
)

if TYPE_CHECKING:
    from app.schemas.test_case import TestCaseResponse
    from app.schemas.traceability import TraceabilityLinkResponse


# ============================================================================
# Base Schemas
# ============================================================================

class RequirementBase(BaseModel):
    """Base requirement schema with common fields"""
    requirement_id: str = Field(..., min_length=1, max_length=50, description="Unique requirement identifier (e.g., AHLR-001)")
    type: RequirementType = Field(..., description="Requirement classification type")
    category: Optional[str] = Field(None, max_length=100, description="Requirement category (e.g., FlightControl, Safety)")
    title: str = Field(..., min_length=1, max_length=200, description="Requirement title")
    description: str = Field(..., min_length=1, description="Detailed requirement description (SHALL statement)")
    priority: RequirementPriority = Field(default=RequirementPriority.MEDIUM, description="Business priority")
    status: RequirementStatus = Field(default=RequirementStatus.DRAFT, description="Current lifecycle status")
    verification_method: Optional[VerificationMethod] = Field(None, description="Method to verify this requirement")

    # Regulatory linkage
    regulatory_document: Optional[str] = Field(None, max_length=200, description="Source regulatory document (e.g., 14 CFR Part 23)")
    regulatory_section: Optional[str] = Field(None, max_length=100, description="Specific section reference (e.g., §23.143)")
    regulatory_page: Optional[int] = Field(None, description="Page number in regulatory document")
    file_path: Optional[str] = Field(None, max_length=500, description="Path to source PDF/document")

    # Version control
    version: str = Field(default="1.0", description="Requirement version")


# ============================================================================
# Create/Update Schemas
# ============================================================================

class RequirementCreate(RequirementBase):
    """Schema for creating a new requirement"""
    pass


class RequirementUpdate(BaseModel):
    """Schema for updating an existing requirement (all fields optional)"""
    requirement_id: Optional[str] = Field(None, min_length=1, max_length=50)
    type: Optional[RequirementType] = None
    category: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[RequirementPriority] = None
    status: Optional[RequirementStatus] = None
    verification_method: Optional[VerificationMethod] = None
    regulatory_document: Optional[str] = Field(None, max_length=200)
    regulatory_section: Optional[str] = Field(None, max_length=100)
    regulatory_page: Optional[int] = None
    file_path: Optional[str] = Field(None, max_length=500)
    version: Optional[str] = None
    revision_notes: Optional[str] = None


# ============================================================================
# Response Schemas
# ============================================================================

class RequirementInDB(RequirementBase):
    """Requirement schema with database fields"""
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class RequirementResponse(RequirementInDB):
    """Full requirement response with relationships"""
    # Will include related test_cases and traces when needed
    test_case_count: int = Field(default=0, description="Number of linked test cases")
    parent_trace_count: int = Field(default=0, description="Number of parent traceability links")
    child_trace_count: int = Field(default=0, description="Number of child traceability links")


class RequirementListResponse(BaseModel):
    """Paginated list of requirements"""
    total: int = Field(..., description="Total number of requirements matching query")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    requirements: List[RequirementResponse]


class RequirementWithRelations(RequirementResponse):
    """Requirement with full nested relationships - simplified"""
    # Using Any type to avoid circular imports
    test_cases: List[dict] = Field(default_factory=list)
    parent_traces: List[dict] = Field(default_factory=list)
    child_traces: List[dict] = Field(default_factory=list)


# ============================================================================
# Query/Filter Schemas
# ============================================================================

class RequirementFilter(BaseModel):
    """Schema for filtering requirements"""
    type: Optional[RequirementType] = None
    category: Optional[str] = None
    status: Optional[RequirementStatus] = None
    priority: Optional[RequirementPriority] = None
    search: Optional[str] = Field(None, description="Search in title and description")
    regulatory_document: Optional[str] = None
    created_by_id: Optional[int] = None

    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=1000, description="Items per page")

    # Sorting
    sort_by: Optional[str] = Field(default="created_at", description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class RequirementStats(BaseModel):
    """Statistics about requirements"""
    total_requirements: int
    by_type: dict = Field(default_factory=dict, description="Count by requirement type")
    by_status: dict = Field(default_factory=dict, description="Count by status")
    by_priority: dict = Field(default_factory=dict, description="Count by priority")
    total_with_tests: int = Field(default=0, description="Requirements with test cases")
    total_with_traces: int = Field(default=0, description="Requirements with traceability links")
    coverage_percentage: float = Field(default=0.0, description="Percentage of requirements with tests")
