"""Production planning optimization tools for MCP server.

This module provides tools for solving production planning problems including:
- Multi-period production planning
- Resource allocation
- Inventory management
"""

import time
from typing import Any

import pulp
from fastmcp import FastMCP
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from mcp_optimizer.utils.resource_monitor import with_resource_limits

from ..schemas.base import OptimizationResult, OptimizationStatus


class Product(BaseModel):
    """Product definition with profit and resource requirements."""

    name: str
    profit: float
    resources: dict[str, float]  # resource_name -> amount_required
    production_time: float = Field(default=0.0, ge=0)
    min_production: float = Field(default=0.0, ge=0)
    max_production: float | None = Field(default=None, ge=0)
    setup_cost: float = Field(default=0.0, ge=0)

    @field_validator("max_production")
    @classmethod
    def validate_max_production(cls, v: float, info: ValidationInfo) -> float:
        if info.data and "min_production" in info.data and v < info.data["min_production"]:
            raise ValueError("max_production must be >= min_production")
        return v


class Resource(BaseModel):
    """Resource definition with availability and cost."""

    name: str
    available: float = Field(ge=0)
    cost: float = Field(default=0.0, ge=0)
    unit: str | None = None
    renewable: bool = Field(default=False)  # Can be replenished each period


class DemandConstraint(BaseModel):
    """Demand constraint for a product."""

    product: str
    min_demand: float = Field(default=0.0, ge=0)
    max_demand: float | None = Field(default=None, ge=0)
    period: int | None = Field(default=None, ge=0)

    @field_validator("max_demand")
    @classmethod
    def validate_max_demand(cls, v: float, info: ValidationInfo) -> float:
        if info.data and "min_demand" in info.data and v < info.data["min_demand"]:
            raise ValueError("max_demand must be >= min_demand")
        return v


class ProductionPlanningInput(BaseModel):
    """Input schema for Production Planning."""

    products: list[Product]
    resources: dict[str, Resource]
    demand_constraints: list[DemandConstraint] = Field(default_factory=list)
    planning_horizon: int = Field(default=1, ge=1)
    objective: str = Field(
        default="maximize_profit",
        pattern="^(maximize_profit|minimize_cost|minimize_time)$",
    )
    allow_backorders: bool = Field(default=False)
    inventory_cost: float = Field(default=0.0, ge=0)

    @field_validator("products")
    @classmethod
    def validate_products(cls, v: list[Product]) -> list[Product]:
        if not v:
            raise ValueError("Must have at least one product")
        return v

    @field_validator("resources")
    @classmethod
    def validate_resources(cls, v: dict[str, Resource]) -> dict[str, Resource]:
        if not v:
            raise ValueError("Must have at least one resource")
        return v

    @field_validator("demand_constraints")
    @classmethod
    def validate_demand_constraints(cls, v: list[DemandConstraint]) -> list[DemandConstraint]:
        if not v:
            raise ValueError("Must have at least one demand constraint")
        return v


