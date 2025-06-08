"""Validation tools for optimization input data."""

import logging
from typing import Any

from fastmcp import FastMCP

from mcp_optimizer.schemas.base import ProblemType, ValidationResult
from mcp_optimizer.utils.resource_monitor import with_resource_limits

logger = logging.getLogger(__name__)


def validate_linear_program(data: dict[str, Any]) -> ValidationResult:
    """Validate linear programming problem data."""
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []

    # Check if data is a dictionary
    if not isinstance(data, dict):
        errors.append(f"Input data must be a dictionary, got {type(data).__name__}")
        suggestions.append("Provide input data as a dictionary with required fields")
    else:
        # Check required fields
        required_fields = ["objective", "variables", "constraints"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Validate objective
        if "objective" in data:
            if not isinstance(data["objective"], dict):
                errors.append("Objective must be a dictionary")
            else:
                obj = data["objective"]
                if "sense" not in obj:
                    errors.append("Objective missing required field: sense")
                elif obj["sense"] not in ["minimize", "maximize"]:
                    errors.append("Objective sense must be 'minimize' or 'maximize'")

                if "coefficients" not in obj:
                    errors.append("Objective missing required field: coefficients")
                elif not isinstance(obj["coefficients"], dict):
                    errors.append("Objective coefficients must be a dictionary")
                elif not obj["coefficients"]:
                    warnings.append("Objective has no coefficients")

        # Validate variables
        if "variables" in data:
            if not isinstance(data["variables"], dict):
                errors.append("Variables must be a dictionary")
            elif not data["variables"]:
                errors.append("No variables defined")

        # Validate constraints
        if "constraints" in data:
            if not isinstance(data["constraints"], list):
                errors.append("Constraints must be a list")
            elif not data["constraints"]:
                warnings.append("No constraints defined - problem may be unbounded")

        # Validate constraints
        if isinstance(data.get("constraints"), list):
            for i, constraint in enumerate(data["constraints"]):
                if not isinstance(constraint, dict):
                    errors.append(f"Constraint {i} must be a dictionary")
                    continue

                if "expression" not in constraint:
                    errors.append(f"Constraint {i} missing required field: expression")
                elif not isinstance(constraint["expression"], dict):
                    errors.append(f"Constraint {i} expression must be a dictionary")

                if "operator" not in constraint:
                    errors.append(f"Constraint {i} missing required field: operator")
                elif constraint["operator"] not in ["<=", ">=", "=="]:
                    errors.append(f"Constraint {i} operator must be '<=', '>=' or '=='")

                if "rhs" not in constraint:
                    errors.append(f"Constraint {i} missing required field: rhs")
                elif not isinstance(constraint["rhs"], int | float):
                    errors.append(f"Constraint {i} rhs must be a number")

        # Check variable consistency
        if isinstance(data.get("objective"), dict) and isinstance(data.get("variables"), dict):
            coefficients = data["objective"].get("coefficients", {})
            if isinstance(coefficients, dict):
                obj_vars = set(coefficients.keys())
                defined_vars = set(data["variables"].keys())

                undefined_vars = obj_vars - defined_vars
                if undefined_vars:
                    errors.append(f"Variables in objective not defined: {list(undefined_vars)}")

                unused_vars = defined_vars - obj_vars
                if unused_vars:
                    warnings.append(f"Defined variables not used in objective: {list(unused_vars)}")
            else:
                errors.append("Objective coefficients must be a dictionary")

        # Suggestions
        if not errors:
            suggestions.append("Consider adding variable bounds for better numerical stability")
            suggestions.append("Use descriptive names for variables and constraints")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
    )


