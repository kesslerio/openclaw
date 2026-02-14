#!/bin/bash
# Memex HISTORIAN Search API Stop Script

echo "Stopping Memex HISTORIAN Search API..."

# Find and kill the process
PID=$(pgrep -f "memex.historian.search_api")

if [ -z "$PID" ]; then
    echo "API server is not running"
    exit 0
fi

kill "$PID"
echo "API server stopped (PID: $PID)"
