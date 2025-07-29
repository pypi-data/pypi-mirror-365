# Migration Guide

This guide helps you migrate to libpresign from boto3 or from older versions of libpresign.

## Migrating from boto3

### Basic Migration

The most common boto3 presigned URL generation can be directly replaced:

=== "boto3 (Before)"

    ```python
    import boto3
    
    # Create S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id='AKIAIOSFODNN7EXAMPLE',
        aws_secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        region_name='us-east-1'
    )
    
    # Generate presigned URL
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'my-bucket', 'Key': 'path/to/file.jpg'},
        ExpiresIn=3600
    )
    ```

=== "libpresign (After)"

    ```python
    import libpresign
    
    # Generate presigned URL directly
    url = libpresign.get(
        access_key_id='AKIAIOSFODNN7EXAMPLE',
        secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        region='us-east-1',
        bucket='my-bucket',
        key='path/to/file.jpg',
        expires=3600
    )
    ```

### Key Differences

| Feature | boto3 | libpresign |
|---------|-------|------------|
| Client initialization | Required | Not needed |
| Function name | `generate_presigned_url()` | `get()` |
| Parameters format | Dict with 'Bucket' and 'Key' | Direct parameters |
| Expiration parameter | `ExpiresIn` | `expires` |
| Default region | No default | Defaults to 'us-east-1' |
| Performance | Baseline | 5-20x faster |

### Advanced Migration Examples

#### With Environment Variables

=== "boto3"

    ```python
    import boto3
    import os
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    )
    
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'my-bucket', 'Key': 'file.txt'},
        ExpiresIn=3600
    )
    ```

=== "libpresign"

    ```python
    import libpresign
    import os
    
    url = libpresign.get(
        access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
        bucket='my-bucket',
        key='file.txt',
        expires=3600
    )
    ```

#### Batch URL Generation

=== "boto3"

    ```python
    import boto3
    
    s3_client = boto3.client('s3', ...)
    
    urls = []
    for key in file_keys:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': 'my-bucket', 'Key': key},
            ExpiresIn=3600
        )
        urls.append(url)
    ```

=== "libpresign"

    ```python
    import libpresign
    
    # Configuration
    config = {
        'access_key_id': '...',
        'secret_access_key': '...',
        'region': 'us-east-1',
        'bucket': 'my-bucket',
        'expires': 3600
    }
    
    # Much faster batch generation
    urls = [libpresign.get(**config, key=key) for key in file_keys]
    ```

#### With Custom Endpoints

=== "boto3"

    ```python
    import boto3
    
    s3_client = boto3.client(
        's3',
        endpoint_url='https://minio.example.com',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        region_name='us-east-1'
    )
    
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'bucket', 'Key': 'file.txt'},
        ExpiresIn=3600
    )
    ```

=== "libpresign"

    ```python
    import libpresign
    
    url = libpresign.get(
        access_key_id='minioadmin',
        secret_access_key='minioadmin',
        region='us-east-1',
        bucket='bucket',
        key='file.txt',
        expires=3600,
        endpoint='https://minio.example.com'
    )
    ```

### Error Handling

Error handling differs slightly between libraries:

=== "boto3"

    ```python
    from botocore.exceptions import ClientError, ParamValidationError
    
    try:
        url = s3_client.generate_presigned_url(...)
    except ParamValidationError as e:
        print(f"Invalid parameters: {e}")
    except ClientError as e:
        print(f"Client error: {e}")
    ```

=== "libpresign"

    ```python
    try:
        url = libpresign.get(...)
    except (SystemError, TypeError) as e:
        print(f"Invalid parameters: {e}")
    ```

### Feature Comparison

#### Supported Features

✅ **libpresign supports:**
- GET operation presigned URLs
- All AWS regions
- Custom S3-compatible endpoints
- Unicode object keys
- URL expiration up to 7 days

❌ **libpresign does not support:**
- PUT/POST/DELETE operations
- Request parameters (response-content-type, etc.)
- S3 Transfer Acceleration
- Requester Pays buckets
- Session tokens (temporary credentials)

### Performance Comparison

Here's what to expect when migrating:

