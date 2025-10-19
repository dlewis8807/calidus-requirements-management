"""
Compliance and Regulatory Mapping API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List, Dict, Optional
from datetime import datetime

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.requirement import Requirement
from app.schemas.compliance import (
    ComplianceOverview,
    ComplianceMetrics,
    RegulationCoverage,
    RegulationListResponse,
    RegulationResponse,
    RegulationDetail,
    RegulationSection,
    GapAnalysisResponse,
    ComplianceGap,
    ComplianceStats,
)

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


@router.get("/overview", response_model=ComplianceOverview)
async def get_compliance_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall compliance overview with metrics and breakdown by regulation
    """
    # Total requirements
    total_requirements = db.query(Requirement).count()

    # Mapped requirements (have regulatory_document)
    mapped_requirements = db.query(Requirement).filter(
        Requirement.regulatory_document.isnot(None),
        Requirement.regulatory_document != ""
    ).count()

    unmapped_requirements = total_requirements - mapped_requirements
    coverage_percentage = (mapped_requirements / total_requirements * 100) if total_requirements > 0 else 0.0

    # Count distinct regulations
    total_regulations = db.query(
        func.count(distinct(Requirement.regulatory_document))
    ).filter(
        Requirement.regulatory_document.isnot(None),
        Requirement.regulatory_document != ""
    ).scalar() or 0

    # Metrics
    metrics = ComplianceMetrics(
        total_requirements=total_requirements,
        mapped_requirements=mapped_requirements,
        unmapped_requirements=unmapped_requirements,
        coverage_percentage=round(coverage_percentage, 2),
        total_regulations=total_regulations
    )

    # Breakdown by regulation
    by_regulation = []

    # Get all unique regulations
    regulations_query = db.query(
        Requirement.regulatory_document,
        func.count(Requirement.id).label('count')
    ).filter(
        Requirement.regulatory_document.isnot(None),
        Requirement.regulatory_document != ""
    ).group_by(Requirement.regulatory_document).all()

    for reg_doc, count in regulations_query:
        # Determine authority
        authority = "FAA"
        if "EASA" in reg_doc or "CS-" in reg_doc:
            authority = "EASA"
        elif "UAE" in reg_doc or "GCAA" in reg_doc:
            authority = "UAE GCAA"

        # Breakdown by type
        by_type_query = db.query(
            Requirement.type,
            func.count(Requirement.id).label('count')
        ).filter(
            Requirement.regulatory_document == reg_doc
        ).group_by(Requirement.type).all()

        by_type = {req_type: count for req_type, count in by_type_query}

        # Breakdown by priority
        by_priority_query = db.query(
            Requirement.priority,
            func.count(Requirement.id).label('count')
        ).filter(
            Requirement.regulatory_document == reg_doc
        ).group_by(Requirement.priority).all()

        by_priority = {priority: count for priority, count in by_priority_query}

        # Coverage percentage (assume total sections is proportional)
        coverage_pct = (count / total_requirements * 100) if total_requirements > 0 else 0.0

        by_regulation.append(RegulationCoverage(
            regulation=reg_doc,
            authority=authority,
            total_requirements=count,
            by_type=by_type,
            by_priority=by_priority,
            coverage_percentage=round(coverage_pct, 2)
        ))

    # Sort by requirement count descending
    by_regulation.sort(key=lambda x: x.total_requirements, reverse=True)

    # Top 5 regulations
    top_regulations = [
        {
            "regulation": reg.regulation,
            "authority": reg.authority,
            "count": reg.total_requirements,
            "coverage": reg.coverage_percentage
        }
        for reg in by_regulation[:5]
    ]

    return ComplianceOverview(
        metrics=metrics,
        by_regulation=by_regulation,
        top_regulations=top_regulations
    )


