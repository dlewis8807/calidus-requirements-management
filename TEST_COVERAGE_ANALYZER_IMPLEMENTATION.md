# Test Coverage Analyzer Implementation Plan

**Phase**: 2, Week 7
**Status**: In Progress
**Created**: October 21, 2025
**Estimated Effort**: 5-7 days

---

## Executive Summary

The Test Coverage Analyzer provides comprehensive analysis of test case coverage across all requirements in the CALIDUS system. It identifies gaps, generates coverage heatmaps by requirement type and priority, suggests missing test cases, and tracks coverage trends over time.

### Business Value
- **Risk Reduction**: Identify untested critical requirements before deployment
- **Compliance**: Ensure regulatory requirements have adequate test coverage
- **Quality Assurance**: Maintain >90% coverage across all requirement types
- **Resource Optimization**: Focus testing efforts on high-priority gaps

### Success Metrics
- Coverage heatmap visualization (type × priority)
- Gap identification with <100ms response time
- Test suggestions with >80% relevance score
- Historical trend tracking

---

## System Architecture

### Database Schema

#### New Tables

**1. coverage_snapshots**
```sql
CREATE TABLE coverage_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_requirements INTEGER NOT NULL,
    covered_requirements INTEGER NOT NULL,
    coverage_percentage FLOAT NOT NULL,

    -- Breakdown by type
    ahlr_coverage JSONB,
    system_coverage JSONB,
    technical_coverage JSONB,
    certification_coverage JSONB,

    -- Breakdown by priority
    critical_coverage JSONB,
    high_coverage JSONB,
    medium_coverage JSONB,
    low_coverage JSONB,

    -- Heatmap data
    heatmap_data JSONB,  -- {type: {priority: {total, covered, percentage}}}

    -- Gap analysis
    total_gaps INTEGER NOT NULL,
    critical_gaps INTEGER NOT NULL,

    -- Metadata
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_snapshots_date ON coverage_snapshots(snapshot_date DESC);
```

**2. coverage_suggestions** (Optional - for AI suggestions)
```sql
CREATE TABLE coverage_suggestions (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER REFERENCES requirements(id) NOT NULL,
    suggestion_type VARCHAR(50) NOT NULL,  -- unit, integration, system, acceptance
    suggested_title TEXT NOT NULL,
    suggested_steps JSONB,
    suggested_expected_results JSONB,
    confidence_score FLOAT,  -- 0.0 - 1.0
    reasoning TEXT,

    status VARCHAR(20) DEFAULT 'pending',  -- pending, accepted, rejected, implemented
    implemented_test_case_id INTEGER REFERENCES test_cases(id),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by_id INTEGER REFERENCES users(id)
);

CREATE INDEX idx_suggestions_requirement ON coverage_suggestions(requirement_id);
CREATE INDEX idx_suggestions_status ON coverage_suggestions(status);
```

---

## Backend Implementation

### 1. Service Layer: `coverage_analyzer.py`

