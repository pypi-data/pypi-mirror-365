# libpresign

[![CI](https://github.com/myk0la-b/libpresign/actions/workflows/ci.yml/badge.svg)](https://github.com/myk0la-b/libpresign/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/libpresign.svg)](https://pypi.org/project/libpresign/)
[![Python Versions](https://img.shields.io/pypi/pyversions/libpresign.svg)](https://pypi.org/project/libpresign/)
[![License](https://img.shields.io/pypi/l/libpresign.svg)](https://github.com/myk0la-b/libpresign/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/libpresign)](https://pepy.tech/project/libpresign)

High-performance library for generating AWS S3 presigned URLs. Generate presigned URLs up to 160x faster than boto3.

## Features

- 🚀 **Lightning Fast**: 5-160x faster than boto3 for presigned URL generation
- 🔐 **Secure**: Full AWS Signature Version 4 compliance
- 🌍 **Compatible**: Works with S3 and S3-compatible services (MinIO, Wasabi, etc.)
- 📦 **Lightweight**: Minimal dependencies, pure C++ implementation
- 🐍 **Python Ready**: Simple Python bindings with type hints
- 🧵 **Thread Safe**: Generate URLs concurrently without locks
- 💰 **Cost Effective**: Reduce compute costs with faster operations

## Installation

```bash
pip install libpresign
```

Pre-built wheels are available for:
- **Linux**: x86_64, aarch64 (Python 3.8-3.13)
- **macOS**: x86_64, arm64 (Python 3.8-3.13)
- **Windows**: AMD64 (Python 3.8-3.13)

## Quick Start

```python
import libpresign

# Generate a presigned URL
url = libpresign.get(
    access_key_id="AKIAIOSFODNN7EXAMPLE",
    secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region="us-east-1",
    bucket="my-bucket",
    key="path/to/file.jpg",
    expires=3600  # URL valid for 1 hour
)

print(url)
# https://my-bucket.s3.us-east-1.amazonaws.com/path/to/file.jpg?X-Amz-Algorithm=...
```

## Performance

### Benchmark Results

Generate 10,000 presigned URLs:

| Library | Time (ms) | URLs/sec | Speedup |
|---------|-----------|----------|---------|
| libpresign | **60** | **166,667** | **160x** |
| boto3 | 9,600 | 1,042 | 1x |

Single URL generation:

| Library | Time (μs) | Memory |
|---------|-----------|---------|
| libpresign | **6** | 262 bytes |
| boto3 | 102 | 1.6 KB |

## Usage Examples

### Basic Usage

```python
import libpresign

# Simple URL generation
url = libpresign.get(
    access_key_id="your-access-key",
    secret_access_key="your-secret-key",
    region="us-east-1",
    bucket="my-bucket",
    key="document.pdf"
)
```

### Custom Endpoint (MinIO/S3-Compatible)

```python
# Use with MinIO or other S3-compatible storage
url = libpresign.get(
    access_key_id="minioadmin",
    secret_access_key="minioadmin",
    region="us-east-1",
    bucket="my-bucket",
    key="file.txt",
    expires=3600,
    endpoint="https://minio.example.com"
)
```

### Batch Generation

```python
# Generate multiple URLs efficiently
config = {
    "access_key_id": "your-access-key",
    "secret_access_key": "your-secret-key",
    "region": "us-west-2",
    "bucket": "my-bucket",
    "expires": 3600
}

urls = []
for i in range(1000):
    url = libpresign.get(**config, key=f"file_{i}.jpg")
    urls.append(url)
```

### Integration with Web Frameworks

#### FastAPI
```python
from fastapi import FastAPI
import libpresign

app = FastAPI()

@app.get("/presigned-url")
async def get_presigned_url(file_key: str):
    url = libpresign.get(
        access_key_id="...",
        secret_access_key="...",
        region="us-east-1",
        bucket="uploads",
        key=file_key,
        expires=3600
    )
    return {"url": url}
```

#### Django
```python
from django.http import JsonResponse
import libpresign

def download_file(request, file_id):
    url = libpresign.get(
        access_key_id=settings.AWS_ACCESS_KEY_ID,
        secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region=settings.AWS_REGION,
        bucket=settings.S3_BUCKET,
        key=f"files/{file_id}",
        expires=300  # 5 minutes
    )
    return JsonResponse({"download_url": url})
```

## API Reference

### `libpresign.get()`

Generate a presigned URL for S3 object access.

**Parameters:**
- `access_key_id` (str): AWS access key ID
- `secret_access_key` (str): AWS secret access key
- `region` (str | None): AWS region (defaults to "us-east-1")
- `bucket` (str): S3 bucket name
- `key` (str): S3 object key
- `expires` (int): URL expiration time in seconds (defaults to 3600)
- `endpoint` (str | None): Custom S3 endpoint URL

**Returns:**
- `str`: Presigned URL

**Raises:**
- `SystemError`: If required parameters are invalid

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/myk0la-b/libpresign.git
cd libpresign

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_basic.py

# Run benchmarks
uv run pytest tests/test_benchmark_boto3.py -v
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy libpresign
```

## Building from Source

### Prerequisites

- C++ compiler with C++11 support
- CMake 3.15+
- OpenSSL 3.x
- Python 3.8+

### Build Instructions

```bash
# Quick build
pip install .

# Development build
pip install -e .

# Build wheel
pip wheel . --no-deps
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/myk0la-b/libpresign/blob/main/docs/contributing.md) for details.

### Reporting Issues

If you find a bug or have a feature request, please [open an issue](https://github.com/myk0la-b/libpresign/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [OpenSSL](https://www.openssl.org/) for cryptographic operations
- Inspired by the need for faster S3 presigned URL generation
- Thanks to all [contributors](https://github.com/myk0la-b/libpresign/graphs/contributors)

## Links

- [Documentation](https://myk0la-b.github.io/libpresign/)
- [PyPI Package](https://pypi.org/project/libpresign/)
- [GitHub Repository](https://github.com/myk0la-b/libpresign)
- [Issue Tracker](https://github.com/myk0la-b/libpresign/issues)
- [Changelog](https://github.com/myk0la-b/libpresign/blob/main/CHANGELOG.md)