@with_resource_limits(timeout_seconds=120.0, estimated_memory_mb=150.0)
def solve_production_planning(input_data: dict[str, Any]) -> OptimizationResult:
    """Solve Production Planning Problem using PuLP.

    Args:
        input_data: Production planning problem specification

    Returns:
        OptimizationResult with optimal production plan
    """
    start_time = time.time()

    try:
        # Parse and validate input
        planning_input = ProductionPlanningInput(**input_data)
        products = planning_input.products
        resources = planning_input.resources
        demand_constraints = planning_input.demand_constraints
        horizon = planning_input.planning_horizon

        # Create optimization problem
        if planning_input.objective == "maximize_profit":
            prob = pulp.LpProblem("Production_Planning", pulp.LpMaximize)
        else:
            prob = pulp.LpProblem("Production_Planning", pulp.LpMinimize)

        # Decision variables: production quantities for each product in each period
        production_vars: dict[int, dict[str, Any]] = {}
        setup_vars: dict[int, dict[str, Any]] = {}  # Binary variables for setup decisions
        inventory_vars: dict[int, dict[str, Any]] = {}  # Inventory levels

        for period in range(horizon):
            production_vars[period] = {}
            setup_vars[period] = {}
            inventory_vars[period] = {}

            for product in products:
                # Production quantity
                production_vars[period][product.name] = pulp.LpVariable(
                    f"production_{product.name}_period_{period}",
                    lowBound=0,
                    cat="Continuous",
                )

                # Setup decision (binary)
                if product.setup_cost > 0:
                    setup_vars[period][product.name] = pulp.LpVariable(
                        f"setup_{product.name}_period_{period}", cat="Binary"
                    )

                # Inventory level
                inventory_vars[period][product.name] = pulp.LpVariable(
                    f"inventory_{product.name}_period_{period}",
                    lowBound=0,
                    cat="Continuous",
                )

        # Resource capacity constraints
        for period in range(horizon):
            for resource_name, resource in resources.items():
                resource_usage = pulp.lpSum(
                    production_vars[period][product.name] * product.resources.get(resource_name, 0)
                    for product in products
                )
                prob += (
                    resource_usage <= resource.available,
                    f"Resource_{resource_name}_Period_{period}",
                )

        # Production constraints
        for period in range(horizon):
            for product in products:
                prod_var = production_vars[period][product.name]

                # Minimum production
                if product.min_production > 0:
                    prob += (
                        prod_var >= product.min_production,
                        f"Min_Production_{product.name}_Period_{period}",
                    )

                # Maximum production
                if product.max_production is not None:
                    prob += (
                        prod_var <= product.max_production,
                        f"Max_Production_{product.name}_Period_{period}",
                    )

                # Setup constraints
                if product.setup_cost > 0:
                    setup_var = setup_vars[period][product.name]
                    # If producing, must setup
                    prob += (
                        prod_var <= (product.max_production or 1000000) * setup_var,
                        f"Setup_{product.name}_Period_{period}",
                    )

        # Demand constraints
        demand_by_product_period = {}
        for constraint in demand_constraints:
            period = constraint.period if constraint.period is not None else 0
            if period < horizon:
                key = (constraint.product, period)
                demand_by_product_period[key] = constraint

        # Inventory balance constraints
        for period in range(horizon):
            for product in products:
                prod_var = production_vars[period][product.name]
                inv_var = inventory_vars[period][product.name]

                # Get demand for this product in this period
                demand_constraint = demand_by_product_period.get((product.name, period))
                demand = demand_constraint.min_demand if demand_constraint else 0

                if period == 0:
                    # First period: production + initial_inventory = demand + ending_inventory
                    prob += (
                        prod_var == demand + inv_var,
                        f"Inventory_Balance_{product.name}_Period_{period}",
                    )
                else:
                    # Other periods: production + previous_inventory = demand + ending_inventory
                    prev_inv_var = inventory_vars[period - 1][product.name]
                    prob += (
                        prod_var + prev_inv_var == demand + inv_var,
                        f"Inventory_Balance_{product.name}_Period_{period}",
                    )

                # Maximum demand constraints
                if demand_constraint and demand_constraint.max_demand is not None:
                    prob += (
                        prod_var + (inventory_vars[period - 1][product.name] if period > 0 else 0)
                        <= demand_constraint.max_demand + inv_var,
                        f"Max_Demand_{product.name}_Period_{period}",
                    )

        # Objective function
        if planning_input.objective == "maximize_profit":
            # Maximize profit = revenue - production costs - setup costs - inventory costs
            total_profit = 0.0

            for period in range(horizon):
                # Production profit
                period_profit = pulp.lpSum(
                    production_vars[period][product.name] * product.profit for product in products
                )
                total_profit += period_profit

                # Setup costs
                if any(product.setup_cost > 0 for product in products):
                    setup_costs = pulp.lpSum(
                        setup_vars[period][product.name] * product.setup_cost
                        for product in products
                        if product.setup_cost > 0
                    )
                    total_profit -= setup_costs

                # Inventory costs
                if planning_input.inventory_cost > 0:
                    inventory_costs = pulp.lpSum(
                        inventory_vars[period][product.name] * planning_input.inventory_cost
                        for product in products
                    )
                    total_profit -= inventory_costs

            prob += total_profit, "Total_Profit"

        elif planning_input.objective == "minimize_cost":
            # Minimize total production and setup costs
            total_cost = 0.0

            for period in range(horizon):
                # Production costs (negative profit)
                production_costs = pulp.lpSum(
                    production_vars[period][product.name] * (-product.profit)
                    for product in products
                )
                total_cost += production_costs

                # Setup costs
                if any(product.setup_cost > 0 for product in products):
                    setup_costs = pulp.lpSum(
                        setup_vars[period][product.name] * product.setup_cost
                        for product in products
                        if product.setup_cost > 0
                    )
                    total_cost += setup_costs

            prob += total_cost, "Total_Cost"

        elif planning_input.objective == "minimize_time":
            # Minimize total production time
            total_time = pulp.lpSum(
                production_vars[period][product.name] * product.production_time
                for period in range(horizon)
                for product in products
            )
            prob += total_time, "Total_Time"

        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        # Process results
        status = pulp.LpStatus[prob.status]
        execution_time = time.time() - start_time

        if prob.status == pulp.LpStatusOptimal:
            # Extract solution
            production_plan: list[dict[str, Any]] = []
            total_profit = 0.0
            total_cost = 0.0
            total_time = 0.0
            resource_utilization: dict[str, list[float]] = {}

            for period in range(horizon):
                period_plan: dict[str, Any] = {
                    "period": period,
                    "products": [],
                    "resource_usage": {},
                    "period_profit": 0.0,
                    "period_cost": 0.0,
                }

                for product in products:
                    production_qty = production_vars[period][product.name].varValue or 0
                    inventory_qty = inventory_vars[period][product.name].varValue or 0
                    setup_decision = (
                        setup_vars[period][product.name].varValue if product.setup_cost > 0 else 0
                    )

                    product_profit = production_qty * product.profit
                    product_cost = production_qty * (-product.profit) if product.profit < 0 else 0
                    product_time = production_qty * product.production_time

                    period_plan["products"].append(
                        {
                            "name": product.name,
                            "production_quantity": production_qty,
                            "inventory_level": inventory_qty,
                            "setup_required": bool(setup_decision),
                            "profit": product_profit,
                            "production_time": product_time,
                        }
                    )

                    period_plan["period_profit"] = float(period_plan["period_profit"]) + float(
                        product_profit
                    )
                    period_plan["period_cost"] = float(period_plan["period_cost"]) + float(
                        product_cost
                    )

                    total_profit += float(product_profit)
                    total_cost += float(product_cost)
                    total_time += float(product_time)

                # Calculate resource usage for this period
                for resource_name, resource in resources.items():
                    usage = sum(
                        production_vars[period][product.name].varValue
                        * product.resources.get(resource_name, 0)
                        for product in products
                    )
                    period_plan["resource_usage"][resource_name] = {
                        "used": usage,
                        "available": resource.available,
                        "utilization": usage / resource.available if resource.available > 0 else 0,
                    }

                    if resource_name not in resource_utilization:
                        resource_utilization[resource_name] = []
                    resource_utilization[resource_name].append(float(usage))

                production_plan.append(period_plan)

            # Calculate summary statistics
            summary = {
                "total_profit": total_profit,
                "total_cost": total_cost,
                "total_production_time": total_time,
                "planning_horizon": horizon,
                "resource_utilization_summary": {},
            }

            for resource_name, usage_list in resource_utilization.items():
                resource = resources[resource_name]
                summary["resource_utilization_summary"][resource_name] = {
                    "total_usage": sum(usage_list),
                    "average_utilization": sum(u / resource.available for u in usage_list)
                    / len(usage_list)
                    if resource.available > 0
                    else 0,
                    "peak_utilization": max(u / resource.available for u in usage_list)
                    if resource.available > 0
                    else 0,
                }

            return OptimizationResult(
                status=OptimizationStatus.OPTIMAL,
                objective_value=pulp.value(prob.objective),
                variables={"production_plan": production_plan, "summary": summary},
                execution_time=execution_time,
                solver_info={
                    "solver_name": "PuLP CBC",
                    "objective": planning_input.objective,
                    "num_products": len(products),
                    "num_resources": len(resources),
                    "planning_horizon": horizon,
                },
            )

        elif prob.status == pulp.LpStatusInfeasible:
            return OptimizationResult(
                status=OptimizationStatus.INFEASIBLE,
                error_message="Production planning problem is infeasible. Check resource constraints and demand requirements.",
                execution_time=execution_time,
            )

        elif prob.status == pulp.LpStatusUnbounded:
            return OptimizationResult(
                status=OptimizationStatus.UNBOUNDED,
                error_message="Production planning problem is unbounded.",
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
            error_message=f"Production planning error: {str(e)}",
            execution_time=time.time() - start_time,
        )


