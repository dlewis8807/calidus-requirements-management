#!/bin/bash

# CALIDUS Integration Test Script
# Tests all backend API endpoints

set -e

BASE_URL="http://localhost:8000"
RESULTS_FILE="/tmp/calidus_test_results.txt"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASS=0
FAIL=0

# Function to print test results
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    local auth_header=$6

    echo -n "Testing $name... "

    if [ -z "$auth_header" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            ${data:+-d "$data"})
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $auth_header" \
            ${data:+-d "$data"})
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
        PASS=$((PASS + 1))
        echo "✓ $name - HTTP $status_code" >> $RESULTS_FILE
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $status_code)"
        echo "Response: $body"
        FAIL=$((FAIL + 1))
        echo "✗ $name - Expected $expected_status, got $status_code" >> $RESULTS_FILE
        return 1
    fi
}

# Initialize results file
echo "CALIDUS Integration Test Results - $(date)" > $RESULTS_FILE
echo "=========================================" >> $RESULTS_FILE
echo ""

echo -e "${YELLOW}Starting CALIDUS Integration Tests...${NC}\n"

# 1. Health Check
echo -e "${YELLOW}1. System Health Tests${NC}"
test_endpoint "Health Check" "GET" "/health" "" 200
test_endpoint "API Root" "GET" "/" "" 200
echo ""

# 2. Authentication Tests
echo -e "${YELLOW}2. Authentication Tests${NC}"
test_endpoint "Invalid Login" "POST" "/api/auth/login" '{"username":"invalid","password":"wrong"}' 401

# Login and get token
echo -n "Logging in as admin... "
login_response=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"demo2024"}')
TOKEN=$(echo $login_response | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASS=$((PASS + 1))
    echo "✓ Admin Login - Token received" >> $RESULTS_FILE
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Failed to get token: $login_response"
    FAIL=$((FAIL + 1))
    echo "✗ Admin Login - Failed to get token" >> $RESULTS_FILE
    exit 1
fi

test_endpoint "Get Current User" "GET" "/api/auth/me" "" 200 "$TOKEN"
echo ""

# 3. Requirements API Tests
echo -e "${YELLOW}3. Requirements API Tests${NC}"
test_endpoint "List Requirements" "GET" "/api/requirements/?page=1&page_size=10" "" 200 "$TOKEN"
test_endpoint "Get Requirement Stats" "GET" "/api/requirements/stats" "" 200 "$TOKEN"
test_endpoint "Get Single Requirement" "GET" "/api/requirements/1" "" 200 "$TOKEN"
echo ""

# 4. Test Cases API Tests
echo -e "${YELLOW}4. Test Cases API Tests${NC}"
test_endpoint "List Test Cases" "GET" "/api/test-cases/?page=1&page_size=10" "" 200 "$TOKEN"
test_endpoint "Get Test Case Stats" "GET" "/api/test-cases/stats" "" 200 "$TOKEN"
test_endpoint "Get Single Test Case" "GET" "/api/test-cases/1" "" 200 "$TOKEN"
echo ""

# 5. Traceability API Tests
echo -e "${YELLOW}5. Traceability API Tests${NC}"
test_endpoint "List Traceability Links" "GET" "/api/traceability/?page=1&page_size=10" "" 200 "$TOKEN"
test_endpoint "Get Traceability Matrix" "GET" "/api/traceability/matrix/1" "" 200 "$TOKEN"
test_endpoint "Get Traceability Report" "GET" "/api/traceability/report" "" 200 "$TOKEN"
echo ""

# 6. User Management API Tests (Admin Only)
echo -e "${YELLOW}6. User Management API Tests (Admin)${NC}"
test_endpoint "List Users" "GET" "/api/users/?page=1&page_size=10" "" 200 "$TOKEN"
test_endpoint "Get Single User" "GET" "/api/users/1" "" 200 "$TOKEN"
echo ""

# 7. Authorization Tests
echo -e "${YELLOW}7. Authorization Tests${NC}"
# Login as engineer (non-admin)
engineer_response=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"engineer","password":"engineer2024"}')
ENGINEER_TOKEN=$(echo $engineer_response | jq -r '.access_token')

if [ "$ENGINEER_TOKEN" != "null" ] && [ -n "$ENGINEER_TOKEN" ]; then
    test_endpoint "Non-Admin Access to Users API" "GET" "/api/users" "" 403 "$ENGINEER_TOKEN"
else
    echo -e "${RED}✗ FAIL${NC} - Failed to login as engineer"
    FAIL=$((FAIL + 1))
fi
echo ""

# Summary
echo "=========================================" >> $RESULTS_FILE
echo "" >> $RESULTS_FILE
echo "Total Tests: $((PASS + FAIL))" >> $RESULTS_FILE
echo "Passed: $PASS" >> $RESULTS_FILE
echo "Failed: $FAIL" >> $RESULTS_FILE
echo "" >> $RESULTS_FILE

echo -e "${YELLOW}=========================================${NC}"
echo -e "Integration Test Summary"
echo -e "${YELLOW}=========================================${NC}"
echo -e "Total Tests: $((PASS + FAIL))"
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""
echo "Results saved to: $RESULTS_FILE"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed! ✗${NC}"
    exit 1
fi
