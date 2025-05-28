# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.8] - 2025-05-28

### Fixed
- **Architecture Simplification**: Completely refactored entry points according to FastMCP documentation
  - Removed complex event loop detection logic from `main.py` and `src/mcp_optimizer/main.py`
  - Use simple `mcp.run(transport="stdio")` pattern as recommended by FastMCP
  - Separated sync and async contexts properly: `run()` for sync, `run_async()` for async
  - Fixed "capture_exceptions" parameter error by following FastMCP API correctly


## [0.3.7] - 2025-05-28

### Fixed
- **Documentation**: Fixed outdated workflow references in repository setup documentation
  - Replaced `auto-finalize-release.yml` references with `ci.yml` (release job)
  - Updated `REPOSITORY_SETUP.md` to reference unified CI/CD pipeline
  - Corrected workflow troubleshooting instructions to reflect current architecture
- **CI/CD Pipeline**: Added `merge/*` branches to pipeline triggers
  - Enables CI checks for merge-back branches before creating PRs to develop
  - Ensures merge-back branches pass all required status checks
  - Improves reliability of automated release-to-develop merge process
  - Updated `CONTRIBUTING.md` and `RELEASE_PROCESS.md` to document merge/* branch workflow
- **Docker Build**: Fixed Docker tag generation for release and hotfix branches
  - Corrected tag patterns to use full ref paths (`refs/heads/release/v*` instead of `release/v*`)
  - Resolves "tag is needed when pushing to registry" error for release branches
  - Ensures proper RC and hotfix Docker image tagging
  - Fixed Docker metadata tag generation for release and hotfix branches to properly extract version from branch names
  - Fixed hardcoded version in `mcp_server.py` to use dynamic version from package metadata instead of outdated `0.1.0`
  - Improved Docker tagging strategy to follow industry best practices: `main` branch now uses `main` tag instead of `main-<sha>`
- **Development Tools**: Removed outdated `scripts/test_release_detection.py`
  - File contained obsolete simple regex patterns that don't match current triple-fallback detection system
  - Current detection logic is thoroughly tested in production CI/CD pipeline
  - Removed references from documentation to avoid confusion
  - Real-world testing in CI/CD provides better validation than isolated test script

## [0.3.6] - 2025-05-28

### Fixed
- **CLI Entry Point**: Fixed CLI command execution error with coroutine handling
  - Corrected entry point in `pyproject.toml` from `main` to `cli_main` function
  - Resolved `<coroutine object main>` error when running `uvx mcp-optimizer`
  - Fixed `RuntimeWarning: coroutine 'main' was never awaited` issue
- **Release Candidate Documentation**: Corrected installation instructions for RC builds
  - Removed incorrect PyPI installation info (RC packages are not published to PyPI)
  - Added proper GitHub Release download instructions for testing RC builds
  - Clarified that release candidates are only available via GitHub Release artifacts
- **Repository Documentation**: Fixed status check names in setup documentation
  - Corrected `ci` → `test (3.11)`, `test (3.12)` in branch protection requirements
  - Corrected `security-scan` → `security` to match actual CI job names
  - Updated both `REPOSITORY_SETUP.md` and `RELEASE_PROCESS.md` with accurate job names

### Changed
- **Version**: Bumped to 0.3.7 for next development cycle

## [0.3.5] - 2025-05-28

### Fixed
- **CI/CD Pipeline**: Critical fixes for PyPI publishing and merge-back automation
  - Fixed PyPI publishing job failure due to missing package artifacts
    - Replaced unreliable GitHub release download with GitHub Actions artifacts
    - Added `upload-artifact` step in release job to preserve build artifacts
    - Updated `pypi-publish` job to use `download-artifact` for reliable artifact retrieval
  - Fixed merge-back job permission and authentication issues
    - Added missing `actions` permission for GitHub Actions operations
    - Added required `GH_TOKEN` environment variable for GitHub CLI operations
    - Implemented intelligent merge conflict resolution for workflow files
  - Enhanced merge-back automation with three-tier conflict resolution strategy
    - Primary: Merge with `-X ours` strategy (prefer main branch for conflicts)
    - Secondary: Standard merge attempt
    - Tertiary: Automatic workflow conflict resolution + manual issue creation for remaining conflicts

### Changed
- **Artifact Management**: Improved reliability of package distribution between CI jobs
  - Standardized artifact naming (`python-package-distributions`) across pipeline
  - Eliminated timing issues with GitHub release file availability
  - Reduced dependency on external GitHub CLI for artifact management
- **Merge Strategy**: Enhanced automation for release-to-develop merges
  - Automatic resolution of workflow file conflicts in favor of main branch
  - Detailed conflict reporting and resolution guidance in created issues
  - Improved PR descriptions with conflict resolution notes

## [0.3.4] - 2025-05-28

### Fixed
- **CI/CD Pipeline**: Resolved PyPI publishing failures and simplified pipeline architecture
  - Fixed OIDC token retrieval failures (503 errors) by splitting publishing into separate jobs

### Changed
- **Pipeline Architecture**: Refactored release process for better reliability and maintainability
  - Split PyPI and Docker publishing into separate parallel jobs (`pypi-publish`, `docker-publish`)
  - Simplified `release` job to focus on core release tasks (tagging, GitHub Release creation)
  - Removed complex error handling and retry mechanisms in favor of manual job re-runs
  - Enhanced workflow summary to reflect new job structure and parallel execution
- **Job Dependencies**: Optimized job execution flow
  - `pypi-publish` and `docker-publish` jobs run in parallel after `release` completion
  - `merge-back` job runs independently of publishing jobs
  - Failed publishing jobs can be re-run individually without affecting other jobs

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
- **CI/CD Optimization**: Optimized Docker image build and push strategy
  - Build job now only pushes images for main, develop, release/*, and hotfix/* branches
  - Feature and merge branches only build images for validation (no push to registry)
  - Eliminates unnecessary Docker images for temporary branches
  - Reduces CI/CD time and registry storage usage
  - Prevents registry pollution with temporary development images

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