"""Tests for production planning optimization tools."""

from unittest.mock import Mock

import pytest

from mcp_optimizer.schemas.base import OptimizationStatus
from mcp_optimizer.tools.production import (
    DemandConstraint,
    Product,
    ProductionPlanningInput,
    Resource,
    optimize_production,
    register_production_tools,
    solve_production_planning,
)


class TestProduct:
    """Test Product model."""

    def test_valid_product(self):
        """Test creating a valid product."""
        product = Product(
            name="Widget",
            profit=50.0,
            resources={"labor": 2.0, "material": 1.5},
            production_time=3.0,
            min_production=10.0,
            max_production=100.0,
            setup_cost=500.0,
        )
        assert product.name == "Widget"
        assert product.profit == 50.0
        assert product.resources == {"labor": 2.0, "material": 1.5}
        assert product.production_time == 3.0
        assert product.min_production == 10.0
        assert product.max_production == 100.0
        assert product.setup_cost == 500.0

    def test_product_defaults(self):
        """Test product with default values."""
        product = Product(name="Test", profit=20.0, resources={"labor": 1.0})
        assert product.production_time == 0.0
        assert product.min_production == 0.0
        assert product.max_production is None
        assert product.setup_cost == 0.0

    def test_invalid_max_production(self):
        """Test product with invalid max_production."""
        with pytest.raises(ValueError, match="max_production must be >= min_production"):
            Product(
                name="Test",
                profit=20.0,
                resources={"labor": 1.0},
                min_production=50.0,
                max_production=30.0,
            )

    def test_negative_values(self):
        """Test product with negative values."""
        with pytest.raises(ValueError):
            Product(name="Test", profit=20.0, resources={"labor": 1.0}, production_time=-1.0)

        with pytest.raises(ValueError):
            Product(name="Test", profit=20.0, resources={"labor": 1.0}, min_production=-10.0)

        with pytest.raises(ValueError):
            Product(name="Test", profit=20.0, resources={"labor": 1.0}, setup_cost=-100.0)


class TestResource:
    """Test Resource model."""

    def test_valid_resource(self):
        """Test creating a valid resource."""
        resource = Resource(
            name="Labor",
            available=100.0,
            cost=15.0,
            unit="hours",
            renewable=True,
        )
        assert resource.name == "Labor"
        assert resource.available == 100.0
        assert resource.cost == 15.0
        assert resource.unit == "hours"
        assert resource.renewable is True

    def test_resource_defaults(self):
        """Test resource with default values."""
        resource = Resource(name="Material", available=50.0)
        assert resource.cost == 0.0
        assert resource.unit is None
        assert resource.renewable is False

    def test_negative_values(self):
        """Test resource with negative values."""
        with pytest.raises(ValueError):
            Resource(name="Test", available=-10.0)

        with pytest.raises(ValueError):
            Resource(name="Test", available=100.0, cost=-5.0)


class TestDemandConstraint:
    """Test DemandConstraint model."""

    def test_valid_demand_constraint(self):
        """Test creating a valid demand constraint."""
        constraint = DemandConstraint(
            product="Widget",
            min_demand=50.0,
            max_demand=200.0,
            period=1,
        )
        assert constraint.product == "Widget"
        assert constraint.min_demand == 50.0
        assert constraint.max_demand == 200.0
        assert constraint.period == 1

    def test_demand_constraint_defaults(self):
        """Test demand constraint with default values."""
        constraint = DemandConstraint(product="Test")
        assert constraint.min_demand == 0.0
        assert constraint.max_demand is None
        assert constraint.period is None

    def test_invalid_max_demand(self):
        """Test demand constraint with invalid max_demand."""
        with pytest.raises(ValueError, match="max_demand must be >= min_demand"):
            DemandConstraint(product="Test", min_demand=100.0, max_demand=50.0)

    def test_negative_values(self):
        """Test demand constraint with negative values."""
        with pytest.raises(ValueError):
            DemandConstraint(product="Test", min_demand=-10.0)

        with pytest.raises(ValueError):
            DemandConstraint(product="Test", period=-1)


