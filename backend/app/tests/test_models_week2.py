"""
Test Week 2 Models
Tests for Requirement, TestCase, and TraceabilityLink models.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import (
    User, Requirement, TestCase, TraceabilityLink,
    RequirementType, RequirementStatus, RequirementPriority,
    TestCaseStatus, TraceLinkType
)


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_week2.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password_here",
        role="engineer"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestRequirementModel:
    """Tests for Requirement model"""

    def test_create_requirement(self, db_session, test_user):
        """Test creating a basic requirement"""
        requirement = Requirement(
            requirement_id="AHLR-001",
            type=RequirementType.AHLR,
            category="FlightControl",
            title="Test Flight Control Requirement",
            description="The aircraft SHALL provide stable flight control",
            priority=RequirementPriority.CRITICAL,
            status=RequirementStatus.APPROVED,
            created_by_id=test_user.id
        )
        db_session.add(requirement)
        db_session.commit()
        db_session.refresh(requirement)

        assert requirement.id is not None
        assert requirement.requirement_id == "AHLR-001"
        assert requirement.type == RequirementType.AHLR
        assert requirement.status == RequirementStatus.APPROVED
        assert requirement.created_by_id == test_user.id

    def test_requirement_with_regulatory_source(self, db_session, test_user):
        """Test requirement with regulatory linking"""
        requirement = Requirement(
            requirement_id="CERT-001",
            type=RequirementType.CERTIFICATION,
            title="14 CFR Part 23 Compliance",
            description="Must comply with 14 CFR Part 23 Section 23.143",
            regulatory_document="14 CFR Part 23",
            regulatory_section="§23.143",
            regulatory_page=23,
            file_path="/path/to/14_CFR_Part_23.pdf",
            created_by_id=test_user.id
        )
        db_session.add(requirement)
        db_session.commit()
        db_session.refresh(requirement)

        assert requirement.regulatory_document == "14 CFR Part 23"
        assert requirement.regulatory_section == "§23.143"
        assert requirement.regulatory_page == 23

    def test_requirement_types(self, db_session, test_user):
        """Test all requirement types"""
        types = [
            RequirementType.AHLR,
            RequirementType.SYSTEM,
            RequirementType.TECHNICAL,
            RequirementType.CERTIFICATION
        ]
        
        for req_type in types:
            requirement = Requirement(
                requirement_id=f"{req_type.name}-001",
                type=req_type,
                title=f"Test {req_type.value}",
                description="Test description",
                created_by_id=test_user.id
            )
            db_session.add(requirement)
        
        db_session.commit()
        count = db_session.query(Requirement).count()
        assert count == 4


class TestTestCaseModel:
    """Tests for TestCase model"""

    def test_create_test_case(self, db_session, test_user):
        """Test creating a test case"""
        # First create a requirement
        requirement = Requirement(
            requirement_id="SYS-001",
            type=RequirementType.SYSTEM,
            title="Test System Requirement",
            description="System requirement for testing",
            created_by_id=test_user.id
        )
        db_session.add(requirement)
        db_session.commit()
        db_session.refresh(requirement)

        # Create test case
        test_case = TestCase(
            test_case_id="TC-001",
            title="Test Flight Control System",
            description="Verify flight control system operates correctly",
            test_steps="1. Power on system\n2. Verify initialization\n3. Test controls",
            expected_results="System initializes and responds to controls",
            status=TestCaseStatus.PENDING,
            requirement_id=requirement.id,
            created_by_id=test_user.id
        )
        db_session.add(test_case)
        db_session.commit()
        db_session.refresh(test_case)

        assert test_case.id is not None
        assert test_case.test_case_id == "TC-001"
        assert test_case.requirement_id == requirement.id
        assert test_case.status == TestCaseStatus.PENDING

    def test_test_case_relationship(self, db_session, test_user):
        """Test relationship between TestCase and Requirement"""
        requirement = Requirement(
            requirement_id="SYS-002",
            type=RequirementType.SYSTEM,
            title="Test Requirement",
            description="Description",
            created_by_id=test_user.id
        )
        db_session.add(requirement)
        db_session.commit()

        test_case = TestCase(
            test_case_id="TC-002",
            title="Test Case",
            test_steps="Steps",
            expected_results="Results",
            requirement_id=requirement.id,
            created_by_id=test_user.id
        )
        db_session.add(test_case)
        db_session.commit()

        # Test relationship
        assert test_case.requirement.requirement_id == "SYS-002"
        assert len(requirement.test_cases) == 1
        assert requirement.test_cases[0].test_case_id == "TC-002"


class TestTraceabilityLinkModel:
    """Tests for TraceabilityLink model"""

    def test_create_trace_link(self, db_session, test_user):
        """Test creating a traceability link"""
        # Create parent requirement
        parent = Requirement(
            requirement_id="AHLR-100",
            type=RequirementType.AHLR,
            title="Parent Requirement",
            description="High level requirement",
            created_by_id=test_user.id
        )
        # Create child requirement
        child = Requirement(
            requirement_id="SYS-100",
            type=RequirementType.SYSTEM,
            title="Child Requirement",
            description="System requirement deriving from parent",
            created_by_id=test_user.id
        )
        db_session.add(parent)
        db_session.add(child)
        db_session.commit()

        # Create trace link
        link = TraceabilityLink(
            source_id=child.id,
            target_id=parent.id,
            link_type=TraceLinkType.DERIVES_FROM,
            description="Child derives from parent",
            created_by_id=test_user.id
        )
        db_session.add(link)
        db_session.commit()
        db_session.refresh(link)

        assert link.id is not None
        assert link.source_id == child.id
        assert link.target_id == parent.id
        assert link.link_type == TraceLinkType.DERIVES_FROM

    def test_trace_link_relationships(self, db_session, test_user):
        """Test bidirectional traceability relationships"""
        parent = Requirement(
            requirement_id="AHLR-200",
            type=RequirementType.AHLR,
            title="Parent",
            description="Parent requirement",
            created_by_id=test_user.id
        )
        child = Requirement(
            requirement_id="SYS-200",
            type=RequirementType.SYSTEM,
            title="Child",
            description="Child requirement",
            created_by_id=test_user.id
        )
        db_session.add_all([parent, child])
        db_session.commit()

        link = TraceabilityLink(
            source_id=child.id,
            target_id=parent.id,
            link_type=TraceLinkType.SATISFIES,
            created_by_id=test_user.id
        )
        db_session.add(link)
        db_session.commit()

        # Test relationships
        assert len(child.child_traces) == 1
        assert len(parent.parent_traces) == 1
        assert child.child_traces[0].target_id == parent.id
        assert parent.parent_traces[0].source_id == child.id

    def test_unique_trace_link_constraint(self, db_session, test_user):
        """Test that duplicate trace links are prevented"""
        parent = Requirement(
            requirement_id="AHLR-300",
            type=RequirementType.AHLR,
            title="Parent",
            description="Parent",
            created_by_id=test_user.id
        )
        child = Requirement(
            requirement_id="SYS-300",
            type=RequirementType.SYSTEM,
            title="Child",
            description="Child",
            created_by_id=test_user.id
        )
        db_session.add_all([parent, child])
        db_session.commit()

        # Create first link
        link1 = TraceabilityLink(
            source_id=child.id,
            target_id=parent.id,
            link_type=TraceLinkType.DERIVES_FROM,
            created_by_id=test_user.id
        )
        db_session.add(link1)
        db_session.commit()

        # Try to create duplicate link
        link2 = TraceabilityLink(
            source_id=child.id,
            target_id=parent.id,
            link_type=TraceLinkType.DERIVES_FROM,
            created_by_id=test_user.id
        )
        db_session.add(link2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()


class TestModelIntegration:
    """Integration tests for all models together"""

    def test_full_requirement_lifecycle(self, db_session, test_user):
        """Test complete requirement with test cases and traceability"""
        # Create AHLR
        ahlr = Requirement(
            requirement_id="AHLR-500",
            type=RequirementType.AHLR,
            title="High Level Requirement",
            description="AHLR description",
            priority=RequirementPriority.CRITICAL,
            status=RequirementStatus.APPROVED,
            created_by_id=test_user.id
        )
        # Create System requirement
        sys_req = Requirement(
            requirement_id="SYS-500",
            type=RequirementType.SYSTEM,
            title="System Requirement",
            description="System level requirement",
            status=RequirementStatus.APPROVED,
            created_by_id=test_user.id
        )
        db_session.add_all([ahlr, sys_req])
        db_session.commit()

        # Create traceability
        trace = TraceabilityLink(
            source_id=sys_req.id,
            target_id=ahlr.id,
            link_type=TraceLinkType.DERIVES_FROM,
            created_by_id=test_user.id
        )
        db_session.add(trace)

        # Create test case
        test_case = TestCase(
            test_case_id="TC-500",
            title="Verify System Requirement",
            test_steps="Test steps",
            expected_results="Expected results",
            requirement_id=sys_req.id,
            created_by_id=test_user.id
        )
        db_session.add(test_case)
        db_session.commit()

        # Verify all relationships
        assert len(sys_req.test_cases) == 1
        assert len(sys_req.child_traces) == 1
        assert len(ahlr.parent_traces) == 1
        assert sys_req.child_traces[0].target.requirement_id == "AHLR-500"
