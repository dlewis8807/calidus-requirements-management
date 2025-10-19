#!/bin/bash

# Test script for Requirement Modal API

echo "=========================================="
echo "Testing Requirement Modal API"
echo "=========================================="
echo ""

# Step 1: Login
echo "Step 1: Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "demo2024"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful! Token obtained."
echo ""

# Step 2: Get list of requirements
echo "Step 2: Getting list of requirements..."
REQUIREMENTS=$(curl -s -X GET "http://localhost:8000/api/requirements?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN")

echo "First 5 requirements:"
echo $REQUIREMENTS | python3 -c "import sys, json; reqs = json.load(sys.stdin).get('requirements', []); [print(f\"  - {r['requirement_id']}: {r['title'][:50]}\") for r in reqs[:5]]" 2>/dev/null
echo ""

# Step 3: Test by-req-id endpoint
echo "Step 3: Testing /api/requirements/by-req-id/ endpoint..."

# Get first requirement ID
REQ_ID=$(echo $REQUIREMENTS | python3 -c "import sys, json; reqs = json.load(sys.stdin).get('requirements', []); print(reqs[0]['requirement_id'] if reqs else '')" 2>/dev/null)

if [ -z "$REQ_ID" ]; then
  echo "❌ No requirements found in database!"
  exit 1
fi

echo "Testing with requirement ID: $REQ_ID"
echo ""

DETAIL_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/requirements/by-req-id/$REQ_ID" \
  -H "Authorization: Bearer $TOKEN")

# Check for errors
ERROR=$(echo $DETAIL_RESPONSE | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('detail', ''))" 2>/dev/null)

if [ ! -z "$ERROR" ]; then
  echo "❌ API Error: $ERROR"
  echo "Full response:"
  echo $DETAIL_RESPONSE | python3 -m json.tool
  exit 1
fi

echo "✅ Successfully retrieved requirement details!"
echo ""
echo "Requirement Details:"
echo $DETAIL_RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"  ID: {data.get('requirement_id', 'N/A')}\")
print(f\"  Title: {data.get('title', 'N/A')}\")
print(f\"  Status: {data.get('status', 'N/A')}\")
print(f\"  Priority: {data.get('priority', 'N/A')}\")
print(f\"  Test Cases: {len(data.get('test_cases', []))}\")
print(f\"  Parent Traces: {len(data.get('parent_traces', []))}\")
print(f\"  Child Traces: {len(data.get('child_traces', []))}\")
" 2>/dev/null

echo ""
echo "=========================================="
echo "✅ All tests passed!"
echo "=========================================="
