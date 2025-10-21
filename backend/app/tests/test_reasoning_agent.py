"""
Unit tests for the intelligent reasoning agent
Tests pattern matching, root cause analysis, and suggestion generation
"""
import pytest
from app.services.reasoning_agent import (
    ReasoningAgent,
    FailureType,
    RootCause,
    Suggestion,
    SuggestionReport
)


class MockTestCase:
    """Mock test case for testing"""
    def __init__(self, test_id, title, test_type, priority, req_type=None, req_category=None):
        self.id = 1
        self.test_case_id = test_id
        self.title = title
        self.test_type = test_type
        self.priority = priority
        self.requirement = MockRequirement(req_type, req_category) if req_type else None


class MockRequirement:
    """Mock requirement for testing"""
    def __init__(self, req_type, category):
        self.type = req_type
        self.category = category


@pytest.fixture
def agent():
    """Create a reasoning agent instance"""
    return ReasoningAgent()


@pytest.fixture
def weight_test_case():
    """Create a mock test case for weight calculation"""
    return MockTestCase(
        test_id="TC-WEIGHT-001",
        title="Verify maximum takeoff weight calculation",
        test_type="System",
        priority="Critical",
        req_type="Certification",
        req_category="Weight and Balance"
    )


@pytest.fixture
def weight_failure_log():
    """Sample failure log for weight calculation"""
    return """
Test failed at step 5: Weight calculation incorrect
Expected: 12,450 lbs
Got: 12,750 lbs
Error: Weight exceeds maximum takeoff weight limit

The test calculated fuel weight at 600 lbs based on standard temperature,
but actual temperature sensor reading shows 95°F which affects fuel density.
Passenger average weight used was 170 lbs per FAA old standard.
"""


class TestFailureClassification:
    """Test failure type classification"""

    def test_classify_assertion_error(self, agent):
        """Test classification of assertion errors"""
        failure_info = {
            'execution_log': "AssertionError: Expected 100 but got 150",
            'error_message': "AssertionError: Expected 100 but got 150",
            'keywords': ['expected', 'got']
        }
        failure_type = agent._classify_failure(failure_info)
        assert failure_type == FailureType.ASSERTION_ERROR

    def test_classify_timeout(self, agent):
        """Test classification of timeout errors"""
        failure_info = {
            'execution_log': "Test execution timed out after 30 seconds",
            'error_message': "Timeout error: exceeded 30s",
            'keywords': ['timeout']
        }
        failure_type = agent._classify_failure(failure_info)
        assert failure_type == FailureType.TIMEOUT

    def test_classify_boundary_violation(self, agent):
        """Test classification of boundary violations"""
        failure_info = {
            'execution_log': "Value exceeds maximum limit of 1000",
            'error_message': "Boundary error: limit exceeded",
            'keywords': ['exceeds', 'limit']
        }
        failure_type = agent._classify_failure(failure_info)
        assert failure_type == FailureType.BOUNDARY_VIOLATION

    def test_classify_integration_error(self, agent):
        """Test classification of integration errors"""
        failure_info = {
            'execution_log': "Connection refused to external API",
            'error_message': "Connection error: API unavailable",
            'keywords': ['connection', 'api']
        }
        failure_type = agent._classify_failure(failure_info)
        assert failure_type == FailureType.INTEGRATION_ERROR


class TestKeywordExtraction:
    """Test keyword extraction from logs"""

    def test_extract_aerospace_keywords(self, agent, weight_failure_log):
        """Test extraction of aerospace-specific keywords"""
        keywords = agent._extract_keywords(weight_failure_log)

        # Should extract weight-related terms
        assert any('weight' in k for k in keywords)
        assert any('fuel' in k for k in keywords)
        assert any('passenger' in k for k in keywords)

    def test_extract_numeric_values_with_units(self, agent):
        """Test extraction of numeric values with units"""
        log = "Aircraft weight is 12,750 lbs, fuel capacity 100 gallons, altitude 5000 ft"
        keywords = agent._extract_keywords(log)

        # Should extract values with units
        assert any('lbs' in k for k in keywords)
        assert any('ft' in k for k in keywords)

    def test_extract_error_keywords(self, agent):
        """Test extraction of error-related keywords"""
        log = "Test failed: value exceeded maximum, invalid input detected"
        keywords = agent._extract_keywords(log)

        assert any('exceeded' in k for k in keywords)
        assert any('invalid' in k for k in keywords)
        assert any('failed' in k for k in keywords)


