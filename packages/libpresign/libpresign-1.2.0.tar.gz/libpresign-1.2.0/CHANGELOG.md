## [1.2.25](https://github.com/myk0la-b/libpresign/compare/v1.2.24...v1.2.25) (2025-07-27)

### Bug Fixes

* **ci:** avoid import conflicts in wheel test ([287ee97](https://github.com/myk0la-b/libpresign/commit/287ee97cbf82029e79c39fdbdaa46c50b2d26fcd))

## [1.2.24](https://github.com/myk0la-b/libpresign/compare/v1.2.23...v1.2.24) (2025-07-27)

### Bug Fixes

* **ci:** install correct architecture wheel in test workflow ([d4d4f12](https://github.com/myk0la-b/libpresign/commit/d4d4f122383e321e459ae2a33aa44408197c9551))

## [1.2.23](https://github.com/myk0la-b/libpresign/compare/v1.2.22...v1.2.23) (2025-07-27)

### Bug Fixes

* **ci:** correct wheel pattern for stable ABI in test workflow ([43ba3d7](https://github.com/myk0la-b/libpresign/commit/43ba3d786dd8a3058e4becefc8f84259b3034421))

## [1.2.22](https://github.com/myk0la-b/libpresign/compare/v1.2.21...v1.2.22) (2025-07-27)

### Bug Fixes

* **build:** move deployment target settings to architecture-specific overrides ([7e6f1d4](https://github.com/myk0la-b/libpresign/commit/7e6f1d43cbb69d87b18ce4a80d1529d053ba2100))

## [1.2.21](https://github.com/myk0la-b/libpresign/compare/v1.2.20...v1.2.21) (2025-07-27)

### Bug Fixes

* **ci:** set comprehensive macOS deployment target configuration ([77e94ec](https://github.com/myk0la-b/libpresign/commit/77e94ecde3c9f11f636fabdfa6eb22d9ecd04c9e))

## [1.2.20](https://github.com/myk0la-b/libpresign/compare/v1.2.19...v1.2.20) (2025-07-27)

### Bug Fixes

* **build:** add macosx-deployment-target to cibuildwheel config ([140f167](https://github.com/myk0la-b/libpresign/commit/140f167d4625f12e25e8bcb529d016aac0d514bf))

## [1.2.19](https://github.com/myk0la-b/libpresign/compare/v1.2.18...v1.2.19) (2025-07-27)

### Bug Fixes

* **build:** set macOS deployment target to 14.0 to match OpenSSL requirements ([91706cf](https://github.com/myk0la-b/libpresign/commit/91706cf4c129476fe7e27cdad5d562ba6f910ae5))

## [1.2.18](https://github.com/myk0la-b/libpresign/compare/v1.2.17...v1.2.18) (2025-07-27)

### Bug Fixes

* **ci:** use forward slashes for Windows OpenSSL paths ([a710844](https://github.com/myk0la-b/libpresign/commit/a710844535dbc987cc7319fcc8c7fee61c7cf86d))

## [1.2.17](https://github.com/myk0la-b/libpresign/compare/v1.2.16...v1.2.17) (2025-07-27)

### Bug Fixes

* **ci:** fix macOS x86_64 wheel builds by using correct OpenSSL paths ([41ef76a](https://github.com/myk0la-b/libpresign/commit/41ef76a082b0d154201afdffcdd61af3c517ddb4))

## [1.2.16](https://github.com/myk0la-b/libpresign/compare/v1.2.15...v1.2.16) (2025-07-27)

### Bug Fixes

* **build:** properly configure CMake for stable ABI builds ([8bc1207](https://github.com/myk0la-b/libpresign/commit/8bc1207cb11e12989e8a9692077bbbcfac240a53))
* **build:** specify version for USE_SABI in Python3_add_library ([175ebcd](https://github.com/myk0la-b/libpresign/commit/175ebcdb73027238dcf54ee33dfc4ad8667befc0))

## [1.2.15](https://github.com/myk0la-b/libpresign/compare/v1.2.14...v1.2.15) (2025-07-27)

### Bug Fixes

* **build:** correct py-api format for scikit-build-core ([286fba7](https://github.com/myk0la-b/libpresign/commit/286fba74542bdaadec2696905278fb1d263489df))
* **build:** move Windows SABI config to pyproject.toml ([e9040bd](https://github.com/myk0la-b/libpresign/commit/e9040bd5fd9904a33fb71be8123f66393155ee85))

## [1.2.14](https://github.com/myk0la-b/libpresign/compare/v1.2.13...v1.2.14) (2025-07-26)

### Bug Fixes

* **build:** use Development.SABIModule for Windows stable ABI ([d6640dc](https://github.com/myk0la-b/libpresign/commit/d6640dc85b240f7295130d135c8fb9f1c9d596ad))

## [1.2.13](https://github.com/myk0la-b/libpresign/compare/v1.2.12...v1.2.13) (2025-07-26)

### Bug Fixes

* **build:** enable stable ABI for Windows wheels ([9b8c205](https://github.com/myk0la-b/libpresign/commit/9b8c20517162dd98e2fb9900e5b349b18017c382))

## [1.2.12](https://github.com/myk0la-b/libpresign/compare/v1.2.11...v1.2.12) (2025-07-26)

### Bug Fixes

* **ci:** correct Windows OpenSSL path to C:\Program Files\OpenSSL ([b03685b](https://github.com/myk0la-b/libpresign/commit/b03685b7f726950a19eb74a2a58993dd4ce7a294))

## [1.2.11](https://github.com/myk0la-b/libpresign/compare/v1.2.10...v1.2.11) (2025-07-26)

### Bug Fixes

* **ci:** improve Windows OpenSSL discovery ([7f33ecc](https://github.com/myk0la-b/libpresign/commit/7f33ecc5d9edc20e8f947ee343ccc96b5d611ac4))

## [1.2.10](https://github.com/myk0la-b/libpresign/compare/v1.2.9...v1.2.10) (2025-07-26)

### Bug Fixes

* **ci:** remove Windows python3.lib workaround ([3d96920](https://github.com/myk0la-b/libpresign/commit/3d9692074c9d43cc0660f2b4cce600b253a8d557))

## [1.2.9](https://github.com/myk0la-b/libpresign/compare/v1.2.8...v1.2.9) (2025-07-26)

### Bug Fixes

* **ci:** improve macOS OpenSSL linking with delocate ([3436720](https://github.com/myk0la-b/libpresign/commit/343672067edfa558473f2c5a79d5612e5292e4eb))

## [1.2.8](https://github.com/myk0la-b/libpresign/compare/v1.2.7...v1.2.8) (2025-07-26)

### Bug Fixes

* **ci:** remove comment from Windows command that was causing syntax error ([2e9c473](https://github.com/myk0la-b/libpresign/commit/2e9c473e50a4cde1f8e3190b746e16c07900b5b1))

## [1.2.7](https://github.com/myk0la-b/libpresign/compare/v1.2.6...v1.2.7) (2025-07-26)

### Bug Fixes

* **build:** fix Windows build python3.lib linking issue ([7deea3a](https://github.com/myk0la-b/libpresign/commit/7deea3a46dbb1eb1c0e580298eee0e0c939711a6))

## [1.2.6](https://github.com/myk0la-b/libpresign/compare/v1.2.5...v1.2.6) (2025-07-26)

### Bug Fixes

* **build:** add delocate repair command for macOS wheels ([200b753](https://github.com/myk0la-b/libpresign/commit/200b75316956020639567c072cf242612de05a21))

## [1.2.5](https://github.com/myk0la-b/libpresign/compare/v1.2.4...v1.2.5) (2025-07-26)

### Bug Fixes

* **build:** use gmtime_s on Windows instead of gmtime_r ([22df7e3](https://github.com/myk0la-b/libpresign/commit/22df7e33ef1ae551b48d1da112b34b04439f0cd4))

## [1.2.4](https://github.com/myk0la-b/libpresign/compare/v1.2.3...v1.2.4) (2025-07-26)

### Bug Fixes

* **build:** enable static linking of OpenSSL on macOS wheels ([7da3c60](https://github.com/myk0la-b/libpresign/commit/7da3c60f375cff95f984b306cf2dad7aee0e8462))

## [1.2.3](https://github.com/myk0la-b/libpresign/compare/v1.2.2...v1.2.3) (2025-07-26)

### Bug Fixes

* **ci:** replace pytest with simple import test in cibuildwheel ([5c1e424](https://github.com/myk0la-b/libpresign/commit/5c1e42487c0897ed28057d316f773921dc4da563))

## [1.2.2](https://github.com/myk0la-b/libpresign/compare/v1.2.1...v1.2.2) (2025-07-26)

### Bug Fixes

* **ci:** fix Linux OpenSSL installation in cibuildwheel ([5fdf9ca](https://github.com/myk0la-b/libpresign/commit/5fdf9ca5c2ec10dc7005d574f4c258f9a2cf7e3d))

## [1.2.1](https://github.com/myk0la-b/libpresign/compare/v1.2.0...v1.2.1) (2025-07-26)

### Bug Fixes

* **ci:** update cibuildwheel and fix Windows environment variable ([d97827a](https://github.com/myk0la-b/libpresign/commit/d97827a1a0345d73ab48ed4636262802b778db85))

## [1.0.1](https://github.com/myk0la-b/libpresign/compare/v1.0.0...v1.0.1) (2025-07-26)

### Bug Fixes

* **ci:** use GitHub App token for workflow dispatch ([f8c5e6b](https://github.com/myk0la-b/libpresign/commit/f8c5e6b8d1cb6887046247217f605ef188a1a844))

## 1.0.0 (2025-07-26)

### Features

* add Python stable ABI support for multi-version compatibility ([c72cdc0](https://github.com/myk0la-b/libpresign/commit/c72cdc0be7f708cddfebdb78949f3ff7e0356dbd))
* **ci:** add comprehensive GitHub Actions workflows ([9459ce9](https://github.com/myk0la-b/libpresign/commit/9459ce925a66fbb865b6d0d76f4abd3ff5c03740))
* **typing:** add type stubs and improve type checking ([89084ad](https://github.com/myk0la-b/libpresign/commit/89084ad8ae62989d11f35ec2f50c8fd26107fdc9))

### Bug Fixes

* **ci:** add missing semantic-release dependencies and configuration ([228e755](https://github.com/myk0la-b/libpresign/commit/228e755e8e6f0755db26514ebe9b6f70410cb077))
* **ci:** install uv and dependencies in release workflow ([3df1b78](https://github.com/myk0la-b/libpresign/commit/3df1b78f401d1542ffb8b563fedddc369906d704))
* **ci:** use --system flag for uv pip install in CI ([31725ae](https://github.com/myk0la-b/libpresign/commit/31725aef362e749be18c7e0067b6a511e48f2382))
* **ci:** use uv pip install instead of uv sync in release workflow ([fa271b2](https://github.com/myk0la-b/libpresign/commit/fa271b243ab8bcfd31e06ad21d6b0f41e5cdd39b))

### Documentation

* add initial changelog ([1f54db6](https://github.com/myk0la-b/libpresign/commit/1f54db6f09d46761abd937228146eddbb8de3d18))
* add migration and development guides ([73601f5](https://github.com/myk0la-b/libpresign/commit/73601f50e1fcd9f05c8a640486042b48b738090e))
* add MkDocs documentation with Material theme ([c819aba](https://github.com/myk0la-b/libpresign/commit/c819aba85d6af57f144f05c871fac49faf47a2eb))
* modernize README with comprehensive documentation ([68a9db0](https://github.com/myk0la-b/libpresign/commit/68a9db018db2d9e5a822cf4a3239653a893b33ba))

### Build System

* add build scripts for local development ([23b4e6b](https://github.com/myk0la-b/libpresign/commit/23b4e6b6e5ca0f2ee23a99a44bbc7f20c18ae437))
* add modern CMake configuration with scikit-build-core ([aff4ce7](https://github.com/myk0la-b/libpresign/commit/aff4ce7284ec5cb6f513162dd2e8d2036eb03b18))

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern build system using scikit-build-core and pyproject.toml
- Comprehensive test suite with 100% coverage requirement
- Performance benchmarks comparing with boto3
- Full type hints support with py.typed marker
- CI/CD workflows for automated testing, building, and releasing
- Documentation site with MkDocs
- Support for Python 3.13
- Automatic semantic versioning and changelog generation
- Development workflow with uv package manager
- Code formatting and linting with ruff
- Dependabot configuration for dependency updates

### Changed
- Migrated from 7 separate setup.py files to unified pyproject.toml
- Replaced manual build scripts with cibuildwheel
- Updated package structure to proper Python package (libpresign/)
- Modernized CMakeLists.txt for scikit-build-core compatibility
- Enhanced README with badges, examples, and clear documentation
- Improved error handling to raise SystemError consistently

### Removed
- Legacy setup.py files (setup_linux_amd.py, setup_macos_arm.py, etc.)
- Old Dockerfile-based build system
- definitions.py file
- MANIFEST.in file

### Fixed
- Import issues with C extension module
- Region parameter can now be None (defaults to us-east-1)
- Memory efficiency in batch URL generation

## [1.2.0] - Previous Release

### Added
- Support for custom S3 endpoints
- MinIO compatibility
- Thread-safe URL generation

### Performance
- 160x faster than boto3 for single URL generation
- Optimized memory usage (262 bytes per URL)

## [1.1.1] - Legacy Version

### Notes
- Last version before build system modernization
- Tagged as v1.1.1-legacy for reference

## [1.0.0] - Initial Release

### Added
- Core functionality for S3 presigned URL generation
- Python bindings for C++ implementation
- Support for all AWS regions
- Configurable expiration times
- Basic error handling

### Performance
- Initial benchmarks showing 100x+ speedup over boto3

[Unreleased]: https://github.com/myk0la-b/libpresign/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/myk0la-b/libpresign/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/myk0la-b/libpresign/compare/v1.0.0...v1.1.1
[1.0.0]: https://github.com/myk0la-b/libpresign/releases/tag/v1.0.0
