"""
Impact Analysis Models
Database models for storing impact analysis reports and change requests.
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class RiskLevel(str, enum.Enum):
    """Risk level classification"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ChangeRequestStatus(str, enum.Enum):
    """Change request workflow status"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IMPLEMENTED = "IMPLEMENTED"
    CANCELLED = "CANCELLED"


class ImpactAnalysisReport(Base):
    """
    Impact analysis report storage.
    Stores the results of impact analysis for a requirement change.
    """
    __tablename__ = "impact_analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False, index=True)
    analyzed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Analysis results
    risk_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False, index=True)
    upstream_count = Column(Integer, default=0)
    downstream_count = Column(Integer, default=0)
    test_case_count = Column(Integer, default=0)
    regulatory_impact = Column(Boolean, default=False)

    # JSON storage for complex data
    upstream_tree = Column(JSON)  # List of upstream ImpactNodes
    downstream_tree = Column(JSON)  # List of downstream ImpactNodes
    affected_requirements = Column(JSON)  # List of affected requirement IDs
    affected_test_cases = Column(JSON)  # List of affected test case IDs
    recommendations = Column(JSON)  # List of recommendation strings
    regulatory_implications = Column(JSON)  # List of regulatory implications
    risk_factors = Column(JSON)  # Dictionary of risk factor contributions

    # Effort estimation
    estimated_effort_hours = Column(Float, default=0.0)

    # Statistics
    stats = Column(JSON)  # Dictionary of statistics (counts by type, priority, etc.)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    requirement = relationship("Requirement", back_populates="impact_reports")
    analyzed_by = relationship("User")
    change_requests = relationship("ChangeRequest", back_populates="impact_report")

    def __repr__(self):
        return f"<ImpactAnalysisReport {self.id}: Req {self.requirement_id}, Risk {self.risk_level}>"


class ChangeRequest(Base):
    """
    Change request with impact analysis.
    Represents a formal request to modify a requirement with impact analysis results.
    """
    __tablename__ = "change_requests"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False, index=True)
    impact_report_id = Column(Integer, ForeignKey("impact_analysis_reports.id"))

    # Change details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    justification = Column(Text)
    proposed_changes = Column(JSON)  # Before/after diff as JSON

    # Workflow
    status = Column(Enum(ChangeRequestStatus), default=ChangeRequestStatus.PENDING, index=True)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by_id = Column(Integer, ForeignKey("users.id"))

    # Review comments
    review_comments = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    implemented_at = Column(DateTime(timezone=True))

    # Relationships
    requirement = relationship("Requirement", back_populates="change_requests")
    impact_report = relationship("ImpactAnalysisReport", back_populates="change_requests")
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])

    def __repr__(self):
        return f"<ChangeRequest {self.id}: {self.title} ({self.status})>"
