# Building from Source

This guide covers building libpresign from source for development or when pre-built wheels are not available for your platform.

## Prerequisites

### All Platforms

- Python 3.8 or higher with development headers
- CMake 3.15 or higher
- C++ compiler with C++11 support
- OpenSSL 3.x development files

### Platform-Specific Requirements

=== "Linux"

    ```bash
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y \
        build-essential \
        cmake \
        libssl-dev \
        python3-dev
    
    # RHEL/CentOS/Fedora
    sudo yum install -y \
        gcc-c++ \
        cmake3 \
        openssl-devel \
        python3-devel
    
    # Arch Linux
    sudo pacman -S \
        base-devel \
        cmake \
        openssl \
        python
    ```

=== "macOS"

    ```bash
    # Install Xcode Command Line Tools
    xcode-select --install
    
    # Install dependencies with Homebrew
    brew install cmake openssl@3
    
    # Set OpenSSL path
    export OPENSSL_ROOT_DIR=$(brew --prefix openssl@3)
    ```

=== "Windows"

    1. Install Visual Studio 2019 or later with C++ support
    2. Install CMake from https://cmake.org/download/
    3. Install OpenSSL:
       ```powershell
       # Using Chocolatey
       choco install openssl
       
       # Or download from https://slproweb.com/products/Win32OpenSSL.html
       ```
    4. Set environment variables:
       ```powershell
       $env:OPENSSL_ROOT_DIR = "C:\Program Files\OpenSSL-Win64"
       ```

## Building with pip

The simplest way to build from source:

```bash
# Clone the repository
git clone https://github.com/myk0la-b/libpresign.git
cd libpresign

# Build and install
pip install .

# Or for development (editable install)
pip install -e .
```

## Building with uv

Using uv for faster builds:

```bash
# Clone the repository
git clone https://github.com/myk0la-b/libpresign.git
cd libpresign

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Build and install
uv pip install -e .
```

## Manual Build with CMake

For more control over the build process:

```bash
# Clone the repository
git clone https://github.com/myk0la-b/libpresign.git
cd libpresign

# Create build directory
mkdir build
cd build

# Configure
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_PYTHON_MODULE=ON

# Build
cmake --build . --config Release

# Install
cmake --install .
```

### CMake Options

| Option | Default | Description |
|--------|---------|-------------|
| `BUILD_PYTHON_MODULE` | ON | Build Python extension module |
| `BUILD_SHARED_LIB` | OFF | Build shared library |
| `BUILD_STATIC_LIB` | OFF | Build static library |
| `CMAKE_BUILD_TYPE` | Release | Build type (Debug/Release) |

## Building Wheels

### Using cibuildwheel

Build wheels for multiple Python versions:

```bash
# Install cibuildwheel
pip install cibuildwheel

# Build for current platform
cibuildwheel --platform auto

# Build for specific platform
cibuildwheel --platform linux
cibuildwheel --platform macos
cibuildwheel --platform windows
```

### Using build

Build a wheel for current Python:

```bash
# Install build
pip install build

# Build wheel and sdist
python -m build

# Wheels will be in dist/
ls dist/
```

## Platform-Specific Notes

### Linux

#### manylinux Builds

For maximum compatibility, build in manylinux containers:

```bash
# Build manylinux wheels
docker run --rm -v $(pwd):/io quay.io/pypa/manylinux2014_x86_64 \
    /io/build-wheels-linux.sh

# For ARM64
docker run --rm -v $(pwd):/io quay.io/pypa/manylinux2014_aarch64 \
    /io/build-wheels-linux.sh
```

#### Custom OpenSSL Location

If OpenSSL is installed in a non-standard location:

```bash
export OPENSSL_ROOT_DIR=/opt/openssl3
pip install .
```

### macOS

#### Universal2 Builds

Build for both Intel and Apple Silicon:

```bash
# Set architectures
export ARCHFLAGS="-arch x86_64 -arch arm64"

# Build universal2 wheel
pip install . --no-binary :all:
```

