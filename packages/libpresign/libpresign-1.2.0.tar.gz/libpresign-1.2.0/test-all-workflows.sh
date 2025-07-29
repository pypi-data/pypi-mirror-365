#!/bin/bash
set -e

echo "Testing All GitHub Workflows Locally with act"
echo "============================================="
echo ""
echo "This will test all workflows in order:"
echo "1. CI Workflow (lint, test, build)"
echo "2. Wheels Workflow (build wheels)"
echo "3. Release Workflow (dry run)"
echo ""
echo "Press Ctrl+C to cancel, or Enter to continue..."
read -r

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "❌ Error: 'act' is not installed"
    echo "Install it with: brew install act"
    exit 1
fi

# Check if colima is running (needed for Docker)
if ! colima status &> /dev/null; then
    echo "⚠️  Warning: Colima is not running"
    echo "Starting colima..."
    colima start
fi

# Run all test scripts
echo "===================="
echo "1. CI WORKFLOW TEST"
echo "===================="
./test-ci-workflow.sh

echo ""
echo "======================="
echo "2. WHEELS WORKFLOW TEST"
echo "======================="
./test-wheels-workflow.sh

echo ""
echo "========================"
echo "3. RELEASE WORKFLOW TEST"
echo "========================"
./test-release-workflow.sh

echo ""
echo "============================================"
echo "ALL WORKFLOW TESTS COMPLETE!"
echo "============================================"
echo ""
echo "Summary:"
echo "- CI workflow: Tests linting, type checking, and tests"
echo "- Wheels workflow: Tests wheel building (Linux only locally)"
echo "- Release workflow: Tests semantic release in dry-run mode"
echo ""
echo "For production use:"
echo "- Push to GitHub and let Actions run"
echo "- Monitor the Actions tab for results"
echo "- Wheels will be built for all platforms"
echo "- Releases will be created automatically"
echo ""