def validate_assignment_problem(data: dict[str, Any]) -> ValidationResult:
    """Validate assignment problem data."""
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []

    # Check required fields
    required_fields = ["workers", "tasks", "costs"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if "workers" in data:
        if not isinstance(data["workers"], list):
            errors.append("Workers must be a list")
        elif not data["workers"]:
            errors.append("No workers defined")

    if "tasks" in data:
        if not isinstance(data["tasks"], list):
            errors.append("Tasks must be a list")
        elif not data["tasks"]:
            errors.append("No tasks defined")

    if "costs" in data:
        if not isinstance(data["costs"], list):
            errors.append("Costs must be a list of lists")
        else:
            workers_count = len(data.get("workers", []))
            tasks_count = len(data.get("tasks", []))

            if len(data["costs"]) != workers_count:
                errors.append(
                    f"Cost matrix rows ({len(data['costs'])}) must match workers count ({workers_count})"
                )

            for i, row in enumerate(data["costs"]):
                if not isinstance(row, list):
                    errors.append(f"Cost matrix row {i} must be a list")
                elif len(row) != tasks_count:
                    errors.append(
                        f"Cost matrix row {i} length ({len(row)}) must match tasks count ({tasks_count})"
                    )

    # Check for balanced assignment
    if "workers" in data and "tasks" in data:
        workers_count = len(data["workers"])
        tasks_count = len(data["tasks"])

        if workers_count != tasks_count:
            warnings.append(f"Unbalanced assignment: {workers_count} workers, {tasks_count} tasks")
            suggestions.append("Consider adding dummy workers/tasks for balanced assignment")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
    )


def validate_knapsack_problem(data: dict[str, Any]) -> ValidationResult:
    """Validate knapsack problem data."""
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []

    # Check required fields
    required_fields = ["items", "capacity"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if "items" in data:
        if not isinstance(data["items"], list):
            errors.append("Items must be a list")
        elif not data["items"]:
            errors.append("No items defined")
        else:
            for i, item in enumerate(data["items"]):
                if not isinstance(item, dict):
                    errors.append(f"Item {i} must be a dictionary")
                    continue

                # Check required item fields
                item_required_fields = ["name", "value", "weight"]
                for field in item_required_fields:
                    if field not in item:
                        errors.append(f"Item {i} missing required field: {field}")

                # Check value and weight are non-negative
                if "value" in item:
                    if not isinstance(item["value"], (int, float)) or item["value"] < 0:
                        errors.append(f"Item {i} value must be a non-negative number")

                if "weight" in item:
                    if not isinstance(item["weight"], (int, float)) or item["weight"] < 0:
                        errors.append(f"Item {i} weight must be a non-negative number")

                # Check optional volume field
                if "volume" in item:
                    if not isinstance(item["volume"], (int, float)) or item["volume"] < 0:
                        errors.append(f"Item {i} volume must be a non-negative number")

    if "capacity" in data:
        if not isinstance(data["capacity"], (int, float)) or data["capacity"] <= 0:
            errors.append("Capacity must be a positive number")

    # Check optional volume capacity
    if "volume_capacity" in data:
        if not isinstance(data["volume_capacity"], (int, float)) or data["volume_capacity"] <= 0:
            errors.append("Volume capacity must be a positive number")

    # Check knapsack type
    if "knapsack_type" in data:
        valid_types = ["0-1", "bounded", "unbounded"]
        if data["knapsack_type"] not in valid_types:
            errors.append(f"Knapsack type must be one of: {valid_types}")

    # Check for items that are too heavy
    if "items" in data and "capacity" in data and not errors:
        capacity = data["capacity"]
        feasible_items = []

        for item in data["items"]:
            if isinstance(item, dict) and "weight" in item:
                if item["weight"] <= capacity:
                    feasible_items.append(item)

        if not feasible_items:
            warnings.append("No items fit within the capacity constraint")
        elif len(feasible_items) < len(data["items"]):
            warnings.append(
                f"Only {len(feasible_items)} out of {len(data['items'])} items fit within capacity"
            )

    if not errors:
        suggestions.append("Consider using realistic item values and weights")
        suggestions.append("For large problems, consider using bounded or unbounded knapsack types")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
    )


