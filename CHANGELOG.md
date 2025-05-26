# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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