class TestProductionPlanningInput:
    """Test ProductionPlanningInput model."""

    def test_valid_production_planning_input(self):
        """Test creating valid production planning input."""
        products = [
            Product(name="Widget", profit=50.0, resources={"labor": 2.0}),
            Product(name="Gadget", profit=30.0, resources={"labor": 1.5}),
        ]
        resources = {
            "labor": Resource(name="Labor", available=100.0),
        }
        demand_constraints = [
            DemandConstraint(product="Widget", min_demand=10.0),
        ]

        input_data = ProductionPlanningInput(
            products=products,
            resources=resources,
            demand_constraints=demand_constraints,
            planning_horizon=3,
            objective="maximize_profit",
            allow_backorders=True,
            inventory_cost=2.0,
        )

        assert len(input_data.products) == 2
        assert len(input_data.resources) == 1
        assert len(input_data.demand_constraints) == 1
        assert input_data.planning_horizon == 3
        assert input_data.objective == "maximize_profit"
        assert input_data.allow_backorders is True
        assert input_data.inventory_cost == 2.0

    def test_empty_products(self):
        """Test production planning input with empty products."""
        resources = {"labor": Resource(name="Labor", available=100.0)}
        demand_constraints = [DemandConstraint(product="Widget", min_demand=10.0)]

        with pytest.raises(ValueError, match="Must have at least one product"):
            ProductionPlanningInput(
                products=[],
                resources=resources,
                demand_constraints=demand_constraints,
            )

    def test_empty_resources(self):
        """Test production planning input with empty resources."""
        products = [Product(name="Widget", profit=50.0, resources={"labor": 2.0})]
        demand_constraints = [DemandConstraint(product="Widget", min_demand=10.0)]

        with pytest.raises(ValueError, match="Must have at least one resource"):
            ProductionPlanningInput(
                products=products,
                resources={},
                demand_constraints=demand_constraints,
            )

    def test_empty_demand_constraints(self):
        """Test production planning input with empty demand constraints."""
        products = [Product(name="Widget", profit=50.0, resources={"labor": 2.0})]
        resources = {"labor": Resource(name="Labor", available=100.0)}

        with pytest.raises(ValueError, match="Must have at least one demand constraint"):
            ProductionPlanningInput(
                products=products,
                resources=resources,
                demand_constraints=[],
            )

    def test_invalid_objective(self):
        """Test production planning input with invalid objective."""
        products = [Product(name="Widget", profit=50.0, resources={"labor": 2.0})]
        resources = {"labor": Resource(name="Labor", available=100.0)}
        demand_constraints = [DemandConstraint(product="Widget", min_demand=10.0)]

        with pytest.raises(ValueError):
            ProductionPlanningInput(
                products=products,
                resources=resources,
                demand_constraints=demand_constraints,
                objective="invalid_objective",
            )

    def test_negative_planning_horizon(self):
        """Test production planning input with negative planning horizon."""
        products = [Product(name="Widget", profit=50.0, resources={"labor": 2.0})]
        resources = {"labor": Resource(name="Labor", available=100.0)}
        demand_constraints = [DemandConstraint(product="Widget", min_demand=10.0)]

        with pytest.raises(ValueError):
            ProductionPlanningInput(
                products=products,
                resources=resources,
                demand_constraints=demand_constraints,
                planning_horizon=0,
            )