def validate_transportation_problem(data: dict[str, Any]) -> ValidationResult:
    """Validate transportation problem data."""
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []

    # Check required fields
    required_fields = ["suppliers", "consumers", "costs"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if "suppliers" in data:
        if not isinstance(data["suppliers"], list):
            errors.append("Suppliers must be a list")
        elif not data["suppliers"]:
            errors.append("No suppliers defined")
        else:
            for i, supplier in enumerate(data["suppliers"]):
                if not isinstance(supplier, dict):
                    errors.append(f"Supplier {i} must be a dictionary")
                    continue
                if "name" not in supplier:
                    errors.append(f"Supplier {i} missing required field: name")
                if "supply" not in supplier:
                    errors.append(f"Supplier {i} missing required field: supply")
                elif not isinstance(supplier["supply"], int | float) or supplier["supply"] < 0:
                    errors.append(f"Supplier {i} supply must be a non-negative number")

    if "consumers" in data:
        if not isinstance(data["consumers"], list):
            errors.append("Consumers must be a list")
        elif not data["consumers"]:
            errors.append("No consumers defined")
        else:
            for i, consumer in enumerate(data["consumers"]):
                if not isinstance(consumer, dict):
                    errors.append(f"Consumer {i} must be a dictionary")
                    continue
                if "name" not in consumer:
                    errors.append(f"Consumer {i} missing required field: name")
                if "demand" not in consumer:
                    errors.append(f"Consumer {i} missing required field: demand")
                elif not isinstance(consumer["demand"], int | float) or consumer["demand"] < 0:
                    errors.append(f"Consumer {i} demand must be a non-negative number")

    if "costs" in data:
        if not isinstance(data["costs"], list):
            errors.append("Costs must be a list of lists")
        else:
            suppliers_count = len(data.get("suppliers", []))
            consumers_count = len(data.get("consumers", []))

            if len(data["costs"]) != suppliers_count:
                errors.append(
                    f"Cost matrix rows ({len(data['costs'])}) must match suppliers count ({suppliers_count})"
                )

            for i, row in enumerate(data["costs"]):
                if not isinstance(row, list):
                    errors.append(f"Cost matrix row {i} must be a list")
                elif len(row) != consumers_count:
                    errors.append(
                        f"Cost matrix row {i} length ({len(row)}) must match consumers count ({consumers_count})"
                    )
                else:
                    for j, cost in enumerate(row):
                        if not isinstance(cost, int | float) or cost < 0:
                            errors.append(
                                f"Cost matrix element [{i}][{j}] must be a non-negative number"
                            )

    # Check supply-demand balance
    if "suppliers" in data and "consumers" in data and not errors:
        total_supply = sum(supplier.get("supply", 0) for supplier in data["suppliers"])
        total_demand = sum(consumer.get("demand", 0) for consumer in data["consumers"])

        if abs(total_supply - total_demand) > 1e-6:
            errors.append(f"Total supply ({total_supply}) must equal total demand ({total_demand})")
            suggestions.append("Consider adding dummy suppliers/consumers to balance the problem")

    if not errors:
        suggestions.append("Ensure cost matrix represents actual transportation costs")
        suggestions.append("Consider using realistic supply and demand values")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
    )


def validate_routing_problem(data: dict[str, Any]) -> ValidationResult:
    """Validate routing problem data (TSP/VRP)."""
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []

    # Check required fields
    if "locations" not in data:
        errors.append("Missing required field: locations")
    elif not isinstance(data["locations"], list):
        errors.append("Locations must be a list")
    elif len(data["locations"]) < 2:
        errors.append("At least 2 locations required")
    else:
        for i, location in enumerate(data["locations"]):
            if not isinstance(location, dict):
                errors.append(f"Location {i} must be a dictionary")
                continue

            if "name" not in location:
                errors.append(f"Location {i} missing required field: name")

            # Check coordinates (support both lat/lng and latitude/longitude)
            has_lat_lng = ("lat" in location and "lng" in location) or (
                "latitude" in location and "longitude" in location
            )
            has_x_y = "x" in location and "y" in location

            if not has_lat_lng and not has_x_y and "distance_matrix" not in data:
                errors.append(
                    f"Location {i} must have either lat/lng or x/y coordinates, or provide distance_matrix"
                )

    # For VRP, check vehicles
    if "vehicles" in data:
        if not isinstance(data["vehicles"], list):
            errors.append("Vehicles must be a list")
        elif not data["vehicles"]:
            errors.append("At least one vehicle required for VRP")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
    )


def validate_scheduling_problem(data: dict[str, Any]) -> ValidationResult:
    """Validate scheduling problem data."""
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []

    # Check required problem_type field
    if "problem_type" not in data:
        errors.append("Missing required field: problem_type")
    elif data["problem_type"] not in ["job_shop", "shift_scheduling"]:
        errors.append("Problem type must be 'job_shop' or 'shift_scheduling'")

    # Job scheduling validation
    if "jobs" in data:
        if not isinstance(data["jobs"], list):
            errors.append("Jobs must be a list")
        elif not data["jobs"]:
            errors.append("At least one job required")
        else:
            for i, job in enumerate(data["jobs"]):
                if not isinstance(job, dict):
                    errors.append(f"Job {i} must be a dictionary")
                    continue

                if "id" not in job:
                    errors.append(f"Job {i} missing required field: id")

                if "tasks" not in job:
                    errors.append(f"Job {i} missing required field: tasks")
                elif not isinstance(job["tasks"], list):
                    errors.append(f"Job {i} tasks must be a list")
                elif not job["tasks"]:
                    errors.append(f"Job {i} must have at least one task")

    # Shift scheduling validation
    if "employees" in data:
        if not isinstance(data["employees"], list):
            errors.append("Employees must be a list")
        elif not data["employees"]:
            errors.append("At least one employee required")

    if "shifts" in data:
        if not isinstance(data["shifts"], list):
            errors.append("Shifts must be a list")
        elif not data["shifts"]:
            errors.append("At least one shift required")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
    )


