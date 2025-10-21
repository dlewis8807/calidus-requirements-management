"""Coverage Analysis Schemas"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class CoverageByCategory(BaseModel):
    """Coverage statistics for a category (type or priority)."""
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
    heatmap: Dict[str, Dict[str, Dict]]  # type -> priority -> {total, covered, uncovered, percentage}
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