class TestPatternMatching:
    """Test pattern matching against known patterns"""

    def test_match_weight_calculation_pattern(self, agent, weight_test_case, weight_failure_log):
        """Test matching weight calculation failure pattern"""
        failure_info = agent._extract_failure_info(weight_test_case, weight_failure_log)
        failure_type = agent._classify_failure(failure_info)
        matched_patterns = agent._match_patterns(failure_info, failure_type)

        # Should find at least one match
        assert len(matched_patterns) > 0

        # Top match should be weight-related
        top_match = matched_patterns[0]
        assert top_match['score'] > 0.5
        assert 'weight' in top_match['pattern']['name'].lower()

    def test_pattern_score_calculation(self, agent):
        """Test pattern match score calculation"""
        failure_info = {
            'execution_log': "weight exceeds maximum limit of 12500 lbs",
            'error_message': "Weight limit exceeded",
            'keywords': ['weight', 'exceeds', 'lbs', 'maximum'],
            'requirement_type': 'Certification',
            'requirement_category': 'Weight and Balance'
        }

        pattern = {
            'failure_patterns': [r'weight.*exceeds.*limit'],
            'keywords': ['weight', 'exceeds', 'maximum'],
            'requirement_types': ['Certification'],
            'category': 'Weight and Balance'
        }

        score = agent._calculate_pattern_match_score(failure_info, pattern)

        # Should have high score due to multiple matches
        assert score > 0.8

    def test_no_pattern_match(self, agent):
        """Test handling when no patterns match"""
        failure_info = {
            'execution_log': "Some random error that doesn't match any pattern",
            'error_message': "Random error",
            'keywords': ['random', 'error'],
            'requirement_type': 'System',
            'requirement_category': 'Other'
        }

        fake_failure_type = FailureType.EXCEPTION
        matched_patterns = agent._match_patterns(failure_info, fake_failure_type)

        # May return empty or low-score matches
        if matched_patterns:
            assert matched_patterns[0]['score'] < 0.7


class TestRootCauseAnalysis:
    """Test root cause hypothesis generation"""

    def test_generate_root_causes_from_pattern(self, agent, weight_test_case, weight_failure_log):
        """Test root cause generation when pattern matches"""
        failure_info = agent._extract_failure_info(weight_test_case, weight_failure_log)
        failure_type = agent._classify_failure(failure_info)
        matched_patterns = agent._match_patterns(failure_info, failure_type)

        root_causes = agent._generate_root_causes(failure_info, matched_patterns, weight_test_case)

        # Should generate root causes
        assert len(root_causes) > 0

        # Root causes should have required attributes
        for cause in root_causes:
            assert cause.cause
            assert 0.0 <= cause.likelihood <= 1.0
            assert isinstance(cause.evidence, list)
            assert isinstance(cause.affected_components, list)

    def test_root_cause_likelihood_ordering(self, agent, weight_test_case, weight_failure_log):
        """Test that root causes are ordered by likelihood"""
        failure_info = agent._extract_failure_info(weight_test_case, weight_failure_log)
        failure_type = agent._classify_failure(failure_info)
        matched_patterns = agent._match_patterns(failure_info, failure_type)

        root_causes = agent._generate_root_causes(failure_info, matched_patterns, weight_test_case)

        # Should be ordered by likelihood (highest first)
        if len(root_causes) > 1:
            for i in range(len(root_causes) - 1):
                assert root_causes[i].likelihood >= root_causes[i + 1].likelihood

    def test_generate_generic_causes_when_no_match(self, agent):
        """Test generic root cause generation"""
        failure_info = {
            'execution_log': "Generic error",
            'error_message': "Error occurred",
            'keywords': []
        }

        test_case = MockTestCase("TC-001", "Test", "Unit", "Low")
        root_causes = agent._generate_root_causes(failure_info, [], test_case)

        # Should generate generic causes
        assert len(root_causes) > 0
        assert any('test data' in cause.cause.lower() for cause in root_causes)


