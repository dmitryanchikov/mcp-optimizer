#!/usr/bin/env python3
"""
MCP Optimizer - FastAPI Integration Example

This module demonstrates how to integrate mcp-optimizer with FastAPI
to create a RESTful optimization service.

Installation:
    pip install mcp-optimizer fastapi uvicorn python-multipart

Usage:
    uvicorn fastapi_integration:app --reload --port 8000

    Then visit: http://localhost:8000/docs
"""

import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import Any

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# Import mcp-optimizer components
try:
    from mcp_optimizer import (
        AssignmentSolver,
        KnapsackSolver,
        LinearProgrammingSolver,
        OptimizationEngine,
        OptimizationResult,
        PortfolioOptimizer,
        RoutingSolver,
        SolverConfig,
        TransportationSolver,
    )
except ImportError:
    print("Error: mcp-optimizer package not found. Install with: pip install mcp-optimizer")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global optimization engine
optimization_engine: OptimizationEngine | None = None
job_store: dict[str, dict] = {}


class ProblemType(str, Enum):
    """Supported optimization problem types."""

    LINEAR_PROGRAMMING = "linear_programming"
    ASSIGNMENT = "assignment"
    TRANSPORTATION = "transportation"
    KNAPSACK = "knapsack"
    ROUTING = "routing"
    PORTFOLIO = "portfolio"


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Pydantic models for request/response
class OptimizationRequest(BaseModel):
    """Base optimization request model."""

    problem_type: ProblemType
    problem_data: dict[str, Any]
    config: dict[str, Any] | None = None
    job_id: str | None = None

    @field_validator("job_id", mode="before")
    @classmethod
    def generate_job_id(cls, v: str | None) -> str:
        return v or str(uuid.uuid4())


class LinearProgrammingRequest(BaseModel):
    """Linear programming specific request."""

    objective: dict[str, Any] = Field(..., description="Objective function")
    constraints: list[dict[str, Any]] = Field(..., description="Problem constraints")
    bounds: list[tuple] = Field(..., description="Variable bounds")
    variable_names: list[str] | None = None


class AssignmentRequest(BaseModel):
    """Assignment problem specific request."""

    cost_matrix: list[list[float]] = Field(..., description="Cost matrix")
    employee_names: list[str] | None = None
    task_names: list[str] | None = None


class TransportationRequest(BaseModel):
    """Transportation problem specific request."""

    supply: list[float] = Field(..., description="Supply capacities")
    demand: list[float] = Field(..., description="Demand requirements")
    costs: list[list[float]] = Field(..., description="Transportation costs")
    supplier_names: list[str] | None = None
    customer_names: list[str] | None = None


class KnapsackRequest(BaseModel):
    """Knapsack problem specific request."""

    items: list[dict[str, Any]] = Field(..., description="Items with weight and value")
    capacity: float = Field(..., description="Knapsack capacity")
    knapsack_type: str = Field(default="0-1", description="Knapsack type")


class RoutingRequest(BaseModel):
    """Routing problem specific request."""

    distance_matrix: list[list[float]] = Field(..., description="Distance matrix")
    locations: list[str] = Field(..., description="Location names")
    start_location: int = Field(default=0, description="Starting location index")
    problem_type: str = Field(default="TSP", description="Routing problem type")


class PortfolioRequest(BaseModel):
    """Portfolio optimization specific request."""

    assets: list[str] = Field(..., description="Asset names")
    expected_returns: list[float] = Field(..., description="Expected returns")
    covariance_matrix: list[list[float]] = Field(..., description="Covariance matrix")
    target_return: float | None = None
    risk_tolerance: float | None = None
    constraints: dict[str, Any] | None = None


class OptimizationResponse(BaseModel):
    """Optimization response model."""

    job_id: str
    status: JobStatus
    problem_type: ProblemType
    created_at: datetime
    completed_at: datetime | None = None
    execution_time: float | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class JobListResponse(BaseModel):
    """Job list response model."""

    jobs: list[OptimizationResponse]
    total: int
    page: int
    page_size: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global optimization_engine

    # Startup
    logger.info("Starting MCP Optimizer FastAPI service...")
    optimization_engine = OptimizationEngine(
        config=SolverConfig(timeout=300, max_iterations=10000, tolerance=1e-6, threads=4)
    )
    logger.info("Optimization engine initialized")

    yield

    # Shutdown
    logger.info("Shutting down MCP Optimizer service...")


# Create FastAPI app
app = FastAPI(
    title="MCP Optimizer API",
    description="RESTful API for mathematical optimization using MCP Optimizer",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_optimization_engine() -> OptimizationEngine:
    """Dependency to get optimization engine."""
    if optimization_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Optimization engine not initialized",
        )
    return optimization_engine


