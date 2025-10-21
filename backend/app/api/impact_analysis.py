"""
Impact Analysis API Endpoints
REST API for performing impact analysis on requirement changes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.requirement import Requirement
from app.models.impact_analysis import ImpactAnalysisReport, ChangeRequest, RiskLevel, ChangeRequestStatus
from app.services.impact_analysis import (
    ImpactAnalysisService,
    ImpactAnalysisConfig as ServiceConfig
)
from app.schemas.impact_analysis import (
    AnalyzeImpactRequest,
    ImpactAnalysisResultSchema,
    ImpactAnalysisReportResponse,
    ImpactAnalysisReportListResponse,
    CreateChangeRequestRequest,
    ChangeRequestResponse,
    ChangeRequestListResponse,
    ReviewChangeRequestRequest,
    ImpactNodeSchema,
    RiskScoreSchema
)
from app.schemas.requirement import RequirementResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/impact-analysis", tags=["Impact Analysis"])


@router.post("/analyze", response_model=ImpactAnalysisResultSchema)
async def analyze_impact(
    request: AnalyzeImpactRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform impact analysis for a requirement change.

    Analyzes upstream (parent) and downstream (child) requirements,
    calculates risk score, and generates recommendations.
    """
    logger.info(f"User {current_user.username} analyzing impact for requirement {request.requirement_id}")

    # Create service
    service = ImpactAnalysisService(db)

    # Convert request config to service config
    config = None
    if request.config:
        config = ServiceConfig(
            max_depth=request.config.max_depth,
            include_test_cases=request.config.include_test_cases,
            include_regulatory=request.config.include_regulatory,
            weights=request.config.weights
        )

    # Perform analysis
    try:
        result = service.analyze_impact(request.requirement_id, config)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during impact analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform impact analysis"
        )

    # Save report to database
    report = ImpactAnalysisReport(
        requirement_id=request.requirement_id,
        analyzed_by_id=current_user.id,
        risk_score=result.risk_score.score,
        risk_level=RiskLevel[result.risk_score.level],
        upstream_count=len(result.upstream),
        downstream_count=len(result.downstream),
        test_case_count=len(result.affected_test_cases),
        regulatory_impact=len(result.regulatory_implications) > 0,
        upstream_tree=[node.to_dict() for node in result.upstream],
        downstream_tree=[node.to_dict() for node in result.downstream],
        affected_requirements=[node.id for node in result.upstream + result.downstream],
        affected_test_cases=result.affected_test_cases,
        recommendations=result.recommendations,
        regulatory_implications=result.regulatory_implications,
        risk_factors=result.risk_score.factors,
        estimated_effort_hours=result.estimated_effort_hours,
        stats=result.stats
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    logger.info(f"Impact analysis report {report.id} created")

    # Convert requirement to dict for response
    req_dict = {
        "id": result.requirement.id,
        "requirement_id": result.requirement.requirement_id,
        "title": result.requirement.title,
        "type": result.requirement.type.value if hasattr(result.requirement.type, 'value') else str(result.requirement.type),
        "priority": result.requirement.priority.value if hasattr(result.requirement.priority, 'value') else str(result.requirement.priority),
        "status": result.requirement.status.value if hasattr(result.requirement.status, 'value') else str(result.requirement.status)
    }

    # Build response
    return ImpactAnalysisResultSchema(
        requirement=req_dict,
        upstream=[ImpactNodeSchema(**node.to_dict()) for node in result.upstream],
        downstream=[ImpactNodeSchema(**node.to_dict()) for node in result.downstream],
        risk_score=RiskScoreSchema(**result.risk_score.to_dict()),
        stats=result.stats,
        affected_test_cases=result.affected_test_cases,
        regulatory_implications=result.regulatory_implications,
        recommendations=result.recommendations,
        estimated_effort_hours=result.estimated_effort_hours
    )


@router.get("/reports/{report_id}", response_model=ImpactAnalysisReportResponse)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a previously generated impact analysis report.
    """
    report = db.query(ImpactAnalysisReport).filter(
        ImpactAnalysisReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )

    return report


@router.get("/reports", response_model=ImpactAnalysisReportListResponse)
async def list_reports(
    requirement_id: Optional[int] = Query(None),
    risk_level: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List impact analysis reports with optional filters.
    """
    query = db.query(ImpactAnalysisReport)

    # Apply filters
    if requirement_id:
        query = query.filter(ImpactAnalysisReport.requirement_id == requirement_id)

    if risk_level:
        try:
            risk_enum = RiskLevel[risk_level.upper()]
            query = query.filter(ImpactAnalysisReport.risk_level == risk_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid risk level: {risk_level}"
            )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    reports = query.order_by(ImpactAnalysisReport.created_at.desc()).offset(offset).limit(page_size).all()

    return ImpactAnalysisReportListResponse(
        reports=reports,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/change-requests", response_model=ChangeRequestResponse)
async def create_change_request(
    request: CreateChangeRequestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a change request with optional impact analysis.
    """
    # Verify requirement exists
    requirement = db.query(Requirement).filter(
        Requirement.id == request.requirement_id
    ).first()

    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {request.requirement_id} not found"
        )

    impact_report_id = None
    impact_summary = None

    # Perform impact analysis if requested
    if request.perform_impact_analysis:
        service = ImpactAnalysisService(db)
        try:
            result = service.analyze_impact(request.requirement_id)

            # Save impact report
            report = ImpactAnalysisReport(
                requirement_id=request.requirement_id,
                analyzed_by_id=current_user.id,
                risk_score=result.risk_score.score,
                risk_level=RiskLevel[result.risk_score.level],
                upstream_count=len(result.upstream),
                downstream_count=len(result.downstream),
                test_case_count=len(result.affected_test_cases),
                regulatory_impact=len(result.regulatory_implications) > 0,
                upstream_tree=[node.to_dict() for node in result.upstream],
                downstream_tree=[node.to_dict() for node in result.downstream],
                affected_requirements=[node.id for node in result.upstream + result.downstream],
                affected_test_cases=result.affected_test_cases,
                recommendations=result.recommendations,
                regulatory_implications=result.regulatory_implications,
                risk_factors=result.risk_score.factors,
                estimated_effort_hours=result.estimated_effort_hours,
                stats=result.stats
            )

            db.add(report)
            db.flush()  # Get report ID without committing

            impact_report_id = report.id
            impact_summary = {
                "risk_level": result.risk_score.level,
                "risk_score": result.risk_score.score,
                "affected_requirements": len(result.upstream) + len(result.downstream),
                "affected_test_cases": len(result.affected_test_cases)
            }

        except Exception as e:
            logger.error(f"Error performing impact analysis: {e}", exc_info=True)
            # Continue creating change request without impact analysis

    # Create change request
    change_request = ChangeRequest(
        requirement_id=request.requirement_id,
        impact_report_id=impact_report_id,
        title=request.title,
        description=request.description,
        justification=request.justification,
        proposed_changes=request.proposed_changes,
        status=ChangeRequestStatus.PENDING,
        requested_by_id=current_user.id
    )

    db.add(change_request)
    db.commit()
    db.refresh(change_request)

    logger.info(f"Change request {change_request.id} created by {current_user.username}")

    # Build response
    response = ChangeRequestResponse(
        id=change_request.id,
        requirement_id=change_request.requirement_id,
        impact_report_id=change_request.impact_report_id,
        title=change_request.title,
        description=change_request.description,
        justification=change_request.justification,
        proposed_changes=change_request.proposed_changes,
        status=change_request.status.value,
        requested_by_id=change_request.requested_by_id,
        reviewed_by_id=change_request.reviewed_by_id,
        review_comments=change_request.review_comments,
        created_at=change_request.created_at,
        updated_at=change_request.updated_at,
        reviewed_at=change_request.reviewed_at,
        implemented_at=change_request.implemented_at,
        impact_summary=impact_summary
    )

    return response


@router.get("/change-requests", response_model=ChangeRequestListResponse)
async def list_change_requests(
    requirement_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List change requests with optional filters.
    """
    query = db.query(ChangeRequest)

    # Apply filters
    if requirement_id:
        query = query.filter(ChangeRequest.requirement_id == requirement_id)

    if status:
        try:
            status_enum = ChangeRequestStatus[status.upper()]
            query = query.filter(ChangeRequest.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    change_requests = query.order_by(ChangeRequest.created_at.desc()).offset(offset).limit(page_size).all()

    # Build responses with impact summaries
    responses = []
    for cr in change_requests:
        impact_summary = None
        if cr.impact_report_id:
            report = db.query(ImpactAnalysisReport).filter(
                ImpactAnalysisReport.id == cr.impact_report_id
            ).first()
            if report:
                impact_summary = {
                    "risk_level": report.risk_level.value,
                    "risk_score": report.risk_score,
                    "affected_requirements": report.upstream_count + report.downstream_count,
                    "affected_test_cases": report.test_case_count
                }

        responses.append(ChangeRequestResponse(
            id=cr.id,
            requirement_id=cr.requirement_id,
            impact_report_id=cr.impact_report_id,
            title=cr.title,
            description=cr.description,
            justification=cr.justification,
            proposed_changes=cr.proposed_changes,
            status=cr.status.value,
            requested_by_id=cr.requested_by_id,
            reviewed_by_id=cr.reviewed_by_id,
            review_comments=cr.review_comments,
            created_at=cr.created_at,
            updated_at=cr.updated_at,
            reviewed_at=cr.reviewed_at,
            implemented_at=cr.implemented_at,
            impact_summary=impact_summary
        ))

    return ChangeRequestListResponse(
        change_requests=responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/change-requests/{change_request_id}", response_model=ChangeRequestResponse)
async def get_change_request(
    change_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific change request by ID.
    """
    change_request = db.query(ChangeRequest).filter(
        ChangeRequest.id == change_request_id
    ).first()

    if not change_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Change request with ID {change_request_id} not found"
        )

    # Get impact summary if available
    impact_summary = None
    if change_request.impact_report_id:
        report = db.query(ImpactAnalysisReport).filter(
            ImpactAnalysisReport.id == change_request.impact_report_id
        ).first()
        if report:
            impact_summary = {
                "risk_level": report.risk_level.value,
                "risk_score": report.risk_score,
                "affected_requirements": report.upstream_count + report.downstream_count,
                "affected_test_cases": report.test_case_count
            }

    return ChangeRequestResponse(
        id=change_request.id,
        requirement_id=change_request.requirement_id,
        impact_report_id=change_request.impact_report_id,
        title=change_request.title,
        description=change_request.description,
        justification=change_request.justification,
        proposed_changes=change_request.proposed_changes,
        status=change_request.status.value,
        requested_by_id=change_request.requested_by_id,
        reviewed_by_id=change_request.reviewed_by_id,
        review_comments=change_request.review_comments,
        created_at=change_request.created_at,
        updated_at=change_request.updated_at,
        reviewed_at=change_request.reviewed_at,
        implemented_at=change_request.implemented_at,
        impact_summary=impact_summary
    )


@router.patch("/change-requests/{change_request_id}/review", response_model=ChangeRequestResponse)
async def review_change_request(
    change_request_id: int,
    review: ReviewChangeRequestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Review (approve/reject) a change request.
    Requires admin or engineer role.
    """
    # Check permissions (admin or engineer can review)
    if current_user.role not in ["admin", "engineer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or engineer users can review change requests"
        )

    change_request = db.query(ChangeRequest).filter(
        ChangeRequest.id == change_request_id
    ).first()

    if not change_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Change request with ID {change_request_id} not found"
        )

    # Validate status transition
    if change_request.status != ChangeRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot review change request with status {change_request.status.value}"
        )

    # Update change request
    try:
        new_status = ChangeRequestStatus[review.status.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {review.status}. Must be APPROVED or REJECTED"
        )

    change_request.status = new_status
    change_request.reviewed_by_id = current_user.id
    change_request.review_comments = review.review_comments
    change_request.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(change_request)

    logger.info(f"Change request {change_request_id} reviewed by {current_user.username}: {new_status.value}")

    # Get impact summary
    impact_summary = None
    if change_request.impact_report_id:
        report = db.query(ImpactAnalysisReport).filter(
            ImpactAnalysisReport.id == change_request.impact_report_id
        ).first()
        if report:
            impact_summary = {
                "risk_level": report.risk_level.value,
                "risk_score": report.risk_score,
                "affected_requirements": report.upstream_count + report.downstream_count,
                "affected_test_cases": report.test_case_count
            }

    return ChangeRequestResponse(
        id=change_request.id,
        requirement_id=change_request.requirement_id,
        impact_report_id=change_request.impact_report_id,
        title=change_request.title,
        description=change_request.description,
        justification=change_request.justification,
        proposed_changes=change_request.proposed_changes,
        status=change_request.status.value,
        requested_by_id=change_request.requested_by_id,
        reviewed_by_id=change_request.reviewed_by_id,
        review_comments=change_request.review_comments,
        created_at=change_request.created_at,
        updated_at=change_request.updated_at,
        reviewed_at=change_request.reviewed_at,
        implemented_at=change_request.implemented_at,
        impact_summary=impact_summary
    )
