# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.4] - 2025-05-28

## [0.3.3] - 2025-05-28

### Fixed
- **CI/CD Pipeline**: Fixed PyPI publishing with Trusted Publisher configuration
  - Eliminated unnecessary `github.ref_type != 'tag'` condition after removing tag triggers
- **Code Quality**: Improved workflow maintainability
  - Translated all Russian comments to English in CI/CD pipeline
  - Enhanced code readability and international collaboration support

### Changed
- **CI/CD Optimization**: Streamlined build job conditions
  - Removed obsolete tag-related checks from build job
  - Simplified workflow logic after tag trigger removal

## [0.3.2] - 2025-05-27

### Fixed
- **CI/CD Pipeline Optimization**: Unified multiple pipeline files into single efficient workflow
  - Consolidated `.github/workflows/ci.yml`, `release-branch.yml`, and `auto-finalize-release.yml` into unified pipeline
  - Eliminated pipeline duplication and race conditions for release branches
  - Added smart job execution based on branch type (main, release/*, hotfix/*, develop, feature/*)
  - Implemented emergency release support with `force_release` and `skip_tests` options
- **Release Process Improvements**: Enhanced automation and reliability
  - Added triple-fallback release detection system (git branch analysis, version change analysis, commit message analysis)
  - Improved automatic merge-back to develop with conflict handling via PR creation
  - Added comprehensive release validation and logging
  - Enhanced release candidate automation for release branches
- **Development Tools**: Fixed version synchronization issues
  - Fixed `scripts/release.py` to automatically sync `uv.lock` after version updates in `pyproject.toml`
  - Prevents dirty git status after running `uv run` commands post-release
  - Added error handling for sync failures with graceful degradation

### Added
- **Unified CI/CD Pipeline**: Single pipeline handling all branch types and scenarios
  - Branch-specific job execution (test + security + build + release/release-candidate + merge-back)
  - Emergency release capabilities via workflow dispatch
  - Automatic release candidate builds for release branches with RC tags
  - Intelligent merge-back automation with conflict resolution
- **Enhanced Documentation**: Comprehensive pipeline and release process documentation
  - Updated `.github/RELEASE_PROCESS.md` with unified pipeline architecture
  - Added emergency procedures and debugging guides
  - Documented job distribution by branch type and detection methods

### Changed
- **Pipeline Architecture**: Streamlined from 3 separate workflows to 1 unified workflow
  - Improved resource efficiency and eliminated redundant executions
  - Centralized logging and monitoring for better debugging
  - Consistent behavior across all branch types

## [0.3.1] - 2025-05-27

### Fixed
- Fixed CI/CD pipeline duplication by separating release branch workflows from main CI
- Enhanced release detection with triple-fallback system (git-based, version-based, message-based)
- Fixed version parsing in auto-finalize-release.yml to target [project] section specifically
- Improved merge conflict handling with automatic PR creation for develop branch merges
- Fixed GitHub CLI installation in auto-finalize workflow for issue creation capabilities

## [0.3.0] - 2025-05-26

### Added
- **Examples Directory**: Comprehensive usage examples in Russian and English
  - Linear programming examples (production, diet, transportation, blending)
  - Assignment problems examples (employee-project, machine-order, task distribution)
  - Portfolio optimization examples (basic, diversified, retirement, aggressive growth)
  - Ready-to-use LLM prompts for each optimization type
  - Bilingual documentation (Russian/English) with practical scenarios
- Multiple installation options (uvx, pip, Docker) in README.md
- Organized project structure with proper file locations
- Automated release script (`scripts/release.py`)
- CI/CD pipeline with PyPI publication
- Comprehensive release documentation
- Development tools documentation (debug_tools.py, comprehensive_test.py)
- Docker build optimization

### Changed
- **Docker Optimization**: Improved image size and performance
  - Multi-stage builds with Python 3.12 Slim (Debian-based)
  - Optimized Python bytecode compilation (PYTHONOPTIMIZE=2)
  - Cleaned build artifacts while preserving essential modules
  - Enhanced security with non-root user (mcp:mcp)
  - Build cache optimization with UV_CACHE_DIR
  - Final image size: ~649MB (down from previous versions)
- Moved `comprehensive_test.py` to `tests/test_integration/`
- Moved `debug_tools.py` to `scripts/`
- Updated README.md with comprehensive installation instructions and usage examples
- Updated installation instructions to use PyPI packages
- Enhanced README.md with detailed Docker build instructions
- Added PyPI publication to GitHub Actions workflow

### Fixed
- Docker build issues with missing README.md and package configuration
- Hatchling build configuration for proper package structure
- PuLP test module dependencies in Docker image (preserved essential test modules)
- Docker build optimization while maintaining full functionality

## [0.2.0] - 2024-01-XX

### Added
- Complete function exports for all optimization tools
- Enhanced comprehensive test suite with 9 integration tests
- Performance optimization and testing
- Production-ready Docker and Kubernetes deployment
- Monitoring setup with Grafana and Prometheus
- Complete documentation translation to English

### Fixed
- Function export issues in tool modules
- Test compatibility and function signatures
- OR-Tools integration stability

### Changed
- Renamed MCP tool functions to avoid naming conflicts
- Updated test structure and organization
- Improved error handling and validation

## [0.1.0] - 2024-01-XX

### Added
- Initial MCP Optimizer server implementation
- Core optimization tools:
  - Linear Programming (PuLP integration)
  - Assignment Problems (OR-Tools Hungarian algorithm)
  - Transportation Problems (OR-Tools)
  - Knapsack Problems (0-1, bounded, unbounded)
  - Routing Problems (TSP, VRP with time windows)
  - Scheduling Problems (Job and shift scheduling)
  - Integer Programming
  - Financial Optimization (Portfolio optimization)
  - Production Planning (Multi-period planning)
- FastMCP server integration
- Pydantic schema validation
- Comprehensive test suite (66 unit tests)
- Docker containerization
- Basic documentation

### Technical Details
- Python 3.12+ support
- OR-Tools and PuLP solver integration
- Support for multiple solvers (CBC, GLPK, GUROBI, CPLEX, SCIP, CP-SAT)
- MCP protocol compliance
- Type hints and validation
- Async/await support

### Performance
- Linear Programming: ~0.01s
- Assignment Problems: ~0.01s  
- Knapsack Problems: ~0.01s
- Complex test suite: 0.02s for 3 optimization problems
- Overall test execution: < 30s for full suite

### Infrastructure
- GitHub Actions CI/CD
- Docker multi-stage builds
- Kubernetes deployment manifests
- Monitoring and observability setup
- Development environment with uv

---

## Release Notes

### Version 0.2.0 - Production Ready Release
This release marks the project as production-ready with complete functionality restoration, comprehensive testing, and international documentation.

### Version 0.1.0 - Initial Release  
First stable release with core optimization capabilities and MCP server integration.

---

## Migration Guide

### From 0.1.x to 0.2.x
- Update import paths if using direct function imports
- Review function signatures for any breaking changes
- Update Docker images to latest version
- Check new installation options (uvx recommended)

---

## Contributors

- Initial development and architecture
- OR-Tools integration and optimization
- FastMCP server implementation
- Comprehensive testing and validation
- Documentation and internationalization

---

## Support

For questions, issues, or contributions:
- 📧 Email: support@mcp-optimizer.com
- 🐛 Issues: [GitHub Issues](https://github.com/dmitryanchikov/mcp-optimizer/issues)
- 📖 Documentation: [docs/](docs/) 