# Define function that can be imported directly
def optimize_production(
    products: list[dict[str, Any]],
    constraints: dict[str, float],
    objective: str = "maximize_profit",
) -> dict[str, Any]:
    """Optimize production to maximize profit or minimize costs."""
    try:
        # Convert simple format to full production planning format
        product_list = []
        for product in products:
            # Handle both profit and cost fields
            profit_value = product.get("profit", 0.0)
            if "cost" in product:
                profit_value = -product["cost"]  # Convert cost to negative profit

            excluded_keys = ["name", "profit", "cost"]
            product_list.append(
                {
                    "name": product["name"],
                    "profit": profit_value,
                    "resources": {k: v for k, v in product.items() if k not in excluded_keys},
                    "production_time": 1.0,
                    "min_production": 0.0,
                    "max_production": 1000000.0,  # Large upper bound instead of None
                    "setup_cost": 0.0,
                }
            )

        resources = {}
        for resource_name, capacity in constraints.items():
            resources[resource_name] = {
                "name": resource_name,
                "available": capacity,
                "cost": 0.0,
                "renewable": True,
            }

        # Add minimal demand constraints for each product
        demand_constraints = []
        for product in product_list:
            demand_constraints.append(
                {
                    "product": product["name"],
                    "min_demand": 0.0,
                    "max_demand": 1000000.0,  # Large upper bound instead of None
                }
            )

        input_data = {
            "products": product_list,
            "resources": resources,
            "demand_constraints": demand_constraints,
            "planning_horizon": 1,
            "objective": objective,
            "allow_backorders": False,
            "inventory_cost": 0.0,
        }

        result = solve_production_planning(input_data)
        result_dict: dict[str, Any] = result.model_dump()
        # Convert status to string for compatibility
        result_dict["status"] = result.status.value
        return result_dict

    except Exception as e:
        return {
            "status": "error",
            "objective_value": None,
            "variables": {},
            "execution_time": 0.0,
            "solver_info": {},
            "error_message": f"Failed to optimize production: {str(e)}",
        }


