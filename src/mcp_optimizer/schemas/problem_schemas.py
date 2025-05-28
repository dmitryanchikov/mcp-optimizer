"""Problem-specific schemas for optimization problems."""

from typing import Any

from pydantic import BaseModel, Field

from mcp_optimizer.schemas.base import (
    BaseOptimizationResult,
    Constraint,
    Objective,
    OptimizationRequest,
    SolverInfo,
    Variable,
)


class LinearProgramRequest(OptimizationRequest):
    """Request schema for linear programming problems."""

    objective: Objective = Field(description="Objective function")
    variables: dict[str, Variable] = Field(description="Variable definitions")
    constraints: list[Constraint] = Field(description="Problem constraints")
    solver: str | None = Field(
        default=None,
        description="Solver to use (CBC, GLPK, GUROBI, CPLEX)",
    )


class LinearProgramResult(BaseOptimizationResult):
    """Result schema for linear programming problems."""

    variables: dict[str, float] = Field(
        default_factory=dict,
        description="Variable values in the solution",
    )
    solver_info: SolverInfo | None = Field(
        default=None,
        description="Information about the solver used",
    )


class AssignmentRequest(OptimizationRequest):
    """Request schema for assignment problems."""

    workers: list[str] = Field(description="List of workers")
    tasks: list[str] = Field(description="List of tasks")
    costs: list[list[float]] = Field(description="Cost matrix (workers x tasks)")
    maximize: bool = Field(
        default=False,
        description="Whether to maximize instead of minimize",
    )
    max_tasks_per_worker: int | None = Field(
        default=None,
        description="Maximum tasks per worker",
        ge=1,
    )
    min_tasks_per_worker: int | None = Field(
        default=None,
        description="Minimum tasks per worker",
        ge=0,
    )


class Assignment(BaseModel):
    """Single assignment result."""

    worker: str = Field(description="Worker name")
    task: str = Field(description="Task name")
    cost: float = Field(description="Cost of this assignment")


class AssignmentResult(BaseOptimizationResult):
    """Result schema for assignment problems."""

    total_cost: float | None = Field(
        default=None,
        description="Total cost of the assignment",
    )
    assignments: list[Assignment] = Field(
        default_factory=list,
        description="List of worker-task assignments",
    )
    solver_info: SolverInfo | None = Field(
        default=None,
        description="Information about the solver used",
    )


class TransportationRequest(OptimizationRequest):
    """Request schema for transportation problems."""

    suppliers: list[dict[str, Any]] = Field(description="List of suppliers with supply amounts")
    consumers: list[dict[str, Any]] = Field(description="List of consumers with demand amounts")
    costs: list[list[float]] = Field(
        description="Transportation cost matrix (suppliers x consumers)"
    )


class TransportationFlow(BaseModel):
    """Single transportation flow result."""

    supplier: str = Field(description="Supplier name")
    consumer: str = Field(description="Consumer name")
    amount: float = Field(description="Amount transported", ge=0)
    cost: float = Field(description="Cost of this flow")


class TransportationResult(BaseOptimizationResult):
    """Result schema for transportation problems."""

    total_cost: float | None = Field(
        default=None,
        description="Total transportation cost",
    )
    flows: list[TransportationFlow] = Field(
        default_factory=list,
        description="List of transportation flows",
    )
    solver_info: SolverInfo | None = Field(
        default=None,
        description="Information about the solver used",
    )


class KnapsackItem(BaseModel):
    """Item for knapsack problem."""

    name: str = Field(description="Item name")
    value: float = Field(description="Item value", ge=0)
    weight: float = Field(description="Item weight", ge=0)
    volume: float | None = Field(
        default=None,
        description="Item volume",
        ge=0,
    )
    quantity: int = Field(
        default=1,
        description="Available quantity",
        ge=1,
    )


class KnapsackRequest(OptimizationRequest):
    """Request schema for knapsack problems."""

    items: list[KnapsackItem] = Field(description="Items to consider")
    capacity: float = Field(description="Weight capacity", ge=0)
    volume_capacity: float | None = Field(
        default=None,
        description="Volume capacity",
        ge=0,
    )
    knapsack_type: str = Field(
        default="0-1",
        description="Type of knapsack problem",
        pattern="^(0-1|bounded|unbounded)$",
    )


class KnapsackSelection(BaseModel):
    """Selected item in knapsack solution."""

    name: str = Field(description="Item name")
    quantity: int = Field(description="Quantity selected", ge=0)
    total_value: float = Field(description="Total value", ge=0)
    total_weight: float = Field(description="Total weight", ge=0)
    total_volume: float | None = Field(
        default=None,
        description="Total volume",
        ge=0,
    )


class KnapsackResult(BaseOptimizationResult):
    """Result schema for knapsack problems."""

    total_value: float | None = Field(
        default=None,
        description="Total value of selected items",
    )
    total_weight: float | None = Field(
        default=None,
        description="Total weight of selected items",
    )
    total_volume: float | None = Field(
        default=None,
        description="Total volume of selected items",
    )
    selected_items: list[KnapsackSelection] = Field(
        default_factory=list,
        description="List of selected items",
    )
    utilization: dict[str, float] | None = Field(
        default=None,
        description="Capacity utilization percentages",
    )
    solver_info: SolverInfo | None = Field(
        default=None,
        description="Information about the solver used",
    )
