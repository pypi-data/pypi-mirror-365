#!/bin/bash
set -ex

# Clean previous builds
# rm -rf build cmake-build

# Create build directory
mkdir -p cmake-build
cd cmake-build

# Configure with CMake
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_PYTHON_MODULE=ON \
    -DBUILD_SHARED_LIB=OFF \
    -DBUILD_STATIC_LIB=OFF \
    -B .

# Build
cmake --build . --config Release -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)

# Copy the built module to the project root for testing
cp libpresign*.so ../libpresign.so 2>/dev/null || cp libpresign*.pyd ../libpresign.pyd 2>/dev/null || true

echo "Build completed successfully!"