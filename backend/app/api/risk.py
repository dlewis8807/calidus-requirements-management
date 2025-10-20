"""
Risk Assessment API Endpoints
Provides risk scoring and analytics for requirements.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.requirement import Requirement, RequirementType, RequirementStatus, RequirementPriority
from app.schemas.risk import (
    RiskScore,
    RequirementRiskResponse,
    RiskOverview,
    RiskDistribution
)
from app.services.risk_analyzer import RiskAnalyzer


router = APIRouter(prefix="/api/risk", tags=["Risk Assessment"])


@router.get("/overview", response_model=RiskOverview)
async def get_risk_overview(
    requirement_type: Optional[RequirementType] = Query(None, description="Filter by requirement type"),
    status: Optional[RequirementStatus] = Query(None, description="Filter by status"),
    priority: Optional[RequirementPriority] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall risk analytics overview.
    Returns risk distribution, key metrics, and top risk requirements.
    """
    # Build query with filters
    query = db.query(Requirement).options(
        joinedload(Requirement.test_cases),
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces)
    )

    if requirement_type:
        query = query.filter(Requirement.type == requirement_type)
    if status:
        query = query.filter(Requirement.status == status)
    if priority:
        query = query.filter(Requirement.priority == priority)

    requirements = query.all()

    if not requirements:
        return RiskOverview(
            distribution=RiskDistribution(critical=0, high=0, medium=0, low=0, total=0),
            average_risk_score=0.0,
            critical_requirements=0,
            untested_requirements=0,
            orphaned_requirements=0,
            non_compliant_requirements=0,
            top_risks=[]
        )

    # Initialize risk analyzer
    analyzer = RiskAnalyzer(db)

    # Calculate risk scores for all requirements
    risk_scores = []
    for req in requirements:
        risk_score = analyzer.calculate_risk_score(req)
        risk_scores.append((req, risk_score))

    # Calculate distribution
    distribution_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    total_risk = 0.0

    for req, risk_score in risk_scores:
        distribution_counts[risk_score.risk_level] += 1
        total_risk += risk_score.total_risk_score

    distribution = RiskDistribution(
        critical=distribution_counts["Critical"],
        high=distribution_counts["High"],
        medium=distribution_counts["Medium"],
        low=distribution_counts["Low"],
        total=len(requirements)
    )

    # Calculate metrics
    average_risk_score = total_risk / len(requirements) if requirements else 0.0

    critical_requirements = sum(1 for req in requirements if req.priority == RequirementPriority.CRITICAL)

    untested_requirements = sum(
        1 for req in requirements
        if not req.test_cases or len(req.test_cases) == 0
    )

    orphaned_requirements = sum(
        1 for req in requirements
        if (not req.parent_traces or len(req.parent_traces) == 0) and
           (not req.child_traces or len(req.child_traces) == 0)
    )

    non_compliant_requirements = sum(
        1 for req in requirements
        if req.compliance_status and req.compliance_status.lower() in ["non_compliant", "failed"]
    )

    # Get top 10 highest risk requirements
    sorted_risks = sorted(risk_scores, key=lambda x: x[1].total_risk_score, reverse=True)[:10]

    top_risks = [
        RequirementRiskResponse(
            id=req.id,
            requirement_id=req.requirement_id,
            title=req.title,
            description=req.description,
            type=req.type,
            status=req.status,
            priority=req.priority,
            category=req.category,
            risk_score=risk_score,
            created_at=req.created_at,
            updated_at=req.updated_at
        )
        for req, risk_score in sorted_risks
    ]

    return RiskOverview(
        distribution=distribution,
        average_risk_score=round(average_risk_score, 1),
        critical_requirements=critical_requirements,
        untested_requirements=untested_requirements,
        orphaned_requirements=orphaned_requirements,
        non_compliant_requirements=non_compliant_requirements,
        top_risks=top_risks
    )


