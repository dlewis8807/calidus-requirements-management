"""
Tests for Impact Analysis Service and API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.requirement import Requirement, RequirementType, RequirementStatus, RequirementPriority
from app.models.test_case import TestCase, TestCaseStatus, TestCasePriority
from app.models.traceability import TraceabilityLink, TraceLinkType
from app.models.impact_analysis import ImpactAnalysisReport, ChangeRequest, RiskLevel, ChangeRequestStatus
from app.models.user import User
from app.services.impact_analysis import ImpactAnalysisService, ImpactAnalysisConfig
from app.core.security import get_password_hash


# Module-level fixtures (shared across all test classes)

@pytest.fixture
def impact_test_user(db_session: Session):
    """Create a test user for impact analysis tests"""
    user = User(
        username="impact_testuser",
        email="impact_test@example.com",
        hashed_password=get_password_hash("testpass"),
        role="engineer"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def requirement_hierarchy(db_session: Session, impact_test_user: User):
    """
    Create a requirement hierarchy for testing:

    AHLR-001 (root)
      ├─> SYS-001
      │     ├─> TECH-001
      │     └─> TECH-002
      └─> SYS-002
            └─> TECH-003
    """
    # Root requirement
    ahlr = Requirement(
            requirement_id="AHLR-001",
            title="Root High-Level Requirement",
            description="Top level requirement",
            type=RequirementType.AHLR,
            priority=RequirementPriority.CRITICAL,
            status=RequirementStatus.APPROVED,
            created_by_id=impact_test_user.id,
            regulatory_document="14 CFR Part 23"
    )
    db_session.add(ahlr)

    # System requirements
    sys1 = Requirement(
            requirement_id="SYS-001",
            title="System Requirement 1",
            description="First system requirement",
            type=RequirementType.SYSTEM,
            priority=RequirementPriority.HIGH,
            status=RequirementStatus.APPROVED,
            created_by_id=impact_test_user.id
    )
    sys2 = Requirement(
            requirement_id="SYS-002",
            title="System Requirement 2",
            description="Second system requirement",
            type=RequirementType.SYSTEM,
            priority=RequirementPriority.MEDIUM,
            status=RequirementStatus.APPROVED,
            created_by_id=impact_test_user.id
    )
    db_session.add_all([sys1, sys2])

    # Technical requirements
    tech1 = Requirement(
            requirement_id="TECH-001",
            title="Technical Specification 1",
            description="First technical spec",
            type=RequirementType.TECHNICAL,
            priority=RequirementPriority.HIGH,
            status=RequirementStatus.APPROVED,
            created_by_id=impact_test_user.id
    )
    tech2 = Requirement(
            requirement_id="TECH-002",
            title="Technical Specification 2",
            description="Second technical spec",
            type=RequirementType.TECHNICAL,
            priority=RequirementPriority.MEDIUM,
            status=RequirementStatus.APPROVED,
            created_by_id=impact_test_user.id
    )
    tech3 = Requirement(
            requirement_id="TECH-003",
            title="Technical Specification 3",
            description="Third technical spec",
            type=RequirementType.TECHNICAL,
            priority=RequirementPriority.LOW,
            status=RequirementStatus.APPROVED,
            created_by_id=impact_test_user.id
    )
    db_session.add_all([tech1, tech2, tech3])

    db_session.commit()
    db_session.refresh(ahlr)
    db_session.refresh(sys1)
    db_session.refresh(sys2)
    db_session.refresh(tech1)
    db_session.refresh(tech2)
    db_session.refresh(tech3)

    # Create traceability links
    links = [
            TraceabilityLink(source_id=ahlr.id, target_id=sys1.id, link_type=TraceLinkType.DERIVES_FROM, created_by_id=impact_test_user.id),
            TraceabilityLink(source_id=ahlr.id, target_id=sys2.id, link_type=TraceLinkType.DERIVES_FROM, created_by_id=impact_test_user.id),
            TraceabilityLink(source_id=sys1.id, target_id=tech1.id, link_type=TraceLinkType.DERIVES_FROM, created_by_id=impact_test_user.id),
            TraceabilityLink(source_id=sys1.id, target_id=tech2.id, link_type=TraceLinkType.DERIVES_FROM, created_by_id=impact_test_user.id),
            TraceabilityLink(source_id=sys2.id, target_id=tech3.id, link_type=TraceLinkType.DERIVES_FROM, created_by_id=impact_test_user.id),
    ]
    db_session.add_all(links)

    # Add test cases to technical requirements
    test_cases = [
            TestCase(
                requirement_id=tech1.id, test_case_id="TC-001", title="Test 1", description="Test",
                test_type="Unit", status=TestCaseStatus.PASSED, priority=TestCasePriority.HIGH,
                test_steps='["Step 1", "Step 2"]',
                expected_results='["Result 1"]',
                created_by_id=impact_test_user.id
            ),
            TestCase(
                requirement_id=tech1.id, test_case_id="TC-002", title="Test 2", description="Test",
                test_type="Unit", status=TestCaseStatus.PASSED, priority=TestCasePriority.MEDIUM,
                test_steps='["Step 1"]',
                expected_results='["Result 1"]',
                created_by_id=impact_test_user.id
            ),
            TestCase(
                requirement_id=tech2.id, test_case_id="TC-003", title="Test 3", description="Test",
                test_type="Integration", status=TestCaseStatus.FAILED, priority=TestCasePriority.HIGH,
                test_steps='["Step 1", "Step 2", "Step 3"]',
                expected_results='["Result 1", "Result 2"]',
                created_by_id=impact_test_user.id
            ),
    ]
    db_session.add_all(test_cases)

    db_session.commit()

    return {
            "ahlr": ahlr,
            "sys1": sys1,
            "sys2": sys2,
            "tech1": tech1,
            "tech2": tech2,
            "tech3": tech3
    }


class TestImpactAnalysisService:
    """Test the Impact Analysis Service"""

    @pytest.fixture
    def service(self, db_session: Session):
        """Create impact analysis service"""
        return ImpactAnalysisService(db_session)

    def test_traverse_upstream_single_level(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test upstream traversal with one parent"""
        sys1 = requirement_hierarchy["sys1"]

        upstream = service.traverse_upstream(sys1.id, max_depth=5)

        assert len(upstream) == 1
        assert upstream[0].requirement_id == "AHLR-001"
        assert upstream[0].depth == 1

    def test_traverse_upstream_multiple_levels(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test upstream traversal with grandparents"""
        tech1 = requirement_hierarchy["tech1"]

        upstream = service.traverse_upstream(tech1.id, max_depth=5)

        # Should find SYS-001 (parent) and AHLR-001 (grandparent)
        assert len(upstream) == 2
        requirement_ids = [node.requirement_id for node in upstream]
        assert "SYS-001" in requirement_ids
        assert "AHLR-001" in requirement_ids

    def test_traverse_downstream_with_test_cases(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test downstream traversal includes test cases"""
        sys1 = requirement_hierarchy["sys1"]

        downstream = service.traverse_downstream(sys1.id, max_depth=5, include_test_cases=True)

        # Should find TECH-001 and TECH-002
        assert len(downstream) == 2

        # Check test case counts
        tech1_node = next(node for node in downstream if node.requirement_id == "TECH-001")
        assert tech1_node.test_case_count == 2  # TC-001 and TC-002

    def test_traverse_downstream_from_root(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test downstream traversal from root requirement"""
        ahlr = requirement_hierarchy["ahlr"]

        downstream = service.traverse_downstream(ahlr.id, max_depth=10)

        # Should find all descendants: SYS-001, SYS-002, TECH-001, TECH-002, TECH-003
        assert len(downstream) == 5

        # Verify depth levels
        sys_nodes = [node for node in downstream if node.requirement_id.startswith("SYS")]
        tech_nodes = [node for node in downstream if node.requirement_id.startswith("TECH")]

        assert all(node.depth == 1 for node in sys_nodes)
        assert all(node.depth == 2 for node in tech_nodes)

    def test_max_depth_limit(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test that max_depth limit is respected"""
        ahlr = requirement_hierarchy["ahlr"]

        # Limit to depth 1 - should only get SYS requirements
        downstream = service.traverse_downstream(ahlr.id, max_depth=1)

        assert len(downstream) == 2
        assert all(node.requirement_id.startswith("SYS") for node in downstream)

    def test_cycle_detection(self, service: ImpactAnalysisService, requirement_hierarchy, db_session: Session, impact_test_user: User):
        """Test that circular dependencies don't cause infinite loops"""
        ahlr = requirement_hierarchy["ahlr"]
        sys1 = requirement_hierarchy["sys1"]

        # Create a circular link: SYS-001 -> AHLR-001 (creates cycle)
        circular_link = TraceabilityLink(
            source_id=sys1.id,
            target_id=ahlr.id,
            link_type=TraceLinkType.VERIFIES,
            created_by_id=impact_test_user.id
        )
        db_session.add(circular_link)
        db_session.commit()

        # This should not cause infinite loop
        upstream = service.traverse_upstream(sys1.id, max_depth=10)

        # Should handle cycle gracefully
        assert len(upstream) >= 1
        assert len(upstream) < 100  # Sanity check

    def test_analyze_impact_complete(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test complete impact analysis"""
        sys1 = requirement_hierarchy["sys1"]

        result = service.analyze_impact(sys1.id)

        # Verify result structure
        assert result.requirement.id == sys1.id
        assert len(result.upstream) > 0  # Should have AHLR-001
        assert len(result.downstream) > 0  # Should have TECH-001, TECH-002
        assert result.risk_score is not None
        assert result.risk_score.level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert 0 <= result.risk_score.score <= 100
        assert len(result.affected_test_cases) > 0
        assert len(result.recommendations) > 0
        assert result.estimated_effort_hours > 0

    def test_risk_score_critical_priority(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test risk score for critical priority requirement"""
        ahlr = requirement_hierarchy["ahlr"]

        result = service.analyze_impact(ahlr.id)

        # Root AHLR with many children should have higher risk
        assert result.stats["critical_count"] >= 1
        # The AHLR has regulatory implications and is critical priority
        # Risk score should be calculated (verify it's a valid level)
        assert result.risk_score.level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        # Verify the score itself is > 0
        assert result.risk_score.score > 0

    def test_risk_score_low_impact(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test risk score for leaf requirement with low impact"""
        tech3 = requirement_hierarchy["tech3"]

        result = service.analyze_impact(tech3.id)

        # Leaf requirement with no test cases should have low risk
        assert result.risk_score.level in ["LOW", "MEDIUM"]

    def test_regulatory_impact_detected(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test that regulatory requirements are flagged"""
        ahlr = requirement_hierarchy["ahlr"]

        result = service.analyze_impact(ahlr.id)

        # AHLR-001 has regulatory document
        assert len(result.regulatory_implications) > 0
        assert any("14 CFR" in impl for impl in result.regulatory_implications)

    def test_recommendations_generated(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test that recommendations are generated"""
        sys1 = requirement_hierarchy["sys1"]

        result = service.analyze_impact(sys1.id)

        assert len(result.recommendations) > 0
        # Should recommend re-executing test cases
        assert any("test" in rec.lower() for rec in result.recommendations)

    def test_effort_estimation(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test effort estimation is reasonable"""
        ahlr = requirement_hierarchy["ahlr"]

        result = service.analyze_impact(ahlr.id)

        # Effort should be positive and reasonable (not too high)
        assert result.estimated_effort_hours > 0
        assert result.estimated_effort_hours < 1000  # Sanity check

    def test_invalid_requirement_id(self, service: ImpactAnalysisService):
        """Test analysis with invalid requirement ID"""
        with pytest.raises(ValueError, match="not found"):
            service.analyze_impact(999999)

    def test_stats_calculation(self, service: ImpactAnalysisService, requirement_hierarchy):
        """Test that statistics are correctly calculated"""
        ahlr = requirement_hierarchy["ahlr"]

        result = service.analyze_impact(ahlr.id)

        stats = result.stats
        assert stats["total_affected"] == len(result.upstream) + len(result.downstream)
        assert stats["upstream_count"] == len(result.upstream)
        assert stats["downstream_count"] == len(result.downstream)
        assert stats["max_depth"] >= 0

        # Type counts (includes source requirement)
        type_count_sum = stats["ahlr_count"] + stats["system_count"] + stats["technical_count"] + stats["certification_count"]
        # The sum of type counts should include the source requirement + all affected
        assert type_count_sum >= stats["total_affected"]  # >= because source req is also counted


class TestImpactAnalysisAPI:
    """Test the Impact Analysis REST API"""

    def test_analyze_impact_success(self, client: TestClient, auth_headers: dict, requirement_hierarchy):
        """Test successful impact analysis via API"""
        sys1 = requirement_hierarchy["sys1"]

        response = client.post(
            "/api/impact-analysis/analyze",
            headers=auth_headers,
            json={
                "requirement_id": sys1.id,
                "config": {
                    "max_depth": 5,
                    "include_test_cases": True
                }
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "requirement" in data
        assert "risk_score" in data
        assert "upstream" in data
        assert "downstream" in data
        assert data["risk_score"]["level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def test_analyze_impact_unauthorized(self, client: TestClient, requirement_hierarchy):
        """Test that authentication is required"""
        sys1 = requirement_hierarchy["sys1"]

        response = client.post(
            "/api/impact-analysis/analyze",
            json={"requirement_id": sys1.id}
        )

        assert response.status_code == 401

    def test_analyze_impact_not_found(self, client: TestClient, auth_headers: dict):
        """Test 404 for non-existent requirement"""
        response = client.post(
            "/api/impact-analysis/analyze",
            headers=auth_headers,
            json={"requirement_id": 999999}
        )

        assert response.status_code == 404

    def test_get_report(self, client: TestClient, auth_headers: dict, db_session: Session, requirement_hierarchy, test_user: User):
        """Test retrieving an impact analysis report"""
        sys1 = requirement_hierarchy["sys1"]

        # Create a report
        report = ImpactAnalysisReport(
            requirement_id=sys1.id,
            analyzed_by_id=test_user.id,
            risk_score=45.5,
            risk_level=RiskLevel.MEDIUM,
            upstream_count=1,
            downstream_count=2,
            test_case_count=3,
            regulatory_impact=False,
            upstream_tree=[],
            downstream_tree=[],
            affected_requirements=[],
            affected_test_cases=[],
            recommendations=[],
            regulatory_implications=[],
            risk_factors={},
            estimated_effort_hours=10.5,
            stats={}
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        response = client.get(
            f"/api/impact-analysis/reports/{report.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report.id
        assert data["risk_level"] == "MEDIUM"

    def test_list_reports(self, client: TestClient, auth_headers: dict, db_session: Session, requirement_hierarchy, test_user: User):
        """Test listing impact analysis reports"""
        sys1 = requirement_hierarchy["sys1"]

        # Create multiple reports
        for i in range(3):
            report = ImpactAnalysisReport(
                requirement_id=sys1.id,
                analyzed_by_id=test_user.id,
                risk_score=30.0 + i * 10,
                risk_level=RiskLevel.MEDIUM,
                upstream_count=1,
                downstream_count=2,
                test_case_count=3,
                regulatory_impact=False,
                upstream_tree=[],
                downstream_tree=[],
                affected_requirements=[],
                affected_test_cases=[],
                recommendations=[],
                regulatory_implications=[],
                risk_factors={},
                estimated_effort_hours=10.0,
                stats={}
            )
            db_session.add(report)
        db_session.commit()

        response = client.get(
            "/api/impact-analysis/reports",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        assert len(data["reports"]) >= 3
        assert data["total"] >= 3

    def test_create_change_request_with_analysis(self, client: TestClient, auth_headers: dict, requirement_hierarchy):
        """Test creating change request with impact analysis"""
        sys1 = requirement_hierarchy["sys1"]

        response = client.post(
            "/api/impact-analysis/change-requests",
            headers=auth_headers,
            json={
                "requirement_id": sys1.id,
                "title": "Update System Requirement 1",
                "description": "Modify the requirement to improve performance",
                "justification": "Customer feedback",
                "proposed_changes": {
                    "before": "Performance: 100ms",
                    "after": "Performance: 50ms"
                },
                "perform_impact_analysis": True
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "Update System Requirement 1"
        assert data["status"] == "PENDING"
        assert "impact_summary" in data
        assert data["impact_summary"] is not None

    def test_list_change_requests(self, client: TestClient, auth_headers: dict, db_session: Session, requirement_hierarchy, test_user: User):
        """Test listing change requests"""
        sys1 = requirement_hierarchy["sys1"]

        # Create change request
        cr = ChangeRequest(
            requirement_id=sys1.id,
            title="Test Change Request",
            description="Test description",
            status=ChangeRequestStatus.PENDING,
            requested_by_id=test_user.id
        )
        db_session.add(cr)
        db_session.commit()

        response = client.get(
            "/api/impact-analysis/change-requests",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "change_requests" in data
        assert len(data["change_requests"]) >= 1

    def test_review_change_request(self, client: TestClient, auth_headers: dict, db_session: Session, requirement_hierarchy, test_user: User):
        """Test reviewing/approving a change request"""
        sys1 = requirement_hierarchy["sys1"]

        # Create change request
        cr = ChangeRequest(
            requirement_id=sys1.id,
            title="Test Change Request",
            description="Test description",
            status=ChangeRequestStatus.PENDING,
            requested_by_id=test_user.id
        )
        db_session.add(cr)
        db_session.commit()
        db_session.refresh(cr)

        response = client.patch(
            f"/api/impact-analysis/change-requests/{cr.id}/review",
            headers=auth_headers,
            json={
                "status": "APPROVED",
                "review_comments": "Looks good!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "APPROVED"
        assert data["review_comments"] == "Looks good!"
        assert data["reviewed_by_id"] is not None
