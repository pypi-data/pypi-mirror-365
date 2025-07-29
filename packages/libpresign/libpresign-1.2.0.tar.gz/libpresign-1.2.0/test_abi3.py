#!/usr/bin/env python3
"""Test stable ABI (abi3) wheel with multiple Python versions."""

import os
import subprocess


def test_python_version(python_path, version):
    """Test libpresign with a specific Python version."""
    print(f"\nTesting with Python {version}...")
    print("-" * 40)

    # First install the wheel
    wheel_file = "dist/libpresign-1.2.0-cp38-abi3-macosx_26_0_arm64.whl"
    result = subprocess.run(
        [python_path, "-m", "pip", "install", "--force-reinstall", wheel_file],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Try with uv
        # env_path = os.path.dirname(os.path.dirname(python_path))  # unused
        result = subprocess.run(
            ["uv", "pip", "install", "--python", python_path, wheel_file],
            capture_output=True,
            text=True,
        )

    # Test import from a different directory to avoid source imports
    test_code = """
import sys
import libpresign

print(f'✓ Python version: {sys.version.split()[0]}')
print(f'✓ Module location: {libpresign.__file__}')
print(f'✓ libpresign version: {libpresign.__version__}')

# Test functionality
url = libpresign.get(
    'AKIAIOSFODNN7EXAMPLE',
    'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    'us-east-1',
    'test-bucket',
    'test.txt',
    3600
)
print(f'✓ Generated URL: {url[:50]}...')
print(f'✓ URL is valid: {url.startswith("https://test-bucket.s3.amazonaws.com/")}')
"""

    # Run test from temp directory
    result = subprocess.run(
        [python_path, "-c", test_code], capture_output=True, text=True, cwd="/tmp"
    )

    if result.returncode == 0:
        print(result.stdout)
        print("✅ Test PASSED")
        return True
    else:
        print(result.stderr)
        print("❌ Test FAILED")
        return False


def main():
    """Test with multiple Python versions."""
    print("Testing stable ABI wheel with multiple Python versions")
    print("=" * 60)

    # Check which wheel we have
    wheel_file = "dist/libpresign-1.2.0-cp38-abi3-macosx_26_0_arm64.whl"
    if os.path.exists(wheel_file):
        print(f"✓ Found wheel: {wheel_file}")
        print("  - cp38: Minimum Python 3.8")
        print("  - abi3: Stable ABI (works with Python 3.8+)")
        print("  - Platform: macOS ARM64")
    else:
        print(f"✗ Wheel not found: {wheel_file}")
        return

    # Test with available Python versions
    base_dir = os.path.dirname(os.path.abspath(__file__))
    versions_to_test = [
        (os.path.join(base_dir, "test-py38/bin/python"), "3.8"),
        (os.path.join(base_dir, "test-py39/bin/python"), "3.9"),
        (os.path.join(base_dir, "test-py310/bin/python"), "3.10"),
        (os.path.join(base_dir, "test-py311/bin/python"), "3.11"),
        (os.path.join(base_dir, "test-py312/bin/python"), "3.12"),
    ]

    results = []
    for python_path, version in versions_to_test:
        if os.path.exists(python_path):
            passed = test_python_version(python_path, version)
            results.append((version, passed))
        else:
            print(f"\n⚠️  Python {version} not found at {python_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)

    for version, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"Python {version}: {status}")

    if all(passed for _, passed in results):
        print(
            "\n🎉 All tests passed! The stable ABI wheel works with all "
            "Python versions."
        )
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()