class TestProductionPlanning:
    """Test Production Planning functions."""

    def test_maximize_profit_single_period(self):
        """Test production planning with maximize profit objective for single period."""
        input_data = {
            "products": [
                {
                    "name": "Widget",
                    "profit": 50.0,
                    "resources": {"labor": 2.0, "material": 1.0},
                    "min_production": 5.0,
                    "max_production": 100.0,
                },
                {
                    "name": "Gadget",
                    "profit": 30.0,
                    "resources": {"labor": 1.5, "material": 0.5},
                    "min_production": 3.0,
                    "max_production": 80.0,
                },
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 100.0},
                "material": {"name": "Material", "available": 50.0},
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 10.0, "max_demand": 50.0},
                {"product": "Gadget", "min_demand": 5.0, "max_demand": 40.0},
            ],
            "planning_horizon": 1,
            "objective": "maximize_profit",
        }

        result = solve_production_planning(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
        assert "production_plan" in result.variables
        assert result.objective_value is not None

    def test_minimize_cost_objective(self):
        """Test production planning with minimize cost objective."""
        input_data = {
            "products": [
                {
                    "name": "Widget",
                    "profit": -20.0,  # Cost represented as negative profit
                    "resources": {"labor": 2.0},
                },
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 100.0, "cost": 15.0},
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 10.0, "max_demand": 50.0},
            ],
            "objective": "minimize_cost",
        }

        result = solve_production_planning(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_minimize_time_objective(self):
        """Test production planning with minimize time objective."""
        input_data = {
            "products": [
                {
                    "name": "Widget",
                    "profit": 0.0,
                    "production_time": 5.0,
                    "resources": {"labor": 2.0},
                },
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 100.0},
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 10.0},
            ],
            "objective": "minimize_time",
        }

        result = solve_production_planning(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_multi_period_planning(self):
        """Test multi-period production planning."""
        input_data = {
            "products": [
                {
                    "name": "Widget",
                    "profit": 50.0,
                    "resources": {"labor": 2.0},
                },
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 100.0, "renewable": True},
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 20.0, "period": 0},
                {"product": "Widget", "min_demand": 30.0, "period": 1},
                {"product": "Widget", "min_demand": 25.0, "period": 2},
            ],
            "planning_horizon": 3,
            "allow_backorders": False,
            "inventory_cost": 2.0,
        }

        result = solve_production_planning(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
        assert "production_plan" in result.variables

    def test_setup_costs(self):
        """Test production planning with setup costs."""
        input_data = {
            "products": [
                {
                    "name": "Widget",
                    "profit": 50.0,
                    "resources": {"labor": 2.0},
                    "setup_cost": 100.0,
                    "max_production": 50.0,
                },
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 100.0},
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 10.0},
            ],
        }

        result = solve_production_planning(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_backorders_allowed(self):
        """Test production planning with backorders allowed."""
        input_data = {
            "products": [
                {
                    "name": "Widget",
                    "profit": 50.0,
                    "resources": {"labor": 10.0},  # High resource requirement
                },
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 50.0},
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 20.0},  # High demand
            ],
            "allow_backorders": True,
            "planning_horizon": 2,
        }

        result = solve_production_planning(input_data)
        assert result.status in [OptimizationStatus.OPTIMAL, OptimizationStatus.INFEASIBLE]

    def test_infeasible_problem(self):
        """Test infeasible production planning problem."""
        input_data = {
            "products": [
                {
                    "name": "Widget",
                    "profit": 50.0,
                    "resources": {"labor": 10.0},  # Very high resource requirement
                    "min_production": 50.0,  # High minimum production
                },
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 10.0},  # Limited resources
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 100.0},  # Very high demand
            ],
            "allow_backorders": False,
        }

        result = solve_production_planning(input_data)
        assert result.status in [OptimizationStatus.INFEASIBLE, OptimizationStatus.UNBOUNDED]

    def test_invalid_input_data(self):
        """Test production planning with invalid input data."""
        result = solve_production_planning(
            {
                "products": [],
                "resources": {"labor": {"name": "Labor", "available": 100.0}},
                "demand_constraints": [{"product": "Widget", "min_demand": 10.0}],
            }
        )
        assert result.status == OptimizationStatus.ERROR
        assert "at least one product" in result.error_message


