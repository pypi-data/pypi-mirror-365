# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Libpresign is a high-performance C++ Python extension for generating AWS S3 presigned URLs. It's designed to be 160x faster than boto3 for this specific use case.

## Architecture

The project consists of:
- **C++ Core**: `src/presign.cpp` implements the S3 presigned URL generation logic using OpenSSL 3.1
- **Python Extension**: `src/module.cpp` provides the Python bindings using the Python C API
- **Build System**: scikit-build-core with CMake for cross-platform builds
- **Package Structure**: `libpresign/` Python package with proper imports

## Development Commands

### Setting Up Development Environment

**Using uv (Recommended):**
```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install in editable mode with all dev dependencies
uv pip install -e ".[dev]"
```

### Building the Extension

**Modern Build (scikit-build-core):**
```bash
# Install in editable mode (development)
uv pip install -e .

# Build wheel
uv build

# Or with pip:
pip install -e .
pip wheel . --no-deps
```

**CMake Build (for testing):**
```bash
# Quick build
./build-cmake.sh

# Or manually:
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build .
```

**Full Build with Docker (all platforms):**
```bash
./build.sh
```

**macOS Only:**
```bash
./build-macos.sh
```

**Linux Wheels (using Docker):**
```bash
docker buildx build --platform linux/amd64 . --file manylinux_amd.Dockerfile -o type=local,dest=./dist/.
docker buildx build --platform linux/aarch64 . --file manylinux_aarch.Dockerfile -o type=local,dest=./dist/.
```

**Windows:**
```batch
build-wheels.bat
```

### Testing

**Run all tests with coverage:**
```bash
uv run pytest
```

**Run specific test file:**
```bash
uv run pytest tests/test_basic.py
```

**Run tests without coverage (faster):**
```bash
uv run pytest --no-cov
```

**Run only performance tests:**
```bash
uv run pytest -m benchmark
```

**Run tests excluding slow ones:**
```bash
uv run pytest -m "not slow"
```

**Quick functionality test:**
```bash
python test.py
```

### Code Quality

**Format code:**
```bash
uv run ruff format .
```

**Lint code:**
```bash
uv run ruff check .
```

**Type checking:**
```bash
uv run mypy libpresign
```

### Installing Dependencies

For manylinux builds:
```bash
./install-deps.sh
```

## Platform-Specific Notes

### macOS
- ARM64 Macs: OpenSSL is expected at `/opt/homebrew/opt/openssl@3/`
- Intel Macs: OpenSSL is expected at `/usr/local/`
- Uses clang++ compiler

### Linux
- Uses g++ compiler
- OpenSSL expected at system locations (`/usr/include`, `/usr/lib`)
- Builds are done in manylinux containers for compatibility

### Windows
- Uses MSVC (cl) compiler
- OpenSSL expected at `C:/Program Files/OpenSSL-Win64/`

## Key Implementation Details

The extension exposes a single function:
```python
libpresign.get(access_key_id, secret_access_key, region, bucket, key, expires, endpoint)
```

**Parameters:**
- `access_key_id` (str, required): AWS access key ID
- `secret_access_key` (str, required): AWS secret access key
- `region` (str or None): AWS region, defaults to "us-east-1" if None
- `bucket` (str, required): S3 bucket name
- `key` (str, required): S3 object key
- `expires` (int, optional): URL expiration in seconds, defaults to 3600 (1 hour)
- `endpoint` (str, optional): Custom S3 endpoint

**Performance:**
- 5-15x faster than boto3 for single URL generation
- Can generate 1000+ URLs per second
- Memory efficient (~262 bytes per URL)

## Version Management

Version is now managed in `pyproject.toml` under the `[project]` section. The version is:
- Set to `1.2.0` in pyproject.toml
- Automatically propagated to the C++ code during build
- Will be managed by semantic-release for automatic version bumping based on commit messages

## Important Files

- `pyproject.toml`: Single source of configuration for the entire project
- `CMakeLists.txt`: CMake configuration simplified for scikit-build-core
- `libpresign/__init__.py`: Python package entry point
- `libpresign/py.typed`: PEP 561 marker for type hints
- `tests/`: Comprehensive test suite with pytest
  - `conftest.py`: Shared fixtures and configuration
  - `test_basic.py`: Core functionality tests
  - `test_performance.py`: Performance benchmarks
  - `test_compatibility.py`: Edge cases and platform tests
  - `test_benchmark_boto3.py`: Comparison with boto3