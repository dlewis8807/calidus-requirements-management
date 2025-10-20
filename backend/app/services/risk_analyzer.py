"""
Risk Assessment Service
Calculates risk scores for requirements based on multiple factors.

Risk Scoring Algorithm:
- Priority Level (25%): Higher priority = higher risk
- Status Risk (20%): Draft/Under Review = higher risk
- Traceability (25%): Missing links = higher risk
- Test Coverage (20%): No tests = higher risk
- Compliance (10%): Non-compliant = higher risk

Total Risk Score: 0-100
- 0-25: Low Risk (Green)
- 26-50: Medium Risk (Amber)
- 51-75: High Risk (Orange)
- 76-100: Critical Risk (Red)
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.requirement import Requirement, RequirementPriority, RequirementStatus
from app.schemas.risk import RiskScore, RiskFactor


class RiskAnalyzer:
    """Service for calculating requirement risk scores"""

    # Scoring weights (must sum to 100)
    WEIGHTS = {
        "priority": 25.0,
        "status": 20.0,
        "traceability": 25.0,
        "test_coverage": 20.0,
        "compliance": 10.0
    }

    # Risk level thresholds
    RISK_LEVELS = {
        "Critical": (76, 100),
        "High": (51, 75),
        "Medium": (26, 50),
        "Low": (0, 25)
    }

    def __init__(self, db: Session):
        self.db = db

    def calculate_risk_score(self, requirement: Requirement) -> RiskScore:
        """
        Calculate complete risk assessment for a requirement.

        Args:
            requirement: Requirement model instance

        Returns:
            RiskScore with breakdown of all factors
        """
        factors = []

        # 1. Priority Level Score (25%)
        priority_score, priority_details = self._calculate_priority_score(requirement)
        factors.append(RiskFactor(
            factor_name="Priority Level",
            weight=self.WEIGHTS["priority"],
            score=priority_score,
            impact=priority_score * self.WEIGHTS["priority"] / 100,
            details=priority_details
        ))

        # 2. Status Risk Score (20%)
        status_score, status_details = self._calculate_status_score(requirement)
        factors.append(RiskFactor(
            factor_name="Status Risk",
            weight=self.WEIGHTS["status"],
            score=status_score,
            impact=status_score * self.WEIGHTS["status"] / 100,
            details=status_details
        ))

        # 3. Traceability Score (25%)
        trace_score, trace_details = self._calculate_traceability_score(requirement)
        factors.append(RiskFactor(
            factor_name="Traceability",
            weight=self.WEIGHTS["traceability"],
            score=trace_score,
            impact=trace_score * self.WEIGHTS["traceability"] / 100,
            details=trace_details
        ))

        # 4. Test Coverage Score (20%)
        test_score, test_details = self._calculate_test_coverage_score(requirement)
        factors.append(RiskFactor(
            factor_name="Test Coverage",
            weight=self.WEIGHTS["test_coverage"],
            score=test_score,
            impact=test_score * self.WEIGHTS["test_coverage"] / 100,
            details=test_details
        ))

        # 5. Compliance Score (10%)
        compliance_score, compliance_details = self._calculate_compliance_score(requirement)
        factors.append(RiskFactor(
            factor_name="Compliance",
            weight=self.WEIGHTS["compliance"],
            score=compliance_score,
            impact=compliance_score * self.WEIGHTS["compliance"] / 100,
            details=compliance_details
        ))

        # Calculate total risk score
        total_risk = sum(factor.impact for factor in factors)
        risk_level = self._determine_risk_level(total_risk)

        return RiskScore(
            requirement_id=requirement.requirement_id,
            total_risk_score=round(total_risk, 1),
            risk_level=risk_level,
            factors=factors
        )

    def _calculate_priority_score(self, requirement: Requirement) -> Tuple[float, str]:
        """
        Calculate risk based on priority level.
        Higher priority = higher risk (more critical to get right)

        Returns:
            (score, details_text)
        """
        priority_scores = {
            RequirementPriority.CRITICAL: (100.0, "Critical priority - highest risk impact"),
            RequirementPriority.HIGH: (75.0, "High priority - significant risk"),
            RequirementPriority.MEDIUM: (50.0, "Medium priority - moderate risk"),
            RequirementPriority.LOW: (25.0, "Low priority - minimal risk impact")
        }

        return priority_scores.get(requirement.priority, (50.0, "Unknown priority"))

    def _calculate_status_score(self, requirement: Requirement) -> Tuple[float, str]:
        """
        Calculate risk based on requirement status.
        Draft/Under Review = higher risk (incomplete/unstable)

        Returns:
            (score, details_text)
        """
        status_scores = {
            RequirementStatus.DRAFT: (100.0, "Draft status - highest instability risk"),
            RequirementStatus.UNDER_REVIEW: (75.0, "Under review - changes likely"),
            RequirementStatus.DEPRECATED: (50.0, "Deprecated - should not be used"),
            RequirementStatus.APPROVED: (10.0, "Approved - stable and verified")
        }

        return status_scores.get(requirement.status, (50.0, "Unknown status"))

    def _calculate_traceability_score(self, requirement: Requirement) -> Tuple[float, str]:
        """
        Calculate risk based on traceability links.
        Missing links = higher risk (isolated requirement)

        Returns:
            (score, details_text)
        """
        # Count parent and child trace links
        parent_count = len(requirement.parent_traces) if requirement.parent_traces else 0
        child_count = len(requirement.child_traces) if requirement.child_traces else 0
        total_links = parent_count + child_count

        if total_links == 0:
            return (100.0, "Orphaned - no traceability links")
        elif total_links == 1:
            return (75.0, f"Limited traceability - only {total_links} link")
        elif total_links <= 3:
            return (50.0, f"Partial traceability - {total_links} links")
        elif total_links <= 6:
            return (25.0, f"Good traceability - {total_links} links")
        else:
            return (10.0, f"Excellent traceability - {total_links}+ links")

    def _calculate_test_coverage_score(self, requirement: Requirement) -> Tuple[float, str]:
        """
        Calculate risk based on test case coverage.
        No tests = higher risk (unverified requirement)

        Returns:
            (score, details_text)
        """
        # Count test cases and their status
        test_cases = requirement.test_cases if requirement.test_cases else []
        total_tests = len(test_cases)

        if total_tests == 0:
            return (100.0, "No test cases - unverified requirement")

        # Count passed tests
        passed_tests = sum(1 for tc in test_cases if tc.status == "Passed")
        failed_tests = sum(1 for tc in test_cases if tc.status == "Failed")
        pending_tests = sum(1 for tc in test_cases if tc.status == "Pending")

        if failed_tests > 0:
            return (90.0, f"{failed_tests} failed test(s) - verification issues")
        elif pending_tests == total_tests:
            return (75.0, f"{total_tests} test(s) pending - not yet verified")
        elif passed_tests == total_tests:
            return (5.0, f"All {total_tests} test(s) passing - fully verified")
        elif passed_tests > 0:
            coverage_pct = (passed_tests / total_tests) * 100
            score = 50 - (coverage_pct / 2)  # 50% pass = 25 score, 100% pass = 0 score
            return (score, f"{passed_tests}/{total_tests} tests passing ({coverage_pct:.0f}%)")
        else:
            return (60.0, f"{total_tests} test(s) exist but none passed")

    def _calculate_compliance_score(self, requirement: Requirement) -> Tuple[float, str]:
        """
        Calculate risk based on compliance status.
        Non-compliant = higher risk (regulatory issues)

        Returns:
            (score, details_text)
        """
        # Check if regulatory mapping exists
        has_regulatory_link = bool(requirement.regulatory_document)

        if not has_regulatory_link:
            return (80.0, "No regulatory mapping - compliance unclear")

        # Check compliance status field
        compliance_status = requirement.compliance_status
        if not compliance_status:
            return (70.0, "Compliance status not assessed")

        compliance_status_lower = compliance_status.lower()
        if compliance_status_lower in ["compliant", "passed", "approved"]:
            return (5.0, f"Compliant - {compliance_status}")
        elif compliance_status_lower in ["pending", "under_review"]:
            return (50.0, f"Compliance pending - {compliance_status}")
        elif compliance_status_lower in ["non_compliant", "failed"]:
            return (100.0, f"Non-compliant - {compliance_status}")
        else:
            return (60.0, f"Unknown compliance status - {compliance_status}")

    def _determine_risk_level(self, score: float) -> str:
        """
        Determine risk level category from numeric score.

        Args:
            score: Total risk score (0-100)

        Returns:
            Risk level string: "Critical", "High", "Medium", or "Low"
        """
        for level, (min_score, max_score) in self.RISK_LEVELS.items():
            if min_score <= score <= max_score:
                return level
        return "Medium"  # Default fallback

    def batch_calculate_risk_scores(self, requirements: List[Requirement]) -> List[RiskScore]:
        """
        Calculate risk scores for multiple requirements in batch.

        Args:
            requirements: List of Requirement model instances

        Returns:
            List of RiskScore objects
        """
        return [self.calculate_risk_score(req) for req in requirements]

    def get_risk_distribution(self, requirements: List[Requirement]) -> dict:
        """
        Get distribution of requirements across risk levels.

        Args:
            requirements: List of Requirement model instances

        Returns:
            Dictionary with counts per risk level
        """
        distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

        for req in requirements:
            risk_score = self.calculate_risk_score(req)
            distribution[risk_score.risk_level] += 1

        return distribution
