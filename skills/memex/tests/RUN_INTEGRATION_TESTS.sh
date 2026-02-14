#!/bin/bash
#
# Quick test runner script for Gmail and Calendar integration tests
#
# Usage:
#   ./RUN_INTEGRATION_TESTS.sh [options]
#
# Options:
#   all         - Run all tests (default)
#   gmail       - Run Gmail tests only
#   calendar    - Run Calendar tests only
#   models      - Run model tests only
#   oauth       - Run OAuth tests only
#   coverage    - Run with coverage report
#   fast        - Skip slow tests
#   verbose     - Verbose output
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test directory
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$TEST_DIR"

echo -e "${GREEN}Gmail and Calendar Integration Test Suite${NC}"
echo "=========================================="
echo ""

# Default options
RUN_COVERAGE=false
VERBOSE=""
MARKERS=""
TEST_FILES=""

# Parse arguments
case "${1:-all}" in
    gmail)
        echo "Running Gmail service tests only..."
        TEST_FILES="test_gmail_service.py"
        ;;
    calendar)
        echo "Running Calendar service tests only..."
        TEST_FILES="test_calendar_service.py"
        ;;
    models)
        echo "Running model tests only..."
        TEST_FILES="test_integration_models.py"
        ;;
    oauth)
        echo "Running OAuth flow tests only..."
        TEST_FILES="test_oauth_flow.py"
        ;;
    coverage)
        echo "Running all tests with coverage..."
        RUN_COVERAGE=true
        TEST_FILES="test_gmail_service.py test_calendar_service.py test_integration_models.py test_oauth_flow.py"
        ;;
    fast)
        echo "Running fast tests only (skipping slow tests)..."
        MARKERS="-m 'not slow and not integration'"
        TEST_FILES="test_gmail_service.py test_calendar_service.py test_integration_models.py test_oauth_flow.py"
        ;;
    verbose)
        echo "Running all tests with verbose output..."
        VERBOSE="-v -s"
        TEST_FILES="test_gmail_service.py test_calendar_service.py test_integration_models.py test_oauth_flow.py"
        ;;
    all|*)
        echo "Running all integration tests..."
        TEST_FILES="test_gmail_service.py test_calendar_service.py test_integration_models.py test_oauth_flow.py"
        ;;
esac

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not found${NC}"
    echo "Install with: pip install -r requirements-test.txt"
    exit 1
fi

# Build pytest command
PYTEST_CMD="pytest $TEST_FILES"

# Add markers (skip integration tests by default)
if [ -z "$MARKERS" ]; then
    MARKERS="-m 'not integration'"
fi
PYTEST_CMD="$PYTEST_CMD $MARKERS"

# Add verbose flag
if [ -n "$VERBOSE" ]; then
    PYTEST_CMD="$PYTEST_CMD $VERBOSE"
else
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add coverage if requested
if [ "$RUN_COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=memex.integrations --cov-report=html --cov-report=term-missing"
fi

echo ""
echo "Command: $PYTEST_CMD"
echo ""

# Run tests
if $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}✓ Tests passed!${NC}"

    if [ "$RUN_COVERAGE" = true ]; then
        echo ""
        echo "Coverage report generated in htmlcov/index.html"
        echo "Open with: open htmlcov/index.html"
    fi

    exit 0
else
    echo ""
    echo -e "${RED}✗ Tests failed!${NC}"
    exit 1
fi
