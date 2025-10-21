"""
Coverage Snapshot Model
Stores historical test coverage snapshots for trend analysis.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CoverageSnapshot(Base):
    """
    Coverage snapshot for historical trend tracking.
    Captures test coverage statistics at a specific point in time.
    """
    __tablename__ = "coverage_snapshots"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Overall coverage
    total_requirements = Column(Integer, nullable=False)
    covered_requirements = Column(Integer, nullable=False)
    coverage_percentage = Column(Float, nullable=False)

    # Breakdown by type (stored as JSON)
    ahlr_coverage = Column(JSON)  # {"total": 500, "covered": 450, "percentage": 90.0, ...}
    system_coverage = Column(JSON)
    technical_coverage = Column(JSON)
    certification_coverage = Column(JSON)

    # Breakdown by priority (stored as JSON)
    critical_coverage = Column(JSON)
    high_coverage = Column(JSON)
    medium_coverage = Column(JSON)
    low_coverage = Column(JSON)

    # Heatmap data (type × priority matrix)
    heatmap_data = Column(JSON)  # {"AHLR": {"Critical": {...}, "High": {...}}, ...}

    # Gap analysis
    total_gaps = Column(Integer, nullable=False, default=0)
    critical_gaps = Column(Integer, nullable=False, default=0)

    # Metadata
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="coverage_snapshots")

    def __repr__(self):
        return f"<CoverageSnapshot {self.snapshot_date}: {self.coverage_percentage:.1f}%>"
