"""
Performance Tests for Week 2 APIs
Ensures all API endpoints respond within 200ms target.
"""
import pytest
import time
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

# Performance threshold (200ms)
MAX_RESPONSE_TIME_MS = 200

# Test user credentials
TEST_USER = {
    "username": "admin",
    "password": "Admin123!",
    "email": "admin@calidus.aero"
}


@pytest.fixture(scope="module")
def auth_headers():
    """Get authentication headers for API requests"""
    # Create access token for test user
    access_token = create_access_token(data={"sub": TEST_USER["username"]})
    return {"Authorization": f"Bearer {access_token}"}


def measure_response_time(func, *args, **kwargs):
    """Measure function execution time in milliseconds"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    response_time_ms = (end_time - start_time) * 1000
    return result, response_time_ms


# ============================================================================
# Requirements API Performance Tests
# ============================================================================

class TestRequirementsPerformance:
    """Performance tests for Requirements API"""

    def test_list_requirements_performance(self, auth_headers):
        """Test GET /api/requirements - list requirements with pagination"""
        response, response_time = measure_response_time(
            client.get,
            "/api/requirements?page=1&page_size=50",
            headers=auth_headers
        )

        assert response.status_code == 200, f"API request failed: {response.json()}"
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ List requirements: {response_time:.2f}ms")

    def test_list_requirements_with_filters_performance(self, auth_headers):
        """Test GET /api/requirements with filtering"""
        response, response_time = measure_response_time(
            client.get,
            "/api/requirements?type=AHLR&status=APPROVED&page_size=50",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ List requirements with filters: {response_time:.2f}ms")

    def test_get_requirement_performance(self, auth_headers):
        """Test GET /api/requirements/{id} - get single requirement"""
        response, response_time = measure_response_time(
            client.get,
            "/api/requirements/1",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ Get single requirement: {response_time:.2f}ms")

    def test_get_requirements_stats_performance(self, auth_headers):
        """Test GET /api/requirements/stats - get requirement statistics"""
        response, response_time = measure_response_time(
            client.get,
            "/api/requirements/stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ Get requirements stats: {response_time:.2f}ms")


# ============================================================================
# Test Cases API Performance Tests
# ============================================================================

class TestTestCasesPerformance:
    """Performance tests for Test Cases API"""

    def test_list_test_cases_performance(self, auth_headers):
        """Test GET /api/test-cases - list test cases with pagination"""
        response, response_time = measure_response_time(
            client.get,
            "/api/test-cases?page=1&page_size=50",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ List test cases: {response_time:.2f}ms")

    def test_list_test_cases_with_filters_performance(self, auth_headers):
        """Test GET /api/test-cases with filtering"""
        response, response_time = measure_response_time(
            client.get,
            "/api/test-cases?status=PASSED&automated=true&page_size=50",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ List test cases with filters: {response_time:.2f}ms")

    def test_get_test_case_performance(self, auth_headers):
        """Test GET /api/test-cases/{id} - get single test case"""
        response, response_time = measure_response_time(
            client.get,
            "/api/test-cases/1",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ Get single test case: {response_time:.2f}ms")

    def test_get_test_cases_stats_performance(self, auth_headers):
        """Test GET /api/test-cases/stats - get test case statistics"""
        response, response_time = measure_response_time(
            client.get,
            "/api/test-cases/stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ Get test cases stats: {response_time:.2f}ms")


# ============================================================================
# Traceability API Performance Tests
# ============================================================================

class TestTraceabilityPerformance:
    """Performance tests for Traceability API"""

    def test_list_traceability_links_performance(self, auth_headers):
        """Test GET /api/traceability - list traceability links"""
        response, response_time = measure_response_time(
            client.get,
            "/api/traceability?page=1&page_size=50",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ List traceability links: {response_time:.2f}ms")

    def test_get_traceability_link_performance(self, auth_headers):
        """Test GET /api/traceability/{id} - get single traceability link"""
        response, response_time = measure_response_time(
            client.get,
            "/api/traceability/1",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ Get single traceability link: {response_time:.2f}ms")

    def test_get_traceability_matrix_performance(self, auth_headers):
        """Test GET /api/traceability/matrix/{id} - get traceability matrix"""
        response, response_time = measure_response_time(
            client.get,
            "/api/traceability/matrix/1",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ Get traceability matrix: {response_time:.2f}ms")

    def test_get_traceability_report_performance(self, auth_headers):
        """Test GET /api/traceability/report - generate traceability report"""
        # Traceability report is complex, allow 500ms instead of 200ms
        EXTENDED_THRESHOLD = 500

        response, response_time = measure_response_time(
            client.get,
            "/api/traceability/report",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < EXTENDED_THRESHOLD, (
            f"Response time {response_time:.2f}ms exceeds {EXTENDED_THRESHOLD}ms threshold"
        )
        print(f"✓ Get traceability report: {response_time:.2f}ms (extended threshold: {EXTENDED_THRESHOLD}ms)")


# ============================================================================
# Search and Pagination Performance Tests
# ============================================================================

class TestSearchPerformance:
    """Performance tests for search functionality"""

    def test_requirements_search_performance(self, auth_headers):
        """Test search across requirements"""
        response, response_time = measure_response_time(
            client.get,
            "/api/requirements?search=FlightControl&page_size=50",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ Search requirements: {response_time:.2f}ms")

    def test_large_page_size_performance(self, auth_headers):
        """Test performance with larger page sizes"""
        LARGE_PAGE_THRESHOLD = 300  # Allow more time for larger datasets

        response, response_time = measure_response_time(
            client.get,
            "/api/requirements?page=1&page_size=200",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < LARGE_PAGE_THRESHOLD, (
            f"Response time {response_time:.2f}ms exceeds {LARGE_PAGE_THRESHOLD}ms threshold"
        )
        print(f"✓ Large page size (200 items): {response_time:.2f}ms")

    def test_deep_pagination_performance(self, auth_headers):
        """Test performance with deep pagination"""
        response, response_time = measure_response_time(
            client.get,
            "/api/requirements?page=100&page_size=50",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"Response time {response_time:.2f}ms exceeds {MAX_RESPONSE_TIME_MS}ms threshold"
        )
        print(f"✓ Deep pagination (page 100): {response_time:.2f}ms")


# ============================================================================
# Summary Report
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def print_performance_summary(request):
    """Print performance test summary after all tests"""
    yield
    print("\n" + "=" * 70)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 70)
    print(f"Target Response Time: {MAX_RESPONSE_TIME_MS}ms")
    print("All API endpoints tested for performance compliance")
    print("=" * 70)