@router.get("/regulations", response_model=RegulationListResponse)
async def list_regulations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all regulations in the system with statistics
    """
    # Get all unique regulations with counts
    regulations_query = db.query(
        Requirement.regulatory_document,
        func.count(Requirement.id).label('requirement_count'),
        func.count(distinct(Requirement.regulatory_section)).label('section_count')
    ).filter(
        Requirement.regulatory_document.isnot(None),
        Requirement.regulatory_document != ""
    ).group_by(Requirement.regulatory_document).all()

    regulations = []
    for reg_doc, req_count, section_count in regulations_query:
        # Determine authority
        authority = "FAA"
        abbreviation = reg_doc
        if "EASA" in reg_doc or "CS-" in reg_doc:
            authority = "EASA"
        elif "UAE" in reg_doc or "GCAA" in reg_doc:
            authority = "UAE GCAA"

        # Estimate coverage (simplified - actual calculation would need total sections)
        coverage_pct = min(100.0, (section_count / 50.0) * 100) if section_count > 0 else 0.0

        regulations.append(RegulationResponse(
            name=reg_doc,
            abbreviation=abbreviation,
            authority=authority,
            description=f"Requirements from {reg_doc}",
            total_requirements=req_count,
            coverage_percentage=round(coverage_pct, 2),
            total_sections=section_count,
            covered_sections=section_count
        ))

    # Sort by requirement count descending
    regulations.sort(key=lambda x: x.total_requirements, reverse=True)

    return RegulationListResponse(
        regulations=regulations,
        total_count=len(regulations)
    )


@router.get("/regulations/{regulation_name}", response_model=RegulationDetail)
async def get_regulation_detail(
    regulation_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed breakdown of a specific regulation by section
    """
    # Decode regulation name (replace %20 with space, etc.)
    from urllib.parse import unquote
    regulation_name = unquote(regulation_name)

    # Get all requirements for this regulation
    requirements = db.query(Requirement).filter(
        Requirement.regulatory_document == regulation_name
    ).all()

    if not requirements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Regulation '{regulation_name}' not found"
        )

    # Determine authority
    authority = "FAA"
    if "EASA" in regulation_name or "CS-" in regulation_name:
        authority = "EASA"
    elif "UAE" in regulation_name or "GCAA" in regulation_name:
        authority = "UAE GCAA"

    # Group by section
    sections_dict: Dict[str, List[Requirement]] = {}
    for req in requirements:
        section = req.regulatory_section or "Unspecified"
        if section not in sections_dict:
            sections_dict[section] = []
        sections_dict[section].append(req)

    # Build section objects
    sections = []
    for section_name, reqs in sections_dict.items():
        # Build requirement summaries
        req_summaries = [
            {
                "id": req.id,
                "requirement_id": req.requirement_id,
                "title": req.title,
                "type": req.type,
                "status": req.status,
                "priority": req.priority,
                "page": req.regulatory_page
            }
            for req in reqs
        ]

        sections.append(RegulationSection(
            section=section_name,
            title=None,  # We don't have section titles in our data
            requirement_count=len(reqs),
            requirements=req_summaries
        ))

    # Sort sections by section number (basic string sort)
    sections.sort(key=lambda x: x.section)

    total_requirements = len(requirements)
    total_sections = len(sections)

    # Coverage percentage (simplified)
    coverage_pct = min(100.0, (total_sections / 50.0) * 100) if total_sections > 0 else 0.0

    return RegulationDetail(
        regulation=regulation_name,
        authority=authority,
        description=f"Requirements from {regulation_name}",
        total_requirements=total_requirements,
        total_sections=total_sections,
        sections=sections,
        coverage_percentage=round(coverage_pct, 2)
    )


