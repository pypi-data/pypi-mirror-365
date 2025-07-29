"""Benchmark tests comparing libpresign to boto3."""

import statistics
import time
from typing import List, Tuple

import pytest

try:
    import boto3
    from botocore.client import Config

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

import libpresign


@pytest.mark.skipif(not BOTO3_AVAILABLE, reason="boto3 not installed")
class TestBoto3Comparison:
    """Compare libpresign performance against boto3."""

    @pytest.fixture
    def boto3_client(self, aws_credentials):
        """Create a boto3 S3 client for comparison."""
        return boto3.client(
            "s3",
            aws_access_key_id=aws_credentials["access_key_id"],
            aws_secret_access_key=aws_credentials["secret_access_key"],
            region_name=aws_credentials["region"],
            config=Config(signature_version="s3v4"),
        )

    def measure_performance(
        self, func, iterations: int = 1000
    ) -> Tuple[float, float, List[float]]:
        """Measure performance of a function over multiple iterations."""
        # Warm up
        for _ in range(10):
            func()

        # Measure
        times: List[float] = []
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)

        return statistics.mean(times), statistics.median(times), times

    @pytest.mark.benchmark
    def test_single_url_comparison(
        self, aws_credentials, test_bucket, test_key, test_expires, boto3_client
    ):
        """Compare single URL generation performance."""

        # Define test functions
        def libpresign_test():
            return libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                test_key,
                test_expires,
            )

        def boto3_test():
            return boto3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": test_bucket, "Key": test_key},
                ExpiresIn=test_expires,
            )

        # Measure performance
        libpresign_mean, libpresign_median, libpresign_times = self.measure_performance(
            libpresign_test
        )
        boto3_mean, boto3_median, boto3_times = self.measure_performance(boto3_test)

        # Calculate speedup
        mean_speedup = boto3_mean / libpresign_mean
        median_speedup = boto3_median / libpresign_median

        print("\nSingle URL Generation Comparison:")
        print("libpresign:")
        print(f"  Mean: {libpresign_mean * 1_000_000:.2f} μs")
        print(f"  Median: {libpresign_median * 1_000_000:.2f} μs")
        print("boto3:")
        print(f"  Mean: {boto3_mean * 1_000_000:.2f} μs")
        print(f"  Median: {boto3_median * 1_000_000:.2f} μs")
        print("Speedup:")
        print(f"  Mean: {mean_speedup:.1f}x faster")
        print(f"  Median: {median_speedup:.1f}x faster")

        # Assert libpresign is significantly faster
        assert (
            mean_speedup > 5
        )  # Should be at least 5x faster (conservative for various environments)
        assert median_speedup > 5

    @pytest.mark.benchmark
    @pytest.mark.slow
    def test_batch_generation_comparison(
        self, aws_credentials, test_bucket, test_expires, boto3_client
    ):
        """Compare batch URL generation performance."""
        batch_size = 1000
        keys = [f"test/file_{i}.txt" for i in range(batch_size)]

        # Test libpresign
        libpresign_start = time.perf_counter()
        libpresign_urls = []
        for key in keys:
            url = libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                key,
                test_expires,
            )
            libpresign_urls.append(url)
        libpresign_end = time.perf_counter()
        libpresign_time = libpresign_end - libpresign_start

        # Test boto3
        boto3_start = time.perf_counter()
        boto3_urls = []
        for key in keys:
            url = boto3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": test_bucket, "Key": key},
                ExpiresIn=test_expires,
            )
            boto3_urls.append(url)
        boto3_end = time.perf_counter()
        boto3_time = boto3_end - boto3_start

        # Calculate speedup
        batch_speedup = boto3_time / libpresign_time

        print(f"\nBatch Generation Comparison ({batch_size} URLs):")
        print("libpresign:")
        print(f"  Total time: {libpresign_time:.3f} seconds")
        print(f"  URLs per second: {batch_size / libpresign_time:.0f}")
        print(f"  Average per URL: {libpresign_time / batch_size * 1_000_000:.2f} μs")
        print("boto3:")
        print(f"  Total time: {boto3_time:.3f} seconds")
        print(f"  URLs per second: {batch_size / boto3_time:.0f}")
        print(f"  Average per URL: {boto3_time / batch_size * 1_000_000:.2f} μs")
        print(f"Speedup: {batch_speedup:.1f}x faster")

        # Assert libpresign is significantly faster
        assert (
            batch_speedup > 5
        )  # Should be at least 5x faster (conservative for various environments)
        assert len(libpresign_urls) == batch_size
        assert len(boto3_urls) == batch_size

    @pytest.mark.benchmark
    def test_memory_comparison(
        self, aws_credentials, test_bucket, test_key, test_expires, boto3_client
    ):
        """Compare memory usage between libpresign and boto3."""
        import gc
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Test libpresign memory usage
        gc.collect()
        libpresign_initial = process.memory_info().rss

        libpresign_urls = []
        for i in range(1000):
            url = libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                f"{test_key}_{i}",
                test_expires,
            )
            libpresign_urls.append(url)

        libpresign_final = process.memory_info().rss
        libpresign_increase = libpresign_final - libpresign_initial

        # Clear for boto3 test
        libpresign_urls.clear()
        gc.collect()
        time.sleep(0.1)  # Allow garbage collection to complete

        # Test boto3 memory usage
        boto3_initial = process.memory_info().rss

        boto3_urls = []
        for i in range(1000):
            url = boto3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": test_bucket, "Key": f"{test_key}_{i}"},
                ExpiresIn=test_expires,
            )
            boto3_urls.append(url)

        boto3_final = process.memory_info().rss
        boto3_increase = boto3_final - boto3_initial

        print("\nMemory Usage Comparison (1000 URLs):")
        print("libpresign:")
        print(f"  Memory increase: {libpresign_increase / 1024 / 1024:.2f} MB")
        print(f"  Per URL: {libpresign_increase / 1000:.0f} bytes")
        print("boto3:")
        print(f"  Memory increase: {boto3_increase / 1024 / 1024:.2f} MB")
        print(f"  Per URL: {boto3_increase / 1000:.0f} bytes")

        # Memory usage comparison - both should be reasonable
        # Note: Memory measurements can be unreliable due to Python's memory management
        ratio = boto3_increase / max(libpresign_increase, 1)
        print(f"\nMemory efficiency ratio: {ratio:.2f}x")
        # Just verify neither uses excessive memory
        assert libpresign_increase < 10 * 1024 * 1024  # Less than 10MB for 1000 URLs
        assert boto3_increase < 50 * 1024 * 1024  # boto3 might use more

    @pytest.mark.benchmark
    def test_different_operations_comparison(
        self, aws_credentials, test_bucket, test_key, boto3_client
    ):
        """Compare performance for different S3 operations."""
        operations = [
            ("get_object", 3600),
            ("put_object", 3600),
            ("delete_object", 1800),
        ]

        print("\nDifferent Operations Comparison:")

        for operation, expires in operations:
            # Note: libpresign currently only supports GET operations
            # This is to document that boto3 supports more operations

            if operation == "get_object":
                # Test libpresign
                def libpresign_test(exp=expires):
                    return libpresign.get(
                        aws_credentials["access_key_id"],
                        aws_credentials["secret_access_key"],
                        aws_credentials["region"],
                        test_bucket,
                        test_key,
                        exp,
                    )

                libpresign_mean, _, _ = self.measure_performance(
                    libpresign_test, iterations=100
                )
            else:
                libpresign_mean = None

            # Test boto3
            def boto3_test(op=operation, exp=expires):
                return boto3_client.generate_presigned_url(
                    op,
                    Params={"Bucket": test_bucket, "Key": test_key},
                    ExpiresIn=exp,
                )

            boto3_mean, _, _ = self.measure_performance(boto3_test, iterations=100)

            print(f"\n{operation}:")
            if libpresign_mean:
                print(f"  libpresign: {libpresign_mean * 1_000_000:.2f} μs")
                print(f"  boto3: {boto3_mean * 1_000_000:.2f} μs")
                print(f"  Speedup: {boto3_mean / libpresign_mean:.1f}x")
            else:
                print("  libpresign: Not supported")
                print(f"  boto3: {boto3_mean * 1_000_000:.2f} μs")

    @pytest.mark.benchmark
    def test_url_validity_comparison(
        self, aws_credentials, test_bucket, test_key, test_expires, boto3_client
    ):
        """Compare the structure of URLs generated by both libraries."""
        # Generate URLs with both libraries
        libpresign_url = libpresign.get(
            aws_credentials["access_key_id"],
            aws_credentials["secret_access_key"],
            aws_credentials["region"],
            test_bucket,
            test_key,
            test_expires,
        )

        boto3_url = boto3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": test_bucket, "Key": test_key},
            ExpiresIn=test_expires,
        )

        print("\nURL Structure Comparison:")
        print(f"libpresign URL length: {len(libpresign_url)}")
        print(f"boto3 URL length: {len(boto3_url)}")

        # Both should generate valid S3 presigned URLs
        from urllib.parse import parse_qs, urlparse

        libpresign_parsed = urlparse(libpresign_url)
        boto3_parsed = urlparse(boto3_url)

        libpresign_params = parse_qs(libpresign_parsed.query)
        boto3_params = parse_qs(boto3_parsed.query)

        # Check that both have required parameters
        required_params = [
            "X-Amz-Algorithm",
            "X-Amz-Credential",
            "X-Amz-Date",
            "X-Amz-Expires",
            "X-Amz-SignedHeaders",
            "X-Amz-Signature",
        ]

        for param in required_params:
            assert param in libpresign_params, f"libpresign missing {param}"
            assert param in boto3_params, f"boto3 missing {param}"

        print(
            "\nBoth libraries generate valid presigned URLs with all required "
            "parameters."
        )


@pytest.mark.skipif(BOTO3_AVAILABLE, reason="boto3 is installed")
class TestWithoutBoto3:
    """Fallback tests when boto3 is not available."""

    @pytest.mark.benchmark
    def test_standalone_performance(
        self, aws_credentials, test_bucket, test_key, test_expires
    ):
        """Test libpresign performance without boto3 comparison."""
        iterations = 10000

        start = time.perf_counter()
        for _ in range(iterations):
            libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                test_key,
                test_expires,
            )
        end = time.perf_counter()

        total_time = end - start
        avg_time = total_time / iterations
        urls_per_second = iterations / total_time

        print("\nStandalone Performance Test:")
        print(f"  Total URLs: {iterations}")
        print(f"  Total time: {total_time:.3f} seconds")
        print(f"  Average per URL: {avg_time * 1_000_000:.2f} μs")
        print(f"  URLs per second: {urls_per_second:.0f}")
        print("\nNote: boto3 not installed, so comparison not available.")
        print("Based on documentation, libpresign should be >100x faster than boto3.")

        # Performance assertions
        assert avg_time < 0.001  # Should be less than 1ms per URL
        assert urls_per_second > 1000  # Should generate >1000 URLs per second