#### Code Signing

For distribution, sign the binary:

```bash
codesign --sign "Developer ID" --timestamp \
    build/lib.*/libpresign*.so
```

### Windows

#### Debug Builds

For debugging on Windows:

```bash
# Configure for Debug
cmake .. -DCMAKE_BUILD_TYPE=Debug

# Build with debug symbols
cmake --build . --config Debug
```

#### Static Runtime

To link the C++ runtime statically:

```cmake
# In CMakeLists.txt
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
```

## Troubleshooting

### OpenSSL Not Found

=== "Linux"

    ```bash
    # Find OpenSSL location
    pkg-config --modversion openssl
    pkg-config --cflags openssl
    
    # Set paths manually
    export CFLAGS="-I/usr/include/openssl"
    export LDFLAGS="-L/usr/lib/x86_64-linux-gnu"
    ```

=== "macOS"

    ```bash
    # Homebrew OpenSSL
    export OPENSSL_ROOT_DIR=$(brew --prefix openssl@3)
    export LDFLAGS="-L$OPENSSL_ROOT_DIR/lib"
    export CPPFLAGS="-I$OPENSSL_ROOT_DIR/include"
    
    # MacPorts OpenSSL
    export OPENSSL_ROOT_DIR=/opt/local
    ```

=== "Windows"

    ```powershell
    # Set OpenSSL location
    $env:OPENSSL_ROOT_DIR = "C:\Program Files\OpenSSL-Win64"
    
    # Or in CMake
    cmake .. -DOPENSSL_ROOT_DIR="C:\OpenSSL"
    ```

### Python Headers Not Found

```bash
# Find Python include directory
python -c "import sysconfig; print(sysconfig.get_path('include'))"

# Install development headers
# Ubuntu/Debian
sudo apt-get install python3-dev

# RHEL/CentOS
sudo yum install python3-devel

# macOS (usually included)
# Windows (included with Python)
```

### Compiler Errors

#### C++11 Support

Ensure your compiler supports C++11:

```bash
# GCC/Clang
g++ --version  # Should be 4.8.1 or later
clang++ --version  # Should be 3.3 or later

# Force C++11
export CXXFLAGS="-std=c++11"
```

#### Missing Dependencies

```bash
# Check CMake can find everything
cmake .. --debug-find
```

## Testing Your Build

After building, verify the installation:

```python
# Test import
import libpresign
print(f"Version: {libpresign.__version__}")

# Test functionality
url = libpresign.get(
    access_key_id="test",
    secret_access_key="test",
    region="us-east-1",
    bucket="test-bucket",
    key="test.txt"
)
print(f"Generated URL: {url[:50]}...")

# Run test suite
pytest tests/
```

## Advanced Building

### Cross-Compilation

For cross-compiling to different architectures:

```bash
# Example: Build for ARM64 on x86_64
cmake .. \
    -DCMAKE_SYSTEM_NAME=Linux \
    -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
    -DCMAKE_C_COMPILER=aarch64-linux-gnu-gcc \
    -DCMAKE_CXX_COMPILER=aarch64-linux-gnu-g++
```

### Custom Build Scripts

The repository includes helper scripts:

- `build-cmake.sh` - Quick CMake build
- `build-wheels.sh` - Build wheels for all platforms
- `build-macos.sh` - macOS-specific build
- `install-deps.sh` - Install build dependencies

### Performance Optimizations

For maximum performance:

```bash
# Enable all optimizations
export CXXFLAGS="-O3 -march=native -mtune=native"

# Link-time optimization
cmake .. -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON

# Profile-guided optimization
cmake .. -DCMAKE_BUILD_TYPE=Release
make
./run_benchmarks  # Generate profile data
cmake .. -DCMAKE_CXX_FLAGS="-fprofile-use"
make
```

## Next Steps

After building libpresign:

- [Run the test suite](testing.md)
- [Check performance](benchmarks.md)
- [Start using it](quickstart.md)
- [Contribute improvements](contributing.md)