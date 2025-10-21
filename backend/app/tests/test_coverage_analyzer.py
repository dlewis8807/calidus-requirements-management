"""
Tests for Coverage Analyzer Service and API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.requirement import Requirement, RequirementType, RequirementStatus, RequirementPriority
from app.models.test_case import TestCase, TestCaseStatus, TestCasePriority
from app.models.coverage import CoverageSnapshot
from app.models.user import User
from app.services.coverage_analyzer import CoverageAnalyzer
from app.core.security import get_password_hash


# Module-level fixtures (shared across all test classes)

@pytest.fixture
def coverage_test_user(db_session: Session):
    """Create a test user for coverage tests."""
    user = User(
        username="coverage_testuser",
        email="coverage@test.com",
        hashed_password=get_password_hash("testpass"),
        role="engineer"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_requirements(db_session: Session, coverage_test_user: User):
    """
    Create test requirements with varying coverage:
    - 2 AHLR (1 covered, 1 uncovered)
    - 2 System (1 covered, 1 uncovered)
    - 2 Technical (both covered)
    - 2 Certification (both uncovered)

    Priority distribution:
    - 2 Critical (1 covered, 1 uncovered)
    - 2 High (1 covered, 1 uncovered)
    - 2 Medium (both covered)
    - 2 Low (both uncovered)
    """
    requirements = []

    # AHLR - Critical (covered)
    req1 = Requirement(
        requirement_id="AHLR-001",
        title="AHLR Requirement 1",
        description="Test",
        type=RequirementType.AHLR,
        priority=RequirementPriority.CRITICAL,
        status=RequirementStatus.APPROVED,
        created_by_id=coverage_test_user.id,
        regulatory_document="14 CFR Part 23"
    )
    requirements.append(req1)

    # AHLR - High (uncovered)
    req2 = Requirement(
        requirement_id="AHLR-002",
        title="AHLR Requirement 2",
        description="Test",
        type=RequirementType.AHLR,
        priority=RequirementPriority.HIGH,
        status=RequirementStatus.APPROVED,
        created_by_id=coverage_test_user.id
    )
    requirements.append(req2)

    # System - Medium (covered)
    req3 = Requirement(
        requirement_id="SYS-001",
        title="System Requirement 1",
        description="Test",
        type=RequirementType.SYSTEM,
        priority=RequirementPriority.MEDIUM,
        status=RequirementStatus.APPROVED,
        created_by_id=coverage_test_user.id
    )
    requirements.append(req3)

    # System - Low (uncovered)
    req4 = Requirement(
        requirement_id="SYS-002",
        title="System Requirement 2",
        description="Test",
        type=RequirementType.SYSTEM,
        priority=RequirementPriority.LOW,
        status=RequirementStatus.APPROVED,
        created_by_id=coverage_test_user.id
    )
    requirements.append(req4)

    # Technical - Critical (uncovered)
    req5 = Requirement(
        requirement_id="TECH-001",
        title="Technical Specification 1",
        description="Test",
        type=RequirementType.TECHNICAL,
        priority=RequirementPriority.CRITICAL,
        status=RequirementStatus.APPROVED,
        created_by_id=coverage_test_user.id
    )
    requirements.append(req5)

    # Technical - High (covered)
    req6 = Requirement(
        requirement_id="TECH-002",
        title="Technical Specification 2",
        description="Test",
        type=RequirementType.TECHNICAL,
        priority=RequirementPriority.HIGH,
        status=RequirementStatus.APPROVED,
        created_by_id=coverage_test_user.id
    )
    requirements.append(req6)

    # Certification - Medium (covered)
    req7 = Requirement(
        requirement_id="CERT-001",
        title="Certification Requirement 1",
        description="Test",
        type=RequirementType.CERTIFICATION,
        priority=RequirementPriority.MEDIUM,
        status=RequirementStatus.APPROVED,
        created_by_id=coverage_test_user.id
    )
    requirements.append(req7)

    # Certification - Low (uncovered)
    req8 = Requirement(
        requirement_id="CERT-002",
        title="Certification Requirement 2",
        description="Test",
        type=RequirementType.CERTIFICATION,
        priority=RequirementPriority.LOW,
        status=RequirementStatus.APPROVED,
        created_by_id=coverage_test_user.id
    )
    requirements.append(req8)

    db_session.add_all(requirements)
    db_session.commit()

    for req in requirements:
        db_session.refresh(req)

    # Create test cases for covered requirements (req1, req3, req6, req7)
    test_cases = [
        # req1 - AHLR Critical (2 tests)
        TestCase(
            requirement_id=req1.id,
            test_case_id="TC-001",
            title="Test 1",
            description="Test",
            test_type="Unit",
            status=TestCaseStatus.PASSED,
            priority=TestCasePriority.HIGH,
            test_steps='["Step 1"]',
            expected_results='["Result 1"]',
            created_by_id=coverage_test_user.id
        ),
        TestCase(
            requirement_id=req1.id,
            test_case_id="TC-002",
            title="Test 2",
            description="Test",
            test_type="Integration",
            status=TestCaseStatus.PASSED,
            priority=TestCasePriority.HIGH,
            test_steps='["Step 1"]',
            expected_results='["Result 1"]',
            created_by_id=coverage_test_user.id
        ),
        # req3 - System Medium (1 test)
        TestCase(
            requirement_id=req3.id,
            test_case_id="TC-003",
            title="Test 3",
            description="Test",
            test_type="Unit",
            status=TestCaseStatus.PASSED,
            priority=TestCasePriority.MEDIUM,
            test_steps='["Step 1"]',
            expected_results='["Result 1"]',
            created_by_id=coverage_test_user.id
        ),
        # req6 - Technical High (1 test)
        TestCase(
            requirement_id=req6.id,
            test_case_id="TC-004",
            title="Test 4",
            description="Test",
            test_type="System",
            status=TestCaseStatus.PASSED,
            priority=TestCasePriority.HIGH,
            test_steps='["Step 1"]',
            expected_results='["Result 1"]',
            created_by_id=coverage_test_user.id
        ),
        # req7 - Certification Medium (1 test)
        TestCase(
            requirement_id=req7.id,
            test_case_id="TC-005",
            title="Test 5",
            description="Test",
            test_type="Acceptance",
            status=TestCaseStatus.PASSED,
            priority=TestCasePriority.MEDIUM,
            test_steps='["Step 1"]',
            expected_results='["Result 1"]',
            created_by_id=coverage_test_user.id
        ),
    ]

    db_session.add_all(test_cases)
    db_session.commit()

    return {
        "all": requirements,
        "covered": [req1, req3, req6, req7],
        "uncovered": [req2, req4, req5, req8],
    }


class TestCoverageAnalyzerService:
    """Test the Coverage Analyzer Service."""

    @pytest.fixture
    def analyzer(self, db_session: Session):
        """Create coverage analyzer instance."""
        return CoverageAnalyzer(db_session)

    def test_overall_coverage_calculation(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test overall coverage percentage calculation."""
        analysis = analyzer.analyze_coverage()

        assert analysis["overall"]["total_requirements"] == 8
        assert analysis["overall"]["covered_requirements"] == 4
        assert analysis["overall"]["uncovered_requirements"] == 4
        assert analysis["overall"]["coverage_percentage"] == 50.0

    def test_coverage_by_type(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test coverage breakdown by requirement type."""
        analysis = analyzer.analyze_coverage()
        by_type = analysis["by_type"]

        # AHLR: 2 total, 1 covered (50%)
        assert by_type["Aircraft_High_Level_Requirement"]["total"] == 2
        assert by_type["Aircraft_High_Level_Requirement"]["covered"] == 1
        assert by_type["Aircraft_High_Level_Requirement"]["coverage_percentage"] == 50.0

        # System: 2 total, 1 covered (50%)
        assert by_type["System_Requirement"]["total"] == 2
        assert by_type["System_Requirement"]["covered"] == 1

        # Technical: 2 total, 1 covered (50%)
        assert by_type["Technical_Specification"]["total"] == 2
        assert by_type["Technical_Specification"]["covered"] == 1

        # Certification: 2 total, 1 covered (50%)
        assert by_type["Certification_Requirement"]["total"] == 2
        assert by_type["Certification_Requirement"]["covered"] == 1

    def test_coverage_by_priority(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test coverage breakdown by priority."""
        analysis = analyzer.analyze_coverage()
        by_priority = analysis["by_priority"]

        # Critical: 2 total, 1 covered (50%)
        assert by_priority["Critical"]["total"] == 2
        assert by_priority["Critical"]["covered"] == 1
        assert by_priority["Critical"]["coverage_percentage"] == 50.0

        # High: 2 total, 1 covered (50%)
        assert by_priority["High"]["total"] == 2
        assert by_priority["High"]["covered"] == 1

        # Medium: 2 total, 2 covered (100%)
        assert by_priority["Medium"]["total"] == 2
        assert by_priority["Medium"]["covered"] == 2
        assert by_priority["Medium"]["coverage_percentage"] == 100.0

        # Low: 2 total, 0 covered (0%)
        assert by_priority["Low"]["total"] == 2
        assert by_priority["Low"]["covered"] == 0
        assert by_priority["Low"]["coverage_percentage"] == 0.0

    def test_heatmap_generation(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test coverage heatmap generation (type × priority)."""
        analysis = analyzer.analyze_coverage()
        heatmap = analysis["heatmap"]

        # Check structure
        assert "Aircraft_High_Level_Requirement" in heatmap
        assert "Critical" in heatmap["Aircraft_High_Level_Requirement"]

        # AHLR × Critical: 1 total, 1 covered (100%)
        cell = heatmap["Aircraft_High_Level_Requirement"]["Critical"]
        assert cell["total"] == 1
        assert cell["covered"] == 1
        assert cell["coverage_percentage"] == 100.0

        # System × Low: 1 total, 0 covered (0%)
        cell = heatmap["System_Requirement"]["Low"]
        assert cell["total"] == 1
        assert cell["covered"] == 0
        assert cell["coverage_percentage"] == 0.0

    def test_gap_identification(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test identification of uncovered requirements."""
        analysis = analyzer.analyze_coverage()
        gaps = analysis["gaps"]

        # Should have 4 gaps
        assert len(gaps) == 4

        # Gaps should be sorted by priority (Critical first)
        gap_priorities = [g["priority"] for g in gaps]
        # Should have: 1 Critical, 1 High, 2 Low
        assert gap_priorities.count("Critical") == 1
        assert gap_priorities.count("High") == 1
        assert gap_priorities.count("Low") == 2

        # First gap should be Critical
        assert gaps[0]["priority"] == "Critical"

    def test_gap_sorting_by_priority(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test that gaps are sorted correctly (Critical > High > Medium > Low)."""
        analysis = analyzer.analyze_coverage()
        gaps = analysis["gaps"]

        priorities = [g["priority"] for g in gaps]

        # Critical should come before High
        if "Critical" in priorities and "High" in priorities:
            assert priorities.index("Critical") < priorities.index("High")

        # Low should be last
        last_priority = priorities[-1]
        assert last_priority == "Low"

    def test_snapshot_creation(self, analyzer: CoverageAnalyzer, coverage_test_user: User, test_requirements):
        """Test creating a coverage snapshot."""
        snapshot = analyzer.create_snapshot(coverage_test_user.id)

        assert snapshot.id is not None
        assert snapshot.total_requirements == 8
        assert snapshot.covered_requirements == 4
        assert snapshot.coverage_percentage == 50.0
        assert snapshot.total_gaps == 4
        assert snapshot.critical_gaps == 1

        # Check JSON data
        assert snapshot.heatmap_data is not None
        assert "Aircraft_High_Level_Requirement" in snapshot.heatmap_data

    def test_trend_retrieval(self, analyzer: CoverageAnalyzer, coverage_test_user: User, test_requirements, db_session: Session):
        """Test retrieving coverage trends."""
        # Create 3 snapshots
        snap1 = analyzer.create_snapshot(coverage_test_user.id)
        snap2 = analyzer.create_snapshot(coverage_test_user.id)
        snap3 = analyzer.create_snapshot(coverage_test_user.id)

        db_session.commit()

        trends = analyzer._get_coverage_trends(limit=5)

        # Should have 3 trends
        assert len(trends) == 3

        # Each trend should have required fields
        for trend in trends:
            assert "date" in trend
            assert "coverage_percentage" in trend
            assert "total_requirements" in trend

    def test_suggest_unit_test(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test suggesting unit test for requirement without any tests."""
        uncovered_req = test_requirements["uncovered"][0]  # AHLR-002

        suggestions = analyzer.suggest_test_cases(uncovered_req.id)

        # Should suggest at least a unit test
        assert len(suggestions) >= 1
        unit_suggestions = [s for s in suggestions if s["type"] == "Unit"]
        assert len(unit_suggestions) == 1

        unit_test = unit_suggestions[0]
        assert unit_test["confidence"] >= 0.8
        assert "steps" in unit_test
        assert len(unit_test["steps"]) > 0

    def test_suggest_integration_test_for_critical(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test suggesting integration test for critical requirement."""
        # TECH-001 is Critical and uncovered
        critical_req = test_requirements["uncovered"][2]  # TECH-001
        assert critical_req.priority == RequirementPriority.CRITICAL

        suggestions = analyzer.suggest_test_cases(critical_req.id)

        # Should suggest unit test AND integration test
        types = [s["type"] for s in suggestions]
        assert "Unit" in types
        assert "Integration" in types

    def test_suggest_system_test_for_regulatory(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test suggesting system test for regulatory requirement."""
        # req1 (AHLR-001) has regulatory_document
        reg_req = test_requirements["covered"][0]  # AHLR-001
        assert reg_req.regulatory_document is not None

        suggestions = analyzer.suggest_test_cases(reg_req.id)

        # Should suggest system test because it's regulatory
        # (even though it already has unit and integration tests)
        types = [s["type"] for s in suggestions]
        assert "System" in types

        system_suggestion = [s for s in suggestions if s["type"] == "System"][0]
        assert reg_req.regulatory_document in system_suggestion["reasoning"]

    def test_suggest_acceptance_test_for_high_priority(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test suggesting acceptance test for high priority with <2 tests."""
        # req6 (TECH-002) is High priority with only 1 test
        high_req = test_requirements["covered"][2]  # TECH-002
        assert high_req.priority == RequirementPriority.HIGH
        assert len(high_req.test_cases) == 1

        suggestions = analyzer.suggest_test_cases(high_req.id)

        # Should suggest acceptance test
        types = [s["type"] for s in suggestions]
        assert "Acceptance" in types

    def test_invalid_requirement_raises_error(self, analyzer: CoverageAnalyzer):
        """Test that invalid requirement ID raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            analyzer.suggest_test_cases(99999)

    def test_empty_database(self, db_session: Session):
        """Test analyzer with no requirements."""
        analyzer = CoverageAnalyzer(db_session)
        analysis = analyzer.analyze_coverage()

        assert analysis["overall"]["total_requirements"] == 0
        assert analysis["overall"]["coverage_percentage"] == 0.0
        assert len(analysis["gaps"]) == 0

    def test_test_case_count_in_by_type(self, analyzer: CoverageAnalyzer, test_requirements):
        """Test that test_case_count is correct in by_type breakdown."""
        analysis = analyzer.analyze_coverage()
        by_type = analysis["by_type"]

        # AHLR has 2 test cases (both on req1)
        assert by_type["Aircraft_High_Level_Requirement"]["test_case_count"] == 2

        # System has 1 test case (on req3)
        assert by_type["System_Requirement"]["test_case_count"] == 1


class TestCoverageAPI:
    """Test the Coverage Analysis REST API."""

    def test_analyze_coverage_success(self, client: TestClient, auth_headers: dict, test_requirements):
        """Test successful coverage analysis via API."""
        response = client.get("/api/coverage/analyze", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "overall" in data
        assert "by_type" in data
        assert "by_priority" in data
        assert "heatmap" in data
        assert "gaps" in data
        assert "trends" in data

        assert data["overall"]["total_requirements"] == 8
        assert data["overall"]["coverage_percentage"] == 50.0

    def test_analyze_coverage_unauthorized(self, client: TestClient, test_requirements):
        """Test that analyzing coverage requires authentication."""
        response = client.get("/api/coverage/analyze")
        assert response.status_code == 401

    def test_create_snapshot_success(self, client: TestClient, auth_headers: dict, test_requirements):
        """Test creating a coverage snapshot via API."""
        response = client.post("/api/coverage/snapshot", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["total_requirements"] == 8
        assert data["covered_requirements"] == 4
        assert data["coverage_percentage"] == 50.0

    def test_get_trends(self, client: TestClient, auth_headers: dict, test_requirements):
        """Test retrieving coverage trends via API."""
        # Create a snapshot first
        client.post("/api/coverage/snapshot", headers=auth_headers)

        response = client.get("/api/coverage/trends?limit=5", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        if len(data) > 0:
            assert "date" in data[0]
            assert "coverage_percentage" in data[0]

    def test_get_gaps(self, client: TestClient, auth_headers: dict, test_requirements):
        """Test retrieving coverage gaps via API."""
        response = client.get("/api/coverage/gaps", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 4

        # First gap should be Critical priority
        assert data[0]["priority"] == "Critical"

    def test_get_gaps_filtered_by_type(self, client: TestClient, auth_headers: dict, test_requirements):
        """Test filtering gaps by requirement type."""
        response = client.get(
            "/api/coverage/gaps?type=Aircraft_High_Level_Requirement",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should only have AHLR gaps (1)
        assert len(data) == 1
        assert data[0]["type"] == "Aircraft_High_Level_Requirement"

    def test_get_gaps_filtered_by_priority(self, client: TestClient, auth_headers: dict, test_requirements):
        """Test filtering gaps by priority."""
        response = client.get(
            "/api/coverage/gaps?priority=Low",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should only have Low priority gaps (2)
        assert len(data) == 2
        for gap in data:
            assert gap["priority"] == "Low"

    def test_get_suggestions_success(self, client: TestClient, auth_headers: dict, test_requirements):
        """Test getting test suggestions for a requirement."""
        uncovered_req = test_requirements["uncovered"][0]

        response = client.get(
            f"/api/coverage/suggestions/{uncovered_req.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 1

        # Check suggestion structure
        suggestion = data[0]
        assert "type" in suggestion
        assert "title" in suggestion
        assert "steps" in suggestion
        assert "expected_results" in suggestion
        assert "confidence" in suggestion
        assert "reasoning" in suggestion

    def test_get_suggestions_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting suggestions for non-existent requirement."""
        response = client.get(
            "/api/coverage/suggestions/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_get_heatmap(self, client: TestClient, auth_headers: dict, test_requirements):
        """Test retrieving coverage heatmap via API."""
        response = client.get("/api/coverage/heatmap", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "Aircraft_High_Level_Requirement" in data
        assert "Critical" in data["Aircraft_High_Level_Requirement"]

        # Check cell structure
        cell = data["Aircraft_High_Level_Requirement"]["Critical"]
        assert "total" in cell
        assert "covered" in cell
        assert "uncovered" in cell
        assert "coverage_percentage" in cell