@router.get("/requirements", response_model=List[RequirementRiskResponse])
async def get_requirements_with_risk(
    requirement_type: Optional[RequirementType] = Query(None, description="Filter by requirement type"),
    status: Optional[RequirementStatus] = Query(None, description="Filter by status"),
    priority: Optional[RequirementPriority] = Query(None, description="Filter by priority"),
    min_risk_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum risk score"),
    max_risk_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum risk score"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level: Critical, High, Medium, Low"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get requirements with risk assessments.
    Supports filtering by requirement properties and risk scores.
    """
    # Build query with filters
    query = db.query(Requirement).options(
        joinedload(Requirement.test_cases),
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces)
    )

    if requirement_type:
        query = query.filter(Requirement.type == requirement_type)
    if status:
        query = query.filter(Requirement.status == status)
    if priority:
        query = query.filter(Requirement.priority == priority)

    # Get all matching requirements (need to calculate risk before filtering by risk score)
    all_requirements = query.all()

    # Initialize risk analyzer
    analyzer = RiskAnalyzer(db)

    # Calculate risk scores and filter
    results = []
    for req in all_requirements:
        risk_score = analyzer.calculate_risk_score(req)

        # Apply risk filters
        if min_risk_score is not None and risk_score.total_risk_score < min_risk_score:
            continue
        if max_risk_score is not None and risk_score.total_risk_score > max_risk_score:
            continue
        if risk_level and risk_score.risk_level != risk_level:
            continue

        results.append(
            RequirementRiskResponse(
                id=req.id,
                requirement_id=req.requirement_id,
                title=req.title,
                description=req.description,
                type=req.type,
                status=req.status,
                priority=req.priority,
                category=req.category,
                risk_score=risk_score,
                created_at=req.created_at,
                updated_at=req.updated_at
            )
        )

    # Sort by risk score (highest first)
    results.sort(key=lambda x: x.risk_score.total_risk_score, reverse=True)

    # Apply pagination
    paginated_results = results[offset:offset + limit]

    return paginated_results


@router.get("/requirements/{requirement_id}", response_model=RequirementRiskResponse)
async def get_requirement_risk(
    requirement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get risk assessment for a specific requirement.

    Args:
        requirement_id: Requirement identifier (e.g., "AHLR-001")
    """
    # Query requirement with all relationships
    requirement = db.query(Requirement).options(
        joinedload(Requirement.test_cases),
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces)
    ).filter(Requirement.requirement_id == requirement_id).first()

    if not requirement:
        raise HTTPException(status_code=404, detail=f"Requirement {requirement_id} not found")

    # Calculate risk score
    analyzer = RiskAnalyzer(db)
    risk_score = analyzer.calculate_risk_score(requirement)

    return RequirementRiskResponse(
        id=requirement.id,
        requirement_id=requirement.requirement_id,
        title=requirement.title,
        description=requirement.description,
        type=requirement.type,
        status=requirement.status,
        priority=requirement.priority,
        category=requirement.category,
        risk_score=risk_score,
        created_at=requirement.created_at,
        updated_at=requirement.updated_at
    )


@router.get("/requirements/by-id/{req_id}", response_model=RiskScore)
async def get_requirement_risk_score_only(
    req_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get only the risk score for a requirement by database ID.
    Lighter endpoint for quick risk lookups.

    Args:
        req_id: Database ID of the requirement
    """
    requirement = db.query(Requirement).options(
        joinedload(Requirement.test_cases),
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces)
    ).filter(Requirement.id == req_id).first()

    if not requirement:
        raise HTTPException(status_code=404, detail=f"Requirement with ID {req_id} not found")

    # Calculate risk score
    analyzer = RiskAnalyzer(db)
    risk_score = analyzer.calculate_risk_score(requirement)

    return risk_score


@router.get("/critical", response_model=List[RequirementRiskResponse])
async def get_critical_risks(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get requirements with critical risk level.
    Sorted by risk score (highest first).
    """
    # Get all requirements
    requirements = db.query(Requirement).options(
        joinedload(Requirement.test_cases),
        joinedload(Requirement.parent_traces),
        joinedload(Requirement.child_traces)
    ).all()

    # Calculate risk scores and filter for critical
    analyzer = RiskAnalyzer(db)
    critical_risks = []

    for req in requirements:
        risk_score = analyzer.calculate_risk_score(req)

        if risk_score.risk_level == "Critical":
            critical_risks.append(
                RequirementRiskResponse(
                    id=req.id,
                    requirement_id=req.requirement_id,
                    title=req.title,
                    description=req.description,
                    type=req.type,
                    status=req.status,
                    priority=req.priority,
                    category=req.category,
                    risk_score=risk_score,
                    created_at=req.created_at,
                    updated_at=req.updated_at
                )
            )

    # Sort by risk score (highest first)
    critical_risks.sort(key=lambda x: x.risk_score.total_risk_score, reverse=True)

    return critical_risks[:limit]