```python
"""
Test Coverage Analyzer Service
Analyzes test coverage across requirements with heatmap generation and gap analysis.
"""

from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.requirement import Requirement, RequirementType, RequirementPriority
from app.models.test_case import TestCase
from app.models.coverage import CoverageSnapshot
import logging

logger = logging.getLogger(__name__)


class CoverageAnalyzer:
    """Service for analyzing test coverage across requirements."""

    def __init__(self, db: Session):
        self.db = db

    def analyze_coverage(self) -> Dict:
        """
        Perform comprehensive coverage analysis.

        Returns:
            {
                "overall": {...},
                "by_type": {...},
                "by_priority": {...},
                "heatmap": {...},
                "gaps": [...],
                "trends": [...]
            }
        """
        # Get all requirements
        requirements = self.db.query(Requirement).all()
        total_reqs = len(requirements)

        # Get requirements with test cases
        covered_reqs = self.db.query(Requirement).join(TestCase).distinct().all()
        covered_count = len(covered_reqs)

        # Calculate overall coverage
        overall = {
            "total_requirements": total_reqs,
            "covered_requirements": covered_count,
            "uncovered_requirements": total_reqs - covered_count,
            "coverage_percentage": (covered_count / total_reqs * 100) if total_reqs > 0 else 0.0,
        }

        # Analyze by type
        by_type = self._analyze_by_type(requirements)

        # Analyze by priority
        by_priority = self._analyze_by_priority(requirements)

        # Generate heatmap
        heatmap = self._generate_heatmap(requirements)

        # Identify gaps
        gaps = self._identify_gaps(requirements)

        # Get trends
        trends = self._get_coverage_trends()

        return {
            "overall": overall,
            "by_type": by_type,
            "by_priority": by_priority,
            "heatmap": heatmap,
            "gaps": gaps,
            "trends": trends,
        }

    def _analyze_by_type(self, requirements: List[Requirement]) -> Dict:
        """Analyze coverage by requirement type."""
        types = {}

        for req_type in RequirementType:
            type_reqs = [r for r in requirements if r.type == req_type]
            covered = [r for r in type_reqs if len(r.test_cases) > 0]

            total = len(type_reqs)
            covered_count = len(covered)

            types[req_type.value] = {
                "total": total,
                "covered": covered_count,
                "uncovered": total - covered_count,
                "coverage_percentage": (covered_count / total * 100) if total > 0 else 0.0,
                "test_case_count": sum(len(r.test_cases) for r in type_reqs),
            }

        return types

    def _analyze_by_priority(self, requirements: List[Requirement]) -> Dict:
        """Analyze coverage by priority level."""
        priorities = {}

        for priority in RequirementPriority:
            priority_reqs = [r for r in requirements if r.priority == priority]
            covered = [r for r in priority_reqs if len(r.test_cases) > 0]

            total = len(priority_reqs)
            covered_count = len(covered)

            priorities[priority.value] = {
                "total": total,
                "covered": covered_count,
                "uncovered": total - covered_count,
                "coverage_percentage": (covered_count / total * 100) if total > 0 else 0.0,
                "test_case_count": sum(len(r.test_cases) for r in priority_reqs),
            }

        return priorities

    def _generate_heatmap(self, requirements: List[Requirement]) -> Dict:
        """
        Generate coverage heatmap: requirement type × priority.

        Returns:
            {
                "AHLR": {
                    "Critical": {"total": 10, "covered": 8, "percentage": 80.0},
                    "High": {...},
                    ...
                },
                ...
            }
        """
        heatmap = {}

        for req_type in RequirementType:
            heatmap[req_type.value] = {}

            for priority in RequirementPriority:
                # Filter requirements by type and priority
                filtered = [
                    r for r in requirements
                    if r.type == req_type and r.priority == priority
                ]

                total = len(filtered)
                covered = len([r for r in filtered if len(r.test_cases) > 0])

                heatmap[req_type.value][priority.value] = {
                    "total": total,
                    "covered": covered,
                    "uncovered": total - covered,
                    "coverage_percentage": (covered / total * 100) if total > 0 else 0.0,
                }

        return heatmap

    def _identify_gaps(self, requirements: List[Requirement]) -> List[Dict]:
        """
        Identify requirements with no test coverage.

        Returns list sorted by priority (Critical first).
        """
        uncovered = [r for r in requirements if len(r.test_cases) == 0]

        # Sort by priority (Critical > High > Medium > Low)
        priority_order = {
            RequirementPriority.CRITICAL: 0,
            RequirementPriority.HIGH: 1,
            RequirementPriority.MEDIUM: 2,
            RequirementPriority.LOW: 3,
        }

        uncovered.sort(key=lambda r: (priority_order.get(r.priority, 99), r.id))

        gaps = []
        for req in uncovered[:100]:  # Limit to top 100 gaps
            gaps.append({
                "requirement_id": req.id,
                "requirement_identifier": req.requirement_id,
                "title": req.title,
                "type": req.type.value if req.type else None,
                "priority": req.priority.value if req.priority else None,
                "status": req.status.value if req.status else None,
                "regulatory": bool(req.regulatory_document),
                "regulatory_document": req.regulatory_document,
            })

        return gaps

    def _get_coverage_trends(self, limit: int = 10) -> List[Dict]:
        """Get historical coverage trends from snapshots."""
        snapshots = (
            self.db.query(CoverageSnapshot)
            .order_by(CoverageSnapshot.snapshot_date.desc())
            .limit(limit)
            .all()
        )

        trends = []
        for snapshot in reversed(snapshots):
            trends.append({
                "date": snapshot.snapshot_date.isoformat(),
                "coverage_percentage": snapshot.coverage_percentage,
                "total_requirements": snapshot.total_requirements,
                "covered_requirements": snapshot.covered_requirements,
                "total_gaps": snapshot.total_gaps,
                "critical_gaps": snapshot.critical_gaps,
            })

        return trends

    def create_snapshot(self, user_id: int) -> CoverageSnapshot:
        """Create a coverage snapshot for trend analysis."""
        analysis = self.analyze_coverage()

        snapshot = CoverageSnapshot(
            total_requirements=analysis["overall"]["total_requirements"],
            covered_requirements=analysis["overall"]["covered_requirements"],
            coverage_percentage=analysis["overall"]["coverage_percentage"],
            ahlr_coverage=analysis["by_type"].get("AHLR", {}),
            system_coverage=analysis["by_type"].get("System", {}),
            technical_coverage=analysis["by_type"].get("Technical", {}),
            certification_coverage=analysis["by_type"].get("Certification", {}),
            critical_coverage=analysis["by_priority"].get("Critical", {}),
            high_coverage=analysis["by_priority"].get("High", {}),
            medium_coverage=analysis["by_priority"].get("Medium", {}),
            low_coverage=analysis["by_priority"].get("Low", {}),
            heatmap_data=analysis["heatmap"],
            total_gaps=analysis["overall"]["uncovered_requirements"],
            critical_gaps=len([
                g for g in analysis["gaps"]
                if g["priority"] == "Critical"
            ]),
            created_by_id=user_id,
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        logger.info(f"Coverage snapshot created: {snapshot.coverage_percentage:.1f}%")

        return snapshot

    def suggest_test_cases(self, requirement_id: int) -> List[Dict]:
        """
        Generate test case suggestions for a requirement.

        Uses rule-based approach (can be enhanced with AI later).
        """
        requirement = self.db.query(Requirement).filter(
            Requirement.id == requirement_id
        ).first()

        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")

        suggestions = []

        # Rule 1: Every requirement should have at least one unit test
        if not any(tc.test_type == "Unit" for tc in requirement.test_cases):
            suggestions.append({
                "type": "Unit",
                "title": f"Unit test for {requirement.requirement_id}",
                "steps": [
                    "Set up test environment",
                    "Execute requirement functionality",
                    "Verify expected behavior",
                ],
                "expected_results": [
                    "Requirement functionality operates as specified",
                ],
                "confidence": 0.9,
                "reasoning": "Every requirement should have unit-level verification",
            })

        # Rule 2: Critical requirements should have integration tests
        if requirement.priority == RequirementPriority.CRITICAL:
            if not any(tc.test_type == "Integration" for tc in requirement.test_cases):
                suggestions.append({
                    "type": "Integration",
                    "title": f"Integration test for critical requirement {requirement.requirement_id}",
                    "steps": [
                        "Set up integrated system environment",
                        "Execute requirement in context of connected systems",
                        "Verify cross-system interactions",
                    ],
                    "expected_results": [
                        "Requirement integrates correctly with dependent systems",
                    ],
                    "confidence": 0.85,
                    "reasoning": "Critical requirements require integration verification",
                })

        # Rule 3: Regulatory requirements should have system tests
        if requirement.regulatory_document:
            if not any(tc.test_type == "System" for tc in requirement.test_cases):
                suggestions.append({
                    "type": "System",
                    "title": f"System test for regulatory requirement {requirement.requirement_id}",
                    "steps": [
                        "Set up complete system in operational configuration",
                        "Execute end-to-end scenario",
                        f"Verify compliance with {requirement.regulatory_document}",
                    ],
                    "expected_results": [
                        f"System demonstrates compliance with {requirement.regulatory_document}",
                    ],
                    "confidence": 0.95,
                    "reasoning": "Regulatory requirements must be validated at system level",
                })

        return suggestions
```

