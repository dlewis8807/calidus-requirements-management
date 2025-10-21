"""
Test Coverage Analyzer Service
Analyzes test coverage across requirements with heatmap generation and gap analysis.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.requirement import Requirement, RequirementType, RequirementPriority
from app.models.test_case import TestCase
from app.models.coverage import CoverageSnapshot
import logging

logger = logging.getLogger(__name__)


class CoverageAnalyzer:
    """Service for analyzing test coverage across requirements."""

    def __init__(self, db: Session):
        self.db = db

    def analyze_coverage(self) -> Dict:
        """
        Perform comprehensive coverage analysis.

        Returns:
            {
                "overall": {...},
                "by_type": {...},
                "by_priority": {...},
                "heatmap": {...},
                "gaps": [...],
                "trends": [...]
            }
        """
        # Get all requirements
        requirements = self.db.query(Requirement).all()
        total_reqs = len(requirements)

        # Get requirements with test cases
        requirements_with_tests = {req.id for req in requirements if len(req.test_cases) > 0}
        covered_count = len(requirements_with_tests)

        # Calculate overall coverage
        overall = {
            "total_requirements": total_reqs,
            "covered_requirements": covered_count,
            "uncovered_requirements": total_reqs - covered_count,
            "coverage_percentage": (covered_count / total_reqs * 100) if total_reqs > 0 else 0.0,
        }

        # Analyze by type
        by_type = self._analyze_by_type(requirements)

        # Analyze by priority
        by_priority = self._analyze_by_priority(requirements)

        # Generate heatmap
        heatmap = self._generate_heatmap(requirements)

        # Identify gaps
        gaps = self._identify_gaps(requirements)

        # Get trends
        trends = self._get_coverage_trends()

        logger.info(
            f"Coverage analysis complete: {covered_count}/{total_reqs} requirements "
            f"({overall['coverage_percentage']:.1f}%)"
        )

        return {
            "overall": overall,
            "by_type": by_type,
            "by_priority": by_priority,
            "heatmap": heatmap,
            "gaps": gaps,
            "trends": trends,
        }

    def _analyze_by_type(self, requirements: List[Requirement]) -> Dict:
        """Analyze coverage by requirement type."""
        types = {}

        for req_type in RequirementType:
            type_reqs = [r for r in requirements if r.type == req_type]
            covered = [r for r in type_reqs if len(r.test_cases) > 0]

            total = len(type_reqs)
            covered_count = len(covered)

            types[req_type.value] = {
                "total": total,
                "covered": covered_count,
                "uncovered": total - covered_count,
                "coverage_percentage": (covered_count / total * 100) if total > 0 else 0.0,
                "test_case_count": sum(len(r.test_cases) for r in type_reqs),
            }

        return types

    def _analyze_by_priority(self, requirements: List[Requirement]) -> Dict:
        """Analyze coverage by priority level."""
        priorities = {}

        for priority in RequirementPriority:
            priority_reqs = [r for r in requirements if r.priority == priority]
            covered = [r for r in priority_reqs if len(r.test_cases) > 0]

            total = len(priority_reqs)
            covered_count = len(covered)

            priorities[priority.value] = {
                "total": total,
                "covered": covered_count,
                "uncovered": total - covered_count,
                "coverage_percentage": (covered_count / total * 100) if total > 0 else 0.0,
                "test_case_count": sum(len(r.test_cases) for r in priority_reqs),
            }

        return priorities

    def _generate_heatmap(self, requirements: List[Requirement]) -> Dict:
        """
        Generate coverage heatmap: requirement type × priority.

        Returns:
            {
                "AHLR": {
                    "Critical": {"total": 10, "covered": 8, "uncovered": 2, "coverage_percentage": 80.0},
                    "High": {...},
                    ...
                },
                ...
            }
        """
        heatmap = {}

        for req_type in RequirementType:
            heatmap[req_type.value] = {}

            for priority in RequirementPriority:
                # Filter requirements by type and priority
                filtered = [
                    r for r in requirements
                    if r.type == req_type and r.priority == priority
                ]

                total = len(filtered)
                covered = len([r for r in filtered if len(r.test_cases) > 0])

                heatmap[req_type.value][priority.value] = {
                    "total": total,
                    "covered": covered,
                    "uncovered": total - covered,
                    "coverage_percentage": (covered / total * 100) if total > 0 else 0.0,
                }

        return heatmap

    def _identify_gaps(self, requirements: List[Requirement]) -> List[Dict]:
        """
        Identify requirements with no test coverage.

        Returns list sorted by priority (Critical first).
        """
        uncovered = [r for r in requirements if len(r.test_cases) == 0]

        # Sort by priority (Critical > High > Medium > Low)
        priority_order = {
            RequirementPriority.CRITICAL: 0,
            RequirementPriority.HIGH: 1,
            RequirementPriority.MEDIUM: 2,
            RequirementPriority.LOW: 3,
        }

        uncovered.sort(key=lambda r: (priority_order.get(r.priority, 99), r.id))

        gaps = []
        for req in uncovered[:100]:  # Limit to top 100 gaps
            gaps.append({
                "requirement_id": req.id,
                "requirement_identifier": req.requirement_id,
                "title": req.title,
                "type": req.type.value if req.type else None,
                "priority": req.priority.value if req.priority else None,
                "status": req.status.value if req.status else None,
                "regulatory": bool(req.regulatory_document),
                "regulatory_document": req.regulatory_document,
            })

        return gaps

    def _get_coverage_trends(self, limit: int = 10) -> List[Dict]:
        """Get historical coverage trends from snapshots."""
        snapshots = (
            self.db.query(CoverageSnapshot)
            .order_by(CoverageSnapshot.snapshot_date.desc())
            .limit(limit)
            .all()
        )

        trends = []
        for snapshot in reversed(snapshots):  # Reverse to show oldest first
            trends.append({
                "date": snapshot.snapshot_date.isoformat(),
                "coverage_percentage": snapshot.coverage_percentage,
                "total_requirements": snapshot.total_requirements,
                "covered_requirements": snapshot.covered_requirements,
                "total_gaps": snapshot.total_gaps,
                "critical_gaps": snapshot.critical_gaps,
            })

        return trends

    def create_snapshot(self, user_id: int) -> CoverageSnapshot:
        """Create a coverage snapshot for trend analysis."""
        analysis = self.analyze_coverage()

        snapshot = CoverageSnapshot(
            total_requirements=analysis["overall"]["total_requirements"],
            covered_requirements=analysis["overall"]["covered_requirements"],
            coverage_percentage=analysis["overall"]["coverage_percentage"],
            ahlr_coverage=analysis["by_type"].get("Aircraft_High_Level", {}),
            system_coverage=analysis["by_type"].get("System_Requirement", {}),
            technical_coverage=analysis["by_type"].get("Technical_Specification", {}),
            certification_coverage=analysis["by_type"].get("Certification_Requirement", {}),
            critical_coverage=analysis["by_priority"].get("Critical", {}),
            high_coverage=analysis["by_priority"].get("High", {}),
            medium_coverage=analysis["by_priority"].get("Medium", {}),
            low_coverage=analysis["by_priority"].get("Low", {}),
            heatmap_data=analysis["heatmap"],
            total_gaps=analysis["overall"]["uncovered_requirements"],
            critical_gaps=len([
                g for g in analysis["gaps"]
                if g["priority"] == "Critical"
            ]),
            created_by_id=user_id,
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        logger.info(f"Coverage snapshot created: {snapshot.coverage_percentage:.1f}%")

        return snapshot

    def suggest_test_cases(self, requirement_id: int) -> List[Dict]:
        """
        Generate test case suggestions for a requirement.

        Uses rule-based approach (can be enhanced with AI later).
        """
        requirement = self.db.query(Requirement).filter(
            Requirement.id == requirement_id
        ).first()

        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")

        suggestions = []

        # Rule 1: Every requirement should have at least one unit test
        if not any(tc.test_type == "Unit" for tc in requirement.test_cases):
            suggestions.append({
                "type": "Unit",
                "title": f"Unit test for {requirement.requirement_id}",
                "steps": [
                    "Set up test environment",
                    f"Execute {requirement.requirement_id} functionality",
                    "Verify expected behavior",
                ],
                "expected_results": [
                    f"{requirement.requirement_id} functionality operates as specified",
                ],
                "confidence": 0.9,
                "reasoning": "Every requirement should have unit-level verification",
            })

        # Rule 2: Critical requirements should have integration tests
        if requirement.priority == RequirementPriority.CRITICAL:
            if not any(tc.test_type == "Integration" for tc in requirement.test_cases):
                suggestions.append({
                    "type": "Integration",
                    "title": f"Integration test for critical requirement {requirement.requirement_id}",
                    "steps": [
                        "Set up integrated system environment",
                        f"Execute {requirement.requirement_id} in context of connected systems",
                        "Verify cross-system interactions",
                    ],
                    "expected_results": [
                        f"{requirement.requirement_id} integrates correctly with dependent systems",
                    ],
                    "confidence": 0.85,
                    "reasoning": "Critical requirements require integration verification",
                })

        # Rule 3: Regulatory requirements should have system tests
        if requirement.regulatory_document:
            if not any(tc.test_type == "System" for tc in requirement.test_cases):
                suggestions.append({
                    "type": "System",
                    "title": f"System test for regulatory requirement {requirement.requirement_id}",
                    "steps": [
                        "Set up complete system in operational configuration",
                        "Execute end-to-end scenario",
                        f"Verify compliance with {requirement.regulatory_document}",
                    ],
                    "expected_results": [
                        f"System demonstrates compliance with {requirement.regulatory_document}",
                    ],
                    "confidence": 0.95,
                    "reasoning": "Regulatory requirements must be validated at system level",
                })

        # Rule 4: High priority requirements should have at least 2 tests
        if requirement.priority == RequirementPriority.HIGH:
            if len(requirement.test_cases) < 2:
                suggestions.append({
                    "type": "Acceptance",
                    "title": f"Acceptance test for {requirement.requirement_id}",
                    "steps": [
                        "Set up acceptance test environment",
                        f"Execute {requirement.requirement_id} from user perspective",
                        "Verify user acceptance criteria",
                    ],
                    "expected_results": [
                        f"{requirement.requirement_id} meets user acceptance criteria",
                    ],
                    "confidence": 0.75,
                    "reasoning": "High priority requirements benefit from multiple test perspectives",
                })

        return suggestions
