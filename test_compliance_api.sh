#!/bin/bash

# Test compliance API endpoints

echo "=== Testing Compliance API Endpoints ==="
echo

# Login
echo "1. Getting auth token..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "demo2024"}' | \
  jq -r '.access_token')

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    exit 1
fi
echo "✅ Token obtained"
echo

# Test /api/compliance/stats
echo "2. Testing GET /api/compliance/stats"
curl -s -X GET "http://localhost:8000/api/compliance/stats" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo

# Test /api/compliance/overview
echo "3. Testing GET /api/compliance/overview"
curl -s -X GET "http://localhost:8000/api/compliance/overview" \
  -H "Authorization: Bearer $TOKEN" | jq '.metrics'
echo

# Test /api/compliance/regulations
echo "4. Testing GET /api/compliance/regulations"
curl -s -X GET "http://localhost:8000/api/compliance/regulations" \
  -H "Authorization: Bearer $TOKEN" | jq '.regulations[] | {name, total_requirements, coverage_percentage}'
echo

# Test /api/compliance/gaps
echo "5. Testing GET /api/compliance/gaps"
curl -s -X GET "http://localhost:8000/api/compliance/gaps?limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '{total_unmapped, by_priority, by_type}'
echo

echo "=== All tests complete ==="
