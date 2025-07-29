"""Performance tests for libpresign."""

import statistics
import time
from typing import List

import pytest

import libpresign


class TestPerformance:
    """Performance benchmarks for libpresign."""

    @pytest.mark.benchmark
    def test_single_url_generation_time(
        self, aws_credentials, test_bucket, test_key, test_expires
    ):
        """Benchmark single URL generation time."""
        # Warm up
        for _ in range(10):
            libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                test_key,
                test_expires,
            )

        # Measure
        times: List[float] = []
        iterations = 1000

        for _ in range(iterations):
            start = time.perf_counter()
            libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                test_key,
                test_expires,
            )
            end = time.perf_counter()
            times.append(end - start)

        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times)

        # Performance assertions
        assert avg_time < 0.001  # Should be less than 1ms on average
        assert median_time < 0.001  # Median should also be under 1ms

        # Log performance metrics
        print("\nSingle URL generation performance:")
        print(f"  Average: {avg_time * 1_000_000:.2f} μs")
        print(f"  Median: {median_time * 1_000_000:.2f} μs")
        print(f"  Std Dev: {std_dev * 1_000_000:.2f} μs")
        print(f"  Min: {min(times) * 1_000_000:.2f} μs")
        print(f"  Max: {max(times) * 1_000_000:.2f} μs")

    @pytest.mark.benchmark
    @pytest.mark.slow
    def test_batch_generation(self, aws_credentials, test_bucket, test_expires):
        """Test batch generation of 1000 URLs."""
        batch_size = 1000
        keys = [f"test/file_{i}.txt" for i in range(batch_size)]

        start = time.perf_counter()
        urls = []
        for key in keys:
            url = libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                key,
                test_expires,
            )
            urls.append(url)
        end = time.perf_counter()

        total_time = end - start
        avg_time_per_url = total_time / batch_size

        # Performance assertions
        assert len(urls) == batch_size
        assert all(isinstance(url, str) for url in urls)
        assert total_time < 1.0  # Should generate 1000 URLs in under 1 second

        print("\nBatch generation performance (1000 URLs):")
        print(f"  Total time: {total_time:.3f} seconds")
        print(f"  Average per URL: {avg_time_per_url * 1_000_000:.2f} μs")
        print(f"  URLs per second: {batch_size / total_time:.0f}")

    @pytest.mark.benchmark
    def test_memory_efficiency(
        self, aws_credentials, test_bucket, test_key, test_expires
    ):
        """Test memory efficiency of URL generation."""
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Get initial memory
        initial_memory = process.memory_info().rss

        # Generate many URLs
        urls = []
        for i in range(10000):
            url = libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                f"{test_key}_{i}",
                test_expires,
            )
            urls.append(url)

        # Get final memory
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        memory_per_url = memory_increase / 10000

        print("\nMemory efficiency:")
        print(f"  Initial memory: {initial_memory / 1024 / 1024:.2f} MB")
        print(f"  Final memory: {final_memory / 1024 / 1024:.2f} MB")
        print(f"  Memory increase: {memory_increase / 1024 / 1024:.2f} MB")
        print(f"  Memory per URL: {memory_per_url:.2f} bytes")

        # Memory should not increase significantly
        assert memory_increase < 100 * 1024 * 1024  # Less than 100MB for 10k URLs

    @pytest.mark.benchmark
    def test_concurrent_generation(
        self, aws_credentials, test_bucket, test_key, test_expires
    ):
        """Test thread safety with concurrent URL generation."""
        import concurrent.futures

        def generate_url(thread_id: int) -> tuple:
            """Generate URL and return with thread ID."""
            url = libpresign.get(
                aws_credentials["access_key_id"],
                aws_credentials["secret_access_key"],
                aws_credentials["region"],
                test_bucket,
                f"{test_key}_thread_{thread_id}",
                test_expires,
            )
            return thread_id, url

        # Test with multiple threads
        num_threads = 10
        urls_per_thread = 100

        start = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for thread_id in range(num_threads):
                for _ in range(urls_per_thread):
                    future = executor.submit(generate_url, thread_id)
                    futures.append(future)

            # Collect results
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]
        end = time.perf_counter()

        total_time = end - start
        total_urls = num_threads * urls_per_thread

        # Verify all URLs were generated
        assert len(results) == total_urls
        assert all(isinstance(result[1], str) for result in results)

        print(f"\nConcurrent generation performance ({num_threads} threads):")
        print(f"  Total URLs: {total_urls}")
        print(f"  Total time: {total_time:.3f} seconds")
        print(f"  URLs per second: {total_urls / total_time:.0f}")

    @pytest.mark.benchmark
    def test_performance_consistency(
        self, aws_credentials, test_bucket, test_key, test_expires
    ):
        """Test that performance remains consistent over time."""
        # Run multiple batches and check consistency
        batch_times = []

        for _ in range(10):
            batch_start = time.perf_counter()
            for _ in range(100):
                libpresign.get(
                    aws_credentials["access_key_id"],
                    aws_credentials["secret_access_key"],
                    aws_credentials["region"],
                    test_bucket,
                    test_key,
                    test_expires,
                )
            batch_end = time.perf_counter()
            batch_times.append(batch_end - batch_start)

        # Calculate coefficient of variation (CV)
        mean_time = statistics.mean(batch_times)
        std_dev = statistics.stdev(batch_times)
        cv = std_dev / mean_time

        print("\nPerformance consistency:")
        print(f"  Batch times: {[f'{t:.3f}' for t in batch_times]}")
        print(f"  Mean: {mean_time:.3f} seconds")
        print(f"  Std Dev: {std_dev:.3f} seconds")
        print(f"  Coefficient of Variation: {cv:.3f}")

        # Performance should be consistent (low CV)
        assert cv < 0.15  # CV should be less than 15% (relaxed for CI environments)