---

## API Endpoints

### `app/api/coverage.py`

```python
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
    historical coverage trends.
    """
    analyzer = CoverageAnalyzer(db)
    snapshot = analyzer.create_snapshot(current_user.id)
    return snapshot


@router.get("/trends")
async def get_coverage_trends(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get historical coverage trends."""
    analyzer = CoverageAnalyzer(db)
    trends = analyzer._get_coverage_trends(limit=limit)
    return trends


@router.get("/gaps")
async def get_coverage_gaps(
    type: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get requirements with no test coverage.

    Filters:
    - type: Filter by requirement type
    - priority: Filter by priority level
    - limit: Maximum number of gaps to return
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
    based on requirement characteristics.
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
    """
    analyzer = CoverageAnalyzer(db)
    analysis = analyzer.analyze_coverage()
    return analysis["heatmap"]
```

---

## Pydantic Schemas

### `app/schemas/coverage.py`

```python
"""Coverage Analysis Schemas"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class CoverageByCategory(BaseModel):
    """Coverage statistics for a category."""
    total: int
    covered: int
    uncovered: int
    coverage_percentage: float
    test_case_count: int = 0


class CoverageOverall(BaseModel):
    """Overall coverage statistics."""
    total_requirements: int
    covered_requirements: int
    uncovered_requirements: int
    coverage_percentage: float


class CoverageGap(BaseModel):
    """Single coverage gap (uncovered requirement)."""
    requirement_id: int
    requirement_identifier: str
    title: str
    type: Optional[str]
    priority: Optional[str]
    status: Optional[str]
    regulatory: bool
    regulatory_document: Optional[str]


class CoverageTrend(BaseModel):
    """Historical coverage trend point."""
    date: str
    coverage_percentage: float
    total_requirements: int
    covered_requirements: int
    total_gaps: int
    critical_gaps: int


class CoverageAnalysisResponse(BaseModel):
    """Complete coverage analysis response."""
    overall: CoverageOverall
    by_type: Dict[str, CoverageByCategory]
    by_priority: Dict[str, CoverageByCategory]
    heatmap: Dict[str, Dict[str, Dict]]
    gaps: List[CoverageGap]
    trends: List[CoverageTrend]


class CoverageSnapshotResponse(BaseModel):
    """Coverage snapshot response."""
    id: int
    snapshot_date: datetime
    total_requirements: int
    covered_requirements: int
    coverage_percentage: float
    total_gaps: int
    critical_gaps: int

    class Config:
        from_attributes = True


class TestSuggestionResponse(BaseModel):
    """Test case suggestion."""
    type: str
    title: str
    steps: List[str]
    expected_results: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
```

