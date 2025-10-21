"""
Impact Analysis Schemas
Pydantic schemas for impact analysis API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class ImpactNodeSchema(BaseModel):
    """Single node in impact tree"""
    requirement_id: str
    id: int
    title: str
    type: str
    priority: str
    status: str
    category: Optional[str] = None
    depth: int
    path: List[str]
    link_type: Optional[str] = None
    test_case_count: int = 0
    regulatory: bool = False
    regulatory_document: Optional[str] = None

    class Config:
        from_attributes = True


class RiskScoreSchema(BaseModel):
    """Risk score calculation result"""
    score: float = Field(..., ge=0, le=100)
    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors: Dict[str, float]
    explanation: str

    class Config:
        from_attributes = True


class ImpactAnalysisConfigSchema(BaseModel):
    """Configuration for impact analysis"""
    max_depth: int = Field(default=10, ge=1, le=20)
    include_test_cases: bool = True
    include_regulatory: bool = True
    weights: Dict[str, float] = {
        "depth": 0.20,
        "breadth": 0.25,
        "critical": 0.25,
        "test": 0.15,
        "regulatory": 0.10,
        "history": 0.05
    }


class AnalyzeImpactRequest(BaseModel):
    """Request to analyze impact of a requirement change"""
    requirement_id: int
    config: Optional[ImpactAnalysisConfigSchema] = None


class ImpactAnalysisResultSchema(BaseModel):
    """Complete impact analysis result"""
    requirement: Dict  # Requirement data
    upstream: List[ImpactNodeSchema]
    downstream: List[ImpactNodeSchema]
    risk_score: RiskScoreSchema
    stats: Dict[str, int]
    affected_test_cases: List[int]
    regulatory_implications: List[str]
    recommendations: List[str]
    estimated_effort_hours: float

    class Config:
        from_attributes = True


class ImpactAnalysisReportResponse(BaseModel):
    """Impact analysis report response"""
    id: int
    requirement_id: int
    analyzed_by_id: int
    risk_score: float
    risk_level: str
    upstream_count: int
    downstream_count: int
    test_case_count: int
    regulatory_impact: bool
    estimated_effort_hours: float
    created_at: datetime

    # Full report data
    upstream_tree: Optional[List[Dict]] = None
    downstream_tree: Optional[List[Dict]] = None
    affected_requirements: Optional[List[int]] = None
    affected_test_cases: Optional[List[int]] = None
    recommendations: Optional[List[str]] = None
    regulatory_implications: Optional[List[str]] = None
    risk_factors: Optional[Dict[str, float]] = None
    stats: Optional[Dict[str, int]] = None

    class Config:
        from_attributes = True


class ImpactAnalysisReportListResponse(BaseModel):
    """List of impact analysis reports"""
    reports: List[ImpactAnalysisReportResponse]
    total: int
    page: int
    page_size: int


class CreateChangeRequestRequest(BaseModel):
    """Request to create a change request"""
    requirement_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    justification: Optional[str] = None
    proposed_changes: Optional[Dict] = None  # {"before": "...", "after": "..."}
    perform_impact_analysis: bool = True


class ChangeRequestResponse(BaseModel):
    """Change request response"""
    id: int
    requirement_id: int
    impact_report_id: Optional[int] = None
    title: str
    description: str
    justification: Optional[str] = None
    proposed_changes: Optional[Dict] = None
    status: str
    requested_by_id: int
    reviewed_by_id: Optional[int] = None
    review_comments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    implemented_at: Optional[datetime] = None

    # Impact summary
    impact_summary: Optional[Dict] = None

    class Config:
        from_attributes = True


class ChangeRequestListResponse(BaseModel):
    """List of change requests"""
    change_requests: List[ChangeRequestResponse]
    total: int
    page: int
    page_size: int


class ReviewChangeRequestRequest(BaseModel):
    """Request to review/approve/reject a change request"""
    status: str  # APPROVED or REJECTED
    review_comments: Optional[str] = None
