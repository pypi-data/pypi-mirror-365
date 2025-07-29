# Testing GitHub Workflows Locally with act

This document describes how to test GitHub Actions workflows locally using [act](https://github.com/nektos/act).

## Prerequisites

1. Install act:
   ```bash
   brew install act
   ```

2. Ensure Docker is running (via colima on macOS ARM64):
   ```bash
   colima start
   ```

## Test Scripts

We've created several test scripts to make testing workflows easier:

- `test-ci-workflow.sh` - Tests the main CI workflow (lint, type-check, tests)
- `test-wheels-workflow.sh` - Tests wheel building workflow
- `test-release-workflow.sh` - Tests semantic release workflow (dry-run)
- `test-all-workflows.sh` - Runs all workflow tests

## Running Tests

### Quick Test of All Workflows
```bash
./test-all-workflows.sh
```

### Individual Workflow Tests

#### CI Workflow
```bash
./test-ci-workflow.sh
```

This tests:
- Linting with ruff
- Type checking with mypy
- Running pytest tests
- Building sdist
- Documentation checks

#### Wheels Workflow
```bash
./test-wheels-workflow.sh
```

This tests:
- Building source distribution
- Building Linux wheels (other platforms simulated)

#### Release Workflow
```bash
./test-release-workflow.sh
```

This tests:
- Semantic release in dry-run mode
- Version bumping logic
- Changelog generation

### Manual act Commands

List all available jobs:
```bash
act -l
```

Run a specific job:
```bash
act -j lint
```

Run with specific event:
```bash
act push
act pull_request
act workflow_dispatch
```

Run with custom inputs:
```bash
act workflow_dispatch --input dry_run=true
```

## Limitations

### Platform Support
- act runs workflows in Docker containers
- macOS and Windows runners are simulated using Linux containers
- Platform-specific features may not work correctly

### Features Not Available Locally
1. **Artifact Upload/Download** - Works in GitHub but not in act
2. **Codecov Upload** - Requires GitHub environment
3. **GitHub App Tokens** - Mocked for local testing
4. **Caching** - Limited support in act
5. **GitHub Context** - Some context variables are simulated

### Workarounds

#### Testing Multi-Platform Builds
For actual multi-platform testing:
- **Linux**: Use `./build-linux-openssl.sh`
- **macOS**: Use `uv build` directly
- **Windows**: Test on actual Windows or use GitHub Actions

#### Secrets
Create a `.secrets` file for testing (don't commit!):
```bash
cat > .secrets <<EOF
GITHUB_TOKEN=mock-token
RELEASE_APP_ID=123456
RELEASE_APP_PRIVATE_KEY=mock-key
EOF

act -j release --secret-file .secrets
```

## Best Practices

1. **Use Dry Run First**
   ```bash
   act -j <job-name> --dryrun
   ```

2. **Test Individual Jobs**
   - Start with simple jobs (lint, type-check)
   - Move to complex jobs (build, test)

3. **Check Docker Resources**
   - Ensure enough disk space
   - Monitor memory usage
   - Clean up old containers: `docker system prune`

4. **Debugging**
   ```bash
   act -j <job-name> --verbose
   ```

## Common Issues

### Docker Not Running
```bash
# Check if colima is running
colima status

# Start if needed
colima start
```

### Permission Errors
The `.actrc` file includes:
```
--container-cap-add SYS_ADMIN
--container-options "--security-opt apparmor:unconfined"
```

### Out of Space
```bash
# Clean Docker
docker system prune -a
```

## Configuration

The `.actrc` file configures:
- Default runner images
- Container architecture (linux/amd64)
- Resource settings
- Image pull behavior

## Summary

act provides a good approximation of GitHub Actions locally, but:
- Use it for quick validation and debugging
- Final testing should always be done on GitHub
- Some features require the real GitHub environment
- Platform-specific builds need actual hardware or VMs

For production releases, always rely on actual GitHub Actions.