class TestSuggestionGeneration:
    """Test actionable suggestion generation"""

    def test_generate_suggestions_from_pattern(self, agent, weight_test_case, weight_failure_log):
        """Test suggestion generation when pattern matches"""
        failure_info = agent._extract_failure_info(weight_test_case, weight_failure_log)
        failure_type = agent._classify_failure(failure_info)
        matched_patterns = agent._match_patterns(failure_info, failure_type)
        root_causes = agent._generate_root_causes(failure_info, matched_patterns, weight_test_case)

        suggestions = agent._generate_suggestions(root_causes, matched_patterns, weight_test_case)

        # Should generate suggestions
        assert len(suggestions) > 0

        # Suggestions should have required attributes
        for suggestion in suggestions:
            assert suggestion.action
            assert suggestion.details
            assert suggestion.priority > 0
            assert isinstance(suggestion.code_locations, list)
            assert isinstance(suggestion.verification_steps, list)
            assert suggestion.estimated_effort_hours > 0

    def test_suggestion_priority_ordering(self, agent, weight_test_case, weight_failure_log):
        """Test that suggestions are ordered by priority"""
        failure_info = agent._extract_failure_info(weight_test_case, weight_failure_log)
        failure_type = agent._classify_failure(failure_info)
        matched_patterns = agent._match_patterns(failure_info, failure_type)
        root_causes = agent._generate_root_causes(failure_info, matched_patterns, weight_test_case)

        suggestions = agent._generate_suggestions(root_causes, matched_patterns, weight_test_case)

        # Should be ordered by priority (lowest number = highest priority)
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i].priority <= suggestions[i + 1].priority

    def test_generate_generic_suggestions(self, agent):
        """Test generic suggestion generation"""
        test_case = MockTestCase("TC-001", "Test", "Unit", "Low")
        root_causes = [
            RootCause(
                cause="Test data format mismatch",
                likelihood=0.7,
                evidence=["Format error in log"],
                affected_components=["DataModule"]
            )
        ]

        suggestions = agent._generate_generic_suggestions(root_causes, test_case)

        # Should generate generic suggestions
        assert len(suggestions) > 0
        assert any('investigate' in s.action.lower() for s in suggestions)