@router.get("/gaps", response_model=GapAnalysisResponse)
async def get_compliance_gaps(
    priority: Optional[str] = None,
    requirement_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get compliance gaps (requirements without regulatory mapping)
    """
    # Query unmapped requirements
    query = db.query(Requirement).filter(
        (Requirement.regulatory_document.is_(None)) |
        (Requirement.regulatory_document == "")
    )

    # Apply filters
    if priority:
        query = query.filter(Requirement.priority == priority)

    if requirement_type:
        query = query.filter(Requirement.type == requirement_type)

    # Limit results
    query = query.limit(limit)

    unmapped_reqs = query.all()

    # Build gap objects
    gaps = []
    for req in unmapped_reqs:
        # Determine severity based on priority
        severity_map = {
            "Critical": "Critical",
            "High": "High",
            "Medium": "Medium",
            "Low": "Low",
            "Informational": "Low"
        }
        severity = severity_map.get(req.priority, "Medium")

        gaps.append(ComplianceGap(
            gap_type="unmapped_requirement",
            requirement_id=req.requirement_id,
            requirement_title=req.title,
            requirement_type=req.type,
            priority=req.priority,
            regulation=None,
            section=None,
            severity=severity,
            description=f"Requirement {req.requirement_id} has no regulatory mapping"
        ))

    # Count by priority
    by_priority_query = db.query(
        Requirement.priority,
        func.count(Requirement.id).label('count')
    ).filter(
        (Requirement.regulatory_document.is_(None)) |
        (Requirement.regulatory_document == "")
    ).group_by(Requirement.priority).all()

    by_priority = {priority: count for priority, count in by_priority_query}

    # Count by type
    by_type_query = db.query(
        Requirement.type,
        func.count(Requirement.id).label('count')
    ).filter(
        (Requirement.regulatory_document.is_(None)) |
        (Requirement.regulatory_document == "")
    ).group_by(Requirement.type).all()

    by_type = {req_type: count for req_type, count in by_type_query}

    # Total unmapped
    total_unmapped = db.query(Requirement).filter(
        (Requirement.regulatory_document.is_(None)) |
        (Requirement.regulatory_document == "")
    ).count()

    return GapAnalysisResponse(
        unmapped_requirements=gaps,
        total_unmapped=total_unmapped,
        by_priority=by_priority,
        by_type=by_type
    )


@router.get("/stats", response_model=ComplianceStats)
async def get_compliance_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get compliance statistics
    """
    # Total requirements
    total_requirements = db.query(Requirement).count()

    # Mapped requirements
    mapped_requirements = db.query(Requirement).filter(
        Requirement.regulatory_document.isnot(None),
        Requirement.regulatory_document != ""
    ).count()

    unmapped_requirements = total_requirements - mapped_requirements
    coverage_percentage = (mapped_requirements / total_requirements * 100) if total_requirements > 0 else 0.0

    # Count regulations
    regulations_count = db.query(
        func.count(distinct(Requirement.regulatory_document))
    ).filter(
        Requirement.regulatory_document.isnot(None),
        Requirement.regulatory_document != ""
    ).scalar() or 0

    # Count sections
    sections_count = db.query(
        func.count(distinct(Requirement.regulatory_section))
    ).filter(
        Requirement.regulatory_section.isnot(None),
        Requirement.regulatory_section != ""
    ).scalar() or 0

    # By regulation
    by_regulation_query = db.query(
        Requirement.regulatory_document,
        func.count(Requirement.id).label('count')
    ).filter(
        Requirement.regulatory_document.isnot(None),
        Requirement.regulatory_document != ""
    ).group_by(Requirement.regulatory_document).all()

    by_regulation = {reg: count for reg, count in by_regulation_query}

    # By authority (simplified detection)
    by_authority = {"FAA": 0, "EASA": 0, "UAE GCAA": 0, "Other": 0}
    for reg, count in by_regulation_query:
        if "EASA" in reg or "CS-" in reg:
            by_authority["EASA"] += count
        elif "UAE" in reg or "GCAA" in reg:
            by_authority["UAE GCAA"] += count
        elif "CFR" in reg or "Part" in reg:
            by_authority["FAA"] += count
        else:
            by_authority["Other"] += count

    return ComplianceStats(
        total_requirements=total_requirements,
        mapped_requirements=mapped_requirements,
        unmapped_requirements=unmapped_requirements,
        coverage_percentage=round(coverage_percentage, 2),
        regulations_count=regulations_count,
        sections_count=sections_count,
        by_regulation=by_regulation,
        by_authority=by_authority
    )
