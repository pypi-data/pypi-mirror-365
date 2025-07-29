"""Compatibility and edge case tests for libpresign."""

import sys
from urllib.parse import unquote, urlparse

import pytest

import libpresign


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_max_expires_value(self, aws_credentials, test_bucket, test_key):
        """Test maximum allowed expiration time (7 days in seconds)."""
        max_expires = 604800  # 7 days
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            test_key,
            max_expires,
        )

        assert isinstance(url, str)
        assert f"X-Amz-Expires={max_expires}" in url

    def test_very_large_expires_value(self, aws_credentials, test_bucket, test_key):
        """Test that very large expires values are handled properly."""
        # S3 has a maximum of 7 days, but let's see how the library handles
        # larger values
        large_expires = 999999999

        # This might raise an exception or clamp the value
        try:
            url = libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                test_key,
                large_expires,
            )
            # If it doesn't raise, check the URL is valid
            assert isinstance(url, str)
            assert "X-Amz-Expires=" in url
        except Exception as e:
            # If it raises, that's also acceptable behavior
            assert "expires" in str(e).lower() or "invalid" in str(e).lower()

    def test_bucket_with_dots(self, aws_credentials, test_key, test_expires):
        """Test bucket names with dots (affects URL format)."""
        dotted_bucket = "my.bucket.name"
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            dotted_bucket,
            test_key,
            test_expires,
        )

        assert isinstance(url, str)
        parsed = urlparse(url)
        # Buckets with dots use path-style URLs
        assert dotted_bucket in parsed.netloc or dotted_bucket in parsed.path

    def test_bucket_with_hyphens(self, aws_credentials, test_key, test_expires):
        """Test bucket names with hyphens."""
        hyphen_bucket = "my-bucket-name"
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            hyphen_bucket,
            test_key,
            test_expires,
        )

        assert isinstance(url, str)
        assert hyphen_bucket in url

    def test_nested_paths(self, aws_credentials, test_bucket, test_expires):
        """Test deeply nested object paths."""
        nested_key = "a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v/w/x/y/z/file.txt"
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            nested_key,
            test_expires,
        )

        assert isinstance(url, str)
        # Check that all path components are present
        assert "a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v/w/x/y/z/" in url

    def test_key_with_query_like_characters(
        self, aws_credentials, test_bucket, test_expires
    ):
        """Test keys that contain characters that look like query parameters."""
        tricky_key = "file?name=test&version=1.0"
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            tricky_key,
            test_expires,
        )

        assert isinstance(url, str)
        parsed = urlparse(url)
        # The ? and & in the key should be encoded, not treated as query parameters
        assert "?" in parsed.path or "%3F" in parsed.path
        assert "&" in parsed.path or "%26" in parsed.path

    def test_empty_region_string(
        self, aws_credentials, test_bucket, test_key, test_expires
    ):
        """Test behavior with empty region string."""
        # Empty region should either use default or raise error
        try:
            url = libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                "",  # Empty region
                test_bucket,
                test_key,
                test_expires,
            )
            # If it works, should default to us-east-1
            assert isinstance(url, str)
            assert "amazonaws.com" in url
        except Exception as e:
            # Or it might raise an error
            assert "region" in str(e).lower()


