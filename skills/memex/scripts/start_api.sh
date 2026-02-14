#!/bin/bash
# Memex HISTORIAN Search API Startup Script

# Navigate to the memex directory
cd "$(dirname "$0")/.." || exit 1

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the API server
echo "Starting Memex HISTORIAN Search API..."
echo "API will be available at http://localhost:8765"
echo "Logs: ~/Library/Logs/memex-api.log"

# Use Poetry if available, otherwise try direct Python
if command -v poetry &> /dev/null; then
    poetry run python -m memex.historian.search_api
else
    # Try virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d "../venv" ]; then
        source ../venv/bin/activate
    fi
    python -m memex.historian.search_api
fi