async def solve_optimization_problem(
    problem_type: ProblemType,
    problem_data: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> OptimizationResult:
    """Solve optimization problem based on type."""
    solver_config = SolverConfig(**(config or {}))

    if problem_type == ProblemType.LINEAR_PROGRAMMING:
        solver = LinearProgrammingSolver(config=solver_config)
        return await asyncio.to_thread(solver.solve, problem_data)

    elif problem_type == ProblemType.ASSIGNMENT:
        solver = AssignmentSolver(config=solver_config)
        return await asyncio.to_thread(solver.solve, problem_data)

    elif problem_type == ProblemType.TRANSPORTATION:
        solver = TransportationSolver(config=solver_config)
        return await asyncio.to_thread(solver.solve, problem_data)

    elif problem_type == ProblemType.KNAPSACK:
        solver = KnapsackSolver(config=solver_config)
        return await asyncio.to_thread(solver.solve, problem_data)

    elif problem_type == ProblemType.ROUTING:
        solver = RoutingSolver(config=solver_config)
        return await asyncio.to_thread(solver.solve, problem_data)

    elif problem_type == ProblemType.PORTFOLIO:
        optimizer = PortfolioOptimizer(config=solver_config)
        return await asyncio.to_thread(optimizer.solve, problem_data)

    else:
        raise ValueError(f"Unsupported problem type: {problem_type}")


async def execute_optimization_job(job_id: str):
    """Execute optimization job in background."""
    job = job_store[job_id]

    try:
        # Update job status
        job["status"] = JobStatus.RUNNING
        job["started_at"] = datetime.now()

        # Solve the problem
        start_time = time.time()
        result = await solve_optimization_problem(
            job["problem_type"], job["problem_data"], job["config"]
        )
        execution_time = time.time() - start_time

        # Update job with results
        job["status"] = JobStatus.COMPLETED
        job["completed_at"] = datetime.now()
        job["execution_time"] = execution_time
        job["result"] = {
            "objective_value": result.objective_value,
            "variables": result.variables,
            "status": result.status,
            "solver_info": result.solver_info,
        }

        logger.info(f"Job {job_id} completed successfully in {execution_time:.3f}s")

    except Exception as e:
        # Update job with error
        job["status"] = JobStatus.FAILED
        job["completed_at"] = datetime.now()
        job["error"] = str(e)

        logger.error(f"Job {job_id} failed: {e}")


# API Endpoints


@app.get("/", response_model=dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "MCP Optimizer API",
        "version": "1.0.0",
        "description": "RESTful API for mathematical optimization",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=dict[str, str])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engine_status": "ready" if optimization_engine else "not_ready",
    }


@app.post("/optimize", response_model=OptimizationResponse)
async def optimize(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    engine: OptimizationEngine = Depends(get_optimization_engine),
):
    """Submit optimization problem for solving."""
    job_id = request.job_id

    # Create job record
    job_store[job_id] = {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "problem_type": request.problem_type,
        "problem_data": request.problem_data,
        "config": request.config,
        "created_at": datetime.now(),
        "completed_at": None,
        "execution_time": None,
        "result": None,
        "error": None,
    }

    # Start background task
    background_tasks.add_task(execute_optimization_job, job_id)

    return OptimizationResponse(**job_store[job_id])


@app.post("/optimize/sync", response_model=OptimizationResponse)
async def optimize_sync(
    request: OptimizationRequest,
    engine: OptimizationEngine = Depends(get_optimization_engine),
):
    """Solve optimization problem synchronously."""
    job_id = request.job_id
    start_time = time.time()

    try:
        # Solve the problem
        result = await solve_optimization_problem(
            request.problem_type, request.problem_data, request.config
        )
        execution_time = time.time() - start_time

        # Create response
        response = OptimizationResponse(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            problem_type=request.problem_type,
            created_at=datetime.now(),
            completed_at=datetime.now(),
            execution_time=execution_time,
            result={
                "objective_value": result.objective_value,
                "variables": result.variables,
                "status": result.status,
                "solver_info": result.solver_info,
            },
        )

        # Store in job store
        job_store[job_id] = response.dict()

        return response

    except Exception as e:
        execution_time = time.time() - start_time

        response = OptimizationResponse(
            job_id=job_id,
            status=JobStatus.FAILED,
            problem_type=request.problem_type,
            created_at=datetime.now(),
            completed_at=datetime.now(),
            execution_time=execution_time,
            error=str(e),
        )

        job_store[job_id] = response.dict()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Optimization failed: {e}"
        ) from e


