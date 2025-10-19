#!/bin/bash

echo "=========================================="
echo "Testing Test Cases API"
echo "=========================================="
echo ""

# Login
echo "Logging in..."
LOGIN_JSON=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "demo2024"}')

TOKEN=$(echo "$LOGIN_JSON" | python3 -c "import sys, json; data=json.loads(sys.stdin.read()); print(data.get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  exit 1
fi

echo "✅ Login successful!"
echo ""

# Get test cases
echo "Fetching test cases..."
RESPONSE=$(curl -s -X GET "http://localhost:8000/api/test-cases?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN")

echo "$RESPONSE" | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
test_cases = data.get('test_cases', [])
print(f'Total test cases in response: {len(test_cases)}')
print('')
print('First 5 test cases:')
for i, tc in enumerate(test_cases[:5], 1):
    req_id = tc.get('requirement_id_str', 'N/A')
    test_id = tc.get('test_case_id', 'N/A')
    print(f'{i}. Test ID: {test_id}')
    print(f'   Requirement: {req_id}')
    print(f'   Has requirement_id_str: {\"requirement_id_str\" in tc}')
    print('')
"

echo ""
echo "=========================================="
echo "✅ Test Complete!"
echo "=========================================="
