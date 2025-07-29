# API Reference

## libpresign module

The libpresign module provides a single function for generating AWS S3 presigned URLs.

### libpresign.get

```python
libpresign.get(
    access_key_id: str,
    secret_access_key: str,
    region: str | None,
    bucket: str,
    key: str,
    expires: int = 3600,
    endpoint: str | None = None
) -> str
```

Generate a presigned URL for an S3 object.

#### Parameters

- **access_key_id** (*str*) – AWS access key ID
  - Required
  - Must be a valid AWS access key ID format
  - Example: `"AKIAIOSFODNN7EXAMPLE"`

- **secret_access_key** (*str*) – AWS secret access key
  - Required
  - Must be a valid AWS secret access key format
  - Example: `"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"`

- **region** (*str | None*) – AWS region
  - Optional, defaults to `"us-east-1"` if `None`
  - Must be a valid AWS region code
  - Examples: `"us-west-2"`, `"eu-central-1"`, `"ap-southeast-1"`

- **bucket** (*str*) – S3 bucket name
  - Required
  - Must follow S3 bucket naming rules
  - Can contain lowercase letters, numbers, hyphens, and periods
  - Examples: `"my-bucket"`, `"data.example.com"`

- **key** (*str*) – S3 object key (path)
  - Required
  - Can be any valid S3 object key
  - Supports Unicode characters
  - Examples: `"file.txt"`, `"path/to/document.pdf"`, `"data/2024/report.csv"`

- **expires** (*int*) – URL expiration time in seconds
  - Optional, defaults to `3600` (1 hour)
  - Must be a positive integer
  - Maximum value: `604800` (7 days)
  - Examples: `3600` (1 hour), `86400` (1 day), `604800` (1 week)

- **endpoint** (*str | None*) – Custom S3 endpoint URL
  - Optional, defaults to `None` (uses standard AWS S3 endpoint)
  - Must be a valid URL if provided
  - Used for S3-compatible storage services
  - Examples: `"https://minio.example.com"`, `"https://storage.googleapis.com"`

#### Returns

**str** – A presigned URL that can be used to access the S3 object

The URL includes:
- The S3 endpoint and bucket/key path
- AWS signature version 4 query parameters
- Expiration timestamp
- Required authentication parameters

#### Raises

- **SystemError** – If any required parameter is `None` or invalid
- **TypeError** – If parameters are not of the expected type

#### Examples

##### Basic usage with all parameters:

```python
import libpresign

url = libpresign.get(
    access_key_id="AKIAIOSFODNN7EXAMPLE",
    secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region="us-east-1",
    bucket="my-bucket",
    key="photos/sunset.jpg",
    expires=3600
)
print(url)
# Output: https://my-bucket.s3.us-east-1.amazonaws.com/photos/sunset.jpg?X-Amz-Algorithm=...
```

##### Using default region and expiration:

```python
url = libpresign.get(
    access_key_id="AKIAIOSFODNN7EXAMPLE",
    secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region=None,  # Defaults to us-east-1
    bucket="my-bucket",
    key="document.pdf"
    # expires defaults to 3600
)
```

##### With custom endpoint:

```python
url = libpresign.get(
    access_key_id="minioadmin",
    secret_access_key="minioadmin",
    region="us-east-1",
    bucket="data",
    key="reports/2024/q1.csv",
    expires=7200,
    endpoint="https://minio.internal.company.com"
)
```

### libpresign.__version__

```python
libpresign.__version__: str
```

The version of the libpresign library.

#### Example

```python
import libpresign
print(f"libpresign version: {libpresign.__version__}")
# Output: libpresign version: 1.2.0
```

## Performance Characteristics

### Time Complexity

- O(1) - Constant time regardless of URL components
- No network calls or disk I/O
- Pure CPU-bound computation

### Memory Usage

- ~262 bytes per generated URL
- No memory leaks or accumulation
- Efficient string handling

### Thread Safety

The `libpresign.get()` function is thread-safe and can be called concurrently from multiple threads without locks.

```python
import threading
import libpresign

def generate_urls(thread_id, count):
    for i in range(count):
        url = libpresign.get(
            access_key_id="AKIAIOSFODNN7EXAMPLE",
            secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            region="us-east-1",
            bucket="my-bucket",
            key=f"thread_{thread_id}/file_{i}.txt"
        )

# Safe to use from multiple threads
threads = []
for i in range(10):
    t = threading.Thread(target=generate_urls, args=(i, 100))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Compatibility

### AWS Signature Version

libpresign implements AWS Signature Version 4, which is:
- The current standard for AWS service authentication
- Required for all AWS regions
- Compatible with all S3 features

### S3-Compatible Services

libpresign works with any S3-compatible storage service that supports signature version 4:
- MinIO
- Wasabi
- DigitalOcean Spaces
- Backblaze B2 (S3 compatible API)
- Ceph Object Gateway

### URL Format

Generated URLs follow the standard S3 presigned URL format:

```
https://{bucket}.s3.{region}.amazonaws.com/{key}?
  X-Amz-Algorithm=AWS4-HMAC-SHA256&
  X-Amz-Credential={access_key_id}/{date}/{region}/s3/aws4_request&
  X-Amz-Date={timestamp}&
  X-Amz-Expires={expires}&
  X-Amz-SignedHeaders=host&
  X-Amz-Signature={signature}
```

## Type Annotations

libpresign includes full type annotations and a `py.typed` marker file for mypy compatibility:

```python
from typing import Optional
import libpresign

def create_download_url(
    file_path: str,
    expires_in: int = 3600,
    custom_endpoint: Optional[str] = None
) -> str:
    """Create a presigned download URL with type safety."""
    return libpresign.get(
        access_key_id="...",
        secret_access_key="...",
        region="us-east-1",
        bucket="my-bucket",
        key=file_path,
        expires=expires_in,
        endpoint=custom_endpoint
    )
```