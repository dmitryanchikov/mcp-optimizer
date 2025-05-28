"""Financial optimization tools for MCP server.

This module provides tools for solving financial optimization problems including:
- Portfolio Optimization
- Risk Management
"""

import math
import time
from typing import Any

import pulp
from fastmcp import FastMCP
from pydantic import BaseModel, Field, validator

from ..schemas.base import OptimizationResult, OptimizationStatus


class Asset(BaseModel):
    """Asset definition with return and risk characteristics."""

    name: str
    expected_return: float
    risk: float = Field(ge=0)
    sector: str | None = None
    current_price: float | None = Field(default=None, ge=0)
    min_allocation: float = Field(default=0.0, ge=0, le=1)
    max_allocation: float = Field(default=1.0, ge=0, le=1)

    @validator("max_allocation")
    def validate_max_allocation(cls, v: float, values: dict[str, Any]) -> float:
        if "min_allocation" in values and v < values["min_allocation"]:
            raise ValueError("max_allocation must be >= min_allocation")
        return v


class PortfolioInput(BaseModel):
    """Input schema for Portfolio Optimization."""

    assets: list[Asset]
    budget: float = Field(gt=0)
    risk_tolerance: float = Field(ge=0)
    min_allocation: float = Field(default=0.0, ge=0, le=1)
    max_allocation: float = Field(default=1.0, ge=0, le=1)
    sector_limits: dict[str, float] = Field(default_factory=dict)
    objective: str = Field(
        default="maximize_return",
        pattern="^(maximize_return|minimize_risk|sharpe_ratio)$",
    )
    risk_free_rate: float = Field(default=0.02, ge=0)
    correlation_matrix: list[list[float]] | None = None

    @validator("assets")
    def validate_assets(cls, v: list[Asset]) -> list[Asset]:
        if not v:
            raise ValueError("At least one asset required")
        return v

    @validator("sector_limits")
    def validate_sector_limits(cls, v: dict[str, float]) -> dict[str, float]:
        for sector, limit in v.items():
            if not (0 <= limit <= 1):
                raise ValueError(f"Sector limit for {sector} must be between 0 and 1")
        return v

    @validator("correlation_matrix")
    def validate_correlation_matrix(
        cls, v: list[list[float]] | None, values: dict[str, Any]
    ) -> list[list[float]] | None:
        if v is not None and "assets" in values:
            n = len(values["assets"])
            if len(v) != n or any(len(row) != n for row in v):
                raise ValueError("Correlation matrix dimensions must match number of assets")
            # Check if matrix is symmetric and diagonal elements are 1
            for i in range(n):
                if abs(v[i][i] - 1.0) > 1e-6:
                    raise ValueError("Diagonal elements of correlation matrix must be 1")
                for j in range(i):
                    if abs(v[i][j] - v[j][i]) > 1e-6:
                        raise ValueError("Correlation matrix must be symmetric")
        return v


