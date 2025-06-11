# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-06-11

### Added
- **Dependency Management**: Added `stable` optional dependency group for reliable installations
  - Added `stable` group in `[project.optional-dependencies]` with pinned versions
  - Includes fastmcp==2.7.0, sse-starlette==2.2.1, starlette==0.46.1, uvicorn==0.34.0
  - Resolves ASGI compatibility issues with latest dependency versions
  - Enables stable SSE mode via `pip install "mcp-optimizer[stable]"`
- **Test Coverage**: Significantly improved test coverage to more than 90%
  - Enhanced test suite with comprehensive coverage of optimization tools
  - Added edge case testing and error handling validation
  - Improved reliability and maintainability of the codebase

### Changed
- **Release Tooling**: Renamed finalize release script to reflect its manual nature
  - Renamed `scripts/finalize_release.py` → `scripts/manual_finalize_release.py`
  - Updated all documentation references to reflect emergency/fallback purpose
  - Enhanced script description to emphasize manual use when CI/CD automation fails
- **Installation Recommendations**: Updated recommended installation order and documentation
  - Prioritized Docker (maximum stability) over pip for production use
  - Updated README.md with clear cross-platform compatibility matrix
  - Enhanced uvx troubleshooting section with direct links to fix scripts
  - Translated all documentation to English for international accessibility

### Documentation
- **Dependency Management**: Added comprehensive dependency strategy documentation
  - Documented version conflicts between fastmcp/starlette/sse-starlette packages
  - Provided best practices for Python package dependency management
  - Explained why uvx caches stable versions while pip installs latest

## [0.3.9] - 2025-06-06

### Added
- **Automated Test Scripts**: Comprehensive testing automation for local and Docker builds
  - Added `test_local_package.sh` for local package build and functionality testing
  - Added `test_docker_container.sh` for Docker container build and validation
  - Added `test_all.sh` for comprehensive test suite with parallel execution
  - Cross-platform compatibility (macOS/Linux) with automatic cleanup

### Removed
- **Non-functional Docker builds**: Removed distroless Docker configuration
  - Deleted `docker/Dockerfile.distroless` that was incompatible with OR-Tools
  - Removed `docker/README.md` containing documentation for non-working solutions
  - Cleaned up references to non-functional distroless builds in documentation
- **Redundant documentation**: Consolidated documentation structure
  - Removed `docker_size_analysis.md` - migrated to main README.md
  - Eliminated duplicate documentation and improved information organization

### Added
- **License**: Added MIT License file to the repository
  - Created LICENSE file with proper MIT license text and copyright notice
  - Enables proper open source licensing and distribution
- **Manual Docker Push**: New workflow_dispatch option for pushing Docker images from any branch
  - Enables testing and debugging of Docker images from feature/merge branches
  - Controlled via push_docker boolean input in GitHub Actions UI
  - Separate docker-push-manual job handles these requests
- **Enhanced Workflow Documentation**: Comprehensive inline documentation
  - Detailed job structure and strategy comments in CI/CD pipeline
  - Anti-duplication logic documentation
  - Branch-specific behavior explanations
- **Resource Monitoring System**: Comprehensive resource monitoring and concurrency control
  - Added `ResourceMonitor` class with memory monitoring via `psutil`
  - Implemented asyncio semaphore-based concurrency control for optimization requests
  - Created `@with_resource_limits` decorator for timeout and memory estimation
  - Added custom exceptions: `MemoryExceededError`, `ConcurrencyLimitError`
  - Health check endpoints with detailed resource metrics and status reporting

- **MCP Server Enhancements**: Production-ready server configuration
  - Integrated resource monitoring into MCP server with health endpoints
  - Added server info and resource statistics endpoints for monitoring
  - Graceful shutdown with proper resource cleanup
  - Real-time resource status tracking with configurable limits

- **MCP Transport Support**: Flexible MCP server deployment modes
  - Added SSE transport mode for remote MCP clients with uvicorn
  - Maintained stdio transport for local MCP client compatibility
  - Environment-based transport mode selection via `TRANSPORT_MODE`
  - Explicit uvicorn configuration with single worker architecture

- **Tool Resource Management**: Individual resource limits for optimization tools
  - Applied `@with_resource_limits` decorator to all 15 optimization tools
  - Configured individual timeouts and memory estimates per tool type:
    - Linear/Integer Programming: 60-90s, 100-150MB
    - Routing (TSP/VRP): 120-180s, 150-250MB
    - Scheduling: 90-120s, 120-200MB
    - Knapsack/Assignment: 60s, 80-100MB
    - Financial/Production: 90-120s, 150-200MB

