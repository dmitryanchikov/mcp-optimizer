# Contributing to MCP Optimizer

Thank you for your interest in contributing to MCP Optimizer! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the [GitHub Issues](https://github.com/your-repo/mcp-optimizer/issues) page
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

### Development Workflow
```bash
# Create a new branch for your feature/fix
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Run tests
uv run pytest tests/ -v

# Run linting and formatting
uv run ruff check src/
uv run ruff format src/
uv run mypy src/

# Run comprehensive tests
uv run python comprehensive_test.py

# Commit your changes
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name

# Create a Pull Request
```

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

### Documentation Style
- Use clear, concise language
- Provide practical examples
- Include parameter descriptions
- Document error conditions

## 🔧 Adding New Optimization Tools

### Tool Structure
When adding a new optimization tool, follow this structure:

```python
"""New optimization tool for MCP server."""

import logging
from typing import Any, Dict, List
from fastmcp import FastMCP
from ..schemas.base import OptimizationResult

logger = logging.getLogger(__name__)


def solve_new_problem(
    input_data: Dict[str, Any],
    solver: str = "default",
) -> Dict[str, Any]:
    """Solve the new optimization problem.
    
    Args:
        input_data: Problem specification
        solver: Solver to use
        
    Returns:
        Optimization result
    """
    # Implementation here
    pass


def register_new_tools(mcp: FastMCP[Any]) -> None:
    """Register new optimization tools with MCP server."""
    
    @mcp.tool()
    def solve_new_problem_tool(
        param1: str,
        param2: List[Dict[str, Any]],
        solver: str = "default",
    ) -> Dict[str, Any]:
        """Tool description for MCP.
        
        Args:
            param1: Description of parameter 1
            param2: Description of parameter 2
            solver: Solver to use
            
        Returns:
            Optimization result
        """
        return solve_new_problem({"param1": param1, "param2": param2}, solver)
    
    logger.info("Registered new optimization tools")
```

### Integration Steps
1. Create the tool module in `src/mcp_optimizer/tools/`
2. Add tests in `tests/test_tools/`
3. Register the tool in `src/mcp_optimizer/mcp_server.py`
4. Add examples to README.md
5. Update comprehensive_test.py if needed

## 🚀 Release Process

### Version Numbering
- Follow [Semantic Versioning](https://semver.org/)
- Format: MAJOR.MINOR.PATCH
- Update version in `pyproject.toml`

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version bumped
- [ ] Changelog updated
- [ ] Performance benchmarks run
- [ ] Security review completed

## 📋 Pull Request Guidelines

### PR Requirements
- Clear, descriptive title
- Detailed description of changes
- Link to related issues
- All tests passing
- Code review approval

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

## 🏷️ Commit Message Format

Use conventional commits format:
```
type(scope): description

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

### Examples
```
feat(knapsack): add support for multi-dimensional constraints
fix(assignment): handle edge case with empty worker list
docs(readme): update installation instructions
test(linear): add tests for integer programming
```

## 🆘 Getting Help

### Communication Channels
- GitHub Issues for bugs and feature requests
- GitHub Discussions for questions and ideas
- Email: dev@mcp-optimizer.com

### Resources
- [Project Documentation](docs/)
- [OR-Tools Documentation](https://developers.google.com/optimization)
- [PuLP Documentation](https://coin-or.github.io/pulp/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## 📄 License

By contributing to MCP Optimizer, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MCP Optimizer! 🚀 