#!/bin/bash
# Test Memex HISTORIAN Search API endpoints

API_URL="http://localhost:8765"

echo "Testing Memex HISTORIAN Search API"
echo "===================================="
echo ""

# Test health endpoint
echo "1. Health Check:"
curl -s "$API_URL/" | python -m json.tool
echo ""
echo ""

# Test stats endpoint
echo "2. Index Statistics:"
curl -s "$API_URL/stats" | python -m json.tool
echo ""
echo ""

# Test search endpoint
echo "3. Search Test (query: 'patient care'):"
curl -s "$API_URL/search?q=patient%20care&limit=3" | python -m json.tool
echo ""
echo ""

echo "API test complete!"
echo ""
echo "Try these commands:"
echo "  curl '$API_URL/'"
echo "  curl '$API_URL/stats'"
echo "  curl '$API_URL/search?q=YOUR_QUERY&limit=5'"