class TestOptimizeProduction:
    """Test optimize_production wrapper function."""

    def test_optimize_production_basic(self):
        """Test basic production optimization wrapper."""
        products = [
            {"name": "Widget", "profit": 50.0, "labor": 2.0, "material": 1.0},
            {"name": "Gadget", "profit": 30.0, "labor": 1.5, "material": 0.5},
        ]
        constraints = {
            "labor": 100.0,
            "material": 50.0,
        }

        result = optimize_production(products, constraints)
        assert result["status"] == "optimal"
        assert "production_plan" in result["variables"]

    def test_optimize_production_minimize_cost(self):
        """Test production optimization with minimize cost objective."""
        products = [
            {"name": "Widget", "cost": 20.0, "labor": 2.0},
        ]
        constraints = {
            "labor": 100.0,
        }

        result = optimize_production(
            products=products, constraints=constraints, objective="minimize_cost"
        )
        assert result["status"] == "optimal"


class TestRegisterProductionTools:
    """Test MCP tool registration."""

    def test_register_production_tools(self):
        """Test registering production tools with MCP."""
        mcp_mock = Mock()
        mcp_mock.tool.return_value = lambda func: func  # Mock decorator

        register_production_tools(mcp_mock)

        # Verify that mcp.tool() was called
        mcp_mock.tool.assert_called()

    def test_optimize_production_plan_tool(self):
        """Test the MCP tool wrapper with real solving."""
        mcp_mock = Mock()
        tool_functions = []

        def mock_tool_decorator():
            def decorator(func):
                tool_functions.append(func)
                return func

            return decorator

        mcp_mock.tool = mock_tool_decorator

        register_production_tools(mcp_mock)

        # Get the registered tool function
        assert len(tool_functions) == 1
        tool_func = tool_functions[0]

        # Test the tool function with real problem
        products = [{"name": "Widget", "profit": 50.0, "resources": {"labor": 2.0}}]
        resources = {"labor": {"name": "Labor", "available": 100.0}}
        demand = [{"product": "Widget", "min_demand": 10.0}]

        result = tool_func(
            products=products,
            resources=resources,
            periods=1,
            demand=demand,
        )

        # Verify real solving occurred
        assert result["status"] == "optimal"
        assert "variables" in result
        assert "execution_time" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_single_product_single_resource(self):
        """Test production planning with single product and resource."""
        input_data = {
            "products": [
                {"name": "Widget", "profit": 50.0, "resources": {"labor": 2.0}},
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 100.0},
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 10.0, "max_demand": 40.0},
            ],
        }

        result = solve_production_planning(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_zero_profit_product(self):
        """Test production planning with zero profit product."""
        input_data = {
            "products": [
                {"name": "Widget", "profit": 0.0, "resources": {"labor": 2.0}},
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 100.0},
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 10.0},
            ],
        }

        result = solve_production_planning(input_data)
        assert result.status == OptimizationStatus.OPTIMAL

    def test_zero_resource_requirement(self):
        """Test production planning with zero resource requirement."""
        input_data = {
            "products": [
                {"name": "Widget", "profit": 50.0, "resources": {"labor": 0.0}},
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 100.0},
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 10.0},
            ],
        }

        result = solve_production_planning(input_data)
        assert result.status in [OptimizationStatus.OPTIMAL, OptimizationStatus.UNBOUNDED]

    def test_high_inventory_cost(self):
        """Test production planning with high inventory cost."""
        input_data = {
            "products": [
                {"name": "Widget", "profit": 50.0, "resources": {"labor": 2.0}},
            ],
            "resources": {
                "labor": {"name": "Labor", "available": 100.0, "renewable": True},
            },
            "demand_constraints": [
                {"product": "Widget", "min_demand": 20.0, "period": 0},
                {"product": "Widget", "min_demand": 10.0, "period": 1},
            ],
            "planning_horizon": 2,
            "inventory_cost": 100.0,  # Very high inventory cost
        }

        result = solve_production_planning(input_data)
        assert result.status == OptimizationStatus.OPTIMAL
