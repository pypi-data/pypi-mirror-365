"""
libpresign - High-performance library for generating AWS S3 presigned URLs

This library provides a fast C++ implementation for generating AWS S3 presigned URLs,
offering significant performance improvements over boto3.
"""

# Import version
try:
    from ._version import __version__
except ImportError:
    __version__ = "1.2.0"  # fallback version

# Import the get function from our C extension
# The extension is built with the same name as our package (libpresign)
# and Python's import system will find it automatically
from .libpresign import get

__all__ = ["get", "__version__"]
