# Contributing to MCP Optimizer

Thank you for your interest in contributing to MCP Optimizer! This document provides comprehensive guidelines for contributors, including our Git Flow policy, development setup, and contribution process.

## 🤝 How to Contribute

### Reporting Issues
- Use the [GitHub Issues](https://github.com/dmitryanchikov/mcp-optimizer/issues) page
- Search existing issues before creating a new one
- Provide detailed information including:
  - Python version
  - Operating system
  - Steps to reproduce
  - Expected vs actual behavior
  - Error messages and stack traces

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the feature and its use case
- Explain why it would be valuable to the project
- Consider providing a basic implementation outline

## 🌳 Git Flow and Branch Policy

### Branch Structure

#### Main Branches

**`main`**
- **Purpose**: Production-ready code
- **Protection**: Fully protected, no direct pushes
- **Merges from**: `release/*` branches only
- **Triggers**: Production deployments, GitHub releases
- **Stability**: Must always be stable and deployable

**`develop`**
- **Purpose**: Integration branch for features
- **Protection**: Protected, no direct pushes except hotfixes
- **Merges from**: `feature/*` branches
- **Merges to**: `release/*` branches
- **Stability**: Should be stable, but may contain experimental features

#### Supporting Branches

**`feature/*`**
- **Purpose**: Development of new features
- **Naming**: `feature/issue-number-short-description` or `feature/short-description`
- **Branches from**: `develop`
- **Merges to**: `develop` via Pull Request
- **Lifetime**: Temporary, deleted after merge
- **Examples**: 
  - `feature/123-add-knapsack-solver`
  - `feature/improve-error-handling`

**`release/*`**
- **Purpose**: Prepare new production releases
- **Naming**: `release/v{major}.{minor}.{patch}`
- **Branches from**: `develop`
- **Merges to**: `main`
- **Lifetime**: Temporary, deleted after release
- **Examples**: 
  - `release/v1.2.0`
  - `release/v2.0.0-beta.1`

**`hotfix/*`**
- **Purpose**: Critical fixes for production issues
- **Naming**: `hotfix/v{major}.{minor}.{patch}` or `hotfix/issue-description`
- **Branches from**: `main`
- **Merges to**: `main`
- **Lifetime**: Temporary, deleted after merge
- **Examples**: 
  - `hotfix/v1.1.1`
  - `hotfix/critical-security-fix`

**`merge/*`**
- **Purpose**: Automated merge-back from main to develop after releases
- **Naming**: `merge/release-v{major}.{minor}.{patch}-to-develop`
- **Branches from**: `main` (automated)
- **Merges to**: `develop` via Pull Request
- **Lifetime**: Temporary, deleted after merge
- **Examples**: 
  - `merge/release-v1.2.0-to-develop`
  - `merge/hotfix-v1.1.1-to-develop`

### Branch Protection Rules

#### `main` Branch Protection
- **Reviews**: 2 required reviewers
- **Status checks**: All tests, security, build must pass
- **Restrictions**: No direct pushes, no force pushes, no deletions
- **History**: Linear history required
- **Code owners**: Review required

#### `develop` Branch Protection
- **Reviews**: 1 required reviewer
- **Status checks**: Tests and security must pass
- **Restrictions**: No force pushes, no deletions
- **Bypass**: Administrators can bypass for hotfixes

#### `release/*` Branch Protection
- **Reviews**: 1 required reviewer, code owners required
- **Status checks**: All tests, security, build must pass
- **Cleanup**: Deletions allowed after release

## 🛠️ Development Setup

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Git

### Getting Started
```bash
# Fork and clone the repository
git clone https://github.com/your-username/mcp-optimizer.git
cd mcp-optimizer

# Install dependencies
uv sync --extra dev

# Install pre-commit hooks (optional but recommended)
uv run pre-commit install
```

## 🔄 Development Workflows

### Feature Development
```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# 2. Make your changes
# ... edit files ...

# 3. Run tests and quality checks
uv run pytest tests/ -v
uv run ruff check src/
uv run ruff format src/
uv run mypy src/
uv run python comprehensive_test.py

# 4. Commit your changes (use conventional commits)
git add .
git commit -m "feat: add your feature description"

# 5. Push to your fork
git push origin feature/your-feature-name

# 6. Create Pull Request to develop branch
# Use the PR template and follow the checklist
```

### Release Process (for maintainers)
```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
uv run python scripts/release.py --type minor

# 2. Create PR to main
gh pr create --base main --head release/v1.2.0 --title "Release v1.2.0"

# 3. Merge PR - automatic finalization happens!
# ✅ Tag creation, PyPI publishing, Docker images, GitHub release
```

### Hotfix Process (for maintainers)
```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
uv run python scripts/release.py --hotfix --type patch

# 2. Fix the issue
git add .
git commit -m "fix: resolve critical security vulnerability"
git push origin hotfix/v1.1.1

# 3. Create PRs to both main and develop
gh pr create --base main --head hotfix/v1.1.1 --title "Hotfix v1.1.1"
gh pr create --base develop --head hotfix/v1.1.1 --title "Hotfix v1.1.1 - Merge to develop"
```

## 📋 Pull Request Guidelines

### Requirements
- **Target Branch**: 
  - Features → `develop`
  - Releases → `main`
  - Hotfixes → `main` and `develop`
- **Title**: Follow conventional commits format
- **Description**: Use PR template
- **Tests**: All tests must pass
- **Review**: Required number of approvals
- **Conflicts**: Must be resolved before merge

### PR Title Format
```
type(scope): description

Examples:
feat(knapsack): add multi-dimensional knapsack solver
fix(assignment): handle empty worker list edge case
docs(readme): update installation instructions
chore(deps): update dependencies to latest versions
```

### Merge Strategy
- **Features**: Squash and merge (clean history)
- **Releases**: Create merge commit (preserve release history)
- **Hotfixes**: Create merge commit (preserve fix history)

## 📝 Code Standards

### Code Style
- Follow [PEP 8](https://pep8.org/) Python style guide
- Use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Maximum line length: 88 characters
- Use type hints for all function parameters and return values

### Code Quality
- Write docstrings for all public functions and classes
- Use meaningful variable and function names
- Keep functions focused and small
- Add comments for complex logic

### Example Code Style
```python
"""Module docstring describing the purpose."""

from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


def solve_optimization_problem(
    objective: Dict[str, Any],
    variables: Dict[str, Dict[str, Any]],
    constraints: List[Dict[str, Any]],
    solver: str = "CBC",
) -> Dict[str, Any]:
    """Solve an optimization problem.
    
    Args:
        objective: Objective function specification
        variables: Variable definitions
        constraints: List of constraints
        solver: Solver name to use
        
    Returns:
        Optimization result with status and solution
        
    Raises:
        ValueError: If input validation fails
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Error solving problem: {e}")
        raise
```

## 🧪 Testing

### Test Requirements
- All new features must include tests
- Maintain or improve test coverage
- Tests should be fast and reliable
- Use descriptive test names

### Running Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_tools/test_linear_programming.py -v

# Run with coverage
uv run pytest tests/ --cov=src/mcp_optimizer --cov-report=html

# Run comprehensive integration tests
uv run python comprehensive_test.py
```

### Test Structure
```python
import pytest
from mcp_optimizer.tools.example import solve_example_problem


class TestExampleTool:
    """Test suite for example optimization tool."""
    
    def test_solve_basic_problem(self):
        """Test solving a basic optimization problem."""
        # Arrange
        objective = {"sense": "maximize", "coefficients": {"x": 1}}
        variables = {"x": {"type": "continuous", "lower": 0}}
        constraints = []
        
        # Act
        result = solve_example_problem(objective, variables, constraints)
        
        # Assert
        assert result["status"] == "optimal"
        assert result["objective_value"] > 0
    
    def test_invalid_input_raises_error(self):
        """Test that invalid input raises appropriate error."""
        with pytest.raises(ValueError, match="Invalid objective"):
            solve_example_problem({}, {}, [])
```

## 📚 Documentation

### Documentation Requirements
- Update README.md if adding new features
- Add docstrings to all public functions
- Include usage examples for new tools
- Update type hints
- **Update CHANGELOG.md** for all user-facing changes (see [Changelog Guidelines](#-changelog-guidelines))

### Documentation Style
- Use clear, concise language
- Provide practical examples
- Include parameter descriptions
- Document error conditions

## 📝 Changelog Guidelines

### Overview
We maintain a detailed changelog following the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format. All user-facing changes must be documented in `CHANGELOG.md`.

### When to Update CHANGELOG.md
**Always update** for:
- ✅ New features or tools
- ✅ Bug fixes
- ✅ Breaking changes
- ✅ Performance improvements
- ✅ Security fixes
- ✅ Dependency updates (major versions)

**Don't update** for:
- ❌ Internal refactoring (no user impact)
- ❌ Test improvements
- ❌ Documentation typos
- ❌ CI/CD changes
- ❌ Development tooling changes

### How to Update CHANGELOG.md

#### 1. Add Entry to [Unreleased] Section
```markdown
## [Unreleased]

### Added
- New knapsack solver with multi-dimensional support

### Changed
- Improved error messages for invalid optimization problems

### Fixed
- Fixed memory leak in large-scale linear programming problems

### Security
- Updated dependencies to address CVE-2024-XXXX
```

#### 2. Use Proper Categories
- **Added**: New features, tools, or capabilities
- **Changed**: Changes to existing functionality
- **Deprecated**: Features marked for removal
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security-related changes

#### 3. Write User-Focused Descriptions
```markdown
# ✅ Good
- Added support for multi-objective optimization problems
- Fixed timeout issues with large transportation problems

# ❌ Bad  
- Refactored solver factory pattern
- Updated unit tests for better coverage
```

#### 4. Include Breaking Changes
```markdown
### Changed
- **BREAKING**: Renamed `solve_problem()` to `optimize()` for consistency
- **BREAKING**: Removed deprecated `legacy_solver` parameter
```

### Automatic Processing
- During release, entries from `[Unreleased]` are automatically moved to versioned sections
- Release dates are automatically added by `scripts/release.py`
- No manual intervention needed for release finalization

### Validation
- PR template includes CHANGELOG.md checklist
- Code owners (@dmitryanchikov) review all changelog changes
- CI validates changelog format during builds

## 🔧 Adding New Optimization Tools

### Tool Structure
```python
# src/mcp_optimizer/tools/new_tool.py
from typing import Any, Dict, List
from mcp_optimizer.schemas.base import OptimizationResult
from mcp_optimizer.utils.validation import validate_input


def solve_new_problem(
    problem_data: Dict[str, Any]
) -> OptimizationResult:
    """Solve a new type of optimization problem.
    
    Args:
        problem_data: Problem specification
        
    Returns:
        Optimization result
    """
    # Validate input
    validate_input(problem_data)
    
    # Solve problem
    # ... implementation ...
    
    return OptimizationResult(
        status="optimal",
        objective_value=42.0,
        variables={"x": 1.0},
        solve_time=0.01
    )
```

### Integration Steps
1. Create tool module in `src/mcp_optimizer/tools/`
2. Add validation schema in `src/mcp_optimizer/schemas/`
3. Write comprehensive tests in `tests/test_tools/`
4. Add MCP tool registration in `src/mcp_optimizer/mcp_server.py`
5. Update documentation and examples

## 🚀 CI/CD Integration

### Trigger Rules
- **Tests**: Run on all branches and PRs
- **Security Scans**: Run on all branches and PRs
- **Docker Build**: Run on `main`, `develop`, and `release/*`
- **PyPI Release**: Run only on version tags from `main`
- **GitHub Release**: Run only on version tags from `main`

### Branch-Specific Behaviors
- **`main`**: Full CI/CD pipeline, production deployments
- **`develop`**: Full CI/CD pipeline, development deployments
- **`feature/*`**: Tests and security scans only
- **`release/*`**: Full CI/CD pipeline, release candidate builds
- **`hotfix/*`**: Full CI/CD pipeline, hotfix builds
- **`merge/*`**: Tests and security scans (for merge-back validation)

## 🏷️ Tagging Strategy

### Version Tags
- Format: `v{major}.{minor}.{patch}`
- Created on `main` branch only
- Triggers production release
- Examples: `v1.0.0`, `v1.2.3`, `v2.0.0-beta.1`

### Pre-release Tags
- Format: `v{major}.{minor}.{patch}-{pre-release}`
- Examples: `v1.2.0-alpha.1`, `v1.2.0-beta.2`, `v1.2.0-rc.1`

## 📞 Getting Help

### Communication Channels
- **Issues**: [GitHub Issues](https://github.com/dmitryanchikov/mcp-optimizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dmitryanchikov/mcp-optimizer/discussions)
- **Email**: support@mcp-optimizer.com

### Before Asking for Help
1. Check existing documentation
2. Search closed issues and discussions
3. Try the troubleshooting steps
4. Provide minimal reproducible example

## 🙏 Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Project README
- Annual contributor highlights

Thank you for contributing to MCP Optimizer! 🚀 