"""
Test Coverage Analyzer API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.coverage_analyzer import CoverageAnalyzer
from app.schemas.coverage import (
    CoverageAnalysisResponse,
    CoverageSnapshotResponse,
    TestSuggestionResponse,
)

router = APIRouter(prefix="/api/coverage", tags=["Coverage Analysis"])


@router.get("/analyze", response_model=CoverageAnalysisResponse)
async def analyze_coverage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Perform comprehensive coverage analysis.

    Returns:
    - Overall coverage statistics
    - Breakdown by requirement type
    - Breakdown by priority
    - Coverage heatmap (type × priority)
    - Gap analysis (uncovered requirements)
    - Historical trends

    **Example Response**:
    ```json
    {
        "overall": {
            "total_requirements": 16600,
            "covered_requirements": 15000,
            "uncovered_requirements": 1600,
            "coverage_percentage": 90.36
        },
        "by_type": {
            "Aircraft_High_Level": {
                "total": 500,
                "covered": 480,
                "uncovered": 20,
                "coverage_percentage": 96.0,
                "test_case_count": 1200
            },
            ...
        },
        "heatmap": {
            "Aircraft_High_Level": {
                "Critical": {
                    "total": 100,
                    "covered": 98,
                    "uncovered": 2,
                    "coverage_percentage": 98.0
                },
                ...
            },
            ...
        },
        "gaps": [...],
        "trends": [...]
    }
    ```
    """
    analyzer = CoverageAnalyzer(db)
    analysis = analyzer.analyze_coverage()
    return analysis


@router.post("/snapshot", response_model=CoverageSnapshotResponse)
async def create_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a coverage snapshot for trend tracking.

    Snapshots are stored in the database and used to generate
    historical coverage trends. This endpoint should be called
    periodically (e.g., daily, weekly) to track coverage over time.

    **Permissions**: Requires authenticated user
    """
    analyzer = CoverageAnalyzer(db)
    snapshot = analyzer.create_snapshot(current_user.id)
    return snapshot


@router.get("/trends")
async def get_coverage_trends(
    limit: int = Query(10, ge=1, le=100, description="Number of historical snapshots to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get historical coverage trends.

    Returns a time-series of coverage snapshots showing how
    coverage has changed over time.

    **Query Parameters**:
    - `limit`: Number of snapshots to return (default: 10, max: 100)
    """
    analyzer = CoverageAnalyzer(db)
    trends = analyzer._get_coverage_trends(limit=limit)
    return trends


@router.get("/gaps")
async def get_coverage_gaps(
    type: Optional[str] = Query(None, description="Filter by requirement type"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of gaps to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get requirements with no test coverage.

    Returns a list of requirements that have zero test cases,
    sorted by priority (Critical first).

    **Query Parameters**:
    - `type`: Filter by requirement type (e.g., "Aircraft_High_Level")
    - `priority`: Filter by priority level (e.g., "Critical", "High")
    - `limit`: Maximum number of gaps to return (default: 100, max: 500)

    **Example Response**:
    ```json
    [
        {
            "requirement_id": 123,
            "requirement_identifier": "AHLR-001",
            "title": "Flight Control System Requirements",
            "type": "Aircraft_High_Level",
            "priority": "Critical",
            "status": "Approved",
            "regulatory": true,
            "regulatory_document": "14 CFR Part 23"
        },
        ...
    ]
    ```
    """
    analyzer = CoverageAnalyzer(db)
    analysis = analyzer.analyze_coverage()
    gaps = analysis["gaps"]

    # Apply filters
    if type:
        gaps = [g for g in gaps if g["type"] == type]
    if priority:
        gaps = [g for g in gaps if g["priority"] == priority]

    return gaps[:limit]


@router.get("/suggestions/{requirement_id}", response_model=List[TestSuggestionResponse])
async def get_test_suggestions(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get test case suggestions for a specific requirement.

    Uses rule-based analysis to suggest appropriate test types
    based on requirement characteristics:

    - **Unit Test**: Suggested for all requirements without unit tests
    - **Integration Test**: Suggested for Critical priority requirements
    - **System Test**: Suggested for requirements with regulatory documents
    - **Acceptance Test**: Suggested for High priority requirements with <2 tests

    **Path Parameters**:
    - `requirement_id`: Database ID of the requirement

    **Example Response**:
    ```json
    [
        {
            "type": "Unit",
            "title": "Unit test for AHLR-001",
            "steps": [
                "Set up test environment",
                "Execute AHLR-001 functionality",
                "Verify expected behavior"
            ],
            "expected_results": [
                "AHLR-001 functionality operates as specified"
            ],
            "confidence": 0.9,
            "reasoning": "Every requirement should have unit-level verification"
        },
        ...
    ]
    ```
    """
    analyzer = CoverageAnalyzer(db)

    try:
        suggestions = analyzer.suggest_test_cases(requirement_id)
        return suggestions
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/heatmap")
async def get_coverage_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get coverage heatmap (type × priority).

    Returns a 2D grid showing coverage percentage for each
    combination of requirement type and priority.

    This is useful for quickly identifying which combinations
    have low coverage and need attention.

    **Example Response**:
    ```json
    {
        "Aircraft_High_Level": {
            "Critical": {
                "total": 100,
                "covered": 98,
                "uncovered": 2,
                "coverage_percentage": 98.0
            },
            "High": {...},
            "Medium": {...},
            "Low": {...}
        },
        "System_Requirement": {...},
        "Technical_Specification": {...},
        "Certification_Requirement": {...}
    }
    ```
    """
    analyzer = CoverageAnalyzer(db)
    analysis = analyzer.analyze_coverage()
    return analysis["heatmap"]