@app.get("/jobs/{job_id}", response_model=OptimizationResponse)
async def get_job(job_id: str):
    """Get job status and results."""
    if job_id not in job_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found")

    return OptimizationResponse(**job_store[job_id])


@app.get("/jobs", response_model=JobListResponse)
async def list_jobs(page: int = 1, page_size: int = 10, status_filter: JobStatus | None = None):
    """List all jobs with pagination."""
    jobs = list(job_store.values())

    # Filter by status if provided
    if status_filter:
        jobs = [job for job in jobs if job["status"] == status_filter]

    # Sort by creation time (newest first)
    jobs.sort(key=lambda x: x["created_at"], reverse=True)

    # Pagination
    total = len(jobs)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_jobs = jobs[start_idx:end_idx]

    return JobListResponse(
        jobs=[OptimizationResponse(**job) for job in page_jobs],
        total=total,
        page=page,
        page_size=page_size,
    )


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job."""
    if job_id not in job_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found")

    del job_store[job_id]
    return {"message": f"Job {job_id} deleted successfully"}


# Problem-specific endpoints


@app.post("/optimize/linear-programming", response_model=OptimizationResponse)
async def optimize_linear_programming(
    request: LinearProgrammingRequest, background_tasks: BackgroundTasks
):
    """Solve linear programming problem."""
    opt_request = OptimizationRequest(
        problem_type=ProblemType.LINEAR_PROGRAMMING, problem_data=request.dict()
    )
    return await optimize(opt_request, background_tasks)


@app.post("/optimize/assignment", response_model=OptimizationResponse)
async def optimize_assignment(request: AssignmentRequest, background_tasks: BackgroundTasks):
    """Solve assignment problem."""
    opt_request = OptimizationRequest(
        problem_type=ProblemType.ASSIGNMENT, problem_data=request.dict()
    )
    return await optimize(opt_request, background_tasks)


@app.post("/optimize/transportation", response_model=OptimizationResponse)
async def optimize_transportation(
    request: TransportationRequest, background_tasks: BackgroundTasks
):
    """Solve transportation problem."""
    opt_request = OptimizationRequest(
        problem_type=ProblemType.TRANSPORTATION, problem_data=request.dict()
    )
    return await optimize(opt_request, background_tasks)


@app.post("/optimize/knapsack", response_model=OptimizationResponse)
async def optimize_knapsack(request: KnapsackRequest, background_tasks: BackgroundTasks):
    """Solve knapsack problem."""
    opt_request = OptimizationRequest(
        problem_type=ProblemType.KNAPSACK, problem_data=request.dict()
    )
    return await optimize(opt_request, background_tasks)


@app.post("/optimize/routing", response_model=OptimizationResponse)
async def optimize_routing(request: RoutingRequest, background_tasks: BackgroundTasks):
    """Solve routing problem."""
    opt_request = OptimizationRequest(problem_type=ProblemType.ROUTING, problem_data=request.dict())
    return await optimize(opt_request, background_tasks)


@app.post("/optimize/portfolio", response_model=OptimizationResponse)
async def optimize_portfolio(request: PortfolioRequest, background_tasks: BackgroundTasks):
    """Solve portfolio optimization problem."""
    opt_request = OptimizationRequest(
        problem_type=ProblemType.PORTFOLIO, problem_data=request.dict()
    )
    return await optimize(opt_request, background_tasks)


# Statistics endpoint
@app.get("/stats", response_model=dict[str, Any])
async def get_statistics():
    """Get API usage statistics."""
    jobs = list(job_store.values())

    stats = {
        "total_jobs": len(jobs),
        "jobs_by_status": {},
        "jobs_by_type": {},
        "average_execution_time": 0,
        "total_execution_time": 0,
    }

    # Count by status
    for job_status in JobStatus:
        stats["jobs_by_status"][job_status.value] = len(
            [job for job in jobs if job["status"] == job_status]
        )

    # Count by type
    for problem_type in ProblemType:
        stats["jobs_by_type"][problem_type.value] = len(
            [job for job in jobs if job["problem_type"] == problem_type]
        )

    # Calculate execution times
    completed_jobs = [job for job in jobs if job["execution_time"] is not None]
    if completed_jobs:
        execution_times = [job["execution_time"] for job in completed_jobs]
        stats["average_execution_time"] = sum(execution_times) / len(execution_times)
        stats["total_execution_time"] = sum(execution_times)

    return stats


if __name__ == "__main__":
    uvicorn.run(
        "fastapi_integration:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
