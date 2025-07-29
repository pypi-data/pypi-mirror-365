#!/bin/bash
set -e

echo "Building Linux wheel with OpenSSL configuration"
echo "==============================================="

# Clean previous Linux builds
rm -rf dist/libpresign-*manylinux*.whl 2>/dev/null || true

echo "Starting build with colima nerdctl..."

# Run the build with OpenSSL paths configured
colima nerdctl -- run --rm \
    -v "$(pwd)":/io \
    -w /io \
    --platform linux/amd64 \
    quay.io/pypa/manylinux_2_28_x86_64 \
    /bin/bash -c '
        # First, let'\''s check what OpenSSL packages are available
        echo "=== Checking OpenSSL availability ==="
        yum list installed | grep -i openssl || true
        
        # Install OpenSSL development packages if needed
        echo "=== Installing OpenSSL development packages ==="
        yum install -y openssl-devel || true
        
        # Find OpenSSL locations
        echo "=== OpenSSL locations ==="
        find /usr -name "libcrypto.so*" 2>/dev/null | head -5 || true
        find /usr -name "openssl" -type d 2>/dev/null | head -5 || true
        
        # Set environment variables for OpenSSL
        export OPENSSL_ROOT_DIR=/usr
        export OPENSSL_INCLUDE_DIR=/usr/include
        export OPENSSL_CRYPTO_LIBRARY=/usr/lib64/libcrypto.so
        
        echo "=== Environment variables set ==="
        echo "OPENSSL_ROOT_DIR=$OPENSSL_ROOT_DIR"
        echo "OPENSSL_INCLUDE_DIR=$OPENSSL_INCLUDE_DIR"
        echo "OPENSSL_CRYPTO_LIBRARY=$OPENSSL_CRYPTO_LIBRARY"
        
        # Install Python build dependencies
        echo "=== Installing build dependencies ==="
        /opt/python/cp38-cp38/bin/pip install -U pip setuptools wheel build auditwheel
        
        # Build the wheel with CMake args
        echo "=== Building wheel ==="
        export CMAKE_ARGS="-DOPENSSL_ROOT_DIR=/usr -DOPENSSL_INCLUDE_DIR=/usr/include"
        /opt/python/cp38-cp38/bin/python -m build --wheel --outdir /tmp/dist
        
        # Show what was built
        echo "=== Wheels built ==="
        ls -la /tmp/dist/
        
        # Repair the wheel
        echo "=== Repairing wheel with auditwheel ==="
        for whl in /tmp/dist/*.whl; do
            if [ -f "$whl" ]; then
                echo "Processing: $whl"
                auditwheel show "$whl" || true
                auditwheel repair "$whl" -w /io/dist/ || echo "Repair failed for $whl"
            fi
        done
        
        echo "=== Final output ==="
        ls -la /io/dist/
    '

echo ""
echo "Build complete! Checking for Linux wheels..."
ls -la dist/*manylinux*.whl 2>/dev/null || echo "No Linux wheels found in dist/"