def solve_portfolio_optimization(input_data: dict[str, Any]) -> OptimizationResult:
    """Solve Portfolio Optimization Problem using PuLP.

    Args:
        input_data: Portfolio optimization problem specification

    Returns:
        OptimizationResult with optimal portfolio allocation
    """
    start_time = time.time()

    try:
        # Parse and validate input
        portfolio_input = PortfolioInput(**input_data)
        assets = portfolio_input.assets
        budget = portfolio_input.budget

        # Create optimization problem
        if portfolio_input.objective == "maximize_return":
            prob = pulp.LpProblem("Portfolio_Optimization", pulp.LpMaximize)
        else:
            prob = pulp.LpProblem("Portfolio_Optimization", pulp.LpMinimize)

        # Decision variables: allocation amounts for each asset
        allocations = {}
        for asset in assets:
            allocations[asset.name] = pulp.LpVariable(
                f"allocation_{asset.name}",
                lowBound=asset.min_allocation * budget,
                upBound=asset.max_allocation * budget,
                cat="Continuous",
            )

        # Budget constraint
        prob += pulp.lpSum(allocations.values()) == budget, "Budget_Constraint"

        # Global allocation constraints
        for asset in assets:
            prob += (
                allocations[asset.name] >= portfolio_input.min_allocation * budget,
                f"Min_Allocation_{asset.name}",
            )
            prob += (
                allocations[asset.name] <= portfolio_input.max_allocation * budget,
                f"Max_Allocation_{asset.name}",
            )

        # Sector constraints
        sectors: dict[str, list[Any]] = {}
        for asset in assets:
            if asset.sector:
                if asset.sector not in sectors:
                    sectors[asset.sector] = []
                sectors[asset.sector].append(allocations[asset.name])

        for sector, limit in portfolio_input.sector_limits.items():
            if sector in sectors:
                prob += (
                    pulp.lpSum(sectors[sector]) <= limit * budget,
                    f"Sector_Limit_{sector}",
                )

        # Objective function
        if portfolio_input.objective == "maximize_return":
            # Maximize expected return
            expected_return = pulp.lpSum(
                allocations[asset.name] * asset.expected_return / budget for asset in assets
            )
            prob += expected_return, "Expected_Return"

        elif portfolio_input.objective == "minimize_risk":
            # Minimize portfolio risk (simplified as weighted average of individual risks)
            # Note: This is a simplification. True portfolio risk requires covariance matrix
            if portfolio_input.correlation_matrix:
                # Use correlation matrix to calculate portfolio variance
                portfolio_variance = 0
                for i, asset_i in enumerate(assets):
                    for j, asset_j in enumerate(assets):
                        weight_i = allocations[asset_i.name] / budget
                        weight_j = allocations[asset_j.name] / budget
                        correlation = portfolio_input.correlation_matrix[i][j]
                        portfolio_variance += (
                            weight_i * weight_j * asset_i.risk * asset_j.risk * correlation
                        )

                # Since PuLP doesn't handle quadratic objectives directly, we'll use a linear approximation
                # This is a limitation - for true portfolio optimization, a QP solver would be better
                portfolio_risk = pulp.lpSum(
                    allocations[asset.name] * asset.risk / budget for asset in assets
                )
            else:
                portfolio_risk = pulp.lpSum(
                    allocations[asset.name] * asset.risk / budget for asset in assets
                )
            prob += portfolio_risk, "Portfolio_Risk"

        elif portfolio_input.objective == "sharpe_ratio":
            # Maximize Sharpe ratio (simplified)
            # This is complex to implement directly in linear programming
            # We'll approximate by maximizing return - risk_penalty * risk
            risk_penalty = (
                1.0 / portfolio_input.risk_tolerance if portfolio_input.risk_tolerance > 0 else 1.0
            )

            expected_return = pulp.lpSum(
                allocations[asset.name] * asset.expected_return / budget for asset in assets
            )
            portfolio_risk = pulp.lpSum(
                allocations[asset.name] * asset.risk / budget for asset in assets
            )

            sharpe_approximation = expected_return - risk_penalty * portfolio_risk
            prob += sharpe_approximation, "Sharpe_Approximation"

        # Risk tolerance constraint
        if portfolio_input.risk_tolerance > 0:
            portfolio_risk = pulp.lpSum(
                allocations[asset.name] * asset.risk / budget for asset in assets
            )
            prob += portfolio_risk <= portfolio_input.risk_tolerance, "Risk_Tolerance"

        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        # Process results
        status = pulp.LpStatus[prob.status]
        execution_time = time.time() - start_time

        if prob.status == pulp.LpStatusOptimal:
            # Extract solution
            portfolio_allocation = {}
            total_allocation = 0
            portfolio_return = 0
            portfolio_risk = 0

            for asset in assets:
                allocation_amount = allocations[asset.name].varValue
                allocation_weight = allocation_amount / budget

                portfolio_allocation[asset.name] = {
                    "amount": allocation_amount,
                    "weight": allocation_weight,
                    "expected_return": asset.expected_return,
                    "risk": asset.risk,
                    "sector": asset.sector,
                }

                total_allocation += allocation_amount
                portfolio_return += allocation_weight * asset.expected_return
                portfolio_risk += allocation_weight * asset.risk

            # Calculate portfolio metrics
            portfolio_variance = portfolio_risk**2  # Simplified
            portfolio_std = math.sqrt(portfolio_variance) if portfolio_variance > 0 else 0
            sharpe_ratio = (
                (portfolio_return - portfolio_input.risk_free_rate) / portfolio_std
                if portfolio_std > 0
                else 0
            )

            # Sector allocation summary
            sector_allocation = {}
            for asset in assets:
                if asset.sector:
                    if asset.sector not in sector_allocation:
                        sector_allocation[asset.sector] = 0
                    sector_allocation[asset.sector] += portfolio_allocation[asset.name]["weight"]

            return OptimizationResult(
                status=OptimizationStatus.OPTIMAL,
                objective_value=pulp.value(prob.objective),
                variables={
                    "portfolio_allocation": portfolio_allocation,
                    "portfolio_metrics": {
                        "total_allocation": total_allocation,
                        "expected_return": portfolio_return,
                        "portfolio_risk": portfolio_risk,
                        "portfolio_std": portfolio_std,
                        "sharpe_ratio": sharpe_ratio,
                        "risk_free_rate": portfolio_input.risk_free_rate,
                    },
                    "sector_allocation": sector_allocation,
                    "budget_utilization": total_allocation / budget,
                },
                execution_time=execution_time,
                solver_info={
                    "solver_name": "PuLP CBC",
                    "objective": portfolio_input.objective,
                    "num_assets": len(assets),
                    "num_sectors": len(sector_allocation),
                },
            )

        elif prob.status == pulp.LpStatusInfeasible:
            return OptimizationResult(
                status=OptimizationStatus.INFEASIBLE,
                error_message="Portfolio optimization problem is infeasible. Check constraints.",
                execution_time=execution_time,
            )

        elif prob.status == pulp.LpStatusUnbounded:
            return OptimizationResult(
                status=OptimizationStatus.UNBOUNDED,
                error_message="Portfolio optimization problem is unbounded.",
                execution_time=execution_time,
            )

        else:
            return OptimizationResult(
                status=OptimizationStatus.ERROR,
                error_message=f"Solver failed with status: {status}",
                execution_time=execution_time,
            )

    except Exception as e:
        return OptimizationResult(
            status=OptimizationStatus.ERROR,
            error_message=f"Portfolio optimization error: {str(e)}",
            execution_time=time.time() - start_time,
        )


