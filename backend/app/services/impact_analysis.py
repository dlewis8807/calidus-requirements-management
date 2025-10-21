"""
Impact Analysis Service
Analyzes the impact of requirement changes using graph traversal algorithms.
"""
from typing import List, Set, Optional, Dict, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.requirement import Requirement
from app.models.traceability import TraceabilityLink
from app.models.test_case import TestCase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ImpactNode:
    """Represents a single node in the impact tree"""

    def __init__(
        self,
        requirement: Requirement,
        depth: int,
        path: List[str],
        link_type: Optional[str] = None,
        test_case_count: int = 0
    ):
        self.requirement_id = requirement.requirement_id
        self.id = requirement.id
        self.title = requirement.title
        self.type = requirement.type.value if hasattr(requirement.type, 'value') else str(requirement.type)
        self.priority = requirement.priority.value if hasattr(requirement.priority, 'value') else str(requirement.priority)
        self.status = requirement.status.value if hasattr(requirement.status, 'value') else str(requirement.status)
        self.category = requirement.category
        self.depth = depth
        self.path = path
        self.link_type = link_type
        self.test_case_count = test_case_count
        self.regulatory = bool(requirement.regulatory_document)
        self.regulatory_document = requirement.regulatory_document

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "requirement_id": self.requirement_id,
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "priority": self.priority,
            "status": self.status,
            "category": self.category,
            "depth": self.depth,
            "path": self.path,
            "link_type": self.link_type,
            "test_case_count": self.test_case_count,
            "regulatory": self.regulatory,
            "regulatory_document": self.regulatory_document
        }


class RiskScore:
    """Risk score calculation result"""

    def __init__(
        self,
        score: float,
        level: str,
        factors: Dict[str, float],
        explanation: str
    ):
        self.score = score
        self.level = level
        self.factors = factors
        self.explanation = explanation

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 2),
            "level": self.level,
            "factors": self.factors,
            "explanation": self.explanation
        }


class ImpactAnalysisConfig:
    """Configuration for impact analysis"""

    def __init__(
        self,
        max_depth: int = 10,
        include_test_cases: bool = True,
        include_regulatory: bool = True,
        weights: Optional[Dict[str, float]] = None
    ):
        self.max_depth = max_depth
        self.include_test_cases = include_test_cases
        self.include_regulatory = include_regulatory
        self.weights = weights or {
            "depth": 0.20,
            "breadth": 0.25,
            "critical": 0.25,
            "test": 0.15,
            "regulatory": 0.10,
            "history": 0.05
        }


class ImpactAnalysisResult:
    """Complete impact analysis result"""

    def __init__(
        self,
        requirement: Requirement,
        upstream: List[ImpactNode],
        downstream: List[ImpactNode],
        risk_score: RiskScore,
        stats: Dict[str, int],
        affected_test_cases: List[int],
        regulatory_implications: List[str],
        recommendations: List[str],
        estimated_effort_hours: float
    ):
        self.requirement = requirement
        self.upstream = upstream
        self.downstream = downstream
        self.risk_score = risk_score
        self.stats = stats
        self.affected_test_cases = affected_test_cases
        self.regulatory_implications = regulatory_implications
        self.recommendations = recommendations
        self.estimated_effort_hours = estimated_effort_hours


