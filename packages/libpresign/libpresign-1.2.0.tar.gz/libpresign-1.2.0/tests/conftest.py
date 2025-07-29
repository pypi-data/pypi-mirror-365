"""Pytest configuration and shared fixtures for libpresign tests."""

from typing import Generator

import pytest


@pytest.fixture
def aws_credentials() -> dict:
    """Provide test AWS credentials."""
    return {
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "region": "us-east-1",
    }


@pytest.fixture
def test_bucket() -> str:
    """Provide test bucket name."""
    return "test-bucket"


@pytest.fixture
def test_key() -> str:
    """Provide test object key."""
    return "test/path/to/file.txt"


@pytest.fixture
def test_expires() -> int:
    """Provide test expiration time in seconds."""
    return 3600


@pytest.fixture
def valid_presigned_url(aws_credentials, test_bucket, test_key) -> str:
    """Expected format for a valid presigned URL."""
    return (
        f"https://{test_bucket}.s3.{aws_credentials['region']}.amazonaws.com/{test_key}"
    )


@pytest.fixture(autouse=True)
def cleanup() -> Generator:
    """Cleanup after each test."""
    yield
    # Add any cleanup code here if needed


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "benchmark: marks tests as benchmarks")
    config.addinivalue_line(
        "markers", "platform_specific: marks tests as platform specific"
    )
