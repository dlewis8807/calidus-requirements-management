#!/usr/bin/env python3
"""
CALIDUS Integration Tests
Tests all backend API endpoints and frontend functionality
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add_pass(self, name: str):
        self.passed += 1
        self.tests.append((name, "PASS"))
        print(f"{Colors.GREEN}✓ PASS{Colors.NC} - {name}")

    def add_fail(self, name: str, error: str = ""):
        self.failed += 1
        self.tests.append((name, f"FAIL: {error}"))
        print(f"{Colors.RED}✗ FAIL{Colors.NC} - {name}")
        if error:
            print(f"  Error: {error}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{Colors.YELLOW}{'='*50}{Colors.NC}")
        print("Integration Test Summary")
        print(f"{Colors.YELLOW}{'='*50}{Colors.NC}")
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.NC}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.NC}")
        print(f"\nPass Rate: {(self.passed/total*100) if total > 0 else 0:.1f}%")

        if self.failed == 0:
            print(f"\n{Colors.GREEN}All tests passed! ✓{Colors.NC}")
            return 0
        else:
            print(f"\n{Colors.RED}Some tests failed! ✗{Colors.NC}")
            return 1

results = TestResults()

def test_endpoint(name: str, method: str, endpoint: str, expected_status: int,
                 headers: Dict = None, data: Dict = None) -> Any:
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            results.add_fail(name, f"Unknown method: {method}")
            return None

        if response.status_code == expected_status:
            results.add_pass(name)
            return response.json() if response.text else None
        else:
            results.add_fail(name, f"Expected {expected_status}, got {response.status_code}")
            return None
    except Exception as e:
        results.add_fail(name, str(e))
        return None

print(f"{Colors.YELLOW}Starting CALIDUS Integration Tests...{Colors.NC}\n")

# 1. System Health Tests
print(f"{Colors.YELLOW}1. System Health Tests{Colors.NC}")
test_endpoint("Health Check", "GET", "/health", 200)
test_endpoint("API Root", "GET", "/", 200)
print()

# 2. Authentication Tests
print(f"{Colors.YELLOW}2. Authentication Tests{Colors.NC}")
test_endpoint("Invalid Login", "POST", "/api/auth/login", 401,
             data={"username": "invalid", "password": "wrong"})

# Login as admin
print(f"{Colors.YELLOW}Logging in as admin...{Colors.NC}")
login_response = test_endpoint("Admin Login", "POST", "/api/auth/login", 200,
                              data={"username": "admin", "password": "demo2024"})

if not login_response or 'access_token' not in login_response:
    print(f"{Colors.RED}Failed to get token! Cannot continue.{Colors.NC}")
    exit(1)

token = login_response['access_token']
auth_headers = {"Authorization": f"Bearer {token}"}

test_endpoint("Get Current User", "GET", "/api/auth/me", 200, headers=auth_headers)
print()

# 3. Requirements API Tests
print(f"{Colors.YELLOW}3. Requirements API Tests{Colors.NC}")
req_list = test_endpoint("List Requirements", "GET", "/api/requirements/?page=1&page_size=10",
                         200, headers=auth_headers)
if req_list:
    print(f"  Found {req_list.get('total', 0)} total requirements")

test_endpoint("Get Requirement Stats", "GET", "/api/requirements/stats", 200, headers=auth_headers)
test_endpoint("Get Single Requirement", "GET", "/api/requirements/1", 200, headers=auth_headers)
print()

# 4. Test Cases API Tests
print(f"{Colors.YELLOW}4. Test Cases API Tests{Colors.NC}")
tc_list = test_endpoint("List Test Cases", "GET", "/api/test-cases/?page=1&page_size=10",
                       200, headers=auth_headers)
if tc_list:
    print(f"  Found {tc_list.get('total', 0)} total test cases")

test_endpoint("Get Test Case Stats", "GET", "/api/test-cases/stats", 200, headers=auth_headers)
test_endpoint("Get Single Test Case", "GET", "/api/test-cases/1", 200, headers=auth_headers)
print()

# 5. Traceability API Tests
print(f"{Colors.YELLOW}5. Traceability API Tests{Colors.NC}")
trace_list = test_endpoint("List Traceability Links", "GET", "/api/traceability/?page=1&page_size=10",
                          200, headers=auth_headers)
if trace_list:
    print(f"  Found {trace_list.get('total', 0)} total trace links")

test_endpoint("Get Traceability Matrix", "GET", "/api/traceability/matrix/1", 200, headers=auth_headers)
trace_report = test_endpoint("Get Traceability Report", "GET", "/api/traceability/report",
                            200, headers=auth_headers)
if trace_report:
    print(f"  Traceability Score: {trace_report.get('traceability_score', 0):.1f}%")
    print(f"  Test Coverage Score: {trace_report.get('test_coverage_score', 0):.1f}%")
print()

# 6. User Management API Tests (Admin Only)
print(f"{Colors.YELLOW}6. User Management API Tests (Admin){Colors.NC}")
user_list = test_endpoint("List Users", "GET", "/api/users/?page=1&page_size=10",
                         200, headers=auth_headers)
if user_list:
    print(f"  Found {user_list.get('total', 0)} total users")

test_endpoint("Get Single User", "GET", "/api/users/1", 200, headers=auth_headers)
print()

# 7. Authorization Tests
print(f"{Colors.YELLOW}7. Authorization Tests{Colors.NC}")
# Login as engineer (non-admin)
engineer_login = test_endpoint("Engineer Login", "POST", "/api/auth/login", 200,
                              data={"username": "engineer", "password": "engineer2024"})

if engineer_login and 'access_token' in engineer_login:
    engineer_token = engineer_login['access_token']
    engineer_headers = {"Authorization": f"Bearer {engineer_token}"}
    test_endpoint("Non-Admin Access to Users API", "GET", "/api/users/", 403,
                 headers=engineer_headers)
else:
    results.add_fail("Engineer Login", "Failed to login as engineer")
print()

# Print summary
exit_code = results.summary()

# Save results to file
with open('/tmp/calidus_integration_test_results.json', 'w') as f:
    json.dump({
        'passed': results.passed,
        'failed': results.failed,
        'tests': results.tests
    }, f, indent=2)

print(f"\nResults saved to: /tmp/calidus_integration_test_results.json")

exit(exit_code)
