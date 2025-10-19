"""
Traceability Links API Routes
CRUD operations for traceability links with matrix and gap analysis.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models import (
    User, Requirement, TraceabilityLink, TraceLinkType,
    RequirementType, RequirementStatus, TestCase
)
from app.schemas.traceability import (
    TraceabilityLinkCreate, TraceabilityLinkUpdate, TraceabilityLinkResponse,
    TraceabilityLinkListResponse, TraceabilityLinkWithRequirements,
    TraceabilityLinkFilter, BulkTraceabilityCreate, BulkTraceabilityResponse,
    TraceabilityMatrix, RequirementTraceNode, TraceabilityGap, TraceabilityReport
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/traceability", tags=["traceability"])


# ============================================================================
# Helper Functions
# ============================================================================

def _build_trace_link_response(link: TraceabilityLink) -> TraceabilityLinkResponse:
    """Convert TraceabilityLink model to TraceabilityLinkResponse schema"""
    return TraceabilityLinkResponse(
        id=link.id,
        source_id=link.source_id,
        target_id=link.target_id,
        link_type=link.link_type,
        description=link.description,
        rationale=link.rationale,
        created_by_id=link.created_by_id,
        created_at=link.created_at,
        updated_at=link.updated_at,
        source_requirement_id=link.source.requirement_id if link.source else None,
        source_title=link.source.title if link.source else None,
        target_requirement_id=link.target.requirement_id if link.target else None,
        target_title=link.target.title if link.target else None
    )


# ============================================================================
# CRUD Operations
# ============================================================================

@router.post("/", response_model=TraceabilityLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_traceability_link(
    link_data: TraceabilityLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new traceability link"""
    # Verify source and target requirements exist
    source = db.query(Requirement).filter(Requirement.id == link_data.source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source requirement with ID {link_data.source_id} not found"
        )

    target = db.query(Requirement).filter(Requirement.id == link_data.target_id).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target requirement with ID {link_data.target_id} not found"
        )

    # Check for duplicate link
    existing = db.query(TraceabilityLink).filter(
        and_(
            TraceabilityLink.source_id == link_data.source_id,
            TraceabilityLink.target_id == link_data.target_id,
            TraceabilityLink.link_type == link_data.link_type
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Traceability link already exists between {source.requirement_id} and {target.requirement_id}"
        )

    # Create new link
    new_link = TraceabilityLink(
        **link_data.model_dump(),
        created_by_id=current_user.id
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    # Load relationships for response
    db.refresh(new_link)
    new_link = db.query(TraceabilityLink).options(
        joinedload(TraceabilityLink.source),
        joinedload(TraceabilityLink.target)
    ).filter(TraceabilityLink.id == new_link.id).first()

    return _build_trace_link_response(new_link)


@router.post("/bulk", response_model=BulkTraceabilityResponse)
async def create_bulk_traceability_links(
    bulk_data: BulkTraceabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create multiple traceability links at once"""
    created = 0
    skipped = 0
    failed = 0
    errors = []

    for link_data in bulk_data.links:
        try:
            # Check if link already exists
            existing = db.query(TraceabilityLink).filter(
                and_(
                    TraceabilityLink.source_id == link_data.source_id,
                    TraceabilityLink.target_id == link_data.target_id,
                    TraceabilityLink.link_type == link_data.link_type
                )
            ).first()

            if existing:
                if bulk_data.skip_duplicates:
                    skipped += 1
                    continue
                else:
                    errors.append(f"Duplicate link: source={link_data.source_id}, target={link_data.target_id}")
                    failed += 1
                    continue

            # Create link
            new_link = TraceabilityLink(
                **link_data.model_dump(),
                created_by_id=current_user.id
            )
            db.add(new_link)
            created += 1

        except Exception as e:
            errors.append(f"Error creating link (source={link_data.source_id}, target={link_data.target_id}): {str(e)}")
            failed += 1

    # Commit all successful links
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to commit bulk links: {str(e)}"
        )

    return BulkTraceabilityResponse(
        created=created,
        skipped=skipped,
        failed=failed,
        errors=errors
    )


@router.get("/", response_model=TraceabilityLinkListResponse)
async def list_traceability_links(
    link_type: Optional[TraceLinkType] = Query(None, description="Filter by link type"),
    source_id: Optional[int] = Query(None, description="Filter by source requirement ID"),
    target_id: Optional[int] = Query(None, description="Filter by target requirement ID"),
    requirement_id: Optional[int] = Query(None, description="Filter by either source or target"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List traceability links with filtering and pagination"""
    # Build query
    query = db.query(TraceabilityLink).options(
        joinedload(TraceabilityLink.source),
        joinedload(TraceabilityLink.target)
    )

    # Apply filters
    if link_type:
        query = query.filter(TraceabilityLink.link_type == link_type)
    if source_id:
        query = query.filter(TraceabilityLink.source_id == source_id)
    if target_id:
        query = query.filter(TraceabilityLink.target_id == target_id)
    if requirement_id:
        query = query.filter(
            or_(
                TraceabilityLink.source_id == requirement_id,
                TraceabilityLink.target_id == requirement_id
            )
        )

    # Get total count
    total = query.count()

    # Apply sorting
    if hasattr(TraceabilityLink, sort_by):
        order_column = getattr(TraceabilityLink, sort_by)
        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    links = query.offset(offset).limit(page_size).all()

    # Build response
    return TraceabilityLinkListResponse(
        total=total,
        page=page,
        page_size=page_size,
        links=[_build_trace_link_response(link) for link in links]
    )


@router.get("/matrix/{requirement_id}", response_model=TraceabilityMatrix)
async def get_traceability_matrix(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get full traceability matrix for a requirement"""
    requirement = db.query(Requirement).options(
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces),
        joinedload(Requirement.test_cases)
    ).filter(Requirement.id == requirement_id).first()

    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {requirement_id} not found"
        )

    # Build parent requirements list
    parent_reqs = []
    for link in requirement.parent_traces:
        if link.target:
            parent_reqs.append(RequirementTraceNode(
                id=link.target.id,
                requirement_id=link.target.requirement_id,
                title=link.target.title,
                type=link.target.type.value,
                status=link.target.status.value,
                has_test_cases=len(link.target.test_cases) > 0,
                test_case_count=len(link.target.test_cases)
            ))

    # Build child requirements list
    child_reqs = []
    for link in requirement.child_traces:
        if link.source:
            child_reqs.append(RequirementTraceNode(
                id=link.source.id,
                requirement_id=link.source.requirement_id,
                title=link.source.title,
                type=link.source.type.value,
                status=link.source.status.value,
                has_test_cases=len(link.source.test_cases) > 0,
                test_case_count=len(link.source.test_cases)
            ))

    # Build test cases list
    test_cases_list = [
        {
            "id": tc.id,
            "test_case_id": tc.test_case_id,
            "title": tc.title,
            "status": tc.status.value
        }
        for tc in requirement.test_cases
    ]

    # Determine coverage status
    if len(test_cases_list) == 0:
        coverage_status = "none"
    elif any(tc["status"] == "passed" for tc in test_cases_list):
        coverage_status = "full"
    else:
        coverage_status = "partial"

    return TraceabilityMatrix(
        requirement_id=requirement.id,
        requirement_identifier=requirement.requirement_id,
        title=requirement.title,
        type=requirement.type.value,
        parent_requirements=parent_reqs,
        child_requirements=child_reqs,
        test_cases=test_cases_list,
        total_parents=len(parent_reqs),
        total_children=len(child_reqs),
        total_tests=len(test_cases_list),
        coverage_status=coverage_status
    )


# ============================================================================
# Graph Visualization Endpoints (must come before /{link_id} to avoid conflicts)
# ============================================================================

@router.get("/graph")
async def get_traceability_graph(
    type: Optional[RequirementType] = Query(None, description="Filter by requirement type"),
    status: Optional[RequirementStatus] = Query(None, description="Filter by status"),
    include_tests: bool = Query(False, description="Include test cases as nodes"),
    max_nodes: int = Query(1000, ge=10, le=10000, description="Maximum nodes to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get graph data for interactive visualization.
    Returns nodes (requirements) and edges (traceability links).
    """
    # Build requirements query
    req_query = db.query(Requirement)

    # Apply filters
    if type:
        req_query = req_query.filter(Requirement.type == type)
    if status:
        req_query = req_query.filter(Requirement.status == status)

    # Limit nodes for performance
    requirements = req_query.limit(max_nodes).all()

    # Build nodes array
    nodes = []
    req_ids = set()

    for req in requirements:
        req_ids.add(req.id)
        nodes.append({
            "id": f"req_{req.id}",
            "label": req.requirement_id,
            "title": req.title,
            "type": req.type.value,
            "status": req.status.value,
            "priority": req.priority.value,
            "category": req.category,
            "test_count": len(req.test_cases),
            "node_type": "requirement"
        })

    # Add test cases as nodes if requested
    if include_tests:
        for req in requirements:
            for test in req.test_cases[:5]:  # Limit test nodes per requirement
                nodes.append({
                    "id": f"test_{test.id}",
                    "label": test.test_case_id,
                    "title": test.title,
                    "status": test.status.value,
                    "node_type": "test_case",
                    "requirement_id": req.id
                })

    # Build edges array from traceability links
    edges = []
    trace_links = db.query(TraceabilityLink).filter(
        or_(
            TraceabilityLink.source_id.in_(req_ids),
            TraceabilityLink.target_id.in_(req_ids)
        )
    ).all()

    for link in trace_links:
        if link.source_id in req_ids and link.target_id in req_ids:
            edges.append({
                "id": f"link_{link.id}",
                "source": f"req_{link.source_id}",
                "target": f"req_{link.target_id}",
                "link_type": link.link_type.value,
                "description": link.description
            })

    # Add test case edges if included
    if include_tests:
        for req in requirements:
            for test in req.test_cases[:5]:
                edges.append({
                    "id": f"test_link_{test.id}",
                    "source": f"req_{req.id}",
                    "target": f"test_{test.id}",
                    "link_type": "tests",
                    "description": "Test case"
                })

    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "filters_applied": {
            "type": type.value if type else None,
            "status": status.value if status else None,
            "include_tests": include_tests
        }
    }


@router.get("/orphaned")
async def get_orphaned_requirements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get requirements with no parent or child traceability links and no test cases.
    These are completely isolated requirements.
    """
    all_requirements = db.query(Requirement).options(
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces),
        joinedload(Requirement.test_cases)
    ).all()

    orphaned = []
    for req in all_requirements:
        has_parents = len(req.parent_traces) > 0
        has_children = len(req.child_traces) > 0
        has_tests = len(req.test_cases) > 0

        if not has_parents and not has_children and not has_tests:
            orphaned.append({
                "id": req.id,
                "requirement_id": req.requirement_id,
                "title": req.title,
                "type": req.type.value,
                "status": req.status.value,
                "priority": req.priority.value,
                "category": req.category,
                "created_at": req.created_at.isoformat()
            })

    return {
        "total_orphaned": len(orphaned),
        "orphaned_requirements": orphaned,
        "percentage": round((len(orphaned) / len(all_requirements) * 100), 2) if all_requirements else 0
    }


@router.get("/gaps")
async def get_traceability_gaps(
    gap_type: Optional[str] = Query(None, description="Filter by gap type: orphan, missing_parent, missing_test"),
    severity: Optional[str] = Query(None, description="Filter by severity: critical, high, medium, low"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive traceability gap analysis.
    Returns requirements missing parents, children, or test coverage.
    """
    all_requirements = db.query(Requirement).options(
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces),
        joinedload(Requirement.test_cases)
    ).all()

    gaps = {
        "missing_parents": [],
        "missing_children": [],
        "missing_tests": [],
        "orphaned": []
    }

    for req in all_requirements:
        has_parents = len(req.parent_traces) > 0
        has_children = len(req.child_traces) > 0
        has_tests = len(req.test_cases) > 0

        req_data = {
            "id": req.id,
            "requirement_id": req.requirement_id,
            "title": req.title,
            "type": req.type.value,
            "status": req.status.value,
            "priority": req.priority.value,
            "category": req.category
        }

        # Orphan check (no connections at all)
        if not has_parents and not has_children and not has_tests:
            gaps["orphaned"].append({**req_data, "severity": "high"})

        # Missing parent check (System/Technical should have parents)
        if req.type in [RequirementType.SYSTEM, RequirementType.TECHNICAL] and not has_parents:
            gaps["missing_parents"].append({**req_data, "severity": "medium"})

        # Missing children check (AHLR should have children)
        if req.type == RequirementType.AHLR and not has_children:
            gaps["missing_children"].append({**req_data, "severity": "medium"})

        # Missing test check (Approved requirements should have tests)
        if req.status == RequirementStatus.APPROVED and not has_tests:
            severity = "critical" if req.priority.value in ["Critical", "High"] else "high"
            gaps["missing_tests"].append({**req_data, "severity": severity})

    # Apply filters
    if gap_type:
        filtered_gaps = {gap_type: gaps.get(gap_type, [])}
    else:
        filtered_gaps = gaps

    # Apply severity filter
    if severity:
        for key in filtered_gaps:
            filtered_gaps[key] = [g for g in filtered_gaps[key] if g.get("severity") == severity]

    # Calculate statistics
    total_gaps = sum(len(v) for v in filtered_gaps.values())

    return {
        "total_gaps": total_gaps,
        "gaps": filtered_gaps,
        "summary": {
            "orphaned_count": len(gaps["orphaned"]),
            "missing_parents_count": len(gaps["missing_parents"]),
            "missing_children_count": len(gaps["missing_children"]),
            "missing_tests_count": len(gaps["missing_tests"])
        }
    }


@router.get("/report", response_model=TraceabilityReport)
async def get_traceability_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate comprehensive traceability analysis report"""
    # Total counts
    total_requirements = db.query(func.count(Requirement.id)).scalar()
    total_trace_links = db.query(func.count(TraceabilityLink.id)).scalar()
    total_test_cases = db.query(func.count(TestCase.id)).scalar()

    # Requirements with parents
    requirements_with_parents = db.query(Requirement).filter(
        Requirement.parent_traces.any()
    ).count()

    # Requirements with children
    requirements_with_children = db.query(Requirement).filter(
        Requirement.child_traces.any()
    ).count()

    # Requirements with tests
    requirements_with_tests = db.query(Requirement).filter(
        Requirement.test_cases.any()
    ).count()

    # Orphaned requirements (no parents, no children, no tests)
    all_requirements = db.query(Requirement).options(
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces),
        joinedload(Requirement.test_cases)
    ).all()

    orphaned_requirements = 0
    traceability_gaps = []

    for req in all_requirements:
        has_parents = len(req.parent_traces) > 0
        has_children = len(req.child_traces) > 0
        has_tests = len(req.test_cases) > 0

        # Orphan check
        if not has_parents and not has_children and not has_tests:
            orphaned_requirements += 1
            traceability_gaps.append(TraceabilityGap(
                requirement_id=req.id,
                requirement_identifier=req.requirement_id,
                title=req.title,
                type=req.type.value,
                gap_type="orphan",
                severity="high",
                description=f"Requirement {req.requirement_id} has no traceability links and no test cases"
            ))

        # Missing parent check (for System/Technical requirements)
        if req.type in [RequirementType.SYSTEM, RequirementType.TECHNICAL] and not has_parents:
            traceability_gaps.append(TraceabilityGap(
                requirement_id=req.id,
                requirement_identifier=req.requirement_id,
                title=req.title,
                type=req.type.value,
                gap_type="missing_parent",
                severity="medium",
                description=f"{req.type.value} requirement {req.requirement_id} is not traced to a parent requirement"
            ))

        # Missing test check
        if req.status == RequirementStatus.APPROVED and not has_tests:
            traceability_gaps.append(TraceabilityGap(
                requirement_id=req.id,
                requirement_identifier=req.requirement_id,
                title=req.title,
                type=req.type.value,
                gap_type="missing_test",
                severity="critical" if req.type == RequirementType.CERTIFICATION else "high",
                description=f"Approved requirement {req.requirement_id} has no test cases"
            ))

    # Statistics by requirement type
    by_type = {}
    type_counts = db.query(
        Requirement.type, func.count(Requirement.id)
    ).group_by(Requirement.type).all()
    for req_type, count in type_counts:
        by_type[req_type.value] = count

    # Calculate health scores
    traceability_score = 0.0
    test_coverage_score = 0.0

    if total_requirements > 0:
        # Traceability score: percentage of non-orphaned requirements
        traceability_score = ((total_requirements - orphaned_requirements) / total_requirements) * 100

        # Test coverage score: percentage with tests
        test_coverage_score = (requirements_with_tests / total_requirements) * 100

    return TraceabilityReport(
        total_requirements=total_requirements,
        total_trace_links=total_trace_links,
        total_test_cases=total_test_cases,
        requirements_with_parents=requirements_with_parents,
        requirements_with_children=requirements_with_children,
        requirements_with_tests=requirements_with_tests,
        orphaned_requirements=orphaned_requirements,
        traceability_gaps=traceability_gaps,
        by_type=by_type,
        traceability_score=round(traceability_score, 2),
        test_coverage_score=round(test_coverage_score, 2)
    )


@router.get("/conflicts")
async def get_requirement_conflicts(
    priority: Optional[str] = None,
    requirement_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Detect and return requirements with conflicts or inconsistencies

    Returns:
    - Explicit conflicts (conflicts_with link type)
    - Potential contradictions (same verification method, different priorities)
    - Duplicate requirements (similar titles)
    """
    from sqlalchemy import or_, and_

    # Get explicit conflicts
    conflict_links = db.query(TraceabilityLink).filter(
        TraceabilityLink.link_type == TraceLinkType.CONFLICTS_WITH
    ).all()

    explicit_conflicts = []
    for link in conflict_links:
        source = db.query(Requirement).filter(Requirement.id == link.source_id).first()
        target = db.query(Requirement).filter(Requirement.id == link.target_id).first()

        if source and target:
            explicit_conflicts.append({
                "conflict_id": link.id,
                "type": "explicit",
                "severity": "high",
                "source": {
                    "id": source.id,
                    "requirement_id": source.requirement_id,
                    "title": source.title,
                    "priority": source.priority.value,
                    "status": source.status.value
                },
                "target": {
                    "id": target.id,
                    "requirement_id": target.requirement_id,
                    "title": target.title,
                    "priority": target.priority.value,
                    "status": target.status.value
                },
                "description": link.description or "Explicit conflict detected",
                "rationale": link.rationale
            })

    # Detect priority inconsistencies within same category
    priority_conflicts = []
    categories = db.query(Requirement.category).distinct().all()

    for (category,) in categories:
        if not category:
            continue

        reqs = db.query(Requirement).filter(
            Requirement.category == category,
            Requirement.status == RequirementStatus.APPROVED
        ).all()

        # Group by verification method
        by_verification = {}
        for req in reqs:
            vm = req.verification_method.value if req.verification_method else "UNSPECIFIED"
            if vm not in by_verification:
                by_verification[vm] = []
            by_verification[vm].append(req)

        # Check for priority inconsistencies
        for vm, req_list in by_verification.items():
            priorities = set(r.priority.value for r in req_list if r.priority)
            if len(priorities) > 2:  # More than 2 different priorities for same verification method
                priority_conflicts.append({
                    "type": "priority_inconsistency",
                    "severity": "medium",
                    "category": category,
                    "verification_method": vm,
                    "priorities": list(priorities),
                    "count": len(req_list),
                    "description": f"{len(req_list)} requirements in {category} with {vm} verification have inconsistent priorities",
                    "requirements": [
                        {
                            "id": r.id,
                            "requirement_id": r.requirement_id,
                            "title": r.title[:100],
                            "priority": r.priority.value
                        } for r in req_list[:5]  # Show first 5
                    ]
                })

    # Detect potential duplicates (similar titles)
    potential_duplicates = []
    all_requirements = db.query(Requirement).filter(
        or_(
            Requirement.status == RequirementStatus.APPROVED,
            Requirement.status == RequirementStatus.UNDER_REVIEW
        )
    ).all()

    # Simple title similarity check (first 50 chars)
    title_groups = {}
    for req in all_requirements:
        title_start = req.title[:50].lower().strip()
        if len(title_start) < 10:  # Skip very short titles
            continue
        if title_start not in title_groups:
            title_groups[title_start] = []
        title_groups[title_start].append(req)

    for title, reqs in title_groups.items():
        if len(reqs) > 1:
            potential_duplicates.append({
                "type": "potential_duplicate",
                "severity": "low",
                "title_prefix": title,
                "count": len(reqs),
                "description": f"{len(reqs)} requirements with similar titles detected",
                "requirements": [
                    {
                        "id": r.id,
                        "requirement_id": r.requirement_id,
                        "title": r.title,
                        "type": r.type.value,
                        "status": r.status.value
                    } for r in reqs
                ]
            })

    # Summary statistics
    total_conflicts = len(explicit_conflicts) + len(priority_conflicts) + len(potential_duplicates)

    return {
        "total_conflicts": total_conflicts,
        "explicit_conflicts": len(explicit_conflicts),
        "priority_inconsistencies": len(priority_conflicts),
        "potential_duplicates": len(potential_duplicates),
        "conflicts": {
            "explicit": explicit_conflicts,
            "priority_inconsistencies": priority_conflicts[:10],  # Limit to 10
            "potential_duplicates": potential_duplicates[:20]  # Limit to 20
        },
        "summary": {
            "high_severity": len(explicit_conflicts),
            "medium_severity": len(priority_conflicts),
            "low_severity": len(potential_duplicates)
        }
    }


@router.get("/{link_id}", response_model=TraceabilityLinkWithRequirements)
async def get_traceability_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific traceability link with full requirement details"""
    link = db.query(TraceabilityLink).options(
        joinedload(TraceabilityLink.source),
        joinedload(TraceabilityLink.target)
    ).filter(TraceabilityLink.id == link_id).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Traceability link with ID {link_id} not found"
        )

    # Build response with full requirements
    from app.schemas.requirement import RequirementResponse

    link_response = _build_trace_link_response(link)

    return TraceabilityLinkWithRequirements(
        **link_response.model_dump(),
        source_requirement=RequirementResponse(
            id=link.source.id,
            requirement_id=link.source.requirement_id,
            type=link.source.type,
            category=link.source.category,
            title=link.source.title,
            description=link.source.description,
            priority=link.source.priority,
            status=link.source.status,
            verification_method=link.source.verification_method,
            regulatory_document=link.source.regulatory_document,
            regulatory_section=link.source.regulatory_section,
            regulatory_page=link.source.regulatory_page,
            file_path=link.source.file_path,
            version=link.source.version,
            revision_notes=link.source.revision_notes,
            created_by_id=link.source.created_by_id,
            created_at=link.source.created_at,
            updated_at=link.source.updated_at,
            test_case_count=0,
            parent_trace_count=0,
            child_trace_count=0
        ),
        target_requirement=RequirementResponse(
            id=link.target.id,
            requirement_id=link.target.requirement_id,
            type=link.target.type,
            category=link.target.category,
            title=link.target.title,
            description=link.target.description,
            priority=link.target.priority,
            status=link.target.status,
            verification_method=link.target.verification_method,
            regulatory_document=link.target.regulatory_document,
            regulatory_section=link.target.regulatory_section,
            regulatory_page=link.target.regulatory_page,
            file_path=link.target.file_path,
            version=link.target.version,
            revision_notes=link.target.revision_notes,
            created_by_id=link.target.created_by_id,
            created_at=link.target.created_at,
            updated_at=link.target.updated_at,
            test_case_count=0,
            parent_trace_count=0,
            child_trace_count=0
        )
    )


@router.put("/{link_id}", response_model=TraceabilityLinkResponse)
async def update_traceability_link(
    link_id: int,
    link_data: TraceabilityLinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing traceability link"""
    link = db.query(TraceabilityLink).filter(TraceabilityLink.id == link_id).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Traceability link with ID {link_id} not found"
        )

    # Update fields
    update_data = link_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(link, field, value)

    db.commit()
    db.refresh(link)

    # Load relationships for response
    link = db.query(TraceabilityLink).options(
        joinedload(TraceabilityLink.source),
        joinedload(TraceabilityLink.target)
    ).filter(TraceabilityLink.id == link_id).first()

    return _build_trace_link_response(link)


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_traceability_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a traceability link"""
    link = db.query(TraceabilityLink).filter(TraceabilityLink.id == link_id).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Traceability link with ID {link_id} not found"
        )

    db.delete(link)
    db.commit()

    return None
