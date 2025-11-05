# MCP Optimizer

🚀 **Mathematical Optimization MCP Server** with PuLP and OR-Tools support

[![Tests](https://img.shields.io/badge/tests-598%20passed-brightgreen)](https://github.com/dmitryanchikov/mcp-optimizer)
[![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)](https://github.com/dmitryanchikov/mcp-optimizer)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

📖 **Quick Links:** [🚀 Quick Start](#-quick-start) | [🔧 macOS Troubleshooting](#-macos-uvx-troubleshooting) | [📊 Examples](#-usage-examples) | [🎯 Features](#-features)

## 🚀 Quick Start

### Recommended Installation Methods (by Priority)

### 1. 🐳 Docker (Recommended) - Cross-platform
**Most stable method with full functionality**

```bash
# Run with STDIO transport (for MCP clients)
docker run --rm -i ghcr.io/dmitryanchikov/mcp-optimizer:latest

# Run with SSE transport (for remote clients)
docker run -d -p 8000:8000 -e TRANSPORT_MODE=sse \
  ghcr.io/dmitryanchikov/mcp-optimizer:latest

# Check SSE endpoint
curl -i http://localhost:8000/sse
```

### 2. 📦 pip + venv - Cross-platform  
**Standard approach**

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Install mcp-optimizer
pip install mcp-optimizer

# For SSE issues, use stable dependency versions:
# pip install "mcp-optimizer[stable]"

# Run (STDIO mode recommended)
mcp-optimizer --transport stdio
```

### 3. 🚀 uvx - Linux/Windows (full), macOS (partially)

```bash
# Linux/Windows - works out of the box
uvx mcp-optimizer

# macOS - requires Python 3.12
uvx --python python3.12 mcp-optimizer

# STDIO mode recommended
uvx mcp-optimizer --transport stdio
```

**macOS users:** If you encounter OR-Tools related errors, see [🔧 macOS uvx Troubleshooting](#-macos-uvx-troubleshooting) section for automated fix scripts.

### 🍎 macOS Specifics

**OR-Tools support:**
- **uvx**: PuLP only (limited functionality)
- **pip**: full OR-Tools support  
- **Docker**: full OR-Tools support

**For full OR-Tools support via pip:**
```bash
# Install OR-Tools via Homebrew
brew install or-tools

# Then install mcp-optimizer
pip install "mcp-optimizer[stable]"
```

### Transport Mode Recommendations

| Installation Method | Recommended Transport | Why |
|---------------------|----------------------|-----|
| Docker | SSE | Full stability |
| pip + venv | STDIO | Avoids dependency issues with newer versions |
| uvx | STDIO | Maximum compatibility |

### Integration with LLM Clients

#### Claude Desktop Integration

**Option 1: Using Docker (Recommended)**
1. Install Claude Desktop from [claude.ai](https://claude.ai/download)
2. Pull the Docker image:
```bash
docker pull ghcr.io/dmitryanchikov/mcp-optimizer:latest
```
3. Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-optimizer": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "ghcr.io/dmitryanchikov/mcp-optimizer:latest",
        "python", "main.py"
      ]
    }
  }
}
```
4. Restart Claude Desktop and look for the 🔨 tools icon

**Option 2: Using pip + venv**
```bash
# Create virtual environment and install
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install mcp-optimizer
```
Then add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "mcp-optimizer": {
      "command": "mcp-optimizer"
    }
  }
}
```

**Option 3: Using uvx**
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-optimizer": {
      "command": "uvx",
      "args": ["mcp-optimizer"]
    }
  }
}
```
*Note: On macOS, uvx provides limited functionality (PuLP solver only) or see [🔧 macOS uvx Troubleshooting](#-macos-uvx-troubleshooting)*

**Advanced Docker Setup (for remote MCP clients)**
```bash
# Run SSE server on port 8000 (uses environment variable)
docker run -d -p 8000:8000 -e TRANSPORT_MODE=sse \
  ghcr.io/dmitryanchikov/mcp-optimizer:latest

# Or with CLI argument and custom port
docker run -d -p 9000:9000 ghcr.io/dmitryanchikov/mcp-optimizer:latest \
  python -m mcp_optimizer.main --transport sse --host 0.0.0.0 --port 9000

# Check server status
docker logs <container-name>

# Verify SSE endpoint (should show event stream)
curl -i http://localhost:8000/sse
```
**SSE Endpoint**: `http://localhost:8000/sse` (Server-Sent Events for MCP communication)

#### Cursor Integration

1. Install the MCP extension in Cursor
2. Add mcp-optimizer to your workspace settings (Docker recommended):
```json
{
  "mcp.servers": {
    "mcp-optimizer": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "ghcr.io/dmitryanchikov/mcp-optimizer:latest",
        "python", "main.py"
      ]
    }
  }
}
```

**Alternative configurations:**
```json
// Using pip installation
{
  "mcp.servers": {
    "mcp-optimizer": {
      "command": "mcp-optimizer"
    }
  }
}

// Using uvx (limited functionality on macOS)
{
  "mcp.servers": {
    "mcp-optimizer": {
      "command": "uvx",
      "args": ["mcp-optimizer"]
    }
  }
}
```

#### Other LLM Clients

For other MCP-compatible clients (Continue, Cody, etc.), use similar configuration patterns. **Recommended priority:**

1. **Docker** (maximum stability across platforms)
2. **pip + venv** (standard Python approach)  
3. **uvx** (quick testing, limited on macOS)

### Advanced Installation Options

#### Local Development
```bash
# Clone the repository
git clone https://github.com/dmitryanchikov/mcp-optimizer.git
cd mcp-optimizer

# Install dependencies with uv
uv sync --extra dev

# Run the server
uv run python main.py
```

#### Local Package Build and Run

For testing and development, you can build the package locally and run it with uvx:

```bash
# Build the package locally
uv build

# Run with uvx from local wheel file
uvx --from ./dist/mcp_optimizer-0.3.9-py3-none-any.whl mcp-optimizer

# Or run with help to see available options
uvx --from ./dist/mcp_optimizer-0.3.9-py3-none-any.whl mcp-optimizer --help

# Test the local package with a simple MCP message
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}, "id": 1}' | uvx --from ./dist/mcp_optimizer-0.3.9-py3-none-any.whl mcp-optimizer
```

**Note**: The local build creates both wheel (`.whl`) and source distribution (`.tar.gz`) files in the `dist/` directory. The wheel file is recommended for uvx installation as it's faster and doesn't require compilation.

#### Docker with Custom Configuration
```bash
# Build locally with optimization
git clone https://github.com/dmitryanchikov/mcp-optimizer.git
cd mcp-optimizer
docker build -t mcp-optimizer:optimized .
docker run -p 8000:8000 mcp-optimizer:optimized

# Check optimized image size (398MB vs 1.03GB original - 61% reduction!)
docker images mcp-optimizer:optimized

# Test the optimized image
./scripts/test_docker_optimization.sh
```

#### Standalone Server Commands
```bash
# Run directly with uvx (no installation needed)
uvx mcp-optimizer

# Or run specific commands
uvx mcp-optimizer --help

# With pip installation
mcp-optimizer

# Or run with Python module (use main.py for stdio mode)
python main.py
```

#### Transport Modes

MCP Optimizer supports two MCP transport protocols:
- **STDIO**: Standard input/output for direct MCP client integration (Claude Desktop, Cursor, etc.)
- **SSE**: Server-Sent Events over HTTP for web-based MCP clients and remote integrations

**STDIO Transport (Default - for MCP clients like Claude Desktop)**
```bash
# Default STDIO mode for MCP protocol
uvx mcp-optimizer
# or
uvx mcp-optimizer --transport stdio
# or
uv run python -m mcp_optimizer.main --transport stdio
# or
python main.py
```

**SSE Transport (for remote MCP clients)**
```bash
# SSE mode for remote MCP clients (default port 8000)
uvx mcp-optimizer --transport sse
# or
uv run python -m mcp_optimizer.main --transport sse

# Custom host and port
uvx mcp-optimizer --transport sse --host 0.0.0.0 --port 9000
# or
uv run python -m mcp_optimizer.main --transport sse --host 0.0.0.0 --port 9000

# With debug mode
uvx mcp-optimizer --transport sse --debug --log-level DEBUG
```

**Available CLI Options**
```bash
# Show all available options
uvx mcp-optimizer --help

# Options:
#   --transport {stdio,sse}    MCP transport protocol (default: stdio)
#   --port PORT               Port for SSE transport (default: 8000)
#   --host HOST               Host for SSE transport (default: 127.0.0.1)
#   --debug                   Enable debug mode
#   --reload                  Enable auto-reload for development
#   --log-level {DEBUG,INFO,WARNING,ERROR}  Logging level (default: INFO)
#
# Environment Variables:
#   TRANSPORT_MODE={stdio,sse}  Override transport mode
#   SERVER_HOST=0.0.0.0        Override server host
#   SERVER_PORT=8000           Override server port
```

## 🔧 Platform Compatibility & Troubleshooting

### macOS Compatibility

**✅ Full Functionality:**
- **Homebrew + pip**: `brew install or-tools && pip install mcp-optimizer`
- **Virtual environments**: `python -m venv venv && source venv/bin/activate && pip install ortools mcp-optimizer`
- **Docker**: Full OR-Tools support in containers

**⚠️ Limited Functionality:**
- **uvx (isolated environments)**: Only PuLP solver available due to OR-Tools native library paths
- **Fallback behavior**: Automatically switches to PuLP when OR-Tools unavailable

**Common Issues & Solutions:**

1. **OR-Tools "Library not loaded" error:**
   ```bash
   # Solution: Install via Homebrew
   brew install or-tools
   # Then use regular pip/venv instead of uvx
   ```

2. **uvx shows OR-Tools warnings:**
   ```bash
   WARNING: OR-Tools not available: No module named 'ortools'
   ```
   This is expected - uvx provides fallback functionality with PuLP solver.

3. **Best practices for macOS:**
   - Use Docker for production deployments
   - Use Homebrew + pip for development
   - Use uvx for quick testing (limited functionality)

### Linux/Windows Compatibility

**✅ Full Functionality:**
- **uvx**: Works out of the box with OR-Tools
- **pip**: Standard installation
- **Docker**: Recommended for production

### Solver Availability by Platform

  | Platform | uvx | pip | Docker |
  |----------|-----|-----|--------|
  | **macOS** | PuLP only | ✅ Full | ✅ Full |
  | **Linux** | ✅ Full | ✅ Full | ✅ Full |
  | **Windows** | ✅ Full | ✅ Full | ✅ Full |

**Solver Features:**
- **OR-Tools**: Advanced algorithms (CP-SAT, routing, scheduling)
- **PuLP**: Basic linear programming, reliable fallback

## 🔧 macOS uvx Troubleshooting 

### Problem: OR-Tools Library Issues with uvx

**Common Error Messages:**
```
Library not loaded: /Users/corentinl/work/stable/temp_python3.13/lib/libscip.9.2.dylib
ImportError: No module named 'ortools'
WARNING: OR-Tools not available
```

**Root Cause**: OR-Tools binary wheels contain hardcoded library paths that fail in uvx isolated environments. This is a macOS-specific issue due to how uvx isolates dependencies.

### 📊 Functionality Impact by Installation Method

**✅ Available with uvx + fallback (PuLP solver only)**:
- **Linear Programming** - Basic optimization, simplex method
- **Financial Optimization** - Portfolio optimization, risk management  
- **Production Planning** - Resource allocation, inventory management

**❌ Lost with uvx (requires OR-Tools)**:
- **Assignment Problems** - Hungarian algorithm, transportation problems
- **Integer Programming** - Mixed-integer, binary programming (SCIP/CBC)
- **Knapsack Problems** - Discrete optimization, multiple variants
- **Vehicle Routing** - TSP, CVRP, time windows (constraint programming)
- **Job Scheduling** - CP-SAT solver, resource planning

### 🛠️ Solutions (in order of preference)

#### 1. Automated Fix Script (Recommended)
```bash
# Smart adaptive script - no hardcoded versions!
# Automatically detects your system libraries and Python versions
./scripts/fix_macos_uvx.sh

# Then uvx works with full functionality
uvx mcp-optimizer --transport stdio
```

#### 2. Manual Fix
```bash
# Install system dependencies
brew install or-tools scip

# Create symlink for hardcoded path
sudo mkdir -p /Users/corentinl/work/stable/temp_python3.13/lib/
sudo ln -sf /opt/homebrew/lib/libscip.9.2.dylib /Users/corentinl/work/stable/temp_python3.13/lib/libscip.9.2.dylib

# Test fix
uvx mcp-optimizer --help
```

#### 3. Use pip (Always Works)
```bash
# Install dependencies first
brew install or-tools

# Install package
pip install mcp-optimizer
mcp-optimizer
```

#### 4. Use Docker (Production Ready)
```bash
docker run -p 8000:8000 mcp-optimizer
```

## 🎯 Features

### Supported Optimization Problem Types:
- **Linear Programming** - Maximize/minimize linear objective functions
- **Assignment Problems** - Optimal resource allocation using Hungarian algorithm
- **Transportation Problems** - Logistics and supply chain optimization
- **Knapsack Problems** - Optimal item selection (0-1, bounded, unbounded)
- **Routing Problems** - TSP and VRP with time windows
- **Scheduling Problems** - Job and shift scheduling
- **Integer Programming** - Discrete optimization problems
- **Financial Optimization** - Portfolio optimization and risk management
- **Production Planning** - Multi-period production planning

### Testing

#### Automated Test Scripts

**Quick Testing:**
```bash
# Test local package build and functionality
./scripts/test_local_package.sh

# Test Docker container build and functionality  
./scripts/test_docker_container.sh

# Run comprehensive test suite (both package and Docker)
./scripts/test_all.sh

# Run only specific tests
./scripts/test_all.sh --skip-docker    # Skip Docker tests
./scripts/test_all.sh --skip-package   # Skip package tests
```

**Manual Testing:**
```bash
# Run simple functionality tests
uv run python tests/test_integration/comprehensive_test.py

# Run comprehensive integration tests
uv run python tests/test_integration/comprehensive_test.py

# Run all unit tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src/mcp_optimizer --cov-report=html
```

**Test Scripts Features:**
- ✅ **Local Package Testing**: Build, STDIO/SSE modes, CLI functionality
- ✅ **Docker Container Testing**: Image build, environment variables, health checks
- ✅ **Comprehensive Suite**: Parallel execution with detailed reporting
- ✅ **Automatic Cleanup**: Processes and containers cleaned up after tests
- ✅ **Cross-Platform**: Works on macOS, Linux (requires Docker for container tests)

**Requirements:**
- For local tests: `uv`, `curl`, `lsof`, `gtimeout`/`timeout`
- For Docker tests: `docker` + local requirements
- macOS: `brew install coreutils` (for gtimeout)

**CI/CD Integration:**
```yaml
# GitHub Actions example
- name: Test Package
  run: ./scripts/test_local_package.sh
- name: Test Docker
  run: ./scripts/test_docker_container.sh
```

## 📊 Usage Examples

### Linear Programming
```python
from mcp_optimizer.tools.linear_programming import solve_linear_program

# Maximize 3x + 2y subject to:
# x + y <= 4
# 2x + y <= 6
# x, y >= 0

objective = {"sense": "maximize", "coefficients": {"x": 3, "y": 2}}
variables = {
    "x": {"type": "continuous", "lower": 0},
    "y": {"type": "continuous", "lower": 0}
}
constraints = [
    {"expression": {"x": 1, "y": 1}, "operator": "<=", "rhs": 4},
    {"expression": {"x": 2, "y": 1}, "operator": "<=", "rhs": 6}
]

result = solve_linear_program(objective, variables, constraints)
# Result: x=2.0, y=2.0, objective=10.0
```

### Assignment Problem
```python
from mcp_optimizer.tools.assignment import solve_assignment_problem

workers = ["Alice", "Bob", "Charlie"]
tasks = ["Task1", "Task2", "Task3"]
costs = [
    [4, 1, 3],  # Alice's costs for each task
    [2, 0, 5],  # Bob's costs for each task
    [3, 2, 2]   # Charlie's costs for each task
]

result = solve_assignment_problem(workers, tasks, costs)
# Result: Total cost = 5.0 with optimal assignments
```

### Knapsack Problem
```python
from mcp_optimizer.tools.knapsack import solve_knapsack_problem

items = [
    {"name": "Item1", "weight": 10, "value": 60},
    {"name": "Item2", "weight": 20, "value": 100},
    {"name": "Item3", "weight": 30, "value": 120}
]

result = solve_knapsack_problem(items, capacity=50)
# Result: Total value = 220.0 with optimal item selection
```

### Portfolio Optimization
```python
from mcp_optimizer.tools.financial import optimize_portfolio

assets = [
    {"name": "Stock A", "expected_return": 0.12, "risk": 0.18},
    {"name": "Stock B", "expected_return": 0.10, "risk": 0.15},
    {"name": "Bond C", "expected_return": 0.06, "risk": 0.08}
]

result = optimize_portfolio(
    assets=assets,
    objective="minimize_risk",
    budget=10000,
    risk_tolerance=0.15
)
# Result: Optimal portfolio allocation with minimized risk
```

## 🏗️ Architecture

```
mcp-optimizer/
├── LICENSE                     # MIT License
├── README.md                   # Project documentation
├── CHANGELOG.md               # Release notes
├── CONTRIBUTING.md            # Contribution guidelines
├── pyproject.toml             # Python project configuration
├── uv.lock                    # Dependency lock file
├── main.py                    # Entry point
├── Dockerfile                 # Main Docker configuration
├── docker-compose.yml         # Multi-service setup
├── .dockerignore             # Docker ignore rules
├── .gitignore                # Git ignore rules
├── .python-version           # Python version specification
├── src/mcp_optimizer/        # Main source code
│   ├── __init__.py
│   ├── __main__.py           # Module entry point
│   ├── main.py               # Application entry point
│   ├── mcp_server.py         # MCP server implementation
│   ├── config.py             # Configuration management
│   ├── tools/                # 9 categories of optimization tools
│   │   ├── linear_programming.py
│   │   ├── assignment.py
│   │   ├── knapsack.py
│   │   ├── routing.py
│   │   ├── scheduling.py
│   │   ├── financial.py
│   │   └── production.py
│   ├── solvers/              # PuLP and OR-Tools integration
│   │   ├── pulp_solver.py
│   │   └── ortools_solver.py
│   ├── schemas/              # Pydantic validation schemas
│   └── utils/                # Utility functions
├── tests/                    # Comprehensive test suite
│   ├── test_tools/           # Tool-specific tests
│   ├── test_solvers/         # Solver tests
│   └── test_integration/     # Integration tests
├── scripts/                  # Automation scripts
├── examples/                 # Usage examples and prompts
│   ├── en/                   # English examples
│   └── ru/                   # Russian examples
├── k8s/                      # Kubernetes deployment manifests
└── monitoring/               # Grafana/Prometheus setup
    └── grafana/
        └── datasources/
```

## 🧪 Test Results

### ✅ Comprehensive Test Suite
```
🧪 Starting Comprehensive MCP Optimizer Tests
==================================================
✅ Server Health PASSED
✅ Linear Programming PASSED
✅ Assignment Problems PASSED  
✅ Knapsack Problems PASSED
✅ Routing Problems PASSED
✅ Scheduling Problems PASSED
✅ Financial Optimization PASSED
✅ Production Planning PASSED
✅ Performance Test PASSED

📊 Test Results: 9 passed, 0 failed
🎉 All tests passed! MCP Optimizer is ready for production!
```

### ✅ Unit Tests
- **66 tests passed, 9 skipped**
- **Execution time: 0.45 seconds**
- **All core components functional**

### 📈 Performance Metrics
- **Linear Programming**: ~0.01s
- **Assignment Problems**: ~0.01s  
- **Knapsack Problems**: ~0.01s
- **Complex test suite**: 0.02s for 3 optimization problems
- **Overall performance**: 🚀 Excellent!

## 🔧 Technical Details

### Core Solvers
- **OR-Tools**: For assignment, transportation, knapsack problems
- **PuLP**: For linear/integer programming
- **FastMCP**: For MCP server integration

### Supported Solvers
- **CBC, GLPK, GUROBI, CPLEX** (via PuLP)
- **SCIP, CP-SAT** (via OR-Tools)

### Key Features
- ✅ Full MCP protocol integration
- ✅ Comprehensive input validation
- ✅ Robust error handling
- ✅ High-performance optimization
- ✅ Production-ready architecture
- ✅ Extensive test coverage
- ✅ Docker and Kubernetes support

## 📋 Requirements

- **Python 3.11+**
- **uv** (for dependency management)
- **OR-Tools** (automatically installed)
- **PuLP** (automatically installed)

## 🚀 Production Deployment

### Docker
```bash
# Build image
docker build -t mcp-optimizer .

# Run container
docker run -p 8000:8000 mcp-optimizer
```

### Kubernetes
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
```

### Monitoring
```bash
# Start monitoring stack
docker-compose up -d
```

## 🎯 Project Status

**✅ PRODUCTION READY** 🚀

- All core optimization tools implemented and tested
- MCP server fully functional
- Comprehensive test coverage (66 unit tests + 9 integration tests)
- OR-Tools integration confirmed working
- Performance optimized (< 30s for complex test suites)
- Ready for production deployment

## 📖 Usage Examples

The `examples/` directory contains practical examples and prompts for using MCP Optimizer with Large Language Models (LLMs):

### Available Examples
- **📊 Linear Programming** ([RU](examples/ru/linear_programming.md) | [EN](examples/en/linear_programming.md))
  - Production optimization, diet planning, transportation, blending problems
- **👥 Assignment Problems** ([RU](examples/ru/assignment_problems.md) | [EN](examples/en/assignment_problems.md))
  - Employee-project assignment, machine-order allocation, task distribution
- **💰 Portfolio Optimization** ([RU](examples/ru/portfolio_optimization.md) | [EN](examples/en/portfolio_optimization.md))
  - Investment portfolios, retirement planning, risk management

### How to Use Examples
1. **For LLM Integration**: Copy the prompt text and provide it to your LLM with MCP Optimizer access
2. **For Direct API Usage**: Use the provided API structures directly with MCP Optimizer functions
3. **For Learning**: Understand different optimization problem types and formulations

Each example includes:
- Problem descriptions and real-world scenarios
- Ready-to-use prompts for LLMs
- Technical API structures
- Common activation phrases
- Practical applications

## 🔄 Recent Updates

### Latest Release Features:
1. **Function Exports** - Added exportable functions to all tool modules:
   - `solve_linear_program()` in linear_programming.py
   - `solve_assignment_problem()` in assignment.py  
   - `solve_knapsack_problem()` in knapsack.py
   - `optimize_portfolio()` in financial.py
   - `optimize_production()` in production.py

2. **Enhanced Testing** - Updated comprehensive test suite with correct function signatures

3. **OR-Tools Integration** - Confirmed full functionality of all OR-Tools components

## 🚀 Fully Automated Release Process

### New Simplified Git Flow (3 steps!)
The project uses a fully automated release process:

#### 1. Create Release Branch
```bash
# For minor release (auto-increment)
uv run python scripts/release.py --type minor

# For specific version
uv run python scripts/release.py 0.2.0

# For hotfix
uv run python scripts/release.py --hotfix --type patch

# Preview changes
uv run python scripts/release.py --type minor --dry-run
```

#### 2. Create PR to main
```bash
# Create PR: release/v0.3.0 → main
gh pr create --base main --head release/v0.3.0 --title "Release v0.3.0"
```

#### 3. Merge PR - DONE! 🎉
After PR merge, automatically happens:
- ✅ Create tag v0.3.0
- ✅ Publish to PyPI
- ✅ Publish Docker images  
- ✅ Create GitHub Release
- ✅ Merge main back to develop
- ✅ Cleanup release branch

**NO NEED** to run `manual_finalize_release.py` manually anymore!

> 🔒 **Secure Detection**: Uses hybrid approach combining GitHub branch protection with automated release detection. See [Release Process](.github/RELEASE_PROCESS.md) for details.

### Automated Release Pipeline
The CI/CD pipeline automatically handles:
- ✅ **Release Candidates**: Built from `release/*` branches
- ✅ **Production Releases**: Triggered by version tags on `main`
- ✅ **PyPI Publishing**: Automatic on tag creation
- ✅ **Docker Images**: Multi-architecture builds
- ✅ **GitHub Releases**: With artifacts and release notes

### CI/CD Pipeline
The GitHub Actions workflow automatically:
- ✅ Runs tests on Python 3.11 and 3.12
- ✅ Performs security scanning
- ✅ Builds and pushes Docker images
- ✅ Publishes to PyPI on tag creation
- ✅ Creates GitHub releases

### Requirements for PyPI Publication
- Set `PYPI_API_TOKEN` secret in GitHub repository
- Ensure all tests pass
- Follow semantic versioning

## 🛠️ Development Tools

### Debug Tools
Use the debug script to inspect MCP server structure:

```bash
# Run debug tools to check server structure
uv run python scripts/debug_tools.py

# This will show:
# - Available MCP tools
# - Tool types and attributes
# - Server configuration
```

### Comprehensive Testing
Run the full integration test suite:

```bash
# Run comprehensive tests
uv run python tests/test_integration/comprehensive_test.py

# This tests:
# - All optimization tools (9 categories)
# - Server health and functionality
# - Performance benchmarks
# - End-to-end workflows
```

### Docker Build Instructions

#### Image Details
- **Base**: Python 3.12 Slim (Debian-based)
- **Size**: ~649MB (optimized with multi-stage builds)
- **Architecture**: Multi-platform support (x86_64, ARM64)
- **Security**: Non-root user, minimal dependencies
- **Performance**: Optimized Python bytecode, cleaned build artifacts

#### Local Build Commands
```bash
# Standard build
docker build -t mcp-optimizer:latest .

# Build with development dependencies
docker build --build-arg ENV=development -t mcp-optimizer:dev .

# Build with cache mount for faster rebuilds
docker build --mount=type=cache,target=/build/.uv -t mcp-optimizer .

# Check image size
docker images mcp-optimizer

# Run container
docker run -p 8000:8000 mcp-optimizer:latest

# For development with volume mounting
docker run -p 8000:8000 -v $(pwd):/app mcp-optimizer:latest

# Test container functionality
docker run --rm mcp-optimizer:latest python -c "from mcp_optimizer.mcp_server import create_mcp_server; print('✅ MCP Optimizer works!')"
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Git Flow Policy
This project follows a standard Git Flow workflow:
- **Feature branches** → `develop` branch
- **Release branches** → `main` branch  
- **Hotfix branches** → `main` and `develop` branches

📚 **Documentation**:
- [Contributing Guide](CONTRIBUTING.md) - Complete development workflow and Git Flow policy
- [Release Process](.github/RELEASE_PROCESS.md) - How releases are created and automated
- [Repository Setup](.github/REPOSITORY_SETUP.md) - Complete setup guide including branch protection and security configuration

### Development Setup
```bash
# Clone and setup
git clone https://github.com/dmitryanchikov/mcp-optimizer.git
cd mcp-optimizer

# Create feature branch from develop
git checkout develop
git checkout -b feature/your-feature-name

# Install dependencies
uv sync --extra dev

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check src/
uv run mypy src/

# Create PR to develop branch (not main!)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OR-Tools](https://developers.google.com/optimization) - Google's optimization tools
- [PuLP](https://coin-or.github.io/pulp/) - Linear programming in Python
- [FastMCP](https://github.com/jlowin/fastmcp) - Fast MCP server implementation

## 📞 Support

- 📧 Email: support@mcp-optimizer.com
- 🐛 Issues: [GitHub Issues](https://github.com/dmitryanchikov/mcp-optimizer/issues)
- 📖 Documentation: [docs/](docs/)

---

**Made with ❤️ for the optimization community**

## 📊 Docker Image Size Analysis

The MCP Optimizer Docker image has been optimized to balance functionality and size:

| Component | Size | % of Total | Description |
|-----------|------|------------|-------------|
| **Python packages (/venv)** | **237.0 MB** | **42.8%** | Virtual environment with dependencies |
| **System libraries (/usr)** | **173.2 MB** | **31.3%** | Base Debian system + Python |
| **Other** | **137.4 MB** | **24.8%** | Base image, filesystem |
| **Configuration (/var, /etc)** | **6.2 MB** | **1.1%** | System settings |
| **Application code (/code)** | **0.2 MB** | **0.04%** | MCP Optimizer source code |

### Key Dependencies by Size
- **OR-Tools**: 75.0 MB (27.8% of venv) - Critical optimization solver (requires pandas + numpy)
- **pandas**: 45.0 MB (16.7% of venv) - Required by OR-Tools for data operations
- **NumPy**: 24.0 MB (8.9% of venv) - Required by OR-Tools for numerical computing
- **PuLP**: 34.9 MB (12.9% of venv) - Linear programming solver  
- **FastMCP**: 15.2 MB (5.6% of venv) - MCP server framework
- **Pydantic**: 12.8 MB (4.7% of venv) - Data validation

### Dependencies Analysis
- **Core packages cannot be reduced further**: OR-Tools (our main optimization engine) requires both pandas and numpy as mandatory dependencies
- **Optional examples moved**: Additional packages for examples (streamlit, plotly) moved to `[examples]` extra
- **Minimal core impact**: Moving examples to optional dependencies only affects development/demo usage

### Image Optimization
- **Current optimized size**: ~420MB
- **Core functionality**: Includes all necessary dependencies for production optimization
- **Example support**: Install with `[examples]` extra for additional demo functionality
- **OR-Tools constraint**: Cannot remove pandas/numpy due to hard dependency requirements
