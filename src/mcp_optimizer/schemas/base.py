"""Base schemas for optimization problems."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OptimizationStatus(str, Enum):
    """Status of optimization solution."""

    OPTIMAL = "optimal"
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    UNBOUNDED = "unbounded"
    ERROR = "error"


class ObjectiveSense(str, Enum):
    """Optimization objective sense."""

    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class VariableType(str, Enum):
    """Variable types for optimization."""

    CONTINUOUS = "continuous"
    INTEGER = "integer"
    BINARY = "binary"


class ConstraintOperator(str, Enum):
    """Constraint operators."""

    LE = "<="
    GE = ">="
    EQ = "=="


class ProblemType(str, Enum):
    """Types of optimization problems."""

    LINEAR_PROGRAM = "linear_program"
    INTEGER_PROGRAM = "integer_program"
    ASSIGNMENT = "assignment"
    TRANSPORTATION = "transportation"
    KNAPSACK = "knapsack"
    TSP = "tsp"
    VRP = "vrp"
    JOB_SCHEDULING = "job_scheduling"
    SHIFT_SCHEDULING = "shift_scheduling"
    PORTFOLIO = "portfolio"
    PRODUCTION_PLANNING = "production_planning"


class BaseOptimizationResult(BaseModel):
    """Base result schema for optimization problems."""

    status: OptimizationStatus = Field(
        description="Status of the optimization solution"
    )
    objective_value: float | None = Field(
        default=None,
        description="Value of the objective function",
    )
    execution_time: float = Field(
        description="Execution time in seconds",
        ge=0,
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if optimization failed",
    )


class SolverInfo(BaseModel):
    """Information about the solver used."""

    solver_name: str = Field(description="Name of the solver")
    iterations: int | None = Field(
        default=None,
        description="Number of iterations performed",
        ge=0,
    )
    gap: float | None = Field(
        default=None,
        description="Optimality gap",
        ge=0,
    )
    nodes: int | None = Field(
        default=None,
        description="Number of nodes explored (for tree-based solvers)",
        ge=0,
    )


class ValidationResult(BaseModel):
    """Result of input validation."""

    is_valid: bool = Field(description="Whether the input is valid")
    errors: list[str] = Field(
        default_factory=list,
        description="List of validation errors",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="List of validation warnings",
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="List of suggestions for improvement",
    )


class Variable(BaseModel):
    """Variable definition for optimization problems."""

    type: VariableType = Field(
        default=VariableType.CONTINUOUS,
        description="Type of the variable",
    )
    lower: float | None = Field(
        default=None,
        description="Lower bound of the variable",
    )
    upper: float | None = Field(
        default=None,
        description="Upper bound of the variable",
    )


class Objective(BaseModel):
    """Objective function definition."""

    sense: ObjectiveSense = Field(description="Optimization sense")
    coefficients: dict[str, float] = Field(
        description="Coefficients for variables in the objective function"
    )


class Constraint(BaseModel):
    """Constraint definition."""

    name: str | None = Field(
        default=None,
        description="Name of the constraint",
    )
    expression: dict[str, float] = Field(description="Left-hand side coefficients")
    operator: ConstraintOperator = Field(description="Constraint operator")
    rhs: float = Field(description="Right-hand side value")


class OptimizationRequest(BaseModel):
    """Base request for optimization problems."""

    problem_type: ProblemType = Field(description="Type of optimization problem")
    time_limit_seconds: float | None = Field(
        default=None,
        description="Time limit for solving in seconds",
        gt=0,
    )
    solver_options: dict[str, Any] | None = Field(
        default=None,
        description="Additional solver-specific options",
    )


class OptimizationResult(BaseOptimizationResult):
    """Extended optimization result with variables."""

    variables: dict[str, Any] | None = Field(
        default=None, description="Solution variables and additional result data"
    )
    solver_info: dict[str, Any] | None = Field(
        default=None, description="Information about the solver used"
    )
