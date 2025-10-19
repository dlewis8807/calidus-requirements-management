"""
Traceability Link Model
Represents parent-child relationships between requirements.
"""
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class TraceLinkType(str, enum.Enum):
    """Types of traceability relationships"""
    DERIVES_FROM = "derives_from"       # Child derives from parent
    SATISFIES = "satisfies"             # Child satisfies parent
    VERIFIES = "verifies"               # Test verifies requirement
    DEPENDS_ON = "depends_on"           # Dependency relationship
    REFINES = "refines"                 # Child refines parent
    CONFLICTS_WITH = "conflicts_with"   # Conflicting requirements


class TraceabilityLink(Base):
    """
    Traceability Link model for requirement relationships.
    Establishes parent-child relationships with typed links.
    """
    __tablename__ = "traceability_links"
    
    __table_args__ = (
        # Prevent duplicate links between same requirements
        UniqueConstraint('source_id', 'target_id', 'link_type', name='unique_trace_link'),
    )

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationship
    source_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False, index=True)
    link_type = Column(Enum(TraceLinkType), nullable=False, index=True)
    
    # Additional information
    description = Column(Text)
    rationale = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    source = relationship(
        "Requirement",
        foreign_keys=[source_id],
        back_populates="child_traces"
    )
    target = relationship(
        "Requirement",
        foreign_keys=[target_id],
        back_populates="parent_traces"
    )
    created_by = relationship("User")

    def __repr__(self):
        return f"<TraceLink {self.source_id} -> {self.target_id} ({self.link_type.value})>"
