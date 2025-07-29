#!/bin/bash
set -e

echo "Testing Wheels Workflow with act"
echo "================================"
echo ""

# Test source distribution build
echo "1. Testing Source Distribution Build"
echo "------------------------------------"
act -j build_sdist --verbose

echo ""
echo "2. Testing Wheel Building (Linux only for local)"
echo "------------------------------------------------"
# For local testing, we'll only test Linux wheels
# macOS and Windows would require their actual runners
act -j build_wheels --matrix os:ubuntu-latest --verbose

echo ""
echo "3. Testing Wheel Testing Job"
echo "----------------------------"
# This job depends on artifacts from previous jobs
# In local testing, we'll skip this as it requires artifact passing
echo "⚠️  Skipping wheel testing job (requires artifact upload/download)"
echo "   This will work in actual GitHub Actions"

echo ""
echo "======================================="
echo "Wheels Workflow Testing Complete!"
echo "======================================="
echo ""
echo "Note: Limitations in local testing:"
echo "- Only Linux wheels can be built locally"
echo "- Artifact upload/download doesn't work in act"
echo "- cibuildwheel may have issues with Docker-in-Docker"
echo "- For full testing, use GitHub Actions"
echo ""
echo "To test wheel building more thoroughly locally, use:"
echo "  ./build-linux-openssl.sh  # For Linux wheels"
echo "  uv build                  # For local platform wheel"
echo ""