| Scenario | boto3 Time | libpresign Time | Improvement |
|----------|------------|-----------------|-------------|
| Single URL | 102 μs | 6 μs | 17x faster |
| 1,000 URLs | 102 ms | 6 ms | 17x faster |
| 10,000 URLs | 1.02 s | 60 ms | 17x faster |
| Memory per URL | 1.6 KB | 262 bytes | 6x less |

### Migration Checklist

- [ ] Identify all `generate_presigned_url()` calls
- [ ] Verify only GET operations are used
- [ ] Check for any request parameters usage
- [ ] Replace boto3 client initialization with libpresign import
- [ ] Update function calls to use `libpresign.get()`
- [ ] Adjust parameter names (ExpiresIn → expires)
- [ ] Update error handling
- [ ] Test with your specific use cases
- [ ] Measure performance improvement

## Migrating from Older libpresign Versions

### From v0.x to v1.x

The API has remained stable, but the build system has been modernized:

```python
# Old import (still works)
import libpresign

# New import with version
from libpresign import get, __version__
print(f"Version: {__version__}")
```

### Build System Changes

If you were building from source:

=== "Old Build System"

    ```bash
    # Multiple setup.py files
    python setup_linux_amd.py bdist_wheel
    python setup_macos_arm.py bdist_wheel
    ```

=== "New Build System"

    ```bash
    # Single unified build
    pip install .
    # or
    uv pip install .
    ```

## Common Migration Patterns

### Django Storage Backend

```python
# custom_storage.py
import libpresign
from django.conf import settings
from django.core.files.storage import Storage

class FastS3Storage(Storage):
    """S3 storage with fast presigned URLs."""
    
    def url(self, name):
        """Return presigned URL for file."""
        return libpresign.get(
            access_key_id=settings.AWS_ACCESS_KEY_ID,
            secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region=settings.AWS_S3_REGION_NAME,
            bucket=settings.AWS_STORAGE_BUCKET_NAME,
            key=name,
            expires=3600
        )
```

### FastAPI Dependency

```python
# dependencies.py
from fastapi import Depends
import libpresign
import os

class S3URLGenerator:
    """Fast S3 URL generation."""
    
    def __init__(self):
        self.config = {
            'access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
            'secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
            'region': os.environ.get('AWS_REGION', 'us-east-1'),
            'bucket': os.environ['S3_BUCKET']
        }
    
    def get_url(self, key: str, expires: int = 3600) -> str:
        return libpresign.get(**self.config, key=key, expires=expires)

# Usage in routes
def get_s3_url(generator: S3URLGenerator = Depends()):
    return generator
```

### Celery Task

```python
# tasks.py
from celery import shared_task
import libpresign

@shared_task
def generate_download_urls(file_ids):
    """Generate presigned URLs for multiple files."""
    config = {
        'access_key_id': settings.AWS_ACCESS_KEY_ID,
        'secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
        'region': settings.AWS_REGION,
        'bucket': settings.S3_BUCKET,
        'expires': 86400  # 24 hours
    }
    
    # Fast batch generation
    urls = {}
    for file_id in file_ids:
        key = f"uploads/{file_id}"
        urls[file_id] = libpresign.get(**config, key=key)
    
    return urls
```

## Testing After Migration

Always test thoroughly after migration:

```python
# test_migration.py
import libpresign
import boto3
import pytest

def test_url_compatibility():
    """Ensure URLs are compatible between libraries."""
    config = {
        'aws_access_key_id': 'test',
        'aws_secret_access_key': 'test',
        'region_name': 'us-east-1'
    }
    
    # Note: URLs won't be identical due to timestamps
    # but structure should be similar
    
    # boto3 URL structure
    s3 = boto3.client('s3', **config)
    boto3_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'test', 'Key': 'file.txt'},
        ExpiresIn=3600
    )
    
    # libpresign URL structure
    libpresign_url = libpresign.get(
        access_key_id='test',
        secret_access_key='test',
        region='us-east-1',
        bucket='test',
        key='file.txt',
        expires=3600
    )
    
    # Both should have required parameters
    assert 'X-Amz-Algorithm' in boto3_url
    assert 'X-Amz-Algorithm' in libpresign_url
```

## Getting Help

If you encounter issues during migration:

1. Check the [API Reference](api.md) for parameter details
2. Review the [FAQ](#) for common issues
3. Open an [issue](https://github.com/myk0la-b/libpresign/issues) on GitHub
4. See [Contributing](contributing.md) to help improve the library