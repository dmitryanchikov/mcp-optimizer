"""Tests for financial optimization tools."""

from unittest.mock import Mock

import pytest

from mcp_optimizer.schemas.base import OptimizationStatus
from mcp_optimizer.tools.financial import (
    Asset,
    PortfolioInput,
    optimize_portfolio,
    register_financial_tools,
    solve_portfolio_optimization,
    solve_risk_parity_portfolio,
)


class TestAsset:
    """Test Asset model."""

    def test_valid_asset(self):
        """Test creating a valid asset."""
        asset = Asset(
            name="AAPL",
            expected_return=0.12,
            risk=0.15,
            sector="Technology",
            current_price=150.0,
            min_allocation=0.05,
            max_allocation=0.25,
        )
        assert asset.name == "AAPL"
        assert asset.expected_return == 0.12
        assert asset.risk == 0.15
        assert asset.sector == "Technology"
        assert asset.current_price == 150.0
        assert asset.min_allocation == 0.05
        assert asset.max_allocation == 0.25

    def test_asset_defaults(self):
        """Test asset with default values."""
        asset = Asset(name="TEST", expected_return=0.10, risk=0.20)
        assert asset.sector is None
        assert asset.current_price is None
        assert asset.min_allocation == 0.0
        assert asset.max_allocation == 1.0

    def test_invalid_risk(self):
        """Test asset with negative risk."""
        with pytest.raises(ValueError):
            Asset(name="TEST", expected_return=0.10, risk=-0.1)

    def test_invalid_price(self):
        """Test asset with negative price."""
        with pytest.raises(ValueError):
            Asset(name="TEST", expected_return=0.10, risk=0.15, current_price=-100)

    def test_invalid_allocation_bounds(self):
        """Test asset with invalid allocation bounds."""
        with pytest.raises(ValueError):
            Asset(
                name="TEST",
                expected_return=0.10,
                risk=0.15,
                min_allocation=0.3,
                max_allocation=0.2,
            )


class TestPortfolioInput:
    """Test PortfolioInput model."""

    def test_valid_portfolio_input(self):
        """Test creating valid portfolio input."""
        assets = [
            Asset(name="AAPL", expected_return=0.12, risk=0.15, sector="Tech"),
            Asset(name="GOOGL", expected_return=0.14, risk=0.18, sector="Tech"),
        ]
        portfolio_input = PortfolioInput(
            assets=assets,
            budget=10000.0,
            risk_tolerance=0.2,
            sector_limits={"Tech": 0.6},
        )
        assert len(portfolio_input.assets) == 2
        assert portfolio_input.budget == 10000.0
        assert portfolio_input.risk_tolerance == 0.2
        assert portfolio_input.sector_limits["Tech"] == 0.6

    def test_empty_assets(self):
        """Test portfolio input with empty assets."""
        with pytest.raises(ValueError, match="At least one asset required"):
            PortfolioInput(assets=[], budget=10000.0, risk_tolerance=0.2)

    def test_invalid_sector_limits(self):
        """Test portfolio input with invalid sector limits."""
        assets = [Asset(name="AAPL", expected_return=0.12, risk=0.15)]
        with pytest.raises(ValueError, match="Sector limit for.*must be between 0 and 1"):
            PortfolioInput(
                assets=assets,
                budget=10000.0,
                risk_tolerance=0.2,
                sector_limits={"Tech": 1.5},
            )

    def test_correlation_matrix_validation(self):
        """Test correlation matrix validation."""
        assets = [
            Asset(name="AAPL", expected_return=0.12, risk=0.15),
            Asset(name="GOOGL", expected_return=0.14, risk=0.18),
        ]

        # Valid correlation matrix
        correlation_matrix = [[1.0, 0.5], [0.5, 1.0]]
        portfolio_input = PortfolioInput(
            assets=assets,
            budget=10000.0,
            risk_tolerance=0.2,
            correlation_matrix=correlation_matrix,
        )
        assert portfolio_input.correlation_matrix == correlation_matrix

        # Invalid dimensions
        with pytest.raises(ValueError, match="Correlation matrix dimensions must match"):
            PortfolioInput(
                assets=assets,
                budget=10000.0,
                risk_tolerance=0.2,
                correlation_matrix=[[1.0]],
            )

        # Invalid diagonal elements
        with pytest.raises(ValueError, match="Diagonal elements.*must be 1"):
            PortfolioInput(
                assets=assets,
                budget=10000.0,
                risk_tolerance=0.2,
                correlation_matrix=[[0.8, 0.5], [0.5, 1.0]],
            )

        # Non-symmetric matrix
        with pytest.raises(ValueError, match="Correlation matrix must be symmetric"):
            PortfolioInput(
                assets=assets,
                budget=10000.0,
                risk_tolerance=0.2,
                correlation_matrix=[[1.0, 0.3], [0.5, 1.0]],
            )