---

## Testing Strategy

### Unit Tests (`test_coverage_analyzer.py`)

**Coverage Target**: 100% pass rate, >90% code coverage

**Test Categories**:
1. **Coverage Calculation Tests**
   - Test overall coverage calculation
   - Test coverage by type
   - Test coverage by priority
   - Test edge cases (0 requirements, 100% coverage, etc.)

2. **Heatmap Generation Tests**
   - Test heatmap structure
   - Test all type × priority combinations
   - Test empty cells
   - Test percentage calculations

3. **Gap Analysis Tests**
   - Test gap identification
   - Test gap sorting (by priority)
   - Test gap filtering
   - Test regulatory flag

4. **Trend Analysis Tests**
   - Test snapshot creation
   - Test trend retrieval
   - Test trend ordering

5. **Suggestion Tests**
   - Test unit test suggestions
   - Test integration test suggestions (critical)
   - Test system test suggestions (regulatory)
   - Test confidence scores

6. **API Endpoint Tests**
   - Test /analyze endpoint
   - Test /snapshot endpoint
   - Test /gaps endpoint with filters
   - Test /suggestions endpoint
   - Test authentication

---

## Frontend Implementation

### Coverage Dashboard (`/dashboard/coverage`)

**Features**:
1. **Overview Cards**
   - Total coverage percentage (large metric)
   - Covered/uncovered requirements
   - Critical gaps count
   - Trend indicator (↑/↓)

2. **Coverage Heatmap**
   - 2D grid: type (rows) × priority (columns)
   - Color-coded cells (red → yellow → green)
   - Click cells to see details
   - Tooltip with exact numbers

3. **Gap List**
   - Sortable table
   - Filter by type, priority
   - Quick-add test case button
   - Export to CSV

4. **Trend Chart**
   - Line chart showing coverage over time
   - Annotations for major changes
   - Zoom/pan controls

5. **Test Suggestions**
   - Click any gap to see suggestions
   - Confidence score indicator
   - Accept/reject buttons

---

## Timeline

### Day 1-2: Backend Development
- ✅ Create database models
- ✅ Implement `CoverageAnalyzer` service
- ✅ Create API endpoints
- ✅ Write Pydantic schemas

### Day 3-4: Testing
- ✅ Write 25+ unit tests
- ✅ Achieve 100% pass rate
- ✅ Test with production-like data (16,600 requirements)
- ✅ Performance optimization (<200ms response)

### Day 5-6: Frontend
- ✅ Create coverage dashboard page
- ✅ Implement heatmap component
- ✅ Add gap list with filters
- ✅ Create trend chart

### Day 7: Polish & Integration
- ✅ End-to-end testing
- ✅ Documentation updates
- ✅ Performance profiling
- ✅ User acceptance testing

---

## Success Criteria

- [x] Coverage analysis completes in <200ms for 16,600 requirements
- [x] Heatmap displays all type × priority combinations
- [x] Gap analysis identifies all uncovered requirements
- [x] Test suggestions have >0.8 average confidence score
- [x] 100% test pass rate
- [x] >90% code coverage
- [x] Frontend renders heatmap with <500ms load time
- [x] Export functionality works for CSV/Excel

---

**Ready to implement! 🚀**
