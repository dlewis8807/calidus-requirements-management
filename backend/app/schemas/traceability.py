"""
Traceability Link Pydantic Schemas
Schema definitions for TraceabilityLink CRUD operations.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.traceability import TraceLinkType

if TYPE_CHECKING:
    from app.schemas.requirement import RequirementResponse


# ============================================================================
# Base Schemas
# ============================================================================

class TraceabilityLinkBase(BaseModel):
    """Base traceability link schema with common fields"""
    source_id: int = Field(..., description="ID of source requirement (child)")
    target_id: int = Field(..., description="ID of target requirement (parent)")
    link_type: TraceLinkType = Field(..., description="Type of traceability relationship")
    description: Optional[str] = Field(None, description="Description of the relationship")
    rationale: Optional[str] = Field(None, description="Rationale for this traceability link")

    @field_validator('target_id')
    @classmethod
    def validate_not_self_reference(cls, v, info):
        """Ensure source and target are not the same"""
        if 'source_id' in info.data and v == info.data['source_id']:
            raise ValueError('Source and target cannot be the same requirement')
        return v


# ============================================================================
# Create/Update Schemas
# ============================================================================

class TraceabilityLinkCreate(TraceabilityLinkBase):
    """Schema for creating a new traceability link"""
    pass


class TraceabilityLinkUpdate(BaseModel):
    """Schema for updating an existing traceability link"""
    link_type: Optional[TraceLinkType] = None
    description: Optional[str] = None
    rationale: Optional[str] = None


# ============================================================================
# Response Schemas
# ============================================================================

class TraceabilityLinkInDB(TraceabilityLinkBase):
    """Traceability link schema with database fields"""
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TraceabilityLinkResponse(TraceabilityLinkInDB):
    """Full traceability link response with requirement details"""
    source_requirement_id: Optional[str] = Field(None, description="Source requirement ID string (e.g., SYS-001)")
    source_title: Optional[str] = Field(None, description="Source requirement title")
    target_requirement_id: Optional[str] = Field(None, description="Target requirement ID string (e.g., AHLR-001)")
    target_title: Optional[str] = Field(None, description="Target requirement title")


class TraceabilityLinkListResponse(BaseModel):
    """Paginated list of traceability links"""
    total: int = Field(..., description="Total number of links matching query")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    links: List[TraceabilityLinkResponse]


class TraceabilityLinkWithRequirements(TraceabilityLinkResponse):
    """Traceability link with full source and target requirement details - simplified"""
    # Using dict to avoid circular imports
    source_requirement: dict
    target_requirement: dict


# ============================================================================
# Traceability Matrix Schemas
# ============================================================================

class RequirementTraceNode(BaseModel):
    """A node in the traceability tree"""
    id: int
    requirement_id: str
    title: str
    type: str
    status: str
    has_test_cases: bool = False
    test_case_count: int = 0


class RequirementTraceTree(RequirementTraceNode):
    """Hierarchical traceability tree"""
    children: List["RequirementTraceNode"] = Field(default_factory=list, description="Child requirements")
    parents: List["RequirementTraceNode"] = Field(default_factory=list, description="Parent requirements")
    trace_depth: int = Field(default=0, description="Depth in traceability hierarchy")


class TraceabilityMatrix(BaseModel):
    """Traceability matrix response"""
    requirement_id: int
    requirement_identifier: str
    title: str
    type: str

    # Upstream traceability (parents)
    parent_requirements: List[RequirementTraceNode] = Field(default_factory=list)

    # Downstream traceability (children)
    child_requirements: List[RequirementTraceNode] = Field(default_factory=list)

    # Test coverage
    test_cases: List[dict] = Field(default_factory=list)

    # Metrics
    total_parents: int = 0
    total_children: int = 0
    total_tests: int = 0
    coverage_status: str = Field(default="unknown", description="none, partial, full")


class TraceabilityGap(BaseModel):
    """Identifies gaps in traceability"""
    requirement_id: int
    requirement_identifier: str
    title: str
    type: str
    gap_type: str = Field(..., description="missing_parent, missing_child, missing_test, orphan")
    severity: str = Field(..., description="critical, high, medium, low")
    description: str


class TraceabilityReport(BaseModel):
    """Comprehensive traceability analysis report"""
    total_requirements: int
    total_trace_links: int
    total_test_cases: int

    # Coverage metrics
    requirements_with_parents: int
    requirements_with_children: int
    requirements_with_tests: int
    orphaned_requirements: int

    # Gaps
    traceability_gaps: List[TraceabilityGap] = Field(default_factory=list)

    # Statistics by requirement type
    by_type: dict = Field(default_factory=dict)

    # Overall health score (0-100)
    traceability_score: float = Field(default=0.0, ge=0.0, le=100.0)
    test_coverage_score: float = Field(default=0.0, ge=0.0, le=100.0)


# ============================================================================
# Query/Filter Schemas
# ============================================================================

class TraceabilityLinkFilter(BaseModel):
    """Schema for filtering traceability links"""
    link_type: Optional[TraceLinkType] = None
    source_id: Optional[int] = None
    target_id: Optional[int] = None
    requirement_id: Optional[int] = Field(None, description="Filter by either source or target")
    created_by_id: Optional[int] = None

    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=1000, description="Items per page")

    # Sorting
    sort_by: Optional[str] = Field(default="created_at", description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class BulkTraceabilityCreate(BaseModel):
    """Schema for creating multiple traceability links at once"""
    links: List[TraceabilityLinkCreate] = Field(..., min_length=1, max_length=100)
    skip_duplicates: bool = Field(default=True, description="Skip duplicate links instead of failing")


class BulkTraceabilityResponse(BaseModel):
    """Response for bulk traceability creation"""
    created: int = Field(..., description="Number of links created")
    skipped: int = Field(default=0, description="Number of duplicates skipped")
    failed: int = Field(default=0, description="Number of links that failed")
    errors: List[str] = Field(default_factory=list, description="Error messages for failed links")
