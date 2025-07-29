# Contributing to libpresign

Thank you for your interest in contributing to libpresign! This guide will help you get started.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating in this project you agree to abide by its terms.

## How to Contribute

### Reporting Issues

Found a bug or have a feature request? Please check if it's already been reported in our [issue tracker](https://github.com/myk0la-b/libpresign/issues). If not, create a new issue with:

- Clear, descriptive title
- Detailed description of the issue
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- System information (OS, Python version, libpresign version)
- Any relevant code samples or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:

- Clear description of the enhancement
- Use case and benefits
- Possible implementation approach (if you have ideas)
- Any potential drawbacks or compatibility concerns

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Set up your development environment** (see below)
3. **Make your changes** following our coding standards
4. **Add tests** for any new functionality
5. **Ensure all tests pass** and coverage remains at 100%
6. **Update documentation** if needed
7. **Submit a pull request** with a clear description

## Development Setup

### Prerequisites

- Python 3.8 or higher
- C++ compiler with C++11 support
- CMake 3.15 or higher
- OpenSSL 3.x development files
- uv package manager (recommended)

### Setting Up Your Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/libpresign.git
cd libpresign

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with all dependencies
uv pip install -e ".[dev]"
```

### Building the Extension

```bash
# Quick rebuild during development
uv pip install -e . --force-reinstall

# Full clean build
rm -rf build/ dist/ *.egg-info/
uv build
```

## Coding Standards

### Python Code

We use [ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .
```

### C++ Code

- Follow the existing code style in `src/`
- Use meaningful variable and function names
- Add comments for complex logic
- Ensure no memory leaks

### Type Hints

All Python code should have type hints:

```python
def process_data(data: dict[str, Any], validate: bool = True) -> str:
    """Process data and return result."""
    ...
```

Run type checking with:

```bash
uv run mypy libpresign
```

## Testing

### Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_basic.py

# Run with verbose output
uv run pytest -v

# Run without coverage (faster)
uv run pytest --no-cov
```

### Writing Tests

- Add tests for all new functionality
- Follow the existing test structure
- Use descriptive test names
- Include edge cases and error conditions
- Maintain 100% code coverage

Example test:

```python
def test_custom_endpoint(aws_credentials, test_bucket, test_key):
    """Test URL generation with custom endpoint."""
    endpoint = "https://minio.example.com"
    
    url = libpresign.get(
        aws_credentials['access_key_id'],
        aws_credentials['secret_access_key'],
        aws_credentials['region'],
        test_bucket,
        test_key,
        expires=3600,
        endpoint=endpoint
    )
    
    assert url.startswith(endpoint)
    assert test_bucket in url
    assert test_key in url
```

### Performance Tests

When adding performance-critical code:

```python
@pytest.mark.benchmark
def test_performance_feature():
    """Test performance of new feature."""
    # Implementation
```

## Documentation

### Updating Documentation

Documentation uses [MkDocs](https://www.mkdocs.org/) with Material theme:

```bash
# Serve documentation locally
uv run mkdocs serve

# Build documentation
uv run mkdocs build
```

### Documentation Standards

- Use clear, concise language
- Include code examples
- Update relevant sections when changing functionality
- Add new pages to `mkdocs.yml` navigation

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Routine tasks

Examples:
```
feat(api): add support for custom endpoints

fix(core): handle Unicode characters in object keys

docs(api): update parameter descriptions

test(performance): add concurrent generation benchmarks

perf(core): optimize HMAC calculation
```

## Release Process

Releases are automated using semantic-release:

1. Merge PR to main with proper commit messages
2. CI automatically determines version bump based on commits
3. Creates release, updates changelog, publishes to PyPI

## Getting Help

- Check existing [issues](https://github.com/myk0la-b/libpresign/issues) and [discussions](https://github.com/myk0la-b/libpresign/discussions)
- Read the [documentation](https://myk0la-b.github.io/libpresign/)
- Ask questions in discussions

## Recognition

Contributors will be recognized in:
- The project's contributors list
- Release notes for significant contributions
- Special thanks in documentation

Thank you for contributing to libpresign!