def solve_risk_parity_portfolio(input_data: dict[str, Any]) -> OptimizationResult:
    """Solve Risk Parity Portfolio Optimization.

    This is a simplified implementation that aims for equal risk contribution
    from each asset in the portfolio.

    Args:
        input_data: Risk parity portfolio specification

    Returns:
        OptimizationResult with risk parity portfolio allocation
    """
    start_time = time.time()

    try:
        # Parse input (reuse PortfolioInput schema)
        portfolio_input = PortfolioInput(**input_data)
        assets = portfolio_input.assets
        budget = portfolio_input.budget

        # For risk parity, we want equal risk contribution
        # Simplified approach: allocate inversely proportional to risk
        total_inverse_risk = sum(1.0 / asset.risk for asset in assets if asset.risk > 0)

        if total_inverse_risk == 0:
            return OptimizationResult(
                status=OptimizationStatus.ERROR,
                error_message="All assets have zero risk - cannot create risk parity portfolio",
                execution_time=time.time() - start_time,
            )

        portfolio_allocation = {}
        portfolio_return = 0.0
        portfolio_risk = 0.0

        for asset in assets:
            if asset.risk > 0:
                weight = (1.0 / asset.risk) / total_inverse_risk
                allocation_amount = weight * budget

                # Apply allocation constraints
                allocation_amount = max(allocation_amount, asset.min_allocation * budget)
                allocation_amount = min(allocation_amount, asset.max_allocation * budget)

                portfolio_allocation[asset.name] = {
                    "amount": allocation_amount,
                    "weight": allocation_amount / budget,
                    "expected_return": asset.expected_return,
                    "risk": asset.risk,
                    "risk_contribution": (allocation_amount / budget) * asset.risk,
                    "sector": asset.sector,
                }

                portfolio_return += (allocation_amount / budget) * asset.expected_return
                portfolio_risk += (allocation_amount / budget) * asset.risk
            else:
                portfolio_allocation[asset.name] = {
                    "amount": 0,
                    "weight": 0,
                    "expected_return": asset.expected_return,
                    "risk": asset.risk,
                    "risk_contribution": 0,
                    "sector": asset.sector,
                }

        # Normalize to budget
        total_allocation = 0.0
        for alloc in portfolio_allocation.values():
            total_allocation += float(alloc["amount"])  # type: ignore[arg-type]
        if total_allocation > 0:
            scale_factor = budget / total_allocation
            for asset_name in portfolio_allocation:
                portfolio_allocation[asset_name]["amount"] *= scale_factor  # type: ignore[operator]
                portfolio_allocation[asset_name]["weight"] *= scale_factor  # type: ignore[operator]
                portfolio_allocation[asset_name]["risk_contribution"] *= scale_factor  # type: ignore[operator]

        execution_time = time.time() - start_time

        return OptimizationResult(
            status=OptimizationStatus.OPTIMAL,
            objective_value=portfolio_risk,  # Risk parity minimizes risk concentration
            variables={
                "portfolio_allocation": portfolio_allocation,
                "portfolio_metrics": {
                    "total_allocation": budget,
                    "expected_return": portfolio_return,
                    "portfolio_risk": portfolio_risk,
                    "risk_parity_score": (
                        1.0
                        - (
                            max(
                                float(alloc["risk_contribution"])  # type: ignore[arg-type]
                                for alloc in portfolio_allocation.values()
                            )
                            - min(
                                float(alloc["risk_contribution"])  # type: ignore[arg-type]
                                for alloc in portfolio_allocation.values()
                            )
                        )
                    )
                    if portfolio_allocation
                    else 0.0,
                },
                "budget_utilization": 1.0,
            },
            execution_time=execution_time,
            solver_info={
                "solver_name": "Risk Parity Heuristic",
                "objective": "risk_parity",
                "num_assets": len(assets),
            },
        )

    except Exception as e:
        return OptimizationResult(
            status=OptimizationStatus.ERROR,
            error_message=f"Risk parity portfolio error: {str(e)}",
            execution_time=time.time() - start_time,
        )


