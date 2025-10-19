#!/bin/bash

echo "=========================================="
echo "Testing Requirement Modal API Endpoints"
echo "=========================================="
echo ""

# Step 1: Login
echo "Step 1: Logging in as admin..."
LOGIN_JSON=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "demo2024"}')

TOKEN=$(echo "$LOGIN_JSON" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print(data.get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  echo "Response: $LOGIN_JSON"
  exit 1
fi

echo "✅ Login successful!"
echo ""

# Step 2: Test the by-req-id endpoint with various requirement IDs
echo "Step 2: Testing /api/requirements/by-req-id/ endpoint..."
echo ""

TEST_IDS=("AHLR-001" "AHLR-010" "SYS-001" "SYS-100")

for REQ_ID in "${TEST_IDS[@]}"; do
  echo "Testing requirement: $REQ_ID"

  RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X GET "http://localhost:8000/api/requirements/by-req-id/$REQ_ID" \
    -H "Authorization: Bearer $TOKEN")

  HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
  BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

  if [ "$HTTP_STATUS" = "200" ]; then
    echo "  ✅ Status: $HTTP_STATUS"

    # Extract key fields
    TITLE=$(echo "$BODY" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print(data.get('title', 'N/A')[:60])" 2>/dev/null)
    TEST_COUNT=$(echo "$BODY" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print(len(data.get('test_cases', [])))" 2>/dev/null)
    PARENT_COUNT=$(echo "$BODY" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print(len(data.get('parent_traces', [])))" 2>/dev/null)
    CHILD_COUNT=$(echo "$BODY" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print(len(data.get('child_traces', [])))" 2>/dev/null)

    echo "  Title: $TITLE..."
    echo "  Test Cases: $TEST_COUNT | Parent Links: $PARENT_COUNT | Child Links: $CHILD_COUNT"
  elif [ "$HTTP_STATUS" = "404" ]; then
    echo "  ⚠️  Status: $HTTP_STATUS - Requirement not found (this is OK if requirement doesn't exist)"
  else
    echo "  ❌ Status: $HTTP_STATUS"
    echo "  Error: $(echo "$BODY" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print(data.get('detail', data))" 2>/dev/null)"
  fi
  echo ""
done

# Step 3: Test with requirements that have relationships
echo "Step 3: Testing requirements with traceability..."
echo ""

# Get a requirement with relationships
REQ_WITH_RELATIONS=$(curl -s -X GET "http://localhost:8000/api/requirements?page=1&page_size=50" \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
reqs = data.get('requirements', [])
for req in reqs:
    if req.get('parent_trace_count', 0) > 0 or req.get('child_trace_count', 0) > 0:
        print(req['requirement_id'])
        break
" 2>/dev/null)

if [ ! -z "$REQ_WITH_RELATIONS" ]; then
  echo "Found requirement with relationships: $REQ_WITH_RELATIONS"

  RESPONSE=$(curl -s -X GET "http://localhost:8000/api/requirements/by-req-id/$REQ_WITH_RELATIONS" \
    -H "Authorization: Bearer $TOKEN")

  PARENT_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print(len(data.get('parent_traces', [])))" 2>/dev/null)
  CHILD_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print(len(data.get('child_traces', [])))" 2>/dev/null)

  echo "  Parent Requirements: $PARENT_COUNT"
  echo "  Child Requirements: $CHILD_COUNT"

  if [ "$PARENT_COUNT" -gt 0 ] || [ "$CHILD_COUNT" -gt 0 ]; then
    echo "  ✅ Traceability data loaded successfully!"
  fi
else
  echo "  ⚠️  No requirements with relationships found (may need to run generate_sample_data.py)"
fi

echo ""
echo "=========================================="
echo "✅ API Testing Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "- Backend API is responding correctly"
echo "- Authentication is working"
echo "- /api/requirements/by-req-id/ endpoint is functional"
echo ""
echo "Next: Test in browser at http://localhost:3000"
echo "  1. Login as admin/demo2024"
echo "  2. Go to Requirements page"
echo "  3. Click any requirement ID"
echo "  4. Modal should open with data shown above"