def register_production_tools(mcp: FastMCP[Any]) -> None:
    """Register production planning optimization tools with MCP server."""

    @mcp.tool()
    def optimize_production_plan_tool(
        products: list[dict[str, Any]],
        resources: list[dict[str, Any]],
        periods: int,
        demand: list[dict[str, Any]],
        objective: str = "maximize_profit",
        inventory_costs: dict[str, float] | None = None,
        setup_costs: dict[str, float] | None = None,
        solver_name: str = "CBC",
        time_limit_seconds: float = 30.0,
    ) -> dict[str, Any]:
        """Optimize multi-period production planning to maximize profit or minimize costs.

        Args:
            products: List of product dictionaries with costs and resource requirements
            resources: List of resource dictionaries with capacity constraints
            periods: Number of planning periods
            demand: List of demand requirements per product per period
            objective: Optimization objective ("maximize_profit", "minimize_cost", "minimize_time")
            inventory_costs: Optional inventory holding costs per product
            setup_costs: Optional setup costs per product
            solver_name: Solver to use ("CBC", "GLPK", "GUROBI", "CPLEX")
            time_limit_seconds: Maximum solving time in seconds (default: 30.0)

        Returns:
            Optimization result with optimal production plan
        """
        input_data = {
            "products": products,
            "resources": resources,
            "periods": periods,
            "demand": demand,
            "objective": objective,
            "inventory_costs": inventory_costs,
            "setup_costs": setup_costs,
            "solver_name": solver_name,
            "time_limit_seconds": time_limit_seconds,
        }

        result = solve_production_planning(input_data)
        result_dict: dict[str, Any] = result.model_dump()
        return result_dict