class TestPythonTypeCompatibility:
    """Test compatibility with various Python types."""

    def test_bytes_parameters(
        self, aws_credentials, test_bucket, test_key, test_expires
    ):
        """Test that bytes parameters are handled correctly."""
        # The C extension expects str, not bytes
        with pytest.raises((TypeError, SystemError)):
            _ = libpresign.get(
                aws_credentials["access_key_id"].encode(),
                aws_credentials["secret_access_key"].encode(),
                aws_credentials["region"].encode(),
                test_bucket.encode(),
                test_key.encode(),
                test_expires,
            )

    def test_integer_types(self, aws_credentials, test_bucket, test_key):
        """Test various integer types for expires parameter."""
        import numpy as np

        # Test different integer types
        for expires in [3600, np.int32(3600), np.int64(3600)]:
            url = libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                test_key,
                expires,
            )
            assert isinstance(url, str)
            assert "X-Amz-Expires=3600" in url

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9+")
    def test_string_types(self, test_expires):
        """Test with different string representations."""
        # Test with different string types and formats
        credentials = {
            "access_key": "AKIAIOSFODNN7EXAMPLE",
            "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "region": "us-east-1",
            "bucket": "test-bucket",
            "key": "test/file.txt",
        }

        # Normal strings
        url1 = libpresign.get(
            credentials["access_key"],
            credentials["secret_key"],
            credentials["region"],
            credentials["bucket"],
            credentials["key"],
            test_expires,
        )

        # f-strings
        url2 = libpresign.get(
            f"{credentials['access_key']}",
            f"{credentials['secret_key']}",
            f"{credentials['region']}",
            f"{credentials['bucket']}",
            f"{credentials['key']}",
            test_expires,
        )

        assert url1 == url2


class TestPlatformSpecific:
    """Platform-specific tests."""

    @pytest.mark.platform_specific
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows specific test")
    def test_windows_path_separators(self, aws_credentials, test_bucket, test_expires):
        """Test handling of Windows-style path separators."""
        # S3 keys should always use forward slashes, even on Windows
        windows_key = "test\\path\\to\\file.txt"
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            windows_key,
            test_expires,
        )

        assert isinstance(url, str)
        # Backslashes should be preserved or encoded, not converted
        assert (
            "test\\path\\to\\file.txt" in unquote(url)
            or "test%5Cpath%5Cto%5Cfile.txt" in url
        )

    @pytest.mark.platform_specific
    def test_locale_independence(
        self, aws_credentials, test_bucket, test_key, test_expires
    ):
        """Test that URL generation is locale-independent."""
        import locale

        # Save current locale
        original_locale = locale.getlocale()

        try:
            # Try different locales
            test_locales = ["C", "en_US.UTF-8"]
            urls = []

            for test_locale in test_locales:
                try:
                    locale.setlocale(locale.LC_ALL, test_locale)
                except locale.Error:
                    continue  # Skip if locale not available

                url = libpresign.get(
                    aws_credentials["access_key_id"],
                    aws_credentials["secret_access_key"],
                    aws_credentials["region"],
                    test_bucket,
                    test_key,
                    test_expires,
                )
                urls.append(url)

            # All URLs should be identical regardless of locale
            if len(urls) > 1:
                assert all(url == urls[0] for url in urls)

        finally:
            # Restore original locale
            locale.setlocale(locale.LC_ALL, original_locale)


class TestRobustness:
    """Test robustness and error recovery."""

    def test_repeated_calls(self, aws_credentials, test_bucket, test_key, test_expires):
        """Test that repeated calls don't cause issues."""
        # Generate the same URL many times
        urls = []
        for _ in range(1000):
            url = libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                test_key,
                test_expires,
            )
            urls.append(url)

        # All URLs should be valid
        assert all(isinstance(url, str) for url in urls)
        assert all(url.startswith("https://") for url in urls)

        # Note: URLs might differ due to timestamps

    def test_alternating_parameters(self, aws_credentials):
        """Test alternating between different parameter sets."""
        params_sets = [
            ("bucket1", "key1", "us-east-1", 3600),
            ("bucket2", "key2", "eu-west-1", 7200),
            ("bucket3", "key3", "ap-southeast-1", 1800),
        ]

        # Alternate between parameter sets
        for _ in range(100):
            for bucket, key, region, expires in params_sets:
                url = libpresign.get(
                    aws_credentials["access_key_id"],
                    aws_credentials["secret_access_key"],
                    region,
                    bucket,
                    key,
                    expires,
                )
                assert isinstance(url, str)
                assert bucket in url
                assert key in url