### Fixed
- **CI/CD Pipeline**: Critical fixes for Docker image duplication and workflow execution
  - Fixed double Docker image pushes during releases (docker-push-auto + docker-push-release)
  - Fixed pipeline not executing on merge/* branches due to incorrect job conditions
  - Fixed incorrect PR titles for hotfixes showing "release" instead of "hotfix"
  - Corrected test and security job conditions to properly handle push events vs workflow_dispatch
- **Merge-back Automation**: Enhanced release type detection and naming
  - Added release_type output to release job for proper hotfix/release/emergency distinction
  - Updated merge-back PR titles and descriptions to correctly reflect hotfix vs release
  - Fixed branch naming in merge-back process to handle different release types
  - Enhanced commit messages and labels to use appropriate release type terminology
- **Code Quality**: Replaced Russian comments with English in release scripts
  - Updated `scripts/manual_finalize_release.py` to use English comments throughout
  - Improved code maintainability and international collaboration support
- **Environment Configuration**: Corrected environment variable naming
  - Fixed environment variables by removing incorrect `MCP_OPTIMIZER_` prefix
  - Updated variable names to match application expectations: `LOG_LEVEL`, `MAX_SOLVE_TIME`, etc.
  - Synchronized configuration across Docker, Kubernetes, and local development

- **Kubernetes Configuration**: Removed hardcoded version labels from deployment manifests
  - Removed obsolete `app.kubernetes.io/version: "0.1.0"` labels from k8s/deployment.yaml
  - Prevents version drift and maintenance overhead in Kubernetes manifests
  - Version information available through Docker image tags instead

- **Type Safety**: Comprehensive mypy error resolution
  - Fixed all mypy type checking errors across 23 source files
  - Corrected return type annotations in tool functions
  - Added explicit type annotations to suppress no-any-return warnings
  - Fixed decorator ordering for proper type inference

- **Docker Configuration**: Corrected Docker Compose and Dockerfile settings
  - Removed invalid `target: production` from docker-compose.yml
  - Updated Dockerfile environment variables to match application expectations
  - Fixed health check configuration for proper server validation

### Changed
- **CI/CD Architecture**: Separated build and Docker push responsibilities for better control
  - Split Docker operations into separate jobs: docker-push-auto, docker-push-manual, docker-push-release
  - Added push_docker option to workflow_dispatch for manual Docker pushes from non-main/develop branches
  - Implemented anti-duplication logic: docker-push-auto skips main branch when release is detected
  - Enhanced workflow summary with detailed status reporting for all Docker operations
- **Docker Registry Strategy**: Improved tagging and push logic
  - main branch → main tag (only for non-release pushes)
  - develop branch → develop tag (always)
  - feature/* → feature-{name} tag (manual only via workflow_dispatch)
  - merge/* → merge-{name} tag (manual only via workflow_dispatch)
  - releases → versioned tags (v1.2.3, 1.2, 1, latest) via docker-push-release
- **Documentation**: Streamlined Docker documentation and removed non-working solutions
  - Removed `docker/` directory containing non-functional distroless Docker image
  - Updated main README.md to reflect only working Docker optimization approaches
  - Removed `docker_size_analysis.md` file, migrated relevant content to main README
  - Clarified that distroless approach is incompatible with OR-Tools requirements
- **Dependencies Architecture**: Refactored project dependencies for cleaner separation
  - Moved `pandas>=2.0.0` and `numpy>=1.24.0` from core dependencies to optional `[examples]` extra
  - Core package now includes only essential dependencies: `fastmcp`, `ortools`, `pulp`, `pydantic`, `uvicorn`
  - Updated installation instructions: use `pip install "mcp-optimizer[examples]"` for running integration examples
  - **Note**: pandas and numpy still present in Docker images due to OR-Tools hard requirements
- **Documentation**: Updated README and examples documentation
  - Added installation instructions for examples dependencies in README.md
  - Updated examples/integration/README.md with correct dependency installation commands
  - Enhanced streamlit_dashboard.py with comprehensive installation notes
  - Updated Docker image size analysis with correct dependency constraints explanation
- **Docker Image Analysis**: Clarified dependency constraints in optimization documentation
  - Documented that OR-Tools requires pandas and numpy as mandatory dependencies (`pandas>=2.0.0`, `numpy>=1.13.3`)
  - Updated image size analysis to reflect actual constraints preventing further optimization
  - Current optimized size: ~420MB (cannot be reduced further due to OR-Tools requirements)
- **Architecture**: Single worker + asyncio semaphore design
  - Explicitly configured `WORKERS=1` for optimal CPU-intensive math operations
  - Implemented asyncio-based concurrency instead of multiple uvicorn workers
  - Leveraged GIL release in PuLP/OR-Tools for true parallelism within single process
  - Optimized memory usage through shared libraries and process pools

- **Configuration Management**: Unified environment variable strategy
  - Standardized configuration across Docker Compose, Kubernetes, and local development
  - Added comprehensive environment variable documentation in deployment configs
  - Enhanced configuration validation and error reporting

- **Dependency Management**: Added psutil for resource monitoring
  - Added `psutil>=5.9.0` to project dependencies for memory monitoring
  - Implemented efficient resource monitoring with caching to minimize overhead
  - Added lazy loading and background monitoring for long-running operations

### Documentation
- **Architecture Documentation**: Documented single worker design rationale
  - Explained why 1 worker + asyncio is more efficient than N workers for math optimization
  - Documented GIL release behavior in PuLP/OR-Tools for parallel execution
  - Added performance comparison and resource utilization analysis

- **Configuration Guide**: Comprehensive environment variable documentation
  - Documented all configuration options with examples and defaults
  - Added deployment-specific configuration recommendations
  - Enhanced troubleshooting guides for resource monitoring issues

## [0.3.8] - 2025-05-28

### Fixed
- **Architecture Simplification**: Completely refactored entry points according to FastMCP documentation
  - Removed complex event loop detection logic from `main.py` and `src/mcp_optimizer/main.py`
  - Use simple `mcp.run(transport="stdio")` pattern as recommended by FastMCP
  - Separated sync and async contexts properly: `run()` for sync, `run_async()` for async
  - Fixed "capture_exceptions" parameter error by following FastMCP API correctly
- **Linting and Code Quality**: Comprehensive linting fixes and configuration improvements
  - Fixed all ruff and mypy linting issues across the codebase
  - Restructured `pyproject.toml` configuration with proper tool sections
  - Added proper type ignores for OR-Tools compatibility issues
  - Fixed unreachable code warnings in validation patterns
  - Updated deprecated ruff configuration settings
  - Added MyPy overrides for modules with specific validation patterns

### Changed
- **Architecture Simplification**: Further simplified entry points based on FastMCP best practices
  - Removed remaining complex event loop detection logic
  - Streamlined `main.py` to use simple `mcp.run(transport="stdio")` pattern
  - Improved separation of sync and async contexts in CLI
  - Enhanced logging consistency across entry points
- **Code Quality**: Improved type safety and maintainability
  - Added comprehensive type annotations and ignores
  - Fixed OR-Tools type conflicts with proper type casting
  - Improved error handling in optimization tools
  - Enhanced code documentation and comments

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
- **Automated Test Scripts**: Comprehensive testing automation for local and Docker builds
  - Added `test_local_package.sh` for local package build and functionality testing
  - Added `test_docker_container.sh` for Docker container build and validation
  - Added `test_all.sh` for comprehensive test suite with parallel execution
  - Cross-platform compatibility (macOS/Linux) with automatic cleanup

### Removed
- **Non-functional Docker builds**: Removed distroless Docker configuration
  - Deleted `docker/Dockerfile.distroless` that was incompatible with OR-Tools
  - Removed `docker/README.md` containing documentation for non-working solutions
  - Cleaned up references to non-functional distroless builds in documentation
- **Redundant documentation**: Consolidated documentation structure
  - Removed `docker_size_analysis.md` - migrated to main README.md
  - Eliminated duplicate documentation and improved information organization

### Added
- **License**: Added MIT License file to the repository
  - Created LICENSE file with proper MIT license text and copyright notice
  - Enables proper open source licensing and distribution
- **Manual Docker Push**: New workflow_dispatch option for pushing Docker images from any branch
  - Enables testing and debugging of Docker images from feature/merge branches
  - Controlled via push_docker boolean input in GitHub Actions UI
  - Separate docker-push-manual job handles these requests
- **Enhanced Workflow Documentation**: Comprehensive inline documentation
  - Detailed job structure and strategy comments in CI/CD pipeline
  - Anti-duplication logic documentation
  - Branch-specific behavior explanations
- **Resource Monitoring System**: Comprehensive resource monitoring and concurrency control
  - Added `ResourceMonitor` class with memory monitoring via `psutil`
  - Implemented asyncio semaphore-based concurrency control for optimization requests
  - Created `@with_resource_limits` decorator for timeout and memory estimation
  - Added custom exceptions: `MemoryExceededError`, `ConcurrencyLimitError`
  - Health check endpoints with detailed resource metrics and status reporting

- **MCP Server Enhancements**: Production-ready server configuration
  - Integrated resource monitoring into MCP server with health endpoints
  - Added server info and resource statistics endpoints for monitoring
  - Graceful shutdown with proper resource cleanup
  - Real-time resource status tracking with configurable limits

- **MCP Transport Support**: Flexible MCP server deployment modes
  - Added SSE transport mode for remote MCP clients with uvicorn
  - Maintained stdio transport for local MCP client compatibility
  - Environment-based transport mode selection via `TRANSPORT_MODE`
  - Explicit uvicorn configuration with single worker architecture

- **Tool Resource Management**: Individual resource limits for optimization tools
  - Applied `@with_resource_limits` decorator to all 15 optimization tools
  - Configured individual timeouts and memory estimates per tool type:
    - Linear/Integer Programming: 60-90s, 100-150MB
    - Routing (TSP/VRP): 120-180s, 150-250MB
    - Scheduling: 90-120s, 120-200MB
    - Knapsack/Assignment: 60s, 80-100MB
    - Financial/Production: 90-120s, 150-200MB

### Fixed
- **CI/CD Pipeline**: Critical fixes for Docker image duplication and workflow execution
  - Fixed double Docker image pushes during releases (docker-push-auto + docker-push-release)
  - Fixed pipeline not executing on merge/* branches due to incorrect job conditions
  - Fixed incorrect PR titles for hotfixes showing "release" instead of "hotfix"
  - Corrected test and security job conditions to properly handle push events vs workflow_dispatch
- **Merge-back Automation**: Enhanced release type detection and naming
  - Added release_type output to release job for proper hotfix/release/emergency distinction
  - Updated merge-back PR titles and descriptions to correctly reflect hotfix vs release
  - Fixed branch naming in merge-back process to handle different release types
  - Enhanced commit messages and labels to use appropriate release type terminology
- **Code Quality**: Replaced Russian comments with English in release scripts
  - Updated `scripts/manual_finalize_release.py` to use English comments throughout
  - Improved code maintainability and international collaboration support
- **Environment Configuration**: Corrected environment variable naming
  - Fixed environment variables by removing incorrect `MCP_OPTIMIZER_` prefix
  - Updated variable names to match application expectations: `LOG_LEVEL`, `MAX_SOLVE_TIME`, etc.
  - Synchronized configuration across Docker, Kubernetes, and local development

- **Kubernetes Configuration**: Removed hardcoded version labels from deployment manifests
  - Removed obsolete `app.kubernetes.io/version: "0.1.0"` labels from k8s/deployment.yaml
  - Prevents version drift and maintenance overhead in Kubernetes manifests
  - Version information available through Docker image tags instead

- **Type Safety**: Comprehensive mypy error resolution
  - Fixed all mypy type checking errors across 23 source files
  - Corrected return type annotations in tool functions
  - Added explicit type annotations to suppress no-any-return warnings
  - Fixed decorator ordering for proper type inference

- **Docker Configuration**: Corrected Docker Compose and Dockerfile settings
  - Removed invalid `target: production` from docker-compose.yml
  - Updated Dockerfile environment variables to match application expectations
  - Fixed health check configuration for proper server validation

### Changed
- **CI/CD Architecture**: Separated build and Docker push responsibilities for better control
  - Split Docker operations into separate jobs: docker-push-auto, docker-push-manual, docker-push-release
  - Added push_docker option to workflow_dispatch for manual Docker pushes from non-main/develop branches
  - Implemented anti-duplication logic: docker-push-auto skips main branch when release is detected
  - Enhanced workflow summary with detailed status reporting for all Docker operations
- **Docker Registry Strategy**: Improved tagging and push logic
  - main branch → main tag (only for non-release pushes)
  - develop branch → develop tag (always)
  - feature/* → feature-{name} tag (manual only via workflow_dispatch)
  - merge/* → merge-{name} tag (manual only via workflow_dispatch)
  - releases → versioned tags (v1.2.3, 1.2, 1, latest) via docker-push-release
- **Documentation**: Streamlined Docker documentation and removed non-working solutions
  - Removed `docker/` directory containing non-functional distroless Docker image
  - Updated main README.md to reflect only working Docker optimization approaches
  - Removed `docker_size_analysis.md` file, migrated relevant content to main README
  - Clarified that distroless approach is incompatible with OR-Tools requirements
- **Dependencies Architecture**: Refactored project dependencies for cleaner separation
  - Moved `pandas>=2.0.0` and `numpy>=1.24.0` from core dependencies to optional `[examples]` extra
  - Core package now includes only essential dependencies: `fastmcp`, `ortools`, `pulp`, `pydantic`, `uvicorn`
  - Updated installation instructions: use `pip install "mcp-optimizer[examples]"` for running integration examples
  - **Note**: pandas and numpy still present in Docker images due to OR-Tools hard requirements
- **Documentation**: Updated README and examples documentation
  - Added installation instructions for examples dependencies in README.md
  - Updated examples/integration/README.md with correct dependency installation commands
  - Enhanced streamlit_dashboard.py with comprehensive installation notes
  - Updated Docker image size analysis with correct dependency constraints explanation
- **Docker Image Analysis**: Clarified dependency constraints in optimization documentation
  - Documented that OR-Tools requires pandas and numpy as mandatory dependencies (`pandas>=2.0.0`, `numpy>=1.13.3`)
  - Updated image size analysis to reflect actual constraints preventing further optimization
  - Current optimized size: ~420MB (cannot be reduced further due to OR-Tools requirements)
- **Architecture**: Single worker + asyncio semaphore design
  - Explicitly configured `WORKERS=1` for optimal CPU-intensive math operations
  - Implemented asyncio-based concurrency instead of multiple uvicorn workers
  - Leveraged GIL release in PuLP/OR-Tools for true parallelism within single process
  - Optimized memory usage through shared libraries and process pools

- **Configuration Management**: Unified environment variable strategy
  - Standardized configuration across Docker Compose, Kubernetes, and local development
  - Added comprehensive environment variable documentation in deployment configs
  - Enhanced configuration validation and error reporting

- **Dependency Management**: Added psutil for resource monitoring
  - Added `psutil>=5.9.0` to project dependencies for memory monitoring
  - Implemented efficient resource monitoring with caching to minimize overhead
  - Added lazy loading and background monitoring for long-running operations

### Documentation
- **Architecture Documentation**: Documented single worker design rationale
  - Explained why 1 worker + asyncio is more efficient than N workers for math optimization
  - Documented GIL release behavior in PuLP/OR-Tools for parallel execution
  - Added performance comparison and resource utilization analysis

- **Configuration Guide**: Comprehensive environment variable documentation
  - Documented all configuration options with examples and defaults
  - Added deployment-specific configuration recommendations
  - Enhanced troubleshooting guides for resource monitoring issues

## [0.3.8] - 2025-05-28

### Fixed
- **Architecture Simplification**: Completely refactored entry points according to FastMCP documentation
  - Removed complex event loop detection logic from `main.py` and `src/mcp_optimizer/main.py`
  - Use simple `mcp.run(transport="stdio")` pattern as recommended by FastMCP
  - Separated sync and async contexts properly: `run()` for sync, `run_async()` for async
  - Fixed "capture_exceptions" parameter error by following FastMCP API correctly
- **Linting and Code Quality**: Comprehensive linting fixes and configuration improvements
  - Fixed all ruff and mypy linting issues across the codebase
  - Restructured `pyproject.toml` configuration with proper tool sections
  - Added proper type ignores for OR-Tools compatibility issues
  - Fixed unreachable code warnings in validation patterns
  - Updated deprecated ruff configuration settings
  - Added MyPy overrides for modules with specific validation patterns

### Changed
- **Architecture Simplification**: Further simplified entry points based on FastMCP best practices
  - Removed remaining complex event loop detection logic
  - Streamlined `main.py` to use simple `mcp.run(transport="stdio")` pattern
  - Improved separation of sync and async contexts in CLI
  - Enhanced logging consistency across entry points
- **Code Quality**: Improved type safety and maintainability
  - Added comprehensive type annotations and ignores
  - Fixed OR-Tools type conflicts with proper type casting
  - Improved error handling in optimization tools
  - Enhanced code documentation and comments

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