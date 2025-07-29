#!/bin/bash
set -e

echo "Testing GitHub Workflows Locally (Without Docker)"
echo "================================================="
echo ""
echo "Since Docker/act is not available, we'll test the workflow steps directly."
echo ""

# Function to run a command and report status
run_step() {
    local description=$1
    local command=$2
    
    echo "🔄 $description"
    if eval "$command"; then
        echo "✅ $description - PASSED"
    else
        echo "❌ $description - FAILED"
        return 1
    fi
    echo ""
}

# CI Workflow Tests
echo "1. CI WORKFLOW TESTS"
echo "===================="

# Lint tests
echo "Testing Lint Job Steps:"
run_step "Ruff format check" "uv run ruff format --check ."
run_step "Ruff linter" "uv run ruff check ."

# Type check tests
echo -e "\nTesting Type Check Job Steps:"
run_step "MyPy type checking" "uv run mypy libpresign"

# Test job
echo -e "\nTesting Test Job Steps:"
run_step "Install test dependencies" "uv pip install -e '.[test]'"
run_step "Run tests with coverage" "uv run pytest -v --cov=libpresign --cov-report=term-missing"

# Build tests
echo -e "\nTesting Build Job Steps:"
run_step "Build sdist" "uv build --sdist"
run_step "List dist contents" "ls -la dist/"

# Documentation check
echo -e "\nTesting Documentation Check Steps:"
run_step "Install readme-renderer" "pip install readme-renderer"
run_step "Validate README" "python -m readme_renderer README.md -o /tmp/README.html"

echo ""
echo "2. WHEELS WORKFLOW TESTS"
echo "========================"

# Clean dist directory
rm -rf dist/
mkdir -p dist/

# Build wheel for current platform
echo -e "\nTesting Wheel Build Steps:"
run_step "Build wheel" "uv build --wheel"
run_step "Check wheel with twine" "pip install twine && twine check dist/*.whl"

# Test wheel installation
echo -e "\nTesting Wheel Installation:"
if [ -f dist/*.whl ]; then
    run_step "Create test venv" "uv venv test-wheel-env"
    run_step "Install wheel" "./test-wheel-env/bin/pip install dist/*.whl"
    run_step "Test import" "./test-wheel-env/bin/python -c 'import libpresign; print(libpresign.__version__)'"
    rm -rf test-wheel-env
fi

echo ""
echo "3. RELEASE WORKFLOW TESTS"
echo "========================="

echo -e "\nTesting Semantic Release Steps (Dry Run):"
# Check if semantic-release is available
if command -v npx &> /dev/null; then
    echo "⚠️  Skipping - semantic-release requires npm/npx"
else
    echo "Would run: npx semantic-release --dry-run"
fi

# Version check
run_step "Check current version" "python -c 'import libpresign; print(f\"Current version: {libpresign.__version__}\")'"

echo ""
echo "============================================"
echo "LOCAL WORKFLOW TESTING COMPLETE!"
echo "============================================"
echo ""
echo "Summary:"
echo "- Linting: Checked code format and style with ruff"
echo "- Type Checking: Validated types with mypy"
echo "- Tests: Ran full test suite with coverage"
echo "- Builds: Created sdist and wheel packages"
echo "- Documentation: Validated README rendering"
echo ""
echo "Note: This is a simplified version of the GitHub Actions workflows."
echo "For full CI/CD testing including:"
echo "- Multi-platform builds"
echo "- Multiple Python versions"
echo "- Artifact uploads"
echo "- Automated releases"
echo ""
echo "Please push to GitHub and use actual Actions."
echo ""
echo "To set up Docker for act testing:"
echo "1. Install OrbStack: https://orbstack.dev/"
echo "2. Or use Docker Desktop"
echo "3. Then run: ./test-all-workflows.sh"
echo ""