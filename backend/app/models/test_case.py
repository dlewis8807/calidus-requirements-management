"""
Test Case Model
Represents test cases for requirement verification.
"""
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class TestCaseStatus(str, enum.Enum):
    """Test case execution status"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"


class TestCasePriority(str, enum.Enum):
    """Test case priority levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TestCase(Base):
    """
    Test Case model for requirement verification.
    Links to requirements to provide traceability.
    """
    __tablename__ = "test_cases"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Content
    title = Column(String(200), nullable=False)
    description = Column(Text)
    preconditions = Column(Text)
    test_steps = Column(Text, nullable=False)
    expected_results = Column(Text, nullable=False)
    actual_results = Column(Text)
    
    # Status and priority
    status = Column(Enum(TestCaseStatus), default=TestCaseStatus.PENDING, index=True)
    priority = Column(Enum(TestCasePriority), default=TestCasePriority.MEDIUM)
    
    # Execution details
    execution_date = Column(DateTime(timezone=True))
    execution_duration = Column(Integer)  # Duration in seconds
    executed_by = Column(String(100))  # Username who executed the test

    # Test metadata
    test_type = Column(String(50))  # unit, integration, system, acceptance
    test_environment = Column(String(100))  # dev, staging, production
    automated = Column(Boolean, default=False)  # Is this test automated?
    automation_script = Column(String(500))  # Path to automation script
    
    # Linking to requirement
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    requirement = relationship("Requirement", back_populates="test_cases")
    created_by = relationship("User", back_populates="test_cases")
    suggestions = relationship("TestCaseSuggestion", back_populates="test_case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestCase {self.test_case_id}: {self.title}>"
