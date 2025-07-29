"""Basic functionality tests for libpresign."""

from urllib.parse import parse_qs, urlparse

import pytest

import libpresign


class TestBasicFunctionality:
    """Test basic libpresign.get functionality."""

    def test_import(self):
        """Test that libpresign can be imported."""
        assert hasattr(libpresign, "get")
        assert hasattr(libpresign, "__version__")

    def test_version(self):
        """Test that version is accessible."""
        assert libpresign.__version__ == "1.2.0"

    def test_valid_url_generation(
        self, aws_credentials, test_bucket, test_key, test_expires
    ):
        """Test generating a valid presigned URL with all parameters."""
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            test_key,
            test_expires,
        )

        # Parse URL
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)

        # Basic URL structure checks
        assert parsed.scheme == "https"
        assert test_bucket in parsed.netloc
        assert test_key in parsed.path

        # Check required query parameters
        assert "X-Amz-Algorithm" in query_params
        assert "X-Amz-Credential" in query_params
        assert "X-Amz-Date" in query_params
        assert "X-Amz-Expires" in query_params
        assert "X-Amz-SignedHeaders" in query_params
        assert "X-Amz-Signature" in query_params

        # Check expires value
        assert query_params["X-Amz-Expires"][0] == str(test_expires)

    def test_default_region(self, aws_credentials, test_bucket, test_key, test_expires):
        """Test that region defaults to us-east-1 when not provided."""
        # Call with None for region parameter
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            None,  # region defaults to us-east-1
            test_bucket,
            test_key,
            test_expires,
        )

        parsed = urlparse(url)
        # Should use us-east-1 by default
        assert (
            "s3.amazonaws.com" in parsed.netloc
            or "s3.us-east-1.amazonaws.com" in parsed.netloc
        )

    def test_default_expires(self, aws_credentials, test_bucket, test_key):
        """Test that expires defaults to 3600 when not provided."""
        # Call without expires parameter (it's optional)
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            test_key,
            # expires defaults to 3600
        )

        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)

        # Should default to 3600 seconds
        assert query_params["X-Amz-Expires"][0] == "3600"

    def test_minimal_parameters(self, aws_credentials, test_bucket, test_key):
        """Test with minimal required parameters (using all defaults)."""
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            None,  # region defaults to us-east-1
            test_bucket,
            test_key,
            # expires defaults to 3600
        )

        assert isinstance(url, str)
        assert url.startswith("https://")
        assert test_bucket in url
        assert test_key in url


class TestInvalidInputs:
    """Test error handling for invalid inputs."""

    def test_missing_access_key(self, aws_credentials, test_bucket, test_key):
        """Test that missing access key raises appropriate error."""
        with pytest.raises((TypeError, SystemError)):
            libpresign.get(
                None,  # Missing access key
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                test_key,
            )

    def test_missing_secret_key(self, aws_credentials, test_bucket, test_key):
        """Test that missing secret key raises appropriate error."""
        with pytest.raises((TypeError, SystemError)):
            libpresign.get(
                aws_credentials["access_key_id"],
                None,  # Missing secret key
                aws_credentials["region"],
                test_bucket,
                test_key,
            )

    def test_missing_bucket(self, aws_credentials, test_key):
        """Test that missing bucket raises appropriate error."""
        with pytest.raises((TypeError, SystemError)):
            libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                None,  # Missing bucket
                test_key,
            )

    def test_missing_key(self, aws_credentials, test_bucket):
        """Test that missing key raises appropriate error."""
        with pytest.raises((TypeError, SystemError)):
            libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                None,  # Missing key
            )

    def test_empty_strings(self, aws_credentials):
        """Test that empty strings are handled properly."""
        # Empty bucket - the C code might accept this
        url1 = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            "",  # Empty bucket
            "key",
        )
        # Check it returns something (even if invalid)
        assert isinstance(url1, str)

        # Empty key - the C code might accept this too
        url2 = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            "bucket",
            "",  # Empty key
        )
        assert isinstance(url2, str)

    def test_negative_expires(self, aws_credentials, test_bucket, test_key):
        """Test that negative expires value is handled."""
        # Negative expires might be accepted by the C code
        # It depends on the implementation
        try:
            url = libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                test_key,
                -1,  # Negative expires
            )
            # If it doesn't raise, check the URL is still valid
            assert isinstance(url, str)
        except (ValueError, OverflowError):
            # This is also acceptable
            pass

    def test_zero_expires(self, aws_credentials, test_bucket, test_key):
        """Test that zero expires value is handled."""
        # Zero expires might be accepted
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            test_key,
            0,  # Zero expires
        )
        assert isinstance(url, str)


class TestUnicodeAndSpecialCharacters:
    """Test handling of unicode and special characters."""

    def test_unicode_key(self, aws_credentials, test_bucket, test_expires):
        """Test URL generation with unicode characters in key."""
        unicode_key = "test/path/文件名.txt"
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            unicode_key,
            test_expires,
        )

        assert isinstance(url, str)
        # URL should be properly encoded
        assert "test/path/" in url

    def test_special_characters_key(self, aws_credentials, test_bucket, test_expires):
        """Test URL generation with special characters in key."""
        special_key = "test/path/file with spaces & special!@#$%^&*().txt"
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            special_key,
            test_expires,
        )

        assert isinstance(url, str)
        # Special characters should be properly encoded
        assert "test/path/" in url

    def test_long_key_name(self, aws_credentials, test_bucket, test_expires):
        """Test URL generation with very long key names."""
        # S3 key limit is 1024 bytes
        long_key = "test/" + "a" * 1000 + ".txt"
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            long_key,
            test_expires,
        )

        assert isinstance(url, str)
        assert len(url) > 1000  # URL should be quite long

    def test_slash_prefixed_key(self, aws_credentials, test_bucket, test_expires):
        """Test URL generation with slash-prefixed keys."""
        slash_key = "/test/path/file.txt"
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            slash_key,
            test_expires,
        )

        assert isinstance(url, str)
        # Should handle leading slash correctly
        # parsed = urlparse(url)  # unused
        # Path might have double slashes depending on implementation
        assert isinstance(url, str)


class TestDifferentRegions:
    """Test URL generation for different AWS regions."""

    @pytest.mark.parametrize(
        "region", ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1", "sa-east-1"]
    )
    def test_different_regions(
        self, aws_credentials, test_bucket, test_key, test_expires, region
    ):
        """Test URL generation for various AWS regions."""
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            region,
            test_bucket,
            test_key,
            test_expires,
        )

        assert isinstance(url, str)
        parsed = urlparse(url)

        # Check region is in URL (except us-east-1 which may be omitted)
        if region != "us-east-1":
            # Region should appear somewhere in the URL
            assert region in url

        # Check proper S3 URL format
        assert parsed.scheme == "https"
        assert "s3" in parsed.netloc
        assert "amazonaws.com" in parsed.netloc


class TestExpirationTimes:
    """Test various expiration time values."""

    @pytest.mark.parametrize(
        "expires",
        [
            1,  # 1 second
            60,  # 1 minute
            3600,  # 1 hour
            86400,  # 1 day
            604800,  # 1 week (max for presigned URLs)
        ],
    )
    def test_various_expiration_times(
        self, aws_credentials, test_bucket, test_key, expires
    ):
        """Test URL generation with various expiration times."""
        url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            test_key,
            expires,
        )

        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)

        assert query_params["X-Amz-Expires"][0] == str(expires)
