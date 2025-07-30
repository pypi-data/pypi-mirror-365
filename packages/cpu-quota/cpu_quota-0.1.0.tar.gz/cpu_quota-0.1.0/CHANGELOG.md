# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-29

### Added
- Initial release of cpu-quota package
- Core functionality migrated from standalone `get_available_cpus.py` script
- Designed specifically for shared computing environments like soma login nodes
- More accurate CPU detection than `nproc` in systems with CPU quotas
- Command-line interface with `get-available-cpus` command
- Support for `--conservative` flag to reserve CPU for system overhead
- Support for `--quiet` flag for script-friendly output
- Comprehensive test suite with mocking for systemd file access
- GitHub Actions workflow for automated publishing to PyPI and Test PyPI
- Trusted publishing configuration for secure package deployment

### Features
- **systemd CPU quota detection**: Reads actual CPU limits from `/run/systemd/system/user-$UID.slice.d/50-CPUQuota.conf`
- **Format support**: Handles both percentage format (`400%`) and decimal format (`2.5`) 
- **Conservative mode**: Intelligently reserves CPU capacity for system overhead on shared systems
- **Graceful fallback**: Uses `os.cpu_count()` when systemd quotas are not available
- **Error handling**: Continues operation with warnings when quota files cannot be parsed
- **Python API**: Provides `get_parallel_workers()` and `get_conservative_parallel_workers()` for easy integration

### Documentation
- Comprehensive README with usage examples
- API documentation with function descriptions
- Migration guide from standalone script
- Examples for multiprocessing integration
