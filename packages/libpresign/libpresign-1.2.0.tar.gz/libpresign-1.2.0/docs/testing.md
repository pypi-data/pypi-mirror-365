# Testing

This guide covers running and writing tests for libpresign.

## Running Tests

### Quick Start

```bash
# Run all tests with coverage
uv run pytest

# Run without coverage (faster)
uv run pytest --no-cov

# Run with verbose output
uv run pytest -v
```

### Running Specific Tests

```bash
# Run a specific test file
uv run pytest tests/test_basic.py

# Run a specific test class
uv run pytest tests/test_basic.py::TestBasicFunctionality

# Run a specific test method
uv run pytest tests/test_basic.py::TestBasicFunctionality::test_import

# Run tests matching a pattern
uv run pytest -k "test_unicode"
```

### Using Test Markers

Tests are organized with markers for different categories:

```bash
# Run only benchmark tests
uv run pytest -m benchmark

# Run tests excluding slow ones
uv run pytest -m "not slow"

# Run platform-specific tests
uv run pytest -m platform_specific

# Combine markers
uv run pytest -m "benchmark and not slow"
```

## Test Structure

The test suite is organized as follows:

```
tests/
├── __init__.py             # Test package marker
├── conftest.py            # Shared fixtures and configuration
├── test_basic.py          # Core functionality tests
├── test_performance.py    # Performance benchmarks
├── test_compatibility.py  # Edge cases and platform tests
└── test_benchmark_boto3.py # Comparison with boto3
```

### Test Categories

#### Basic Functionality (`test_basic.py`)
- Import and version verification
- Valid URL generation with all parameters
- Default parameter handling
- Invalid input validation
- Unicode and special character support
- Different AWS regions
- Custom endpoints

#### Performance (`test_performance.py`)
- Single URL generation timing
- Batch generation benchmarks
- Memory efficiency tests
- Thread safety verification
- Performance consistency checks

#### Compatibility (`test_compatibility.py`)
- Edge cases (max values, empty strings)
- Various bucket naming conventions
- Complex object keys
- Platform-specific behaviors
- Type compatibility

#### Boto3 Comparison (`test_benchmark_boto3.py`)
- Speed comparisons
- Memory usage analysis
- URL structure validation
- Feature parity checks

## Test Configuration

### pytest Configuration

Configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--cov=libpresign",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=100",
]
```

### Coverage Configuration

```toml
[tool.coverage.run]
source = ["libpresign"]
omit = ["*/tests/*", "*/_version.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

## Writing Tests

### Using Fixtures

Common test fixtures are defined in `conftest.py`:

```python
def test_url_generation(aws_credentials, test_bucket, test_key, test_expires):
    """Test URL generation using fixtures."""
    url = libpresign.get(
        aws_credentials['access_key_id'],
        aws_credentials['secret_access_key'],
        aws_credentials['region'],
        test_bucket,
        test_key,
        test_expires
    )
    assert isinstance(url, str)
    assert test_bucket in url
```

### Available Fixtures

| Fixture | Description | Value |
|---------|-------------|-------|
| `aws_credentials` | AWS credential dict | Access key, secret, region |
| `test_bucket` | S3 bucket name | "test-bucket" |
| `test_key` | S3 object key | "test/file.txt" |
| `test_expires` | Expiration time | 3600 |

### Writing New Tests

#### Basic Test Structure

```python
def test_new_feature():
    """Test description."""
    # Arrange
    input_data = prepare_test_data()
    
    # Act
    result = libpresign.get(...)
    
    # Assert
    assert result is not None
    assert "expected" in result
```

#### Testing Error Cases

```python
def test_invalid_input():
    """Test that invalid input raises appropriate errors."""
    with pytest.raises((SystemError, TypeError)) as exc_info:
        libpresign.get(
            access_key_id=None,  # Invalid!
            secret_access_key="secret",
            region="us-east-1",
            bucket="bucket",
            key="key"
        )
    
    assert "access_key_id" in str(exc_info.value)
```

#### Performance Tests

```python
@pytest.mark.benchmark
def test_performance_metric():
    """Test performance of specific operation."""
    import time
    
    start = time.perf_counter()
    for _ in range(1000):
        libpresign.get(...)
    elapsed = time.perf_counter() - start
    
    assert elapsed < 0.1  # Should complete in under 100ms
    urls_per_second = 1000 / elapsed
    assert urls_per_second > 10000  # At least 10k URLs/second
```

#### Platform-Specific Tests

```python
@pytest.mark.platform_specific
@pytest.mark.skipif(sys.platform != "win32", reason="Windows specific test")
def test_windows_paths():
    """Test Windows-specific path handling."""
    # Windows-specific test implementation
```

### Test Markers

Add markers to categorize tests:

```python
# Slow test that takes time
@pytest.mark.slow
def test_large_batch():
    """Test with large data set."""
    pass

# Performance benchmark
@pytest.mark.benchmark
def test_speed():
    """Benchmark test."""
    pass

# Platform-specific
@pytest.mark.platform_specific
def test_platform_feature():
    """Platform-dependent test."""
    pass
```

## Debugging Tests

### Verbose Output

```bash
# Show test names as they run
uv run pytest -v

# Show print statements
uv run pytest -s

# Show local variables on failure
uv run pytest -l
```

### Debugging Failed Tests

```bash
# Stop on first failure
uv run pytest -x

# Drop into debugger on failure
uv run pytest --pdb

# Show full traceback
uv run pytest --tb=long

# Run only last failed tests
uv run pytest --lf
```

### Test Isolation

Each test should be independent:

```python
class TestFeature:
    """Group related tests."""
    
    def setup_method(self):
        """Run before each test method."""
        self.test_data = create_test_data()
    
    def teardown_method(self):
        """Run after each test method."""
        cleanup_test_data()
    
    def test_feature_a(self):
        """Test feature A independently."""
        assert self.test_data is not None
```

## Coverage Reports

### Viewing Coverage

```bash
# Terminal report
uv run pytest --cov-report=term-missing

# HTML report
uv run pytest --cov-report=html
# Open htmlcov/index.html in browser

# XML report (for CI)
uv run pytest --cov-report=xml
```

### Improving Coverage

1. Check uncovered lines:
   ```bash
   uv run pytest --cov-report=term-missing | grep "MISS"
   ```

2. Focus on specific module:
   ```bash
   uv run pytest --cov=libpresign.specific_module
   ```

3. Exclude non-testable code:
   ```python
   if __name__ == "__main__":  # pragma: no cover
       main()
   ```

## Continuous Integration

Tests run automatically on:
- Every push to main branch
- All pull requests
- Multiple Python versions (3.8-3.13)
- Multiple platforms (Linux, macOS, Windows)

### CI Test Matrix

| Platform | Python Versions | Special Notes |
|----------|----------------|---------------|
| Ubuntu | 3.8-3.13 | Primary platform |
| macOS | 3.9-3.13 | No 3.8 on M1 |
| Windows | 3.8-3.13 | MSVC compiler |

## Performance Testing

### Running Benchmarks

```bash
# Run all benchmarks
uv run pytest tests/test_performance.py -v

# Run with benchmark plugin
uv run pytest --benchmark-only

# Compare with baseline
uv run pytest --benchmark-compare
```

### Benchmark Best Practices

1. **Warm-up**: Always warm up before timing
2. **Multiple runs**: Use sufficient iterations
3. **Isolation**: Minimize external factors
4. **Consistency**: Use same test data

Example benchmark:

```python
def test_batch_performance(benchmark, aws_credentials):
    """Benchmark batch URL generation."""
    def generate_batch():
        urls = []
        for i in range(100):
            url = libpresign.get(
                **aws_credentials,
                bucket="test-bucket",
                key=f"file_{i}.txt"
            )
            urls.append(url)
        return urls
    
    result = benchmark(generate_batch)
    assert len(result) == 100
```

## Test Data

### Using Fixtures

```python
# In conftest.py
@pytest.fixture
def large_key():
    """Provide a large object key for testing."""
    return "deep/nested/path/" + "x" * 1000 + "/file.txt"

# In test file
def test_large_key(aws_credentials, test_bucket, large_key):
    """Test with large object key."""
    url = libpresign.get(
        **aws_credentials,
        bucket=test_bucket,
        key=large_key
    )
    assert large_key in url
```

### Parametrized Tests

```python
@pytest.mark.parametrize("region", [
    "us-east-1",
    "eu-west-1",
    "ap-southeast-1",
    "sa-east-1",
])
def test_regions(aws_credentials, test_bucket, test_key, region):
    """Test different AWS regions."""
    creds = aws_credentials.copy()
    creds['region'] = region
    
    url = libpresign.get(
        **creds,
        bucket=test_bucket,
        key=test_key
    )
    assert region in url
```

## Next Steps

- [Contributing Guide](contributing.md) - Submit your tests
- [API Reference](api.md) - Understand the API
- [Performance Benchmarks](benchmarks.md) - Performance testing details