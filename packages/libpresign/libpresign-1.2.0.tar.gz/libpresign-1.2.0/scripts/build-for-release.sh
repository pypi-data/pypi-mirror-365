#!/bin/bash
# Build script for semantic-release

set -e

echo "Building libpresign for release..."

# Activate virtual environment if it exists
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi

# Clean previous builds
rm -rf dist/

# Build with uv if available, otherwise fall back to pip
if command -v uv &> /dev/null; then
    echo "Building with uv..."
    uv build
else
    echo "uv not found, building with pip..."
    python -m pip install --upgrade build
    python -m build
fi

# List the built artifacts
echo "Built artifacts:"
ls -la dist/