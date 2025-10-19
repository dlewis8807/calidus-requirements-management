"""
Requirements API Routes
CRUD operations for requirements with filtering, pagination, and statistics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional
from app.database import get_db
from app.models import User, Requirement, RequirementStatus, RequirementType, RequirementPriority
from app.schemas.requirement import (
    RequirementCreate, RequirementUpdate, RequirementResponse,
    RequirementListResponse, RequirementWithRelations, RequirementFilter,
    RequirementStats
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/requirements", tags=["requirements"])


# ============================================================================
# Helper Functions
# ============================================================================

def _build_requirement_response(req: Requirement) -> RequirementResponse:
    """Convert Requirement model to RequirementResponse schema"""
    return RequirementResponse(
        id=req.id,
        requirement_id=req.requirement_id,
        type=req.type,
        category=req.category,
        title=req.title,
        description=req.description,
        priority=req.priority,
        status=req.status,
        verification_method=req.verification_method,
        regulatory_document=req.regulatory_document,
        regulatory_section=req.regulatory_section,
        regulatory_page=req.regulatory_page,
        file_path=req.file_path,
        version=req.version,
        created_by_id=req.created_by_id,
        created_at=req.created_at,
        updated_at=req.updated_at,
        test_case_count=len(req.test_cases) if req.test_cases else 0,
        parent_trace_count=len(req.parent_traces) if req.parent_traces else 0,
        child_trace_count=len(req.child_traces) if req.child_traces else 0,
    )


# ============================================================================
# CRUD Operations
# ============================================================================

@router.post("/", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement(
    requirement_data: RequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new requirement"""
    # Check if requirement_id already exists
    existing = db.query(Requirement).filter(
        Requirement.requirement_id == requirement_data.requirement_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Requirement with ID '{requirement_data.requirement_id}' already exists"
        )

    # Create new requirement
    new_requirement = Requirement(
        **requirement_data.model_dump(),
        created_by_id=current_user.id
    )
    db.add(new_requirement)
    db.commit()
    db.refresh(new_requirement)

    return _build_requirement_response(new_requirement)