class TestEndToEndAnalysis:
    """Test complete failure analysis workflow"""

    def test_analyze_weight_calculation_failure(self, agent, weight_test_case, weight_failure_log):
        """Test complete analysis of weight calculation failure"""
        report = agent.analyze_failure(weight_test_case, weight_failure_log)

        # Report should have all components
        assert isinstance(report, SuggestionReport)
        assert report.test_case_id == weight_test_case.id
        assert report.failure_type
        assert len(report.root_causes) > 0
        assert len(report.suggestions) > 0
        assert 0.0 <= report.confidence_score <= 1.0

    def test_high_confidence_for_matched_pattern(self, agent, weight_test_case, weight_failure_log):
        """Test that confidence is high when pattern matches well"""
        report = agent.analyze_failure(weight_test_case, weight_failure_log)

        # Should have reasonable confidence
        assert report.confidence_score > 0.5

    def test_analyze_timeout_failure(self, agent):
        """Test analysis of timeout failure"""
        test_case = MockTestCase(
            "TC-DB-001",
            "Test database query performance",
            "Integration",
            "High",
            "System",
            "Database"
        )

        timeout_log = """
Test execution failed: Database query timeout
Query exceeded maximum execution time of 5 seconds
Actual execution time: 12.5 seconds
Table scan detected on 'requirements' table with 16,600 rows
"""

        report = agent.analyze_failure(test_case, timeout_log)

        # Should classify as timeout
        assert report.failure_type == FailureType.TIMEOUT.value

        # Should generate relevant suggestions
        assert len(report.suggestions) > 0

    def test_analyze_api_integration_failure(self, agent):
        """Test analysis of API integration failure"""
        test_case = MockTestCase(
            "TC-API-001",
            "Test external API connection",
            "Integration",
            "High",
            "System",
            "Integration"
        )

        api_log = """
Connection refused: Unable to connect to external API
Error: Connection error at https://api.example.com/v1/data
Status: 503 Service Unavailable
Network timeout after 10 retries
"""

        report = agent.analyze_failure(test_case, api_log)

        # Should classify as integration error
        assert report.failure_type == FailureType.INTEGRATION_ERROR.value

        # Should suggest retry logic or credential check
        assert len(report.suggestions) > 0
        suggestion_text = ' '.join([s.action + s.details for s in report.suggestions]).lower()
        assert 'retry' in suggestion_text or 'credential' in suggestion_text


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_execution_log(self, agent):
        """Test handling of empty execution log"""
        test_case = MockTestCase("TC-001", "Test", "Unit", "Low")

        report = agent.analyze_failure(test_case, "")

        # Should still generate a report
        assert isinstance(report, SuggestionReport)
        assert report.failure_type
        assert len(report.root_causes) > 0

    def test_very_long_execution_log(self, agent):
        """Test handling of very long execution logs"""
        test_case = MockTestCase("TC-001", "Test", "Unit", "Low")
        long_log = "Error occurred\n" * 1000  # Very long log

        report = agent.analyze_failure(test_case, long_log)

        # Should handle gracefully
        assert isinstance(report, SuggestionReport)

    def test_test_case_without_requirement(self, agent):
        """Test handling of test case without linked requirement"""
        test_case = MockTestCase("TC-001", "Test", "Unit", "Low", None, None)

        report = agent.analyze_failure(test_case, "Test failed")

        # Should still work
        assert isinstance(report, SuggestionReport)
        assert len(report.root_causes) > 0

    def test_unicode_in_logs(self, agent):
        """Test handling of unicode characters in logs"""
        test_case = MockTestCase("TC-001", "Test", "Unit", "Low")
        unicode_log = "Test failed: température exceeds 50°C ✈️"

        report = agent.analyze_failure(test_case, unicode_log)

        # Should handle unicode gracefully
        assert isinstance(report, SuggestionReport)


class TestDataClasses:
    """Test data class conversions"""

    def test_root_cause_to_dict(self):
        """Test RootCause to_dict conversion"""
        root_cause = RootCause(
            cause="Test cause",
            likelihood=0.75,
            evidence=["Evidence 1", "Evidence 2"],
            affected_components=["Component1"],
            regulatory_impact="14 CFR §23.2005"
        )

        result = root_cause.to_dict()

        assert result['cause'] == "Test cause"
        assert result['likelihood'] == 0.75
        assert len(result['evidence']) == 2
        assert result['regulatory_impact'] == "14 CFR §23.2005"

    def test_suggestion_to_dict(self):
        """Test Suggestion to_dict conversion"""
        suggestion = Suggestion(
            priority=1,
            action="Fix the issue",
            details="Detailed fix",
            code_locations=["file.py:10"],
            verification_steps=["Step 1", "Step 2"],
            estimated_effort_hours=2.5
        )

        result = suggestion.to_dict()

        assert result['priority'] == 1
        assert result['action'] == "Fix the issue"
        assert len(result['verification_steps']) == 2
        assert result['estimated_effort_hours'] == 2.5

    def test_report_to_dict(self):
        """Test SuggestionReport to_dict conversion"""
        report = SuggestionReport(
            test_case_id=123,
            failure_type=FailureType.ASSERTION_ERROR.value,
            root_causes=[],
            suggestions=[],
            similar_failures=[],
            confidence_score=0.85
        )

        result = report.to_dict()

        assert result['test_case_id'] == 123
        assert result['failure_type'] == FailureType.ASSERTION_ERROR.value
        assert result['confidence_score'] == 0.85
        assert 'root_causes' in result
        assert 'suggestions' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