class ImpactAnalysisService:
    """
    Service for analyzing the impact of requirement changes.
    Uses graph traversal algorithms to identify affected requirements and test cases.
    """

    def __init__(self, db: Session):
        self.db = db
        self.visited_upstream: Set[int] = set()
        self.visited_downstream: Set[int] = set()

    def analyze_impact(
        self,
        requirement_id: int,
        config: Optional[ImpactAnalysisConfig] = None
    ) -> ImpactAnalysisResult:
        """
        Perform complete impact analysis for a requirement.

        Args:
            requirement_id: ID of the requirement to analyze
            config: Optional configuration for analysis parameters

        Returns:
            ImpactAnalysisResult with all affected items and risk score
        """
        if config is None:
            config = ImpactAnalysisConfig()

        logger.info(f"Starting impact analysis for requirement {requirement_id}")

        # Get the requirement
        requirement = self.db.query(Requirement).filter(
            Requirement.id == requirement_id
        ).first()

        if not requirement:
            raise ValueError(f"Requirement with ID {requirement_id} not found")

        # Reset visited sets
        self.visited_upstream = set()
        self.visited_downstream = set()

        # Traverse upstream (parents)
        upstream_nodes = self.traverse_upstream(
            requirement_id,
            depth=0,
            max_depth=config.max_depth,
            path=[requirement.requirement_id]
        )

        # Traverse downstream (children)
        downstream_nodes = self.traverse_downstream(
            requirement_id,
            depth=0,
            max_depth=config.max_depth,
            path=[requirement.requirement_id],
            include_test_cases=config.include_test_cases
        )

        # Collect all affected test cases
        affected_test_cases = self._collect_test_cases(
            requirement_id,
            downstream_nodes,
            config.include_test_cases
        )

        # Calculate statistics (include the source requirement)
        stats = self._calculate_stats(requirement, upstream_nodes, downstream_nodes)

        # Calculate risk score
        risk_score = self.calculate_risk_score(
            requirement,
            upstream_nodes,
            downstream_nodes,
            affected_test_cases,
            config
        )

        # Identify regulatory implications
        regulatory_implications = self._identify_regulatory_implications(
            requirement,
            upstream_nodes,
            downstream_nodes
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            requirement,
            upstream_nodes,
            downstream_nodes,
            affected_test_cases,
            risk_score
        )

        # Estimate effort
        estimated_effort_hours = self._estimate_effort(
            stats,
            affected_test_cases,
            risk_score
        )

        logger.info(
            f"Impact analysis complete: {stats['total_affected']} requirements, "
            f"{len(affected_test_cases)} test cases, risk level: {risk_score.level}"
        )

        return ImpactAnalysisResult(
            requirement=requirement,
            upstream=upstream_nodes,
            downstream=downstream_nodes,
            risk_score=risk_score,
            stats=stats,
            affected_test_cases=affected_test_cases,
            regulatory_implications=regulatory_implications,
            recommendations=recommendations,
            estimated_effort_hours=estimated_effort_hours
        )

    def traverse_upstream(
        self,
        req_id: int,
        depth: int = 0,
        max_depth: int = 10,
        path: Optional[List[str]] = None
    ) -> List[ImpactNode]:
        """
        Recursively traverse parent requirements using DFS.

        Args:
            req_id: Current requirement ID
            depth: Current depth in traversal
            max_depth: Maximum depth to traverse
            path: Path of requirement IDs from root

        Returns:
            List of ImpactNode objects representing upstream requirements
        """
        if path is None:
            path = []

        # Stop if max depth reached or already visited (cycle detection)
        if depth >= max_depth or req_id in self.visited_upstream:
            return []

        self.visited_upstream.add(req_id)
        result = []

        # Get all parent links (where current requirement is the target)
        parent_links = self.db.query(TraceabilityLink).filter(
            TraceabilityLink.target_id == req_id
        ).options(
            joinedload(TraceabilityLink.source)
        ).all()

        for link in parent_links:
            parent_req = link.source

            if parent_req and parent_req.id not in self.visited_upstream:
                # Create impact node for parent
                node = ImpactNode(
                    requirement=parent_req,
                    depth=depth + 1,
                    path=path + [parent_req.requirement_id],
                    link_type=link.link_type
                )
                result.append(node)

                # Recursive traversal
                result.extend(
                    self.traverse_upstream(
                        parent_req.id,
                        depth + 1,
                        max_depth,
                        path + [parent_req.requirement_id]
                    )
                )

        return result

    def traverse_downstream(
        self,
        req_id: int,
        depth: int = 0,
        max_depth: int = 10,
        path: Optional[List[str]] = None,
        include_test_cases: bool = True
    ) -> List[ImpactNode]:
        """
        Recursively traverse child requirements and test cases using DFS.

        Args:
            req_id: Current requirement ID
            depth: Current depth in traversal
            max_depth: Maximum depth to traverse
            path: Path of requirement IDs from root
            include_test_cases: Whether to count test cases

        Returns:
            List of ImpactNode objects representing downstream requirements
        """
        if path is None:
            path = []

        # Stop if max depth reached or already visited (cycle detection)
        if depth >= max_depth or req_id in self.visited_downstream:
            return []

        self.visited_downstream.add(req_id)
        result = []

        # Get all child links (where current requirement is the source)
        child_links = self.db.query(TraceabilityLink).filter(
            TraceabilityLink.source_id == req_id
        ).options(
            joinedload(TraceabilityLink.target)
        ).all()

        for link in child_links:
            child_req = link.target

            if child_req and child_req.id not in self.visited_downstream:
                # Count test cases for this requirement
                test_case_count = 0
                if include_test_cases:
                    test_case_count = self.db.query(TestCase).filter(
                        TestCase.requirement_id == child_req.id
                    ).count()

                # Create impact node for child
                node = ImpactNode(
                    requirement=child_req,
                    depth=depth + 1,
                    path=path + [child_req.requirement_id],
                    link_type=link.link_type,
                    test_case_count=test_case_count
                )
                result.append(node)

                # Recursive traversal
                result.extend(
                    self.traverse_downstream(
                        child_req.id,
                        depth + 1,
                        max_depth,
                        path + [child_req.requirement_id],
                        include_test_cases
                    )
                )

        return result

    def _collect_test_cases(
        self,
        requirement_id: int,
        downstream_nodes: List[ImpactNode],
        include_test_cases: bool
    ) -> List[int]:
        """Collect all test case IDs affected by the change"""
        if not include_test_cases:
            return []

        test_case_ids = set()

        # Get test cases for the requirement itself
        test_cases = self.db.query(TestCase.id).filter(
            TestCase.requirement_id == requirement_id
        ).all()
        test_case_ids.update([tc.id for tc in test_cases])

        # Get test cases from all downstream requirements
        for node in downstream_nodes:
            test_cases = self.db.query(TestCase.id).filter(
                TestCase.requirement_id == node.id
            ).all()
            test_case_ids.update([tc.id for tc in test_cases])

        return list(test_case_ids)

    def _calculate_stats(
        self,
        requirement: Requirement,
        upstream_nodes: List[ImpactNode],
        downstream_nodes: List[ImpactNode]
    ) -> Dict[str, int]:
        """Calculate statistics about affected requirements (including source requirement)"""
        all_nodes = upstream_nodes + downstream_nodes

        stats = {
            "total_affected": len(all_nodes),
            "upstream_count": len(upstream_nodes),
            "downstream_count": len(downstream_nodes),
            "ahlr_count": 0,
            "system_count": 0,
            "technical_count": 0,
            "certification_count": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "max_depth": 0
        }

        # Count source requirement
        req_type = str(requirement.type).upper() if requirement.type else ""
        if "AHLR" in req_type or "AIRCRAFT_HIGH_LEVEL" in req_type:
            stats["ahlr_count"] += 1
        elif "SYSTEM" in req_type:
            stats["system_count"] += 1
        elif "TECHNICAL" in req_type:
            stats["technical_count"] += 1
        elif "CERTIFICATION" in req_type:
            stats["certification_count"] += 1

        req_priority = str(requirement.priority).upper() if requirement.priority else ""
        if "CRITICAL" in req_priority:
            stats["critical_count"] += 1
        elif "HIGH" in req_priority:
            stats["high_count"] += 1
        elif "MEDIUM" in req_priority:
            stats["medium_count"] += 1
        elif "LOW" in req_priority:
            stats["low_count"] += 1

        # Count affected nodes
        for node in all_nodes:
            # Count by type
            if "AHLR" in node.type or "Aircraft_High_Level" in node.type:
                stats["ahlr_count"] += 1
            elif "SYSTEM" in node.type or "System_Requirement" in node.type:
                stats["system_count"] += 1
            elif "TECHNICAL" in node.type or "Technical_Specification" in node.type:
                stats["technical_count"] += 1
            elif "CERTIFICATION" in node.type or "Certification_Requirement" in node.type:
                stats["certification_count"] += 1

            # Count by priority
            priority_upper = node.priority.upper() if node.priority else ""
            if "CRITICAL" in priority_upper:
                stats["critical_count"] += 1
            elif "HIGH" in priority_upper:
                stats["high_count"] += 1
            elif "MEDIUM" in priority_upper:
                stats["medium_count"] += 1
            elif "LOW" in priority_upper:
                stats["low_count"] += 1

            # Track max depth
            if node.depth > stats["max_depth"]:
                stats["max_depth"] = node.depth

        return stats

    def calculate_risk_score(
        self,
        requirement: Requirement,
        upstream_nodes: List[ImpactNode],
        downstream_nodes: List[ImpactNode],
        affected_test_cases: List[int],
        config: ImpactAnalysisConfig
    ) -> RiskScore:
        """
        Calculate risk score based on impact analysis results.

        Formula:
        Risk Score = weighted sum of normalized factors
        """
        all_nodes = upstream_nodes + downstream_nodes
        stats = self._calculate_stats(requirement, upstream_nodes, downstream_nodes)

        # Calculate individual factors (normalized to 0-100)
        factors = {}

        # Depth factor (0-100)
        max_depth = stats["max_depth"]
        factors["depth"] = min((max_depth / 10) * 100, 100)

        # Breadth factor (0-100)
        total_affected = len(all_nodes)
        factors["breadth"] = min((total_affected / 20) * 100, 100)

        # Critical priority factor (0-100)
        critical_count = stats["critical_count"]
        factors["critical"] = min((critical_count / 5) * 100, 100)

        # Test case factor (0-100)
        test_count = len(affected_test_cases)
        factors["test"] = min((test_count / 30) * 100, 100)

        # Regulatory factor (0-100)
        regulatory_count = sum(1 for node in all_nodes if node.regulatory)
        if requirement.regulatory_document:
            regulatory_count += 1
        factors["regulatory"] = min((regulatory_count / 5) * 100, 100)

        # History factor (0-100) - placeholder for now
        # TODO: Implement change frequency tracking
        factors["history"] = 0.0

        # Calculate weighted score
        weights = config.weights
        score = (
            weights["depth"] * factors["depth"] +
            weights["breadth"] * factors["breadth"] +
            weights["critical"] * factors["critical"] +
            weights["test"] * factors["test"] +
            weights["regulatory"] * factors["regulatory"] +
            weights["history"] * factors["history"]
        )

        # Determine risk level
        if score >= 81:
            level = "CRITICAL"
        elif score >= 61:
            level = "HIGH"
        elif score >= 31:
            level = "MEDIUM"
        else:
            level = "LOW"

        # Generate explanation
        explanation_parts = []
        if level in ["CRITICAL", "HIGH"]:
            if critical_count > 0:
                explanation_parts.append(f"{critical_count} critical priority requirements affected")
            if total_affected >= 15:
                explanation_parts.append(f"{total_affected} total requirements impacted")
            if test_count >= 20:
                explanation_parts.append(f"{test_count} test cases require re-execution")
            if regulatory_count > 0:
                explanation_parts.append(f"regulatory compliance verification needed")
        else:
            explanation_parts.append(f"Limited impact: {total_affected} requirements affected")

        explanation = f"{level.capitalize()} risk due to " + ", ".join(explanation_parts) if explanation_parts else f"{level} risk"

        return RiskScore(
            score=score,
            level=level,
            factors={k: round(v * weights.get(k, 0), 2) for k, v in factors.items()},
            explanation=explanation
        )

    def _identify_regulatory_implications(
        self,
        requirement: Requirement,
        upstream_nodes: List[ImpactNode],
        downstream_nodes: List[ImpactNode]
    ) -> List[str]:
        """Identify regulatory compliance implications"""
        implications = []
        regulatory_docs = set()

        # Check requirement itself
        if requirement.regulatory_document:
            regulatory_docs.add(requirement.regulatory_document)

        # Check all affected requirements
        for node in upstream_nodes + downstream_nodes:
            if node.regulatory and node.regulatory_document:
                regulatory_docs.add(node.regulatory_document)

        # Generate implications
        for doc in regulatory_docs:
            if "14 CFR" in doc or "FAA" in doc:
                implications.append(f"{doc} compliance verification required")
            elif "CS-" in doc or "EASA" in doc:
                implications.append(f"{doc} compliance re-assessment needed")
            elif "GCAA" in doc or "UAEMAR" in doc:
                implications.append(f"{doc} compliance review required")
            else:
                implications.append(f"{doc} compliance check required")

        return implications

    def _generate_recommendations(
        self,
        requirement: Requirement,
        upstream_nodes: List[ImpactNode],
        downstream_nodes: List[ImpactNode],
        affected_test_cases: List[int],
        risk_score: RiskScore
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Risk-based recommendations
        if risk_score.level in ["CRITICAL", "HIGH"]:
            recommendations.append("Schedule detailed impact review with engineering team")
            recommendations.append("Obtain management approval before proceeding")

        # Test execution recommendations
        if len(affected_test_cases) > 0:
            test_count = len(affected_test_cases)
            recommendations.append(
                f"Re-execute {test_count} test case{'s' if test_count != 1 else ''} to verify changes"
            )

        # Stakeholder notifications
        categories = set(node.category for node in downstream_nodes if node.category)
        if categories:
            recommendations.append(
                f"Notify teams responsible for: {', '.join(sorted(categories))}"
            )

        # Regulatory recommendations
        if requirement.regulatory_document or any(
            node.regulatory for node in upstream_nodes + downstream_nodes
        ):
            recommendations.append("Update compliance documentation and notify certification authority")

        # Documentation recommendations
        total_affected = len(upstream_nodes) + len(downstream_nodes)
        if total_affected > 10:
            recommendations.append("Document change rationale and impact analysis results")

        return recommendations

    def _estimate_effort(
        self,
        stats: Dict[str, int],
        affected_test_cases: List[int],
        risk_score: RiskScore
    ) -> float:
        """Estimate effort in hours"""
        effort = 0.0

        # Base analysis effort
        effort += 2.0

        # Review effort (0.5 hours per affected requirement)
        effort += stats["total_affected"] * 0.5

        # Test execution effort (1 hour per test case)
        effort += len(affected_test_cases) * 1.0

        # Risk adjustment
        if risk_score.level == "CRITICAL":
            effort *= 1.5
        elif risk_score.level == "HIGH":
            effort *= 1.25

        return round(effort, 1)
