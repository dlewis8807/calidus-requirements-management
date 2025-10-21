"""
Database models for test failure analysis and suggestions
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TestCaseSuggestion(Base):
    """Stores AI-generated suggestions for test case failures"""
    __tablename__ = "test_case_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    suggestion_type = Column(String(50), nullable=False)  # 'root_cause', 'fix_suggestion', 'investigation'

    # Suggestion content
    priority = Column(Integer, nullable=False)
    action = Column(Text, nullable=False)
    details = Column(Text)
    code_locations = Column(JSON)  # Array of file paths
    verification_steps = Column(JSON)  # Array of steps
    estimated_effort_hours = Column(Float)

    # Analysis metadata
    failure_type = Column(String(50))
    confidence_score = Column(Float)
    matched_rule_id = Column(String(50))

    # Status
    status = Column(String(20), default='active')  # 'active', 'resolved', 'dismissed'
    resolved_by_id = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(TIMESTAMP(timezone=True))

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    test_case = relationship("TestCase", back_populates="suggestions")
    resolved_by = relationship("User")


class SuggestionFeedback(Base):
    """Tracks user feedback on suggestion helpfulness"""
    __tablename__ = "suggestion_feedback"

    id = Column(Integer, primary_key=True, index=True)
    suggestion_id = Column(Integer, ForeignKey("test_case_suggestions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Feedback
    helpful = Column(Boolean, nullable=False)
    comment = Column(Text)

    # Timestamp
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class FailurePattern(Base):
    """Learned failure patterns from resolved test cases"""
    __tablename__ = "failure_patterns"

    id = Column(Integer, primary_key=True, index=True)
    pattern_name = Column(String(200), nullable=False)
    category = Column(String(100))

    # Pattern definition
    failure_indicators = Column(JSON)  # Keywords that indicate this pattern
    root_cause = Column(Text)
    resolution = Column(Text)

    # Usage statistics
    times_matched = Column(Integer, default=0)
    times_helpful = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.5)

    # Source
    learned_from_test_id = Column(Integer, ForeignKey("test_cases.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    created_by = relationship("User")