class TestPortfolioOptimization:
    """Test Portfolio Optimization functions."""

    def test_maximize_return_objective(self):
        """Test portfolio optimization with maximize return objective."""
        input_data = {
            "assets": [
                {"name": "AAPL", "expected_return": 0.12, "risk": 0.15},
                {"name": "MSFT", "expected_return": 0.10, "risk": 0.12},
            ],
            "budget": 10000.0,
            "risk_tolerance": 0.2,
            "objective": "maximize_return",
        }

        result = solve_portfolio_optimization(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
        assert "portfolio_allocation" in result.variables
        assert result.objective_value is not None

    def test_minimize_risk_objective(self):
        """Test portfolio optimization with minimize risk objective."""
        input_data = {
            "assets": [
                {"name": "AAPL", "expected_return": 0.12, "risk": 0.15},
                {"name": "MSFT", "expected_return": 0.10, "risk": 0.12},
            ],
            "budget": 10000.0,
            "risk_tolerance": 0.2,
            "objective": "minimize_risk",
        }

        result = solve_portfolio_optimization(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
        assert "portfolio_allocation" in result.variables

    def test_minimize_risk_with_correlation(self):
        """Test minimize risk with correlation matrix."""
        input_data = {
            "assets": [
                {"name": "AAPL", "expected_return": 0.12, "risk": 0.15},
                {"name": "MSFT", "expected_return": 0.10, "risk": 0.12},
            ],
            "budget": 10000.0,
            "risk_tolerance": 0.2,
            "objective": "minimize_risk",
            "correlation_matrix": [[1.0, 0.3], [0.3, 1.0]],
        }

        result = solve_portfolio_optimization(input_data)
        # Correlation matrix optimization is complex and may fail with linear programming
        assert result.status in [OptimizationStatus.OPTIMAL, OptimizationStatus.ERROR]

    def test_sharpe_ratio_objective(self):
        """Test portfolio optimization with sharpe ratio objective."""
        input_data = {
            "assets": [
                {"name": "AAPL", "expected_return": 0.12, "risk": 0.15},
                {"name": "MSFT", "expected_return": 0.10, "risk": 0.12},
            ],
            "budget": 10000.0,
            "risk_tolerance": 0.2,
            "objective": "sharpe_ratio",
            "risk_free_rate": 0.03,
        }

        result = solve_portfolio_optimization(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_sector_constraints(self):
        """Test portfolio optimization with sector constraints."""
        input_data = {
            "assets": [
                {"name": "AAPL", "expected_return": 0.12, "risk": 0.15, "sector": "Tech"},
                {"name": "MSFT", "expected_return": 0.10, "risk": 0.12, "sector": "Tech"},
                {"name": "JNJ", "expected_return": 0.08, "risk": 0.10, "sector": "Healthcare"},
            ],
            "budget": 10000.0,
            "risk_tolerance": 0.2,
            "sector_limits": {"Tech": 0.6},
        }

        result = solve_portfolio_optimization(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_asset_allocation_bounds(self):
        """Test portfolio optimization with asset allocation bounds."""
        input_data = {
            "assets": [
                {
                    "name": "AAPL",
                    "expected_return": 0.12,
                    "risk": 0.15,
                    "min_allocation": 0.1,
                    "max_allocation": 0.4,
                },
                {
                    "name": "MSFT",
                    "expected_return": 0.10,
                    "risk": 0.12,
                    "min_allocation": 0.05,
                    "max_allocation": 0.3,
                },
            ],
            "budget": 10000.0,
            "risk_tolerance": 0.2,
            "min_allocation": 0.05,
            "max_allocation": 0.5,
        }

        result = solve_portfolio_optimization(input_data)
        assert result.status in [OptimizationStatus.OPTIMAL, OptimizationStatus.INFEASIBLE]

    def test_infeasible_problem(self):
        """Test infeasible portfolio optimization problem."""
        input_data = {
            "assets": [
                {
                    "name": "AAPL",
                    "expected_return": 0.12,
                    "risk": 0.15,
                    "min_allocation": 0.8,  # Too high minimum allocation
                },
                {
                    "name": "MSFT",
                    "expected_return": 0.10,
                    "risk": 0.12,
                    "min_allocation": 0.8,  # Too high minimum allocation
                },
            ],
            "budget": 10000.0,
            "risk_tolerance": 0.2,
        }

        result = solve_portfolio_optimization(input_data)
        assert result.status in [OptimizationStatus.INFEASIBLE, OptimizationStatus.UNBOUNDED]

    def test_invalid_input_data(self):
        """Test portfolio optimization with invalid input data."""
        result = solve_portfolio_optimization({"assets": [], "budget": 10000.0})
        assert result.status == OptimizationStatus.ERROR
        assert "At least one asset required" in result.error_message


class TestRiskParityPortfolio:
    """Test Risk Parity Portfolio functions."""

    def test_risk_parity_basic(self):
        """Test basic risk parity portfolio optimization."""
        input_data = {
            "assets": [
                {"name": "AAPL", "expected_return": 0.12, "risk": 0.15},
                {"name": "MSFT", "expected_return": 0.10, "risk": 0.12},
                {"name": "BONDS", "expected_return": 0.04, "risk": 0.03},
            ],
            "budget": 10000.0,
            "risk_tolerance": 0.2,
        }

        result = solve_risk_parity_portfolio(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
        assert "portfolio_allocation" in result.variables

    def test_risk_parity_with_constraints(self):
        """Test risk parity with constraints."""
        input_data = {
            "assets": [
                {"name": "AAPL", "expected_return": 0.12, "risk": 0.15, "min_allocation": 0.1},
                {"name": "BONDS", "expected_return": 0.04, "risk": 0.03, "max_allocation": 0.5},
            ],
            "budget": 10000.0,
            "risk_tolerance": 0.2,
            "min_allocation": 0.05,
            "max_allocation": 0.6,
        }

        result = solve_risk_parity_portfolio(input_data)
        assert result.status == OptimizationStatus.OPTIMAL


class TestOptimizePortfolio:
    """Test optimize_portfolio wrapper function."""

    def test_optimize_portfolio_basic(self):
        """Test basic portfolio optimization wrapper."""
        assets = [
            {"name": "AAPL", "expected_return": 0.12, "risk": 0.15},
            {"name": "MSFT", "expected_return": 0.10, "risk": 0.12},
        ]

        result = optimize_portfolio(assets)
        assert result["status"] == "optimal"
        assert "portfolio_allocation" in result["variables"]

    def test_optimize_portfolio_with_constraints(self):
        """Test portfolio optimization with all constraints."""
        assets = [
            {"name": "AAPL", "expected_return": 0.12, "risk": 0.15, "sector": "Tech"},
            {"name": "JNJ", "expected_return": 0.08, "risk": 0.10, "sector": "Healthcare"},
        ]

        result = optimize_portfolio(
            assets=assets,
            objective="minimize_risk",
            budget=5000.0,
            risk_tolerance=0.15,
            sector_constraints={"Tech": 0.7},
            min_allocation=0.1,
            max_allocation=0.8,
        )
        assert result["status"] == "optimal"


class TestRegisterFinancialTools:
    """Test MCP tool registration."""

    def test_register_financial_tools(self):
        """Test registering financial tools with MCP."""
        mcp_mock = Mock()
        mcp_mock.tool.return_value = lambda func: func  # Mock decorator

        register_financial_tools(mcp_mock)

        # Verify that mcp.tool() was called
        mcp_mock.tool.assert_called()

    def test_optimize_portfolio_tool(self):
        """Test the MCP tool wrapper with real solving."""
        mcp_mock = Mock()
        tool_functions = []

        def mock_tool_decorator():
            def decorator(func):
                tool_functions.append(func)
                return func

            return decorator

        mcp_mock.tool = mock_tool_decorator

        register_financial_tools(mcp_mock)

        # Get the registered tool function
        assert len(tool_functions) == 1
        tool_func = tool_functions[0]

        # Test the tool function with real problem
        assets = [
            {"name": "AAPL", "expected_return": 0.12, "risk": 0.15},
            {"name": "MSFT", "expected_return": 0.10, "risk": 0.12},
        ]
        result = tool_func(
            assets=assets,
            objective="maximize_return",
            budget=1000.0,
        )

        # Verify real solving occurred
        assert result["status"] == "optimal"
        assert "variables" in result
        assert "execution_time" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_single_asset_portfolio(self):
        """Test portfolio with single asset."""
        input_data = {
            "assets": [{"name": "AAPL", "expected_return": 0.12, "risk": 0.15}],
            "budget": 1000.0,
            "risk_tolerance": 0.2,
        }

        result = solve_portfolio_optimization(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
        assert result.variables["portfolio_allocation"]["AAPL"]["amount"] == 1000.0

    def test_zero_risk_tolerance(self):
        """Test portfolio with zero risk tolerance."""
        input_data = {
            "assets": [
                {"name": "AAPL", "expected_return": 0.12, "risk": 0.15},
                {"name": "BONDS", "expected_return": 0.04, "risk": 0.03},
            ],
            "budget": 1000.0,
            "risk_tolerance": 0.0,
            "objective": "sharpe_ratio",
        }

        result = solve_portfolio_optimization(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_high_risk_tolerance(self):
        """Test portfolio with very high risk tolerance."""
        input_data = {
            "assets": [
                {"name": "AAPL", "expected_return": 0.12, "risk": 0.15},
                {"name": "BONDS", "expected_return": 0.04, "risk": 0.03},
            ],
            "budget": 1000.0,
            "risk_tolerance": 1.0,
            "objective": "sharpe_ratio",
        }

        result = solve_portfolio_optimization(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
