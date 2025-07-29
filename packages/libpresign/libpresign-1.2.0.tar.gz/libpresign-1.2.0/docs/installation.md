# Installation

libpresign provides pre-built wheels for most platforms, making installation quick and easy.

## Requirements

- Python 3.8 or higher
- pip 19.3 or higher (for manylinux2014 support)

## Quick Install

=== "pip"

    ```bash
    pip install libpresign
    ```

=== "uv"

    ```bash
    uv add libpresign
    ```

=== "poetry"

    ```bash
    poetry add libpresign
    ```

=== "pipenv"

    ```bash
    pipenv install libpresign
    ```

## Supported Platforms

libpresign provides pre-built binary wheels for the following platforms:

| Platform | Architecture | Python Versions |
|----------|--------------|-----------------|
| Linux | x86_64 | 3.8-3.13 |
| Linux | aarch64 | 3.8-3.13 |
| macOS | x86_64 | 3.8-3.13 |
| macOS | arm64 (Apple Silicon) | 3.8-3.13 |
| Windows | AMD64 | 3.8-3.13 |

!!! note "Platform Notes"
    - Linux wheels are manylinux2014 compatible
    - macOS wheels are universal2 when possible
    - Windows wheels require Visual C++ 2015-2022 Redistributable

## Verify Installation

After installation, verify that libpresign is working correctly:

```python
import libpresign

# Check version
print(f"libpresign version: {libpresign.__version__}")

# Test basic functionality
url = libpresign.get(
    access_key_id="test",
    secret_access_key="test",
    region="us-east-1",
    bucket="test-bucket",
    key="test.txt"
)
print(f"Generated URL: {url[:50]}...")
```

## Installing from Source

If pre-built wheels are not available for your platform, you can build from source.

### Prerequisites

- C++ compiler with C++11 support
- CMake 3.15 or higher
- OpenSSL 3.x development files
- Python development headers

=== "Ubuntu/Debian"

    ```bash
    sudo apt-get update
    sudo apt-get install build-essential cmake libssl-dev python3-dev
    ```

=== "RHEL/CentOS/Fedora"

    ```bash
    sudo yum install gcc-c++ cmake3 openssl-devel python3-devel
    ```

=== "macOS"

    ```bash
    brew install cmake openssl@3
    ```

=== "Windows"

    Install Visual Studio 2019 or later with C++ support, then:
    ```powershell
    choco install cmake openssl
    ```

### Build and Install

```bash
# Clone the repository
git clone https://github.com/myk0la-b/libpresign.git
cd libpresign

# Install build dependencies
pip install -U pip build

# Build and install
pip install .
```

## Development Installation

For development work, install in editable mode with development dependencies:

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Using pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Troubleshooting

### ImportError: libpresign module not found

This usually means the C extension failed to build. Check that:

1. You have a C++ compiler installed
2. OpenSSL development files are available
3. Python development headers are installed

### OpenSSL not found during build

=== "macOS"

    ```bash
    export OPENSSL_ROOT_DIR=$(brew --prefix openssl@3)
    pip install libpresign
    ```

=== "Linux"

    ```bash
    # Install OpenSSL development files
    sudo apt-get install libssl-dev  # Debian/Ubuntu
    sudo yum install openssl-devel   # RHEL/CentOS
    ```

=== "Windows"

    ```powershell
    # Set OpenSSL location
    $env:OPENSSL_ROOT_DIR="C:\Program Files\OpenSSL-Win64"
    pip install libpresign
    ```

### Unsupported platform

If your platform is not supported by pre-built wheels, you'll need to build from source. Please ensure all prerequisites are installed.

## Next Steps

Now that you have libpresign installed, check out the [Quick Start guide](quickstart.md) to learn how to use it.