"""
Requirement Model
Represents aerospace requirements with full traceability support.
"""
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class RequirementType(str, enum.Enum):
    """Requirement classification types"""
    AHLR = "Aircraft_High_Level_Requirement"
    SYSTEM = "System_Requirement"
    TECHNICAL = "Technical_Specification"
    CERTIFICATION = "Certification_Requirement"


class RequirementStatus(str, enum.Enum):
    """Requirement lifecycle status"""
    DRAFT = "draft"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    UNDER_REVIEW = "under_review"


class RequirementPriority(str, enum.Enum):
    """Requirement priority levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class VerificationMethod(str, enum.Enum):
    """Requirement verification methods"""
    TEST = "Test"
    ANALYSIS = "Analysis"
    INSPECTION = "Inspection"
    DEMONSTRATION = "Demonstration"


class Requirement(Base):
    """
    Requirement model for aerospace requirements management.
    Supports multiple requirement types with full traceability.
    """
    __tablename__ = "requirements"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Classification
    type = Column(Enum(RequirementType), nullable=False, index=True)
    category = Column(String(100), index=True)
    
    # Content
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text)
    
    # Priority and status
    priority = Column(Enum(RequirementPriority), default=RequirementPriority.MEDIUM)
    status = Column(Enum(RequirementStatus), default=RequirementStatus.DRAFT, index=True)
    
    # Regulatory source linkage
    regulatory_document = Column(String(200))
    regulatory_section = Column(String(100))
    regulatory_title = Column(String(200))
    regulatory_page = Column(Integer)
    file_path = Column(String(500))
    
    # Verification
    verification_method = Column(Enum(VerificationMethod))
    compliance_status = Column(String(20))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = Column(String(100))
    version = Column(String(20), default="1.0")
    
    # Issues tracking
    issues = Column(Text)  # JSON string for storing issue list
    
    # Relationships
    created_by = relationship("User", back_populates="requirements")
    test_cases = relationship("TestCase", back_populates="requirement", cascade="all, delete-orphan")

    # Traceability relationships
    parent_traces = relationship(
        "TraceabilityLink",
        foreign_keys="TraceabilityLink.target_id",
        back_populates="target",
        cascade="all, delete-orphan"
    )
    child_traces = relationship(
        "TraceabilityLink",
        foreign_keys="TraceabilityLink.source_id",
        back_populates="source",
        cascade="all, delete-orphan"
    )

    # Impact analysis relationships
    impact_reports = relationship("ImpactAnalysisReport", back_populates="requirement", cascade="all, delete-orphan")
    change_requests = relationship("ChangeRequest", back_populates="requirement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Requirement {self.requirement_id}: {self.title}>"