def validate_portfolio_problem(data: dict[str, Any]) -> ValidationResult:
    """Validate portfolio optimization data."""
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []

    if "assets" not in data:
        errors.append("Missing required field: assets")
    elif not isinstance(data["assets"], list):
        errors.append("Assets must be a list")
    elif not data["assets"]:
        errors.append("At least one asset required")
    else:
        for i, asset in enumerate(data["assets"]):
            if not isinstance(asset, dict):
                errors.append(f"Asset {i} must be a dictionary")
                continue

            required_fields = ["symbol", "expected_return", "risk"]
            for field in required_fields:
                if field not in asset:
                    errors.append(f"Asset {i} missing required field: {field}")

    # Budget is optional, objective is required
    if "objective" not in data:
        errors.append("Missing required field: objective")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
    )


def validate_production_problem(data: dict[str, Any]) -> ValidationResult:
    """Validate production planning data."""
    errors: list[str] = []
    warnings: list[str] = []
    suggestions: list[str] = []

    if "products" not in data:
        errors.append("Missing required field: products")
    elif not isinstance(data["products"], list):
        errors.append("Products must be a list")
    elif not data["products"]:
        errors.append("At least one product required")

    if "resources" not in data:
        errors.append("Missing required field: resources")
    elif not isinstance(data["resources"], list):
        errors.append("Resources must be a list")
    elif not data["resources"]:
        errors.append("At least one resource required")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
    )


def register_validation_tools(mcp: FastMCP[Any]) -> None:
    """Register validation tools with the MCP server."""

    @with_resource_limits(timeout_seconds=30.0, estimated_memory_mb=50.0)  # type: ignore[arg-type]
    @mcp.tool()
    def validate_optimization_input(
        problem_type: str,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate input data for optimization problems.

        Args:
            problem_type: Type of optimization problem
            input_data: Input data to validate

        Returns:
            Validation result with errors, warnings, and suggestions
        """
        try:
            # Validate problem type
            try:
                prob_type = ProblemType(problem_type)
            except ValueError:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Unknown problem type: {problem_type}"],
                    warnings=[],
                    suggestions=[f"Supported types: {[t.value for t in ProblemType]}"],
                ).model_dump()

            # Route to appropriate validator
            if prob_type == ProblemType.LINEAR_PROGRAM:
                result = validate_linear_program(input_data)
            elif prob_type == ProblemType.INTEGER_PROGRAM:
                result = validate_linear_program(input_data)  # Same validation as linear program
            elif prob_type == ProblemType.ASSIGNMENT:
                result = validate_assignment_problem(input_data)
            elif prob_type == ProblemType.TRANSPORTATION:
                result = validate_transportation_problem(input_data)
            elif prob_type == ProblemType.KNAPSACK:
                result = validate_knapsack_problem(input_data)
            elif prob_type in [ProblemType.TSP, ProblemType.VRP]:
                result = validate_routing_problem(input_data)
            elif prob_type in [
                ProblemType.JOB_SCHEDULING,
                ProblemType.SHIFT_SCHEDULING,
            ]:
                result = validate_scheduling_problem(input_data)
            elif prob_type == ProblemType.PORTFOLIO:
                result = validate_portfolio_problem(input_data)
            elif prob_type == ProblemType.PRODUCTION_PLANNING:
                result = validate_production_problem(input_data)
            else:
                result = ValidationResult(
                    is_valid=False,
                    errors=[f"Validation not yet implemented for {problem_type}"],
                    warnings=[],
                    suggestions=["This problem type will be supported in future versions"],
                )

            logger.info(
                f"Validated {problem_type} problem: {'valid' if result.is_valid else 'invalid'}"
            )
            return result.model_dump()

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                suggestions=["Check input data format and try again"],
            ).model_dump()

    logger.info("Registered validation tools")
