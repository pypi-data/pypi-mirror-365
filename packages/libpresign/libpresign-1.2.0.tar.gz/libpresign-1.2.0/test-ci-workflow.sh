#!/bin/bash
set -e

echo "Testing CI Workflow with act"
echo "============================"
echo ""

# Function to run a specific job
run_job() {
    local job_name=$1
    local description=$2
    
    echo "🔄 Testing: $description"
    echo "   Job: $job_name"
    echo ""
    
    if act -j "$job_name" --verbose; then
        echo "✅ $description - PASSED"
    else
        echo "❌ $description - FAILED"
        return 1
    fi
    echo ""
    echo "---"
    echo ""
}

# Test individual jobs
echo "1. Testing Lint Job"
run_job "lint" "Code linting with ruff"

echo "2. Testing Type Check Job"
run_job "type-check" "Type checking with mypy"

echo "3. Testing Test Job (Ubuntu only for local testing)"
# For local testing, we'll only test on Linux since act doesn't support real macOS/Windows
act -j test --matrix os:ubuntu-latest --matrix python-version:3.12

echo "4. Testing Build Test Job"
run_job "test-builds" "Building and testing sdist"

echo "5. Testing Documentation Check Job"
run_job "check-docs" "Documentation validation"

echo ""
echo "======================================="
echo "CI Workflow Testing Complete!"
echo "======================================="
echo ""
echo "Note: Some features may not work in act:"
echo "- Codecov upload (requires real GitHub environment)"
echo "- macOS/Windows runners (simulated with Linux)"
echo "- Cache actions (limited support)"
echo ""