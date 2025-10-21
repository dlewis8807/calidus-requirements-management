"""
Intelligent Reasoning Agent for Test Failure Analysis
Rule-based system with pattern matching and domain knowledge
No LLM required - pure deterministic reasoning
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path


class FailureType(Enum):
    """Classification of test failure types"""
    ASSERTION_ERROR = "assertion_error"
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    BOUNDARY_VIOLATION = "boundary_violation"
    CONCURRENCY_ERROR = "concurrency_error"
    INTEGRATION_ERROR = "integration_error"
    DATA_ERROR = "data_error"
    CONFIGURATION_ERROR = "configuration_error"
    REGULATORY_VIOLATION = "regulatory_violation"


@dataclass
class RootCause:
    """Root cause hypothesis with evidence"""
    cause: str
    likelihood: float  # 0.0 to 1.0
    evidence: List[str]
    affected_components: List[str]
    regulatory_impact: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Suggestion:
    """Actionable suggestion for remediation"""
    priority: int
    action: str
    details: str
    code_locations: List[str]
    verification_steps: List[str]
    estimated_effort_hours: float

    def to_dict(self):
        return asdict(self)


@dataclass
class SuggestionReport:
    """Complete analysis report"""
    test_case_id: int
    failure_type: str
    root_causes: List[RootCause]
    suggestions: List[Suggestion]
    similar_failures: List[Dict]
    confidence_score: float

    def to_dict(self):
        return {
            "test_case_id": self.test_case_id,
            "failure_type": self.failure_type,
            "root_causes": [rc.to_dict() for rc in self.root_causes],
            "suggestions": [s.to_dict() for s in self.suggestions],
            "similar_failures": self.similar_failures,
            "confidence_score": self.confidence_score
        }


class ReasoningAgent:
    """Rule-based intelligent agent for test failure analysis"""

    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.aerospace_rules = self._load_aerospace_rules()

    def _load_knowledge_base(self) -> Dict:
        """Load pattern matching rules from JSON"""
        kb_path = Path(__file__).parent.parent / "knowledge" / "failure_patterns.json"
        if kb_path.exists():
            with open(kb_path, 'r') as f:
                return json.load(f)
        return {"patterns": []}

    def _load_aerospace_rules(self) -> Dict:
        """Load aerospace-specific domain rules"""
        rules_path = Path(__file__).parent.parent / "knowledge" / "aerospace_rules.json"
        if rules_path.exists():
            with open(rules_path, 'r') as f:
                return json.load(f)
        return {"rules": []}

    def analyze_failure(self, test_case, execution_log: str) -> SuggestionReport:
        """Main entry point for failure analysis"""

        # Extract failure information
        failure_info = self._extract_failure_info(test_case, execution_log)

        # Classify failure type
        failure_type = self._classify_failure(failure_info)

        # Match against patterns
        matched_patterns = self._match_patterns(failure_info, failure_type)

        # Generate root causes
        root_causes = self._generate_root_causes(
            failure_info,
            matched_patterns,
            test_case
        )

        # Create suggestions
        suggestions = self._generate_suggestions(
            root_causes,
            matched_patterns,
            test_case
        )

        # Find similar failures
        similar_failures = self._find_similar_failures(test_case, failure_info)

        # Calculate confidence
        confidence = self._calculate_confidence(matched_patterns, root_causes)

        return SuggestionReport(
            test_case_id=test_case.id,
            failure_type=failure_type.value,
            root_causes=root_causes,
            suggestions=suggestions,
            similar_failures=similar_failures,
            confidence_score=confidence
        )

    def _extract_failure_info(self, test_case, execution_log: str) -> Dict:
        """Extract structured information from failure"""
        return {
            "test_id": test_case.test_case_id,
            "test_title": test_case.title,
            "test_type": test_case.test_type,
            "priority": test_case.priority,
            "requirement_type": test_case.requirement.type if test_case.requirement else None,
            "requirement_category": test_case.requirement.category if test_case.requirement else None,
            "execution_log": execution_log,
            "error_message": self._extract_error_message(execution_log),
            "stack_trace": self._extract_stack_trace(execution_log),
            "keywords": self._extract_keywords(execution_log)
        }

    def _extract_error_message(self, log: str) -> str:
        """Extract primary error message"""
        # Look for common error patterns
        patterns = [
            r"Error:\s*(.+?)(?:\n|$)",
            r"Failed:\s*(.+?)(?:\n|$)",
            r"AssertionError:\s*(.+?)(?:\n|$)",
            r"Exception:\s*(.+?)(?:\n|$)"
        ]

        for pattern in patterns:
            match = re.search(pattern, log, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Fallback: first line of log
        return log.split('\n')[0][:200]

    def _extract_stack_trace(self, log: str) -> List[str]:
        """Extract stack trace lines"""
        lines = log.split('\n')
        stack_lines = []
        in_stack = False

        for line in lines:
            if 'Traceback' in line or 'at ' in line:
                in_stack = True
            if in_stack:
                stack_lines.append(line.strip())

        return stack_lines[:10]  # Limit to 10 lines

    def _extract_keywords(self, log: str) -> List[str]:
        """Extract important keywords from log"""
        keywords = set()
        keyword_patterns = [
            r'\b(weight|fuel|passenger|cargo|balance)\b',
            r'\b(altitude|airspeed|velocity|acceleration)\b',
            r'\b(temperature|pressure|density)\b',
            r'\b(exceeded|invalid|failed|error|timeout)\b',
            r'\b(sensor|actuator|control|system)\b',
            r'\b(\d+\.\d+|\d+)\s*(lbs|kg|ft|m|kts|mph)\b'
        ]

        for pattern in keyword_patterns:
            matches = re.finditer(pattern, log, re.IGNORECASE)
            for match in matches:
                keywords.add(match.group(0).lower())

        return list(keywords)

    def _classify_failure(self, failure_info: Dict) -> FailureType:
        """Classify failure type based on patterns"""
        log = failure_info['execution_log'].lower()
        error = failure_info['error_message'].lower()

        # Classification rules
        if 'timeout' in error or 'timed out' in log:
            return FailureType.TIMEOUT

        if 'assertionerror' in error or 'expected' in error:
            return FailureType.ASSERTION_ERROR

        if 'boundary' in error or 'exceeds' in error or 'limit' in error:
            return FailureType.BOUNDARY_VIOLATION

        if 'race condition' in log or 'deadlock' in log:
            return FailureType.CONCURRENCY_ERROR

        if 'connection' in error or 'network' in error or 'api' in error:
            return FailureType.INTEGRATION_ERROR

        if 'invalid data' in error or 'parse' in error:
            return FailureType.DATA_ERROR

        if 'configuration' in error or 'environment' in error:
            return FailureType.CONFIGURATION_ERROR

        if 'cfr' in log or 'regulation' in log or 'compliance' in log:
            return FailureType.REGULATORY_VIOLATION

        # Default
        return FailureType.EXCEPTION

    def _match_patterns(self, failure_info: Dict, failure_type: FailureType) -> List[Dict]:
        """Match failure against known patterns"""
        matched = []

        for pattern in self.knowledge_base.get("patterns", []):
            score = self._calculate_pattern_match_score(failure_info, pattern)
            if score > 0.5:  # Threshold for match
                matched.append({
                    "pattern": pattern,
                    "score": score
                })

        # Sort by score
        matched.sort(key=lambda x: x['score'], reverse=True)
        return matched[:3]  # Top 3 matches

    def _calculate_pattern_match_score(self, failure_info: Dict, pattern: Dict) -> float:
        """Calculate how well a pattern matches the failure"""
        score = 0.0
        weights = {
            "regex": 0.4,
            "keywords": 0.3,
            "requirement_type": 0.2,
            "category": 0.1
        }

        # Check regex patterns
        for regex in pattern.get("failure_patterns", []):
            if re.search(regex, failure_info['execution_log'], re.IGNORECASE):
                score += weights["regex"]
                break

        # Check keyword overlap
        pattern_keywords = set(pattern.get("keywords", []))
        failure_keywords = set(failure_info['keywords'])
        keyword_overlap = len(pattern_keywords & failure_keywords)
        if len(pattern_keywords) > 0:
            score += weights["keywords"] * (keyword_overlap / len(pattern_keywords))

        # Check requirement type match
        if failure_info['requirement_type'] in pattern.get("requirement_types", []):
            score += weights["requirement_type"]

        # Check category match
        if failure_info['requirement_category'] == pattern.get("category"):
            score += weights["category"]

        return score

    def _generate_root_causes(
        self,
        failure_info: Dict,
        matched_patterns: List[Dict],
        test_case
    ) -> List[RootCause]:
        """Generate root cause hypotheses"""
        root_causes = []

        # From matched patterns
        for match in matched_patterns:
            pattern = match["pattern"]
            for cause_data in pattern.get("root_causes", []):
                # Check if evidence keywords are present
                evidence_score = self._check_evidence(
                    failure_info,
                    cause_data.get("indicators", [])
                )

                if evidence_score > 0.3:
                    root_causes.append(RootCause(
                        cause=cause_data["cause"],
                        likelihood=cause_data["likelihood"] * evidence_score,
                        evidence=self._build_evidence_list(failure_info, cause_data),
                        affected_components=cause_data.get("affected_components", []),
                        regulatory_impact=cause_data.get("regulatory_impact")
                    ))

        # Add generic causes if no patterns matched
        if not root_causes:
            root_causes = self._generate_generic_causes(failure_info)

        # Sort by likelihood
        root_causes.sort(key=lambda x: x.likelihood, reverse=True)
        return root_causes[:5]  # Top 5

    def _check_evidence(self, failure_info: Dict, indicators: List[str]) -> float:
        """Check how much evidence supports this cause"""
        if not indicators:
            return 0.5  # Neutral if no indicators

        keywords = failure_info['keywords']
        log = failure_info['execution_log'].lower()

        matches = 0
        for indicator in indicators:
            if indicator.lower() in keywords or indicator.lower() in log:
                matches += 1

        return matches / len(indicators) if indicators else 0.0

    def _build_evidence_list(self, failure_info: Dict, cause_data: Dict) -> List[str]:
        """Build evidence list for root cause"""
        evidence = []

        # Error message
        if failure_info['error_message']:
            evidence.append(f"Error message: {failure_info['error_message'][:100]}")

        # Matching indicators
        for indicator in cause_data.get("indicators", []):
            if indicator.lower() in failure_info['execution_log'].lower():
                evidence.append(f"Log contains keyword: '{indicator}'")

        return evidence[:5]  # Top 5 pieces of evidence

    def _generate_generic_causes(self, failure_info: Dict) -> List[RootCause]:
        """Generate generic root causes when no patterns match"""
        return [
            RootCause(
                cause="Test data may not match expected format or range",
                likelihood=0.6,
                evidence=["No specific pattern matched"],
                affected_components=["Test Data Module"]
            ),
            RootCause(
                cause="Environment configuration may differ from test assumptions",
                likelihood=0.5,
                evidence=["Generic failure pattern"],
                affected_components=["Test Environment"]
            )
        ]

    def _generate_suggestions(
        self,
        root_causes: List[RootCause],
        matched_patterns: List[Dict],
        test_case
    ) -> List[Suggestion]:
        """Generate actionable suggestions"""
        suggestions = []

        # From matched patterns
        for match in matched_patterns:
            pattern = match["pattern"]
            for sug_data in pattern.get("suggestions", []):
                suggestions.append(Suggestion(
                    priority=sug_data["priority"],
                    action=sug_data["action"],
                    details=sug_data["details"],
                    code_locations=sug_data.get("code_locations", []),
                    verification_steps=sug_data.get("verification_steps", []),
                    estimated_effort_hours=sug_data.get("estimated_effort_hours", 2.0)
                ))

        # Add generic suggestions
        if not suggestions:
            suggestions = self._generate_generic_suggestions(root_causes, test_case)

        # Sort by priority
        suggestions.sort(key=lambda x: x.priority)
        return suggestions[:5]  # Top 5

    def _generate_generic_suggestions(
        self,
        root_causes: List[RootCause],
        test_case
    ) -> List[Suggestion]:
        """Generate generic suggestions"""
        suggestions = []

        if root_causes:
            top_cause = root_causes[0]
            suggestions.append(Suggestion(
                priority=1,
                action=f"Investigate: {top_cause.cause}",
                details=f"Review components: {', '.join(top_cause.affected_components)}",
                code_locations=[],
                verification_steps=[
                    "Review test execution logs in detail",
                    "Check test data validity",
                    "Verify environment configuration"
                ],
                estimated_effort_hours=3.0
            ))

        suggestions.append(Suggestion(
            priority=2,
            action="Review test case specification",
            details="Verify that test case correctly implements requirement",
            code_locations=[],
            verification_steps=[
                "Compare test steps with requirement specification",
                "Check pass/fail criteria alignment"
            ],
            estimated_effort_hours=1.0
        ))

        return suggestions

    def _find_similar_failures(self, test_case, failure_info: Dict) -> List[Dict]:
        """Find similar historical failures from database"""
        # This would query the database for similar test failures
        # For now, return empty list (to be implemented with DB integration)
        return []

    def _calculate_confidence(
        self,
        matched_patterns: List[Dict],
        root_causes: List[RootCause]
    ) -> float:
        """Calculate overall confidence in analysis"""
        if not matched_patterns:
            return 0.4  # Low confidence with no pattern matches

        # Average of top pattern scores and top root cause likelihood
        pattern_score = sum(m['score'] for m in matched_patterns[:2]) / min(2, len(matched_patterns))
        cause_score = root_causes[0].likelihood if root_causes else 0.5

        return (pattern_score + cause_score) / 2
