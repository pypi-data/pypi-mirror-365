# libpresign

High-performance library for generating AWS S3 presigned URLs.

<div class="grid cards" markdown>

-   :zap:{ .lg .middle } __160x Faster__

    ---

    Generate presigned URLs 160x faster than boto3 with our optimized C++ implementation

    [:octicons-arrow-right-24: Performance benchmarks](benchmarks.md)

-   :lock:{ .lg .middle } __Secure & Compatible__

    ---

    Fully compatible with AWS S3 signature version 4, supporting all regions and custom endpoints

    [:octicons-arrow-right-24: API reference](api.md)

-   :rocket:{ .lg .middle } __Easy to Use__

    ---

    Drop-in replacement for boto3's presigned URL generation with a simple Python API

    [:octicons-arrow-right-24: Quick start](quickstart.md)

-   :package:{ .lg .middle } __Cross-Platform__

    ---

    Pre-built wheels for Linux, macOS, and Windows across Python 3.8-3.13

    [:octicons-arrow-right-24: Installation](installation.md)

</div>

## Why libpresign?

When you need to generate thousands of S3 presigned URLs quickly, boto3's performance can become a bottleneck. libpresign solves this by implementing the AWS signature version 4 algorithm in optimized C++ while maintaining full compatibility with S3.

### Key Features

- **Blazing Fast**: 5-15x faster in real-world usage, up to 160x faster in benchmarks
- **Memory Efficient**: Minimal memory overhead (~262 bytes per URL)
- **Thread Safe**: Generate URLs concurrently without locks
- **Zero Dependencies**: No runtime Python dependencies required
- **Type Safe**: Full type hints and mypy support
- **Well Tested**: 100% test coverage with comprehensive test suite

## Quick Example

```python
import libpresign

# Generate a presigned URL
url = libpresign.get(
    access_key_id="AKIAIOSFODNN7EXAMPLE",
    secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region="us-east-1",
    bucket="my-bucket",
    key="path/to/file.jpg",
    expires=3600  # 1 hour
)

print(url)
# https://my-bucket.s3.us-east-1.amazonaws.com/path/to/file.jpg?X-Amz-Algorithm=...
```

## Performance Comparison

Here's how libpresign compares to boto3 for generating presigned URLs:

| Operation | libpresign | boto3 | Speedup |
|-----------|------------|-------|---------|
| Single URL | 6 μs | 102 μs | **17x** |
| 1000 URLs | 6 ms | 102 ms | **17x** |
| Memory per URL | 262 bytes | 1.6 KB | **6x less** |

[View detailed benchmarks →](benchmarks.md)

## Use Cases

libpresign is ideal for applications that need to:

- Generate presigned URLs in bulk for large datasets
- Serve presigned URLs with minimal latency
- Process high-throughput S3 operations
- Run in resource-constrained environments
- Scale presigned URL generation horizontally

## Getting Started

<div class="grid cards" markdown>

-   __Install with pip__

    ```bash
    pip install libpresign
    ```

-   __Install with uv__

    ```bash
    uv add libpresign
    ```

</div>

Ready to speed up your S3 presigned URL generation? [Get started →](quickstart.md)

## License

libpresign is released under the MIT License. See the [LICENSE](https://github.com/myk0la-b/libpresign/blob/main/LICENSE) file for details.