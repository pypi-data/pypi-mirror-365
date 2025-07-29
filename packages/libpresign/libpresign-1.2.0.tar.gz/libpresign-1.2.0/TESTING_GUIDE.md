# Testing Guide for libpresign

## Overview

The libpresign project uses pytest for testing with comprehensive test coverage including functionality, performance, and compatibility tests.

## Test Structure

```
tests/
├── __init__.py             # Test package marker
├── conftest.py            # Shared fixtures and configuration
├── test_basic.py          # Core functionality tests
├── test_performance.py    # Performance benchmarks
├── test_compatibility.py  # Edge cases and platform tests
└── test_benchmark_boto3.py # Comparison with boto3
```

## Running Tests

### Basic Commands

```bash
# Run all tests with coverage
uv run pytest

# Run tests without coverage (faster)
uv run pytest --no-cov

# Run specific test file
uv run pytest tests/test_basic.py

# Run specific test class
uv run pytest tests/test_basic.py::TestBasicFunctionality

# Run specific test
uv run pytest tests/test_basic.py::TestBasicFunctionality::test_import
```

### Using Test Markers

```bash
# Run only benchmark tests
uv run pytest -m benchmark

# Run tests excluding slow ones
uv run pytest -m "not slow"

# Run platform-specific tests
uv run pytest -m platform_specific
```

### Verbose Output

```bash
# Show test names as they run
uv run pytest -v

# Show print statements
uv run pytest -s

# Show local variables on failure
uv run pytest -l
```

## Test Categories

### 1. Basic Functionality Tests (`test_basic.py`)
- Import and version checks
- Valid URL generation with all parameters
- Default parameter handling (region, expires)
- Invalid input handling
- Unicode and special character support
- Different AWS regions
- Various expiration times

### 2. Performance Tests (`test_performance.py`)
- Single URL generation timing (< 1ms requirement)
- Batch generation (1000 URLs in < 1 second)
- Memory efficiency
- Thread safety and concurrent generation
- Performance consistency

### 3. Compatibility Tests (`test_compatibility.py`)
- Edge cases (max expires, empty strings)
- Bucket naming variations
- Python type compatibility
- Platform-specific behaviors
- Locale independence

### 4. Boto3 Comparison (`test_benchmark_boto3.py`)
- Speed comparison (5x+ faster requirement)
- Memory usage comparison
- URL validity comparison
- Feature parity checks

## Writing New Tests

### Test Fixtures (from conftest.py)

```python
def test_example(aws_credentials, test_bucket, test_key, test_expires):
    """Example test using fixtures."""
    url = libpresign.get(
        aws_credentials['access_key_id'],
        aws_credentials['secret_access_key'],
        aws_credentials['region'],
        test_bucket,
        test_key,
        test_expires
    )
    assert isinstance(url, str)
```

### Adding Test Markers

```python
@pytest.mark.slow
@pytest.mark.benchmark
def test_performance_intensive():
    """Test that takes a long time."""
    pass
```

## Coverage Requirements

The project requires 100% test coverage. Coverage configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=libpresign",
    "--cov-fail-under=100",
]
```

To see coverage report:
```bash
# HTML report
uv run pytest --cov-report=html
# Then open htmlcov/index.html

# Terminal report
uv run pytest --cov-report=term-missing
```

## Debugging Test Failures

```bash
# Stop on first failure
uv run pytest -x

# Drop into debugger on failure
uv run pytest --pdb

# Show full traceback
uv run pytest --tb=long

# Run last failed tests
uv run pytest --lf
```

## Performance Testing

Performance tests use pytest-benchmark. To run detailed benchmarks:

```bash
# Run with benchmark stats
uv run pytest tests/test_performance.py -v --benchmark-only

# Compare with previous runs
uv run pytest tests/test_performance.py --benchmark-compare

# Save benchmark results
uv run pytest tests/test_performance.py --benchmark-save=baseline
```

## CI/CD Integration

Tests are configured to run in CI with:
- Multiple Python versions (3.8-3.13)
- Multiple platforms (Linux, macOS, Windows)
- Coverage reporting
- Performance regression detection

## Common Issues

### SystemError instead of TypeError
The C extension may raise SystemError when given invalid types. Tests should accept both:
```python
with pytest.raises((TypeError, SystemError)):
    libpresign.get(None, ...)
```

### Import Errors
Always run tests through uv to ensure proper environment:
```bash
uv run pytest  # Correct
pytest         # May fail
```

### Performance Variations
Performance tests may vary based on system load. The thresholds are conservative to account for CI environments.