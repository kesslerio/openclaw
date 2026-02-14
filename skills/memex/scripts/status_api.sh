#!/bin/bash
# Memex HISTORIAN Search API Status Check

PID=$(pgrep -f "memex.historian.search_api")

if [ -z "$PID" ]; then
    echo "Status: NOT RUNNING"
    exit 1
else
    echo "Status: RUNNING (PID: $PID)"
    echo ""
    echo "Testing API endpoint..."
    curl -s http://localhost:8765/ | python -m json.tool || echo "API not responding"
fi