@router.get("/", response_model=RequirementListResponse)
async def list_requirements(
    type: Optional[RequirementType] = Query(None, description="Filter by requirement type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[RequirementStatus] = Query(None, description="Filter by status"),
    priority: Optional[RequirementPriority] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    regulatory_document: Optional[str] = Query(None, description="Filter by regulatory document"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List requirements with filtering and pagination"""
    # Build query
    query = db.query(Requirement).options(
        joinedload(Requirement.test_cases),
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces)
    )

    # Apply filters
    if type:
        query = query.filter(Requirement.type == type)
    if category:
        query = query.filter(Requirement.category == category)
    if status:
        query = query.filter(Requirement.status == status)
    if priority:
        query = query.filter(Requirement.priority == priority)
    if regulatory_document:
        query = query.filter(Requirement.regulatory_document.ilike(f"%{regulatory_document}%"))
    if search:
        search_filter = or_(
            Requirement.title.ilike(f"%{search}%"),
            Requirement.description.ilike(f"%{search}%"),
            Requirement.requirement_id.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # Get total count
    total = query.count()

    # Apply sorting
    if hasattr(Requirement, sort_by):
        order_column = getattr(Requirement, sort_by)
        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    requirements = query.offset(offset).limit(page_size).all()

    # Build response
    return RequirementListResponse(
        total=total,
        page=page,
        page_size=page_size,
        requirements=[_build_requirement_response(req) for req in requirements]
    )


@router.get("/stats", response_model=RequirementStats)
async def get_requirement_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics about requirements"""
    # Total count
    total_requirements = db.query(func.count(Requirement.id)).scalar()

    # Count by type
    by_type = {}
    type_counts = db.query(
        Requirement.type, func.count(Requirement.id)
    ).group_by(Requirement.type).all()
    for req_type, count in type_counts:
        by_type[req_type.value] = count

    # Count by status
    by_status = {}
    status_counts = db.query(
        Requirement.status, func.count(Requirement.id)
    ).group_by(Requirement.status).all()
    for req_status, count in status_counts:
        by_status[req_status.value] = count

    # Count by priority
    by_priority = {}
    priority_counts = db.query(
        Requirement.priority, func.count(Requirement.id)
    ).group_by(Requirement.priority).all()
    for req_priority, count in priority_counts:
        by_priority[req_priority.value] = count

    # Requirements with test cases
    total_with_tests = db.query(Requirement).filter(
        Requirement.test_cases.any()
    ).count()

    # Requirements with traceability links
    total_with_traces = db.query(Requirement).filter(
        or_(
            Requirement.parent_traces.any(),
            Requirement.child_traces.any()
        )
    ).count()

    # Coverage percentage
    coverage_percentage = (total_with_tests / total_requirements * 100) if total_requirements > 0 else 0.0

    return RequirementStats(
        total_requirements=total_requirements,
        by_type=by_type,
        by_status=by_status,
        by_priority=by_priority,
        total_with_tests=total_with_tests,
        total_with_traces=total_with_traces,
        coverage_percentage=round(coverage_percentage, 2)
    )


@router.get("/by-req-id/{req_id}", response_model=RequirementWithRelations)
async def get_requirement_by_req_id(
    req_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific requirement by requirement_id (e.g., AHLR-001) with all relationships"""
    requirement = db.query(Requirement).options(
        joinedload(Requirement.test_cases),
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces)
    ).filter(Requirement.requirement_id == req_id).first()

    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID '{req_id}' not found"
        )

    # Build response with relationships
    from app.schemas.test_case import TestCaseResponse
    from app.schemas.traceability import TraceabilityLinkResponse

    response_data = _build_requirement_response(requirement)

    return RequirementWithRelations(
        **response_data.model_dump(),
        test_cases=[
            TestCaseResponse(
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
                requirement_title=requirement.title,
                requirement_id_str=requirement.requirement_id
            ).model_dump() for tc in requirement.test_cases
        ],
        parent_traces=[
            TraceabilityLinkResponse(
                id=link.id,
                source_id=link.source_id,
                target_id=link.target_id,
                link_type=link.link_type,
                description=link.description,
                rationale=link.rationale,
                created_by_id=link.created_by_id,
                created_at=link.created_at,
                updated_at=None,  # TraceabilityLink model doesn't have updated_at field
                source_requirement_id=link.source.requirement_id if link.source else None,
                source_title=link.source.title if link.source else None,
                target_requirement_id=link.target.requirement_id if link.target else None,
                target_title=link.target.title if link.target else None
            ).model_dump() for link in requirement.parent_traces
        ],
        child_traces=[
            TraceabilityLinkResponse(
                id=link.id,
                source_id=link.source_id,
                target_id=link.target_id,
                link_type=link.link_type,
                description=link.description,
                rationale=link.rationale,
                created_by_id=link.created_by_id,
                created_at=link.created_at,
                updated_at=None,  # TraceabilityLink model doesn't have updated_at field
                source_requirement_id=link.source.requirement_id if link.source else None,
                source_title=link.source.title if link.source else None,
                target_requirement_id=link.target.requirement_id if link.target else None,
                target_title=link.target.title if link.target else None
            ).model_dump() for link in requirement.child_traces
        ]
    )


@router.get("/{requirement_id}", response_model=RequirementWithRelations)
async def get_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific requirement by database ID with all relationships"""
    requirement = db.query(Requirement).options(
        joinedload(Requirement.test_cases),
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces)
    ).filter(Requirement.id == requirement_id).first()

    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {requirement_id} not found"
        )

    # Build response with relationships
    from app.schemas.test_case import TestCaseResponse
    from app.schemas.traceability import TraceabilityLinkResponse

    response_data = _build_requirement_response(requirement)

    return RequirementWithRelations(
        **response_data.model_dump(),
        test_cases=[
            TestCaseResponse(
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
                requirement_title=requirement.title,
                requirement_id_str=requirement.requirement_id
            ).model_dump() for tc in requirement.test_cases
        ],
        parent_traces=[
            TraceabilityLinkResponse(
                id=link.id,
                source_id=link.source_id,
                target_id=link.target_id,
                link_type=link.link_type,
                description=link.description,
                rationale=link.rationale,
                created_by_id=link.created_by_id,
                created_at=link.created_at,
                updated_at=None,  # TraceabilityLink model doesn't have updated_at field
                source_requirement_id=link.source.requirement_id if link.source else None,
                source_title=link.source.title if link.source else None,
                target_requirement_id=link.target.requirement_id if link.target else None,
                target_title=link.target.title if link.target else None
            ).model_dump() for link in requirement.parent_traces
        ],
        child_traces=[
            TraceabilityLinkResponse(
                id=link.id,
                source_id=link.source_id,
                target_id=link.target_id,
                link_type=link.link_type,
                description=link.description,
                rationale=link.rationale,
                created_by_id=link.created_by_id,
                created_at=link.created_at,
                updated_at=None,  # TraceabilityLink model doesn't have updated_at field
                source_requirement_id=link.source.requirement_id if link.source else None,
                source_title=link.source.title if link.source else None,
                target_requirement_id=link.target.requirement_id if link.target else None,
                target_title=link.target.title if link.target else None
            ).model_dump() for link in requirement.child_traces
        ]
    )


@router.put("/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(
    requirement_id: int,
    requirement_data: RequirementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing requirement"""
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()

    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {requirement_id} not found"
        )

    # Update fields
    update_data = requirement_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(requirement, field, value)

    db.commit()
    db.refresh(requirement)

    return _build_requirement_response(requirement)


@router.delete("/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a requirement (CASCADE deletes test cases and traceability links)"""
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()

    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {requirement_id} not found"
        )

    db.delete(requirement)
    db.commit()

    return None
