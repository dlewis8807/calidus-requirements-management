"""
Pydantic schemas for compliance and regulatory mapping
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# Regulation Schemas
class RegulationBase(BaseModel):
    """Base schema for regulation"""
    name: str = Field(..., description="Regulation name (e.g., '14 CFR Part 23')")
    abbreviation: str = Field(..., description="Short name (e.g., 'Part 23')")
    authority: str = Field(..., description="Regulatory authority (FAA, EASA, UAE GCAA)")
    description: Optional[str] = Field(None, description="Regulation description")


class RegulationResponse(RegulationBase):
    """Regulation response with statistics"""
    total_requirements: int = Field(0, description="Total requirements mapped to this regulation")
    coverage_percentage: float = Field(0.0, description="Percentage of regulation covered")
    total_sections: int = Field(0, description="Number of sections in regulation")
    covered_sections: int = Field(0, description="Number of sections with requirements")


class RegulationListResponse(BaseModel):
    """List of regulations with statistics"""
    regulations: List[RegulationResponse]
    total_count: int


# Compliance Overview Schemas
class ComplianceMetrics(BaseModel):
    """Overall compliance metrics"""
    total_requirements: int = Field(..., description="Total requirements in system")
    mapped_requirements: int = Field(..., description="Requirements with regulation mapping")
    unmapped_requirements: int = Field(..., description="Requirements without regulation mapping")
    coverage_percentage: float = Field(..., description="Percentage of requirements mapped")
    total_regulations: int = Field(..., description="Number of regulations referenced")


class RegulationCoverage(BaseModel):
    """Coverage for a specific regulation"""
    regulation: str = Field(..., description="Regulation name")
    authority: str = Field(..., description="Regulatory authority")
    total_requirements: int = Field(..., description="Requirements mapped to this regulation")
    by_type: Dict[str, int] = Field(..., description="Breakdown by requirement type")
    by_priority: Dict[str, int] = Field(..., description="Breakdown by priority")
    coverage_percentage: float = Field(..., description="Coverage percentage")


class ComplianceOverview(BaseModel):
    """Complete compliance overview"""
    metrics: ComplianceMetrics
    by_regulation: List[RegulationCoverage]
    top_regulations: List[Dict[str, Any]]


# Regulation Section Schemas
class RegulationSection(BaseModel):
    """A section within a regulation"""
    section: str = Field(..., description="Section number (e.g., '§23.143')")
    title: Optional[str] = Field(None, description="Section title")
    requirement_count: int = Field(0, description="Number of requirements mapped to this section")
    requirements: List[Dict] = Field(default_factory=list, description="Requirements in this section")


class RegulationDetail(BaseModel):
    """Detailed breakdown of a regulation"""
    regulation: str
    authority: str
    description: Optional[str] = None
    total_requirements: int
    total_sections: int
    sections: List[RegulationSection]
    coverage_percentage: float


# Gap Analysis Schemas
class ComplianceGap(BaseModel):
    """A compliance gap (unmapped requirement or uncovered section)"""
    gap_type: str = Field(..., description="Type: 'unmapped_requirement' or 'uncovered_section'")
    requirement_id: Optional[str] = Field(None, description="Requirement ID if applicable")
    requirement_title: Optional[str] = Field(None, description="Requirement title")
    requirement_type: Optional[str] = Field(None, description="Requirement type")
    priority: Optional[str] = Field(None, description="Requirement priority")
    regulation: Optional[str] = Field(None, description="Regulation if applicable")
    section: Optional[str] = Field(None, description="Section if applicable")
    severity: str = Field(..., description="Severity: Critical, High, Medium, Low")
    description: str = Field(..., description="Gap description")


class GapAnalysisResponse(BaseModel):
    """Gap analysis results"""
    unmapped_requirements: List[ComplianceGap]
    total_unmapped: int
    by_priority: Dict[str, int]
    by_type: Dict[str, int]


# Mapping Schemas
class RegulationMappingCreate(BaseModel):
    """Create a regulation mapping"""
    requirement_id: int = Field(..., description="Requirement database ID")
    regulation: str = Field(..., description="Regulation name")
    section: Optional[str] = Field(None, description="Section number")
    page: Optional[int] = Field(None, description="Page number")
    rationale: Optional[str] = Field(None, description="Mapping rationale")


class RegulationMappingUpdate(BaseModel):
    """Update a regulation mapping"""
    regulation: Optional[str] = None
    section: Optional[str] = None
    page: Optional[int] = None
    rationale: Optional[str] = None


class RegulationMappingResponse(BaseModel):
    """Regulation mapping response"""
    id: int
    requirement_id: int
    requirement_id_str: str
    requirement_title: str
    regulation: str
    section: Optional[str] = None
    page: Optional[int] = None
    rationale: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BulkMappingCreate(BaseModel):
    """Bulk create regulation mappings"""
    mappings: List[RegulationMappingCreate]


class BulkMappingResponse(BaseModel):
    """Bulk mapping operation response"""
    created: int
    failed: int
    errors: List[str] = Field(default_factory=list)


# Statistics Schemas
class ComplianceStats(BaseModel):
    """Compliance statistics"""
    total_requirements: int
    mapped_requirements: int
    unmapped_requirements: int
    coverage_percentage: float
    regulations_count: int
    sections_count: int
    by_regulation: Dict[str, int]
    by_authority: Dict[str, int]
