"""Type stubs for libpresign C extension module."""

def get(
    access_key_id: str,
    secret_access_key: str,
    region: str | None,
    bucket: str,
    key: str,
    expires: int = 3600,
    endpoint: str | None = None,
) -> str:
    """
    Generate an S3 presigned URL.

    Args:
        access_key_id: AWS access key ID
        secret_access_key: AWS secret access key
        region: AWS region (defaults to "us-east-1" if None)
        bucket: S3 bucket name
        key: S3 object key
        expires: URL expiration time in seconds (default: 3600, max: 604800)
        endpoint: Custom S3 endpoint URL (optional)

    Returns:
        A presigned URL string

    Raises:
        ValueError: If parameters are invalid
        OverflowError: If expires value is too large
    """
    ...
