# Migration Guide: Legacy Build System to scikit-build-core

This guide helps you migrate from the legacy build system (multiple setup.py files) to the new unified scikit-build-core build system.

## What Changed

### Build System
- **Before**: 7 different setup.py files for various platforms
- **After**: Single `pyproject.toml` with scikit-build-core

### Development Workflow
- **Before**: Platform-specific build scripts and manual dependency management
- **After**: Unified workflow with `uv` package manager

### Package Structure
- **Before**: Direct C extension module
- **After**: Proper Python package structure with `libpresign/__init__.py`

## Migration Steps

### 1. Update Your Development Environment

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or on macOS with Homebrew
brew install uv
```

### 2. Clean Your Working Directory

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info/
rm -rf build_*/ wheelhouse/
rm -f *.so *.pyd *.dll
```

### 3. Set Up New Development Environment

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows

# Install in editable mode with dev dependencies
uv pip install -e ".[dev]"
```

### 4. Update Your Build Commands

#### Building Wheels

**Before:**
```bash
python setup_linux_amd.py bdist_wheel
python setup_macos_arm.py bdist_wheel
# etc...
```

**After:**
```bash
# Build wheel for current platform
uv build

# Or use cibuildwheel for multiple platforms
cibuildwheel --platform linux
```

#### Development Build

**Before:**
```bash
python setup.py build_ext --inplace
```

**After:**
```bash
uv pip install -e .
```

### 5. Update Your CI/CD Scripts

Replace platform-specific build logic with:

```yaml
# GitHub Actions example
- uses: astral-sh/setup-uv@v2
- run: uv build
```

### 6. Update Import Statements

The import remains the same:
```python
import libpresign
```

But now you can also access the version:
```python
from libpresign import __version__
```

## Common Issues and Solutions

### Issue: ModuleNotFoundError after migration
**Solution**: Make sure to clean all old build artifacts and reinstall:
```bash
rm -rf build/ dist/ *.egg-info/
uv pip install -e . --force-reinstall
```

### Issue: OpenSSL not found during build
**Solution**: The new system uses the same OpenSSL detection. On macOS:
```bash
brew install openssl@3
```

### Issue: Tests not finding the module
**Solution**: Always run tests through uv:
```bash
uv run pytest
```

### Issue: Coverage failing with 100% requirement
**Solution**: Run tests without coverage for debugging:
```bash
uv run pytest --no-cov
```

## Benefits of the New System

1. **Single Configuration File**: All project metadata and build configuration in `pyproject.toml`
2. **Standards Compliance**: Full PEP 517/660 compliance
3. **Better Dependency Management**: Fast, reliable dependency resolution with uv
4. **Automatic Versioning**: Semantic versioning with automatic changelog generation
5. **Simplified CI/CD**: One workflow for all platforms using cibuildwheel
6. **Comprehensive Testing**: Full test suite with pytest, performance benchmarks, and boto3 comparisons
7. **Type Safety**: Type hints support with py.typed marker

## Rollback Plan

If you need to temporarily use the old build system:

1. The legacy setup files are preserved in the `legacy/pre-refactoring` branch
2. Check out that branch: `git checkout legacy/pre-refactoring`
3. Use the old build commands as before

## Getting Help

- Report issues: https://github.com/myk0la-b/libpresign/issues
- Documentation: https://myk0la-b.github.io/libpresign/
- Changelog: See CHANGELOG.md for detailed changes