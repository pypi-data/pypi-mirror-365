#!/bin/bash
set -e

echo "Testing Release Workflow with act (Dry Run)"
echo "==========================================="
echo ""

# Create mock secrets file for testing
echo "Creating mock secrets for testing..."
cat > .secrets <<EOF
RELEASE_APP_ID=123456
RELEASE_APP_PRIVATE_KEY=mock-private-key
GITHUB_TOKEN=mock-github-token
EOF

echo "Running release workflow in dry-run mode..."
echo ""

# Run with dry_run input to avoid actual releases
act push \
    --workflows .github/workflows/release.yml \
    --secret-file .secrets \
    --input dry_run=true \
    --verbose \
    -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest

# Clean up
rm -f .secrets

echo ""
echo "======================================="
echo "Release Workflow Testing Complete!"
echo "======================================="
echo ""
echo "Note: This was a dry-run test. In actual usage:"
echo "- Real GitHub App credentials are needed"
echo "- Semantic release will analyze commits"
echo "- Version bumping will occur automatically"
echo "- Git tags and GitHub releases will be created"
echo "- Changelog will be updated"
echo ""
echo "The release workflow is designed to run on:"
echo "- Push to main branch"
echo "- Manual workflow dispatch"
echo ""