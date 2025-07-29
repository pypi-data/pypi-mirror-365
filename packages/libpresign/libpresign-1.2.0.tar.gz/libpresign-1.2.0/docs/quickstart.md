# Quick Start

Get up and running with libpresign in minutes.

## Basic Usage

The simplest way to generate a presigned URL:

```python
import libpresign

url = libpresign.get(
    access_key_id="AKIAIOSFODNN7EXAMPLE",
    secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region="us-east-1",
    bucket="my-bucket",
    key="path/to/file.jpg",
    expires=3600  # 1 hour
)

print(url)
```

## Parameters

The `libpresign.get()` function accepts the following parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `access_key_id` | str | Yes | - | AWS access key ID |
| `secret_access_key` | str | Yes | - | AWS secret access key |
| `region` | str or None | No | "us-east-1" | AWS region |
| `bucket` | str | Yes | - | S3 bucket name |
| `key` | str | Yes | - | S3 object key (path) |
| `expires` | int | No | 3600 | URL expiration in seconds |
| `endpoint` | str | No | None | Custom S3 endpoint URL |

## Common Examples

### Default Region and Expiration

```python
# Region defaults to us-east-1, expires defaults to 3600 seconds
url = libpresign.get(
    access_key_id="AKIAIOSFODNN7EXAMPLE",
    secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region=None,  # Will use us-east-1
    bucket="my-bucket",
    key="document.pdf"
)
```

### Different AWS Regions

```python
# Generate URL for eu-west-1 region
url = libpresign.get(
    access_key_id="AKIAIOSFODNN7EXAMPLE",
    secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region="eu-west-1",
    bucket="european-bucket",
    key="data/file.csv",
    expires=7200  # 2 hours
)
```

### Custom Endpoint (S3-Compatible Storage)

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

### Batch URL Generation

Generate multiple URLs efficiently:

```python
import libpresign
import time

# Configuration
config = {
    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "region": "us-east-1",
    "bucket": "my-bucket",
    "expires": 3600
}

# Generate 1000 URLs
keys = [f"data/file_{i}.json" for i in range(1000)]

start = time.time()
urls = [libpresign.get(**config, key=key) for key in keys]
elapsed = time.time() - start

print(f"Generated {len(urls)} URLs in {elapsed:.3f} seconds")
print(f"Rate: {len(urls)/elapsed:.0f} URLs/second")
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
import libpresign
import os

app = FastAPI()

# Configuration from environment
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET = os.environ["S3_BUCKET"]

@app.get("/presigned-url")
async def get_presigned_url(key: str, expires: int = 3600):
    """Generate a presigned URL for an S3 object."""
    try:
        url = libpresign.get(
            access_key_id=AWS_ACCESS_KEY_ID,
            secret_access_key=AWS_SECRET_ACCESS_KEY,
            region=AWS_REGION,
            bucket=S3_BUCKET,
            key=key,
            expires=expires
        )
        return {"url": url, "expires_in": expires}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Django Integration

```python
from django.conf import settings
from django.http import JsonResponse
import libpresign

def get_download_url(request, file_key):
    """Generate a presigned URL for file download."""
    try:
        url = libpresign.get(
            access_key_id=settings.AWS_ACCESS_KEY_ID,
            secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region=settings.AWS_REGION,
            bucket=settings.AWS_STORAGE_BUCKET_NAME,
            key=file_key,
            expires=3600
        )
        return JsonResponse({"download_url": url})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
```

### Async Usage with asyncio

```python
import asyncio
import libpresign
from concurrent.futures import ThreadPoolExecutor

async def generate_urls_async(keys, config):
    """Generate URLs asynchronously using thread pool."""
    loop = asyncio.get_event_loop()
    
    def generate_url(key):
        return libpresign.get(**config, key=key)
    
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(executor, generate_url, key)
            for key in keys
        ]
        urls = await asyncio.gather(*tasks)
    
    return urls

# Usage
async def main():
    config = {
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "region": "us-east-1",
        "bucket": "my-bucket",
        "expires": 3600
    }
    
    keys = [f"file_{i}.pdf" for i in range(100)]
    urls = await generate_urls_async(keys, config)
    print(f"Generated {len(urls)} URLs")

asyncio.run(main())
```

## Error Handling

libpresign raises `SystemError` for invalid inputs:

```python
import libpresign

try:
    url = libpresign.get(
        access_key_id=None,  # Invalid!
        secret_access_key="secret",
        region="us-east-1",
        bucket="bucket",
        key="key"
    )
except (SystemError, TypeError) as e:
    print(f"Error: {e}")
    # Handle invalid input
```

## Performance Tips

1. **Reuse Configuration**: Store common parameters in a dict to avoid repetition
2. **Batch Generation**: Generate multiple URLs in a single loop for best performance
3. **Thread Safety**: libpresign is thread-safe, use threading for parallel generation
4. **Memory Efficiency**: URLs are generated on-demand with minimal memory overhead

## Next Steps

- Learn about [performance benchmarks](benchmarks.md)
- Read the complete [API reference](api.md)
- Explore [building from source](building.md)