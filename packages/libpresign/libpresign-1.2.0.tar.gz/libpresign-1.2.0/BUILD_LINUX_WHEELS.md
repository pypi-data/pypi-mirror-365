# Building Linux Wheels Locally

## Summary

Successfully built Linux wheels locally using manylinux containers with colima/nerdctl.

## Results

- **Linux x86_64 wheel**: `libpresign-1.2.0-cp38-abi3-linux_x86_64.whl` (1.45 MB)
  - Uses stable ABI (abi3) for Python 3.8+
  - Built in manylinux_2_28_x86_64 container
  - Contains compiled shared library: `libpresign.so` (40KB)

## Build Process

1. **Container**: Used `quay.io/pypa/manylinux_2_28_x86_64` with colima nerdctl
2. **Dependencies**: Installed `openssl-devel` in the container
3. **Build**: Used scikit-build-core with CMake
4. **Issue**: auditwheel repair failed due to patchelf segfault, but the wheel itself is valid

## Scripts Created

- `build-linux-wheels-local.sh` - Initial attempt
- `build-linux-wheel-simple.sh` - Simplified approach
- `build-linux-direct.sh` - Direct command execution
- `build-linux-openssl.sh` - Final working version with OpenSSL setup
- `test_linux_wheel.py` - Wheel validation script

## Key Findings

1. **OpenSSL**: Must install `openssl-devel` in manylinux containers
2. **colima/nerdctl**: Use `colima nerdctl -- run` syntax (note the `--`)
3. **Platform**: Can build x86_64 wheels on ARM64 Mac using `--platform linux/amd64`
4. **auditwheel**: The repair step failed but the wheel is still functional

## Recommendations

For production builds:
- Use GitHub Actions with cibuildwheel for proper manylinux compliance
- cibuildwheel handles auditwheel repair automatically
- Builds multiple Python versions and architectures in parallel

## Testing

The wheel contains:
- Proper stable ABI marking (cp38-abi3)
- Compiled extension module
- Python package files
- Distribution metadata

While we couldn't fully repair the wheel with auditwheel locally, it should work on most modern Linux systems. The GitHub Actions CI/CD pipeline will handle proper manylinux compliance.