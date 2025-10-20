"""
Risk Assessment Pydantic Schemas
Schema definitions for risk scoring and analysis.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.requirement import RequirementType, RequirementStatus, RequirementPriority


# ============================================================================
# Risk Factor Schemas
# ============================================================================

class RiskFactor(BaseModel):
    """Individual risk factor with score and weight"""
    factor_name: str = Field(..., description="Name of the risk factor")
    weight: float = Field(..., ge=0, le=100, description="Weight percentage (0-100)")
    score: float = Field(..., ge=0, le=100, description="Raw score (0-100)")
    impact: float = Field(..., ge=0, le=100, description="Weighted contribution to total risk")
    details: Optional[str] = Field(None, description="Additional context about this factor")


class RiskScore(BaseModel):
    """Complete risk assessment for a requirement"""
    requirement_id: str = Field(..., description="Requirement identifier (e.g., AHLR-001)")
    total_risk_score: float = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level: Critical, High, Medium, Low")
    factors: List[RiskFactor] = Field(..., description="Breakdown of all risk factors")

    # Metadata
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="When this score was calculated")

    class Config:
        json_schema_extra = {
            "example": {
                "requirement_id": "AHLR-042",
                "total_risk_score": 93.0,
                "risk_level": "Critical",
                "factors": [
                    {
                        "factor_name": "Priority Level",
                        "weight": 25.0,
                        "score": 100.0,
                        "impact": 25.0,
                        "details": "Critical priority requirement"
                    },
                    {
                        "factor_name": "Status Risk",
                        "weight": 20.0,
                        "score": 75.0,
                        "impact": 15.0,
                        "details": "Under review status"
                    },
                    {
                        "factor_name": "Traceability",
                        "weight": 25.0,
                        "score": 100.0,
                        "impact": 25.0,
                        "details": "Missing parent traceability"
                    },
                    {
                        "factor_name": "Test Coverage",
                        "weight": 20.0,
                        "score": 100.0,
                        "impact": 20.0,
                        "details": "No test cases linked"
                    },
                    {
                        "factor_name": "Compliance",
                        "weight": 10.0,
                        "score": 80.0,
                        "impact": 8.0,
                        "details": "Compliance status pending"
                    }
                ],
                "calculated_at": "2025-10-20T12:00:00Z"
            }
        }


# ============================================================================
# Requirement Risk Response
# ============================================================================

class RequirementRiskResponse(BaseModel):
    """Requirement with embedded risk assessment"""
    # Requirement details
    id: int
    requirement_id: str
    title: str
    description: str
    type: RequirementType
    status: RequirementStatus
    priority: RequirementPriority
    category: Optional[str]

    # Risk assessment
    risk_score: RiskScore

    # Metadata
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# Risk Overview Schemas
# ============================================================================

class RiskDistribution(BaseModel):
    """Distribution of requirements across risk levels"""
    critical: int = Field(..., description="Number of critical risk requirements")
    high: int = Field(..., description="Number of high risk requirements")
    medium: int = Field(..., description="Number of medium risk requirements")
    low: int = Field(..., description="Number of low risk requirements")
    total: int = Field(..., description="Total requirements analyzed")


class RiskOverview(BaseModel):
    """Overall risk analytics for the system"""
    distribution: RiskDistribution
    average_risk_score: float = Field(..., ge=0, le=100, description="Average risk score across all requirements")
    critical_requirements: int = Field(..., description="Count of critical priority requirements")
    untested_requirements: int = Field(..., description="Count of requirements with no test cases")
    orphaned_requirements: int = Field(..., description="Count of requirements with no traceability links")
    non_compliant_requirements: int = Field(..., description="Count of requirements with compliance issues")

    # Top risks
    top_risks: List[RequirementRiskResponse] = Field(..., description="Top 10 highest risk requirements")

    class Config:
        json_schema_extra = {
            "example": {
                "distribution": {
                    "critical": 45,
                    "high": 120,
                    "medium": 320,
                    "low": 215,
                    "total": 700
                },
                "average_risk_score": 52.3,
                "critical_requirements": 45,
                "untested_requirements": 23,
                "orphaned_requirements": 12,
                "non_compliant_requirements": 8,
                "top_risks": []
            }
        }


# ============================================================================
# Filter Schemas
# ============================================================================

class RiskFilterParams(BaseModel):
    """Parameters for filtering risk assessments"""
    min_risk_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum risk score threshold")
    max_risk_score: Optional[float] = Field(None, ge=0, le=100, description="Maximum risk score threshold")
    risk_level: Optional[str] = Field(None, description="Filter by risk level: Critical, High, Medium, Low")
    requirement_type: Optional[RequirementType] = Field(None, description="Filter by requirement type")
    priority: Optional[RequirementPriority] = Field(None, description="Filter by priority")
    status: Optional[RequirementStatus] = Field(None, description="Filter by status")
    has_test_cases: Optional[bool] = Field(None, description="Filter by test coverage")
    has_traceability: Optional[bool] = Field(None, description="Filter by traceability")
