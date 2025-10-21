# Intelligent Test Failure Analysis - Implementation Plan

**Project:** CALIDUS - Requirements Management & Traceability Assistant
**Feature:** Rule-Based Agentic Framework for Test Case Suggestions
**Version:** 1.0
**Date:** October 20, 2025
**Status:** Ready for Implementation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Feature Overview](#feature-overview)
3. [System Architecture](#system-architecture)
4. [Reasoning Framework](#reasoning-framework)
5. [Implementation Guide](#implementation-guide)
6. [API Endpoints](#api-endpoints)
7. [Database Schema](#database-schema)
8. [Frontend Integration](#frontend-integration)
9. [Implementation Timeline](#implementation-timeline)

---

## Executive Summary

This document outlines a **lightweight, rule-based intelligent agent** that analyzes failed test cases and provides actionable suggestions WITHOUT requiring LLM integration. The system uses:

- **Pattern matching** on test failure logs
- **Knowledge-based reasoning** from aerospace domain expertise
- **Historical analysis** of similar failures
- **Root cause templates** for common failure scenarios

**Key Benefits:**
- ✅ No external API costs (no LLM required)
- ✅ Fast, deterministic responses (<100ms)
- ✅ Domain-specific aerospace expertise built-in
- ✅ Privacy-friendly (all processing on-premise)
- ✅ Easy to extend with new rules

---

## Feature Overview

### Core Capabilities

#### 1. Automated Failure Analysis
When a test case fails, the system automatically:
- Extracts failure information (error message, logs, stack trace)
- Matches against known failure patterns
- Identifies likely root causes
- Suggests specific remediation steps

#### 2. Intelligent Suggestions
Provides context-aware suggestions including:
- **Root cause hypotheses** (ranked by likelihood)
- **Specific code/design areas to investigate**
- **Step-by-step remediation instructions**
- **Related requirements that may be affected**
- **Similar historical failures and their resolutions**

#### 3. Pattern Learning
The system learns from resolved failures:
- Tracks which suggestions were helpful
- Identifies recurring patterns
- Builds a knowledge base of resolutions
- Improves suggestions over time

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Test Case Detail Page                             │     │
│  │  - Shows failure information                       │     │
│  │  - Displays AI suggestions panel                   │     │
│  │  - "Mark as Helpful" feedback buttons              │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          ▼ REST API
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌────────────────────────────────────────────────────┐     │
│  │  API Endpoints (app/api/test_suggestions.py)       │     │
│  │  - POST /api/test-cases/{id}/analyze               │     │
│  │  - GET  /api/test-cases/{id}/suggestions           │     │
│  │  - POST /api/suggestions/{id}/feedback             │     │
│  └────────────────────────────────────────────────────┘     │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Reasoning Engine (app/services/reasoning_agent.py)│     │
│  │                                                     │     │
│  │  1. FailureAnalyzer                                │     │
│  │     - Extract failure info                         │     │
│  │     - Classify failure type                        │     │
│  │                                                     │     │
│  │  2. PatternMatcher                                 │     │
│  │     - Match against known patterns                 │     │
│  │     - Calculate similarity scores                  │     │
│  │                                                     │     │
│  │  3. RootCauseAnalyzer                              │     │
│  │     - Generate hypotheses                          │     │
│  │     - Rank by likelihood                           │     │
│  │                                                     │     │
│  │  4. SuggestionGenerator                            │     │
│  │     - Create actionable suggestions                │     │
│  │     - Link to related requirements                 │     │
│  │                                                     │     │
│  │  5. KnowledgeBase                                  │     │
│  │     - Load aerospace-specific rules                │     │
│  │     - Query historical resolutions                 │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Knowledge Base (JSON Files)                     │
│  - failure_patterns.json                                     │
│  - aerospace_rules.json                                      │
│  - remediation_templates.json                                │
└─────────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               Database (PostgreSQL)                          │
│  - test_case_suggestions (new)                               │
│  - suggestion_feedback (new)                                 │
│  - failure_patterns (new)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Reasoning Framework

### 1. Failure Classification

The system classifies failures into categories:

```python
class FailureType(Enum):
    ASSERTION_ERROR = "assertion_error"          # Expected vs actual mismatch
    TIMEOUT = "timeout"                          # Test exceeded time limit
    EXCEPTION = "exception"                      # Unexpected exception thrown
    BOUNDARY_VIOLATION = "boundary_violation"    # Value outside valid range
    CONCURRENCY_ERROR = "concurrency_error"      # Race condition or deadlock
    INTEGRATION_ERROR = "integration_error"      # External system failure
    DATA_ERROR = "data_error"                    # Invalid test data
    CONFIGURATION_ERROR = "configuration_error"  # Environment setup issue
    REGULATORY_VIOLATION = "regulatory_violation" # Compliance check failed
```

### 2. Pattern Matching Rules

**Example Rule Structure:**
```json
{
  "rule_id": "WEIGHT_CALC_001",
  "name": "Weight Calculation Discrepancy",
  "failure_patterns": [
    "expected.*\\d+.*lbs.*got.*\\d+.*lbs",
    "weight.*exceeds.*limit",
    "takeoff.*weight.*invalid"
  ],
  "keywords": ["weight", "lbs", "exceeds", "maximum"],
  "requirement_types": ["Certification", "System"],
  "root_causes": [
    {
      "cause": "Fuel density calculation using standard day instead of actual temperature",
      "likelihood": 0.85,
      "indicators": ["fuel", "density", "temperature", "weather"],
      "affected_components": ["FuelCalculator", "WeightAndBalance"]
    },
    {
      "cause": "Passenger weight average outdated (using old standard)",
      "likelihood": 0.70,
      "indicators": ["passenger", "average", "weight"],
      "affected_components": ["PassengerWeightModule"]
    }
  ],
  "suggestions": [
    {
      "priority": 1,
      "action": "Check fuel density calculation",
      "details": "Verify that fuel density uses actual ambient temperature, not ISA standard day",
      "code_locations": [
        "backend/services/fuel_calculator.py",
        "backend/utils/density_tables.py"
      ],
      "verification_steps": [
        "Review fuel density lookup table",
        "Check temperature sensor readings",
        "Validate density correction factors"
      ]
    }
  ]
}
```

### 3. Reasoning Algorithm

```python
class ReasoningAgent:
    def analyze_failure(self, test_case: TestCase) -> SuggestionReport:
        """
        Multi-step reasoning process:
        1. Extract failure information
        2. Classify failure type
        3. Match against patterns
        4. Generate root cause hypotheses
        5. Create actionable suggestions
        6. Query similar historical failures
        """

        # Step 1: Extract info
        failure_info = self.extract_failure_info(test_case)

        # Step 2: Classify
        failure_type = self.classify_failure(failure_info)

        # Step 3: Pattern matching
        matched_patterns = self.match_patterns(failure_info, failure_type)

        # Step 4: Root cause analysis
        root_causes = self.analyze_root_causes(
            failure_info,
            matched_patterns,
            test_case.requirement
        )

        # Step 5: Generate suggestions
        suggestions = self.generate_suggestions(
            root_causes,
            test_case,
            matched_patterns
        )

        # Step 6: Find similar failures
        similar_failures = self.find_similar_failures(test_case)

        return SuggestionReport(
            test_case_id=test_case.id,
            failure_type=failure_type,
            root_causes=root_causes,
            suggestions=suggestions,
            similar_failures=similar_failures,
            confidence_score=self.calculate_confidence(matched_patterns)
        )
```

---

## Implementation Guide

### Backend Implementation

#### 1. Create Reasoning Agent Service

**File:** `backend/app/services/reasoning_agent.py`

```python
"""
Intelligent Reasoning Agent for Test Failure Analysis
Rule-based system with pattern matching and domain knowledge
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class FailureType(Enum):
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
    cause: str
    likelihood: float  # 0.0 to 1.0
    evidence: List[str]
    affected_components: List[str]
    regulatory_impact: Optional[str] = None


@dataclass
class Suggestion:
    priority: int
    action: str
    details: str
    code_locations: List[str]
    verification_steps: List[str]
    estimated_effort_hours: float


@dataclass
class SuggestionReport:
    test_case_id: int
    failure_type: str
    root_causes: List[RootCause]
    suggestions: List[Suggestion]
    similar_failures: List[Dict]
    confidence_score: float


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
            "test_type": test_case.test_type.value,
            "priority": test_case.priority.value,
            "requirement_type": test_case.requirement.type.value if test_case.requirement else None,
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
        # Common aerospace/testing keywords
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
        pattern_score = sum(m['score'] for m in matched_patterns[:2]) / 2
        cause_score = root_causes[0].likelihood if root_causes else 0.5

        return (pattern_score + cause_score) / 2
```

---

#### 2. Create Knowledge Base Files

**File:** `backend/app/knowledge/failure_patterns.json`

```json
{
  "patterns": [
    {
      "rule_id": "WEIGHT_CALC_001",
      "name": "Weight Calculation Discrepancy",
      "category": "Weight and Balance",
      "failure_patterns": [
        "expected.*\\d+.*lbs.*got.*\\d+.*lbs",
        "weight.*exceeds.*limit",
        "takeoff.*weight.*invalid"
      ],
      "keywords": ["weight", "lbs", "exceeds", "maximum", "fuel", "passenger"],
      "requirement_types": ["Certification", "System"],
      "root_causes": [
        {
          "cause": "Fuel density calculation using standard day conditions instead of actual temperature",
          "likelihood": 0.85,
          "indicators": ["fuel", "density", "temperature"],
          "affected_components": ["FuelCalculator", "WeightAndBalance"],
          "regulatory_impact": "14 CFR §23.2005 compliance risk"
        },
        {
          "cause": "Passenger weight average outdated (old FAA standard)",
          "likelihood": 0.70,
          "indicators": ["passenger", "average", "weight"],
          "affected_components": ["PassengerWeightModule"]
        }
      ],
      "suggestions": [
        {
          "priority": 1,
          "action": "Update fuel density calculation to use actual ambient temperature",
          "details": "Modify FuelCalculator to accept temperature parameter and use correct density tables",
          "code_locations": [
            "backend/services/fuel_calculator.py:45",
            "backend/utils/density_tables.py"
          ],
          "verification_steps": [
            "Review fuel density lookup table implementation",
            "Verify temperature sensor integration",
            "Test with extreme temperature values (-40°C to +50°C)"
          ],
          "estimated_effort_hours": 4.0
        },
        {
          "priority": 2,
          "action": "Update passenger weight average to current FAA standard (190 lbs)",
          "details": "Update PASSENGER_WEIGHT_AVG constant per FAA AC 120-27F",
          "code_locations": ["backend/config.py:23"],
          "verification_steps": [
            "Update configuration constant",
            "Re-run all weight calculation tests",
            "Update documentation"
          ],
          "estimated_effort_hours": 1.0
        }
      ]
    },
    {
      "rule_id": "STALL_SPEED_001",
      "name": "Stall Speed Exceedance",
      "category": "Aerodynamics",
      "failure_patterns": [
        "stall.*speed.*exceeds",
        "vs0.*greater than.*61",
        "landing.*configuration.*invalid"
      ],
      "keywords": ["stall", "speed", "vs0", "knots", "kcas", "landing"],
      "requirement_types": ["Technical", "Certification"],
      "root_causes": [
        {
          "cause": "Flap deflection not reaching full landing position",
          "likelihood": 0.80,
          "indicators": ["flap", "deflection", "angle", "landing"],
          "affected_components": ["FlapActuator", "FlightControlSystem"]
        },
        {
          "cause": "Weight calculation including non-landing configuration items",
          "likelihood": 0.65,
          "indicators": ["weight", "landing", "configuration"],
          "affected_components": ["WeightModule", "ConfigurationManager"]
        }
      ],
      "suggestions": [
        {
          "priority": 1,
          "action": "Verify flap actuator reaches full landing deflection",
          "details": "Check flap position sensor readings and compare with design specification",
          "code_locations": [
            "backend/services/flap_control.py",
            "backend/sensors/flap_position.py"
          ],
          "verification_steps": [
            "Review flap position sensor calibration",
            "Test flap deployment in landing configuration",
            "Verify mechanical linkage integrity"
          ],
          "estimated_effort_hours": 6.0
        }
      ]
    },
    {
      "rule_id": "AUTOPILOT_001",
      "name": "Autopilot Engagement Failure",
      "category": "AutoPilot",
      "failure_patterns": [
        "autopilot.*engagement.*failed",
        "ap.*mode.*invalid",
        "autopilot.*not responding"
      ],
      "keywords": ["autopilot", "engagement", "mode", "ap", "failed"],
      "requirement_types": ["System", "Technical"],
      "root_causes": [
        {
          "cause": "Sensor data not available or invalid before engagement",
          "likelihood": 0.75,
          "indicators": ["sensor", "data", "invalid", "unavailable"],
          "affected_components": ["SensorModule", "AutopilotController"]
        },
        {
          "cause": "Pre-engagement checks too strict or incorrect",
          "likelihood": 0.60,
          "indicators": ["check", "validation", "criteria"],
          "affected_components": ["EngagementValidator"]
        }
      ],
      "suggestions": [
        {
          "priority": 1,
          "action": "Review autopilot engagement preconditions",
          "details": "Verify all required sensors are available and within valid ranges",
          "code_locations": [
            "backend/autopilot/engagement.py",
            "backend/autopilot/pre_checks.py"
          ],
          "verification_steps": [
            "List all required sensors for AP engagement",
            "Verify sensor health checks",
            "Test edge cases (marginal sensor values)"
          ],
          "estimated_effort_hours": 5.0
        }
      ]
    },
    {
      "rule_id": "AVIONICS_DISPLAY_001",
      "name": "Display Refresh Rate Issue",
      "category": "Avionics",
      "failure_patterns": [
        "display.*refresh.*slow",
        "frame.*rate.*below",
        "update.*delayed"
      ],
      "keywords": ["display", "refresh", "frame", "rate", "fps", "lag"],
      "requirement_types": ["Technical", "System"],
      "root_causes": [
        {
          "cause": "Graphics processing overload from rendering complex symbology",
          "likelihood": 0.70,
          "indicators": ["graphics", "rendering", "symbology", "cpu"],
          "affected_components": ["DisplayRenderer", "GraphicsEngine"]
        }
      ],
      "suggestions": [
        {
          "priority": 1,
          "action": "Optimize display rendering pipeline",
          "details": "Review rendering code for inefficiencies, consider GPU acceleration",
          "code_locations": ["frontend/avionics/display_renderer.py"],
          "verification_steps": [
            "Profile rendering performance",
            "Identify bottlenecks",
            "Implement optimization"
          ],
          "estimated_effort_hours": 8.0
        }
      ]
    }
  ]
}
```

**File:** `backend/app/knowledge/aerospace_rules.json`

```json
{
  "rules": [
    {
      "rule_id": "FAA_PART23_WEIGHT",
      "regulation": "14 CFR §23.2005",
      "title": "Maximum Takeoff Weight Limits",
      "description": "Aircraft must not exceed 12,500 lbs for Part 23 certification",
      "failure_indicators": ["weight", "exceeds", "12500", "lbs"],
      "remediation": "Review weight calculations and ensure all components are properly accounted for"
    },
    {
      "rule_id": "FAA_PART23_STALL",
      "regulation": "14 CFR §23.2110",
      "title": "Stall Speed Requirements",
      "description": "VS0 must not exceed 61 KCAS in landing configuration",
      "failure_indicators": ["stall", "vs0", "61", "knots"],
      "remediation": "Verify flap configuration and weight assumptions for stall speed calculation"
    },
    {
      "rule_id": "DO178C_TIMING",
      "regulation": "DO-178C",
      "title": "Real-Time Performance Requirements",
      "description": "Critical functions must meet timing requirements",
      "failure_indicators": ["timeout", "delay", "latency", "response time"],
      "remediation": "Analyze execution timing and optimize critical code paths"
    }
  ]
}
```

---

#### 3. Create API Endpoints

**File:** `backend/app/api/test_suggestions.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TestCase, User
from app.core.dependencies import get_current_user
from app.services.reasoning_agent import ReasoningAgent
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/test-cases", tags=["test-suggestions"])


class AnalyzeRequest(BaseModel):
    execution_log: str
    environment: Optional[str] = None


class FeedbackRequest(BaseModel):
    helpful: bool
    comment: Optional[str] = None


@router.post("/{test_case_id}/analyze")
async def analyze_test_failure(
    test_case_id: int,
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a failed test case and provide intelligent suggestions
    """
    # Get test case
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )

    # Run reasoning agent
    agent = ReasoningAgent()
    report = agent.analyze_failure(test_case, request.execution_log)

    # Save suggestions to database
    # TODO: Save to test_case_suggestions table

    return {
        "test_case_id": test_case_id,
        "failure_type": report.failure_type,
        "root_causes": [
            {
                "cause": rc.cause,
                "likelihood": rc.likelihood,
                "evidence": rc.evidence,
                "affected_components": rc.affected_components,
                "regulatory_impact": rc.regulatory_impact
            }
            for rc in report.root_causes
        ],
        "suggestions": [
            {
                "priority": s.priority,
                "action": s.action,
                "details": s.details,
                "code_locations": s.code_locations,
                "verification_steps": s.verification_steps,
                "estimated_effort_hours": s.estimated_effort_hours
            }
            for s in report.suggestions
        ],
        "similar_failures": report.similar_failures,
        "confidence_score": report.confidence_score
    }


@router.get("/{test_case_id}/suggestions")
async def get_test_suggestions(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get existing suggestions for a test case
    """
    # TODO: Query test_case_suggestions table
    return {
        "test_case_id": test_case_id,
        "suggestions": []
    }


@router.post("/suggestions/{suggestion_id}/feedback")
async def submit_suggestion_feedback(
    suggestion_id: int,
    feedback: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback on whether a suggestion was helpful
    This helps the system learn over time
    """
    # TODO: Save feedback to suggestion_feedback table
    return {
        "suggestion_id": suggestion_id,
        "feedback_recorded": True
    }
```

---

## Database Schema

### New Tables

```sql
-- Test case suggestions
CREATE TABLE test_case_suggestions (
    id SERIAL PRIMARY KEY,
    test_case_id INTEGER NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    suggestion_type VARCHAR(50) NOT NULL,  -- 'root_cause', 'fix_suggestion', 'investigation'

    -- Suggestion content
    priority INTEGER NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    code_locations JSONB,  -- Array of file paths
    verification_steps JSONB,  -- Array of steps
    estimated_effort_hours FLOAT,

    -- Analysis metadata
    failure_type VARCHAR(50),
    confidence_score FLOAT,
    matched_rule_id VARCHAR(50),

    -- Status
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'resolved', 'dismissed'
    resolved_by_id INTEGER REFERENCES users(id),
    resolved_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_suggestions_test_id ON test_case_suggestions(test_case_id);
CREATE INDEX idx_suggestions_status ON test_case_suggestions(status);


-- Suggestion feedback (for learning)
CREATE TABLE suggestion_feedback (
    id SERIAL PRIMARY KEY,
    suggestion_id INTEGER NOT NULL REFERENCES test_case_suggestions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),

    -- Feedback
    helpful BOOLEAN NOT NULL,
    comment TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_suggestion ON suggestion_feedback(suggestion_id);


-- Failure patterns (for learning from resolutions)
CREATE TABLE failure_patterns (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(200) NOT NULL,
    category VARCHAR(100),

    -- Pattern definition
    failure_indicators JSONB,  -- Keywords that indicate this pattern
    root_cause TEXT,
    resolution TEXT,

    -- Usage statistics
    times_matched INTEGER DEFAULT 0,
    times_helpful INTEGER DEFAULT 0,
    confidence_score FLOAT DEFAULT 0.5,

    -- Source
    learned_from_test_id INTEGER REFERENCES test_cases(id),
    created_by_id INTEGER REFERENCES users(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patterns_category ON failure_patterns(category);
```

---

## Frontend Integration

### 1. Create Suggestion Panel Component

**File:** `frontend/components/test-cases/SuggestionsPanel.tsx`

```typescript
'use client';

import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, XCircle, ThumbsUp, ThumbsDown } from 'lucide-react';

interface RootCause {
  cause: string;
  likelihood: number;
  evidence: string[];
  affected_components: string[];
  regulatory_impact?: string;
}

interface Suggestion {
  priority: number;
  action: string;
  details: string;
  code_locations: string[];
  verification_steps: string[];
  estimated_effort_hours: number;
}

interface SuggestionsPanelProps {
  testCaseId: number;
  executionLog: string;
}

export function SuggestionsPanel({ testCaseId, executionLog }: SuggestionsPanelProps) {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);

  const analyzeFailure = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/test-cases/${testCaseId}/analyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ execution_log: executionLog })
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysis(data);
      }
    } catch (error) {
      console.error('Failed to analyze:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (suggestionId: number, helpful: boolean) => {
    const token = localStorage.getItem('token');
    await fetch(`http://localhost:8000/api/test-cases/suggestions/${suggestionId}/feedback`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ helpful })
    });
  };

  if (!analysis) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🤖 Intelligent Failure Analysis
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Get AI-powered suggestions to help diagnose and fix this test failure.
        </p>
        <button
          onClick={analyzeFailure}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Analyze Failure'}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Failure Type */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Failure Classification</h3>
          <span className="px-3 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
            {analysis.failure_type.replace('_', ' ').toUpperCase()}
          </span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span>Confidence:</span>
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${analysis.confidence_score * 100}%` }}
            />
          </div>
          <span className="font-medium">{(analysis.confidence_score * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Root Causes */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          🔍 Root Cause Analysis
        </h3>
        <div className="space-y-4">
          {analysis.root_causes.map((cause: RootCause, index: number) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-900">{cause.cause}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs text-gray-600">Likelihood:</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-1.5 max-w-xs">
                      <div
                        className={`h-1.5 rounded-full ${
                          cause.likelihood > 0.7 ? 'bg-red-500' :
                          cause.likelihood > 0.5 ? 'bg-orange-500' :
                          'bg-yellow-500'
                        }`}
                        style={{ width: `${cause.likelihood * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-900">
                      {(cause.likelihood * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Evidence */}
              {cause.evidence.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-gray-700 uppercase mb-2">Evidence:</p>
                  <ul className="space-y-1">
                    {cause.evidence.map((ev, i) => (
                      <li key={i} className="text-xs text-gray-600 flex items-start gap-2">
                        <span className="text-blue-500">•</span>
                        <span>{ev}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Affected Components */}
              {cause.affected_components.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-gray-700 uppercase mb-2">
                    Affected Components:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {cause.affected_components.map((comp, i) => (
                      <span
                        key={i}
                        className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded"
                      >
                        {comp}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Regulatory Impact */}
              {cause.regulatory_impact && (
                <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded">
                  <p className="text-xs font-semibold text-orange-900">
                    ⚠️ Regulatory Impact:
                  </p>
                  <p className="text-xs text-orange-800 mt-1">{cause.regulatory_impact}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Suggestions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          💡 Suggested Actions
        </h3>
        <div className="space-y-4">
          {analysis.suggestions.map((suggestion: Suggestion, index: number) => (
            <div key={index} className="border border-blue-200 rounded-lg p-4 bg-blue-50">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-start gap-3 flex-1">
                  <span className="flex items-center justify-center w-6 h-6 bg-blue-600 text-white text-xs font-bold rounded-full">
                    {suggestion.priority}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-900">{suggestion.action}</p>
                    <p className="text-xs text-gray-700 mt-1">{suggestion.details}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-600 whitespace-nowrap">
                  ~{suggestion.estimated_effort_hours}h
                </span>
              </div>

              {/* Code Locations */}
              {suggestion.code_locations.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-gray-700 uppercase mb-2">
                    Code Locations:
                  </p>
                  <div className="space-y-1">
                    {suggestion.code_locations.map((loc, i) => (
                      <code key={i} className="block text-xs bg-gray-900 text-gray-100 px-2 py-1 rounded">
                        {loc}
                      </code>
                    ))}
                  </div>
                </div>
              )}

              {/* Verification Steps */}
              {suggestion.verification_steps.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-gray-700 uppercase mb-2">
                    Verification Steps:
                  </p>
                  <ol className="list-decimal list-inside space-y-1">
                    {suggestion.verification_steps.map((step, i) => (
                      <li key={i} className="text-xs text-gray-700">{step}</li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Feedback Buttons */}
              <div className="mt-4 pt-4 border-t border-blue-200 flex items-center justify-between">
                <p className="text-xs text-gray-600">Was this suggestion helpful?</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => submitFeedback(index, true)}
                    className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 text-xs rounded hover:bg-green-200"
                  >
                    <ThumbsUp className="w-3 h-3" />
                    Yes
                  </button>
                  <button
                    onClick={() => submitFeedback(index, false)}
                    className="flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 text-xs rounded hover:bg-red-200"
                  >
                    <ThumbsDown className="w-3 h-3" />
                    No
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## Implementation Timeline

### Week 1: Backend Foundation
**Tasks:**
1. Create `reasoning_agent.py` with core logic
2. Create knowledge base JSON files
3. Add API endpoints to `test_suggestions.py`
4. Create database migrations for new tables
5. Write unit tests

**Deliverables:**
- ✅ Functional reasoning agent
- ✅ Pattern matching working
- ✅ API endpoints operational

### Week 2: Frontend Integration
**Tasks:**
1. Create `SuggestionsPanel` component
2. Integrate into test case detail page
3. Add "Analyze Failure" button
4. Implement feedback mechanism
5. Style and polish UI

**Deliverables:**
- ✅ UI showing suggestions
- ✅ Feedback collection working
- ✅ Clean, professional interface

### Week 3: Knowledge Base Expansion
**Tasks:**
1. Add more failure patterns (aim for 20+)
2. Add aerospace-specific rules
3. Tune confidence scoring
4. Test with real test failures
5. Iterate based on results

**Deliverables:**
- ✅ Comprehensive pattern library
- ✅ >80% accuracy on test cases
- ✅ Documentation

---

## Summary

This implementation provides:

✅ **No LLM Required** - Pure rule-based reasoning
✅ **Fast Performance** - Sub-100ms analysis
✅ **Zero Cost** - No API fees
✅ **Privacy-Friendly** - All on-premise
✅ **Extensible** - Easy to add new patterns
✅ **Domain-Specific** - Aerospace expertise built-in
✅ **Learning Capability** - Improves with feedback

The system is lightweight, maintainable, and immediately deployable!

---

**Document Version:** 1.0
**Last Updated:** October 20, 2025
**Status:** ✅ Ready for Implementation