# Define function that can be imported directly
def optimize_portfolio(
    assets: list[dict[str, Any]],
    objective: str = "maximize_return",
    budget: float = 1.0,
    risk_tolerance: float | None = None,
    sector_constraints: dict[str, float] | None = None,
    min_allocation: float = 0.0,
    max_allocation: float = 1.0,
) -> dict[str, Any]:
    """Optimize portfolio allocation to maximize return or minimize risk."""
    try:
        input_data = {
            "assets": assets,
            "objective": objective,
            "budget": budget,
            "risk_tolerance": risk_tolerance or 0.0,
            "sector_limits": sector_constraints or {},
            "min_allocation": min_allocation,
            "max_allocation": max_allocation,
        }

        result = solve_portfolio_optimization(input_data)
        return {
            "status": result.status,
            "objective_value": result.objective_value,
            "variables": result.variables,
            "execution_time": result.execution_time,
            "solver_info": result.solver_info,
            "error_message": result.error_message,
        }

    except Exception as e:
        return {
            "status": "error",
            "objective_value": None,
            "variables": {},
            "execution_time": 0.0,
            "solver_info": {},
            "error_message": f"Failed to optimize portfolio: {str(e)}",
        }


def register_financial_tools(mcp: FastMCP[Any]) -> None:
    """Register financial optimization tools with MCP server."""

    @mcp.tool()
    def optimize_portfolio_tool(
        assets: list[dict[str, Any]],
        objective: str = "maximize_return",
        budget: float = 1.0,
        risk_tolerance: float | None = None,
        sector_constraints: dict[str, float] | None = None,
        min_allocation: float = 0.0,
        max_allocation: float = 1.0,
        solver_name: str = "CBC",
        time_limit_seconds: float = 30.0,
    ) -> dict[str, Any]:
        """Optimize portfolio allocation to maximize return or minimize risk.

        Args:
            assets: List of asset dictionaries with expected return, risk, and sector
            objective: Optimization objective ("maximize_return", "minimize_risk", "maximize_sharpe", "risk_parity")
            budget: Total budget to allocate (default: 1.0)
            risk_tolerance: Maximum acceptable portfolio risk (optional)
            sector_constraints: Maximum allocation per sector (optional)
            min_allocation: Minimum allocation per asset (default: 0.0)
            max_allocation: Maximum allocation per asset (default: 1.0)
            solver_name: Solver to use ("CBC", "GLPK", "GUROBI", "CPLEX")
            time_limit_seconds: Maximum solving time in seconds (default: 30.0)

        Returns:
            Optimization result with optimal portfolio allocation
        """
        return optimize_portfolio(
            assets,
            objective,
            budget,
            risk_tolerance,
            sector_constraints,
            min_allocation,
            max_allocation,
        )
