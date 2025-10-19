"""
Test Cases API Routes
CRUD operations for test cases with execution tracking and statistics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import User, TestCase, Requirement, TestCaseStatus, TestCasePriority
from app.schemas.test_case import (
    TestCaseCreate, TestCaseUpdate, TestCaseResponse,
    TestCaseListResponse, TestCaseWithRequirement,
    TestCaseExecutionUpdate, TestCaseFilter, TestCaseStats
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/test-cases", tags=["test-cases"])


# ============================================================================
# Helper Functions
# ============================================================================

def _build_test_case_response(tc: TestCase, include_requirement: bool = True) -> TestCaseResponse:
    """Convert TestCase model to TestCaseResponse schema"""
    response = TestCaseResponse(
        id=tc.id,
        test_case_id=tc.test_case_id,
        title=tc.title,
        description=tc.description,
        test_steps=tc.test_steps,
        expected_results=tc.expected_results,
        actual_results=tc.actual_results,
        status=tc.status,
        priority=tc.priority,
        execution_date=tc.execution_date,
        execution_duration=tc.execution_duration,
        executed_by=tc.executed_by,
        test_type=tc.test_type,
        test_environment=tc.test_environment,
        automated=tc.automated,
        automation_script=tc.automation_script,
        requirement_id=tc.requirement_id,
        created_by_id=tc.created_by_id,
        created_at=tc.created_at,
        updated_at=tc.updated_at,
        requirement_title=tc.requirement.title if include_requirement and tc.requirement else None,
        requirement_id_str=tc.requirement.requirement_id if include_requirement and tc.requirement else None
    )
    return response


# ============================================================================
# CRUD Operations
# ============================================================================

@router.post("/", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case_data: TestCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new test case"""
    # Check if test_case_id already exists
    existing = db.query(TestCase).filter(
        TestCase.test_case_id == test_case_data.test_case_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Test case with ID '{test_case_data.test_case_id}' already exists"
        )

    # Verify requirement exists
    requirement = db.query(Requirement).filter(
        Requirement.id == test_case_data.requirement_id
    ).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {test_case_data.requirement_id} not found"
        )

    # Create new test case
    new_test_case = TestCase(
        **test_case_data.model_dump(),
        created_by_id=current_user.id
    )
    db.add(new_test_case)
    db.commit()
    db.refresh(new_test_case)

    return _build_test_case_response(new_test_case)


