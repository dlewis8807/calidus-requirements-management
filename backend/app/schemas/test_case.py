"""
Test Case Pydantic Schemas
Schema definitions for TestCase CRUD operations.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.test_case import TestCaseStatus, TestCasePriority

if TYPE_CHECKING:
    from app.schemas.requirement import RequirementResponse


# ============================================================================
# Base Schemas
# ============================================================================

class TestCaseBase(BaseModel):
    """Base test case schema with common fields"""
    test_case_id: str = Field(..., min_length=1, max_length=50, description="Unique test case identifier (e.g., TC-001)")
    title: str = Field(..., min_length=1, max_length=200, description="Test case title")
    description: Optional[str] = Field(None, description="Detailed test case description")
    test_steps: str = Field(..., min_length=1, description="Step-by-step test instructions")
    expected_results: str = Field(..., min_length=1, description="Expected test outcomes")
    actual_results: Optional[str] = Field(None, description="Actual results after execution")
    status: TestCaseStatus = Field(default=TestCaseStatus.PENDING, description="Execution status")
    priority: TestCasePriority = Field(default=TestCasePriority.MEDIUM, description="Test priority")

    # Execution tracking
    execution_date: Optional[datetime] = Field(None, description="When test was last executed")
    execution_duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    executed_by: Optional[str] = Field(None, description="Username who executed the test")

    # Test case metadata
    test_type: Optional[str] = Field(None, description="Type of test (unit, integration, system, acceptance)")
    test_environment: Optional[str] = Field(None, description="Test environment (dev, staging, production)")
    automated: bool = Field(default=False, description="Whether test is automated")
    automation_script: Optional[str] = Field(None, description="Path to automation script if automated")

    # Link to requirement
    requirement_id: int = Field(..., description="ID of the requirement this test verifies")


# ============================================================================
# Create/Update Schemas
# ============================================================================

class TestCaseCreate(TestCaseBase):
    """Schema for creating a new test case"""
    pass


class TestCaseUpdate(BaseModel):
    """Schema for updating an existing test case (all fields optional)"""
    test_case_id: Optional[str] = Field(None, min_length=1, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    test_steps: Optional[str] = Field(None, min_length=1)
    expected_results: Optional[str] = Field(None, min_length=1)
    actual_results: Optional[str] = None
    status: Optional[TestCaseStatus] = None
    priority: Optional[TestCasePriority] = None
    execution_date: Optional[datetime] = None
    execution_duration: Optional[int] = Field(None, ge=0)
    executed_by: Optional[str] = None
    test_type: Optional[str] = None
    test_environment: Optional[str] = None
    automated: Optional[bool] = None
    automation_script: Optional[str] = None
    requirement_id: Optional[int] = None


# ============================================================================
# Response Schemas
# ============================================================================

class TestCaseInDB(TestCaseBase):
    """Test case schema with database fields"""
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TestCaseResponse(TestCaseInDB):
    """Full test case response"""
    requirement_title: Optional[str] = Field(None, description="Title of linked requirement")
    requirement_id_str: Optional[str] = Field(None, description="Requirement ID string (e.g., AHLR-001)")


class TestCaseListResponse(BaseModel):
    """Paginated list of test cases"""
    total: int = Field(..., description="Total number of test cases matching query")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    test_cases: List[TestCaseResponse]


class TestCaseWithRequirement(TestCaseResponse):
    """Test case with full requirement details - simplified"""
    # Using dict to avoid circular imports
    requirement: dict


# ============================================================================
# Execution Schemas
# ============================================================================

class TestCaseExecutionUpdate(BaseModel):
    """Schema for updating test execution results"""
    status: TestCaseStatus = Field(..., description="Execution status (PASSED, FAILED, BLOCKED)")
    actual_results: str = Field(..., min_length=1, description="Actual test results")
    execution_duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    executed_by: Optional[str] = Field(None, description="Username who executed the test")
    execution_notes: Optional[str] = Field(None, description="Additional notes about execution")


# ============================================================================
# Query/Filter Schemas
# ============================================================================

class TestCaseFilter(BaseModel):
    """Schema for filtering test cases"""
    status: Optional[TestCaseStatus] = None
    priority: Optional[TestCasePriority] = None
    requirement_id: Optional[int] = None
    test_type: Optional[str] = None
    automated: Optional[bool] = None
    search: Optional[str] = Field(None, description="Search in title and description")
    created_by_id: Optional[int] = None

    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=1000, description="Items per page")

    # Sorting
    sort_by: Optional[str] = Field(default="created_at", description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class TestCaseStats(BaseModel):
    """Statistics about test cases"""
    total_test_cases: int
    by_status: dict = Field(default_factory=dict, description="Count by status")
    by_priority: dict = Field(default_factory=dict, description="Count by priority")
    total_automated: int = Field(default=0, description="Number of automated tests")
    total_manual: int = Field(default=0, description="Number of manual tests")
    pass_rate: float = Field(default=0.0, description="Percentage of passed tests")
    avg_execution_duration: Optional[float] = Field(None, description="Average execution time in seconds")