@router.get("/", response_model=TestCaseListResponse)
async def list_test_cases(
    status: Optional[TestCaseStatus] = Query(None, description="Filter by test status"),
    priority: Optional[TestCasePriority] = Query(None, description="Filter by priority"),
    requirement_id: Optional[int] = Query(None, description="Filter by requirement ID"),
    test_type: Optional[str] = Query(None, description="Filter by test type"),
    automated: Optional[bool] = Query(None, description="Filter automated/manual tests"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List test cases with filtering and pagination"""
    # Build query
    query = db.query(TestCase).options(joinedload(TestCase.requirement))

    # Apply filters
    if status:
        query = query.filter(TestCase.status == status)
    if priority:
        query = query.filter(TestCase.priority == priority)
    if requirement_id:
        query = query.filter(TestCase.requirement_id == requirement_id)
    if test_type:
        query = query.filter(TestCase.test_type.ilike(f"%{test_type}%"))
    if automated is not None:
        query = query.filter(TestCase.automated == automated)
    if search:
        search_filter = or_(
            TestCase.title.ilike(f"%{search}%"),
            TestCase.description.ilike(f"%{search}%"),
            TestCase.test_case_id.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # Get total count
    total = query.count()

    # Apply sorting
    if hasattr(TestCase, sort_by):
        order_column = getattr(TestCase, sort_by)
        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    test_cases = query.offset(offset).limit(page_size).all()

    # Build response
    return TestCaseListResponse(
        total=total,
        page=page,
        page_size=page_size,
        test_cases=[_build_test_case_response(tc) for tc in test_cases]
    )


@router.get("/stats", response_model=TestCaseStats)
async def get_test_case_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics about test cases"""
    # Total count
    total_test_cases = db.query(func.count(TestCase.id)).scalar()

    # Count by status
    by_status = {}
    status_counts = db.query(
        TestCase.status, func.count(TestCase.id)
    ).group_by(TestCase.status).all()
    for tc_status, count in status_counts:
        by_status[tc_status.value] = count

    # Count by priority
    by_priority = {}
    priority_counts = db.query(
        TestCase.priority, func.count(TestCase.id)
    ).group_by(TestCase.priority).all()
    for tc_priority, count in priority_counts:
        by_priority[tc_priority.value] = count

    # Automated vs manual
    total_automated = db.query(TestCase).filter(TestCase.automated == True).count()
    total_manual = total_test_cases - total_automated

    # Pass rate
    total_passed = db.query(TestCase).filter(TestCase.status == TestCaseStatus.PASSED).count()
    total_executed = db.query(TestCase).filter(
        TestCase.status.in_([TestCaseStatus.PASSED, TestCaseStatus.FAILED])
    ).count()
    pass_rate = (total_passed / total_executed * 100) if total_executed > 0 else 0.0

    # Average execution duration
    avg_duration = db.query(func.avg(TestCase.execution_duration)).filter(
        TestCase.execution_duration.isnot(None)
    ).scalar()

    return TestCaseStats(
        total_test_cases=total_test_cases,
        by_status=by_status,
        by_priority=by_priority,
        total_automated=total_automated,
        total_manual=total_manual,
        pass_rate=round(pass_rate, 2),
        avg_execution_duration=round(avg_duration, 2) if avg_duration else None
    )


@router.get("/{test_case_id}", response_model=TestCaseWithRequirement)
async def get_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific test case with requirement details"""
    test_case = db.query(TestCase).options(
        joinedload(TestCase.requirement)
    ).filter(TestCase.id == test_case_id).first()

    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with ID {test_case_id} not found"
        )

    # Build response with requirement
    from app.schemas.requirement import RequirementResponse
    from app.models.requirement import Requirement

    tc_response = _build_test_case_response(test_case)

    return TestCaseWithRequirement(
        **tc_response.model_dump(),
        requirement=RequirementResponse(
            id=test_case.requirement.id,
            requirement_id=test_case.requirement.requirement_id,
            type=test_case.requirement.type,
            category=test_case.requirement.category,
            title=test_case.requirement.title,
            description=test_case.requirement.description,
            priority=test_case.requirement.priority,
            status=test_case.requirement.status,
            verification_method=test_case.requirement.verification_method,
            regulatory_document=test_case.requirement.regulatory_document,
            regulatory_section=test_case.requirement.regulatory_section,
            regulatory_page=test_case.requirement.regulatory_page,
            file_path=test_case.requirement.file_path,
            version=test_case.requirement.version,
            revision_notes=test_case.requirement.revision_notes,
            created_by_id=test_case.requirement.created_by_id,
            created_at=test_case.requirement.created_at,
            updated_at=test_case.requirement.updated_at,
            test_case_count=0,
            parent_trace_count=0,
            child_trace_count=0
        )
    )


@router.put("/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    test_case_id: int,
    test_case_data: TestCaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing test case"""
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()

    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with ID {test_case_id} not found"
        )

    # If requirement_id is being updated, verify it exists
    update_data = test_case_data.model_dump(exclude_unset=True)
    if "requirement_id" in update_data:
        requirement = db.query(Requirement).filter(
            Requirement.id == update_data["requirement_id"]
        ).first()
        if not requirement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Requirement with ID {update_data['requirement_id']} not found"
            )

    # Update fields
    for field, value in update_data.items():
        setattr(test_case, field, value)

    db.commit()
    db.refresh(test_case)

    return _build_test_case_response(test_case)


@router.patch("/{test_case_id}/execute", response_model=TestCaseResponse)
async def execute_test_case(
    test_case_id: int,
    execution_data: TestCaseExecutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update test case execution results"""
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()

    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with ID {test_case_id} not found"
        )

    # Update execution fields
    test_case.status = execution_data.status
    test_case.actual_results = execution_data.actual_results
    test_case.execution_date = datetime.utcnow()
    test_case.execution_duration = execution_data.execution_duration
    test_case.executed_by = execution_data.executed_by or current_user.username

    db.commit()
    db.refresh(test_case)

    return _build_test_case_response(test_case)


@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a test case"""
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()

    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with ID {test_case_id} not found"
        )

    db.delete(test_case)
    db.commit()

    return None
