"""Routing optimization tools for MCP server.

This module provides tools for solving routing problems including:
- Traveling Salesman Problem (TSP)
- Vehicle Routing Problem (VRP)
"""

import math
import time
from typing import Any

from fastmcp import FastMCP
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from pydantic import BaseModel, Field, validator

from ..schemas.base import OptimizationResult, OptimizationStatus


class Location(BaseModel):
    """Location with coordinates and optional properties."""

    name: str
    lat: float | None = None
    lng: float | None = None
    x: float | None = None
    y: float | None = None
    demand: float = Field(default=0.0, ge=0)
    time_window: tuple[int, int] | None = None
    service_time: int = Field(default=0, ge=0)

    @validator("time_window")
    def validate_time_window(cls, v: tuple[int, int] | None) -> tuple[int, int] | None:
        if v is not None and len(v) == 2:
            start, end = v
            if start >= end:
                raise ValueError("Time window start must be less than end")
        return v


class Vehicle(BaseModel):
    """Vehicle with capacity and constraints."""

    capacity: float = Field(ge=0)
    start_location: int = Field(default=0, ge=0)
    end_location: int | None = None
    max_distance: float | None = Field(default=None, ge=0)
    max_time: int | None = Field(default=None, ge=0)


class TSPInput(BaseModel):
    """Input schema for Traveling Salesman Problem."""

    locations: list[Location]
    distance_matrix: list[list[float]] | None = None
    start_location: int = Field(default=0, ge=0)
    return_to_start: bool = True
    time_limit_seconds: float = Field(default=30.0, ge=0)

    @validator("start_location")
    def validate_start_location(cls, v: int, values: dict[str, Any]) -> int:
        if "locations" in values and v >= len(values["locations"]):
            raise ValueError("Start location index out of range")
        return v


class VRPInput(BaseModel):
    """Input schema for Vehicle Routing Problem."""

    locations: list[Location]
    vehicles: list[Vehicle]
    distance_matrix: list[list[float]] | None = None
    time_matrix: list[list[int]] | None = None
    depot: int = Field(default=0, ge=0)
    time_limit_seconds: float = Field(default=30.0, ge=0)

    @validator("depot")
    def validate_depot(cls, v: int, values: dict[str, Any]) -> int:
        if "locations" in values and v >= len(values["locations"]):
            raise ValueError("Depot index out of range")
        return v


def calculate_distance_matrix(
    locations: list[Location | dict[str, Any]],
) -> list[list[float]]:
    """Calculate Euclidean distance matrix from location coordinates."""
    n = len(locations)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 0.0
            else:
                loc1, loc2 = locations[i], locations[j]

                # Handle both Location objects and dictionaries
                def get_coord(loc: Location | dict[str, Any], key: str) -> float | None:
                    if isinstance(loc, dict):
                        return loc.get(key)
                    else:
                        return getattr(loc, key, None)

                # Use lat/lng if available, otherwise use x/y
                lat1, lng1 = get_coord(loc1, "lat"), get_coord(loc1, "lng")
                lat2, lng2 = get_coord(loc2, "lat"), get_coord(loc2, "lng")
                x1, y1 = get_coord(loc1, "x"), get_coord(loc1, "y")
                x2, y2 = get_coord(loc2, "x"), get_coord(loc2, "y")

                if (
                    lat1 is not None
                    and lng1 is not None
                    and lat2 is not None
                    and lng2 is not None
                ):
                    # Haversine distance for lat/lng
                    distance = haversine_distance(lat1, lng1, lat2, lng2)
                elif (
                    x1 is not None
                    and y1 is not None
                    and x2 is not None
                    and y2 is not None
                ):
                    # Euclidean distance for x/y
                    distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                else:
                    raise ValueError(
                        f"Insufficient coordinate data for locations {i} and {j}"
                    )

                matrix[i][j] = distance

    return matrix


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate haversine distance between two lat/lng points in kilometers."""
    R = 6371  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def solve_traveling_salesman(input_data: dict[str, Any]) -> OptimizationResult:
    """Solve Traveling Salesman Problem using OR-Tools.

    Args:
        input_data: TSP problem specification

    Returns:
        OptimizationResult with route and total distance
    """
    start_time = time.time()

    try:
        # Parse and validate input
        tsp_input = TSPInput(**input_data)
        locations = tsp_input.locations
        n_locations = len(locations)

        if n_locations < 2:
            return OptimizationResult(
                status=OptimizationStatus.ERROR,
                error_message="At least 2 locations required for TSP",
                execution_time=time.time() - start_time,
            )

        # Get or calculate distance matrix
        if tsp_input.distance_matrix:
            distance_matrix = tsp_input.distance_matrix
            if len(distance_matrix) != n_locations or any(
                len(row) != n_locations for row in distance_matrix
            ):
                return OptimizationResult(
                    status=OptimizationStatus.ERROR,
                    error_message="Distance matrix dimensions don't match number of locations",
                    execution_time=time.time() - start_time,
                )
        else:
            distance_matrix = calculate_distance_matrix(locations)  # type: ignore

        # Create routing model
        manager = pywrapcp.RoutingIndexManager(n_locations, 1, tsp_input.start_location)
        routing = pywrapcp.RoutingModel(manager)

        # Create distance callback
        def distance_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node] * 1000)  # Scale for integer

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.time_limit.seconds = int(tsp_input.time_limit_seconds)

        # Solve
        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            # Extract route
            route = []
            total_distance = 0.0
            index = routing.Start(0)

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                route.append(
                    {
                        "location": locations[node].name,
                        "index": node,
                        "coordinates": {
                            "lat": locations[node].lat,
                            "lng": locations[node].lng,
                            "x": locations[node].x,
                            "y": locations[node].y,
                        },
                    }
                )

                previous_index = index
                index = solution.Value(routing.NextVar(index))
                if not routing.IsEnd(index):
                    from_node = manager.IndexToNode(previous_index)
                    to_node = manager.IndexToNode(index)
                    total_distance += distance_matrix[from_node][to_node]

            # Add final location if returning to start
            if tsp_input.return_to_start:
                final_node = manager.IndexToNode(index)
                route.append(
                    {
                        "location": locations[final_node].name,
                        "index": final_node,
                        "coordinates": {
                            "lat": locations[final_node].lat,
                            "lng": locations[final_node].lng,
                            "x": locations[final_node].x,
                            "y": locations[final_node].y,
                        },
                    }
                )
                # Add distance back to start
                if len(route) > 1:
                    last_node = route[-2]["index"]
                    start_node = route[-1]["index"]
                    total_distance += distance_matrix[last_node][start_node]

            execution_time = time.time() - start_time

            return OptimizationResult(
                status=OptimizationStatus.OPTIMAL,
                objective_value=total_distance,
                variables={
                    "route": route,
                    "total_distance": total_distance,
                    "num_locations": len(route),
                },
                execution_time=execution_time,
                solver_info={
                    "solver_name": "OR-Tools Routing",
                    "search_strategy": "PATH_CHEAPEST_ARC",
                },
            )
        else:
            return OptimizationResult(
                status=OptimizationStatus.INFEASIBLE,
                error_message="No solution found within time limit",
                execution_time=time.time() - start_time,
            )

    except Exception as e:
        return OptimizationResult(
            status=OptimizationStatus.ERROR,
            error_message=f"TSP solving error: {str(e)}",
            execution_time=time.time() - start_time,
        )


def solve_vehicle_routing(input_data: dict[str, Any]) -> OptimizationResult:
    """Solve Vehicle Routing Problem using OR-Tools.

    Args:
        input_data: VRP problem specification

    Returns:
        OptimizationResult with routes for all vehicles
    """
    start_time = time.time()

    try:
        # Parse and validate input
        vrp_input = VRPInput(**input_data)
        locations = vrp_input.locations
        vehicles = vrp_input.vehicles
        n_locations = len(locations)
        n_vehicles = len(vehicles)

        if n_locations < 2:
            return OptimizationResult(
                status=OptimizationStatus.ERROR,
                error_message="At least 2 locations required for VRP",
                execution_time=time.time() - start_time,
            )

        if n_vehicles < 1:
            return OptimizationResult(
                status=OptimizationStatus.ERROR,
                error_message="At least 1 vehicle required for VRP",
                execution_time=time.time() - start_time,
            )

        # Get or calculate distance matrix
        if vrp_input.distance_matrix:
            distance_matrix = vrp_input.distance_matrix
        else:
            distance_matrix = calculate_distance_matrix(locations)  # type: ignore

        # Create routing model
        manager = pywrapcp.RoutingIndexManager(n_locations, n_vehicles, vrp_input.depot)
        routing = pywrapcp.RoutingModel(manager)

        # Create distance callback
        def distance_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node] * 1000)

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add capacity constraints
        demands = [int(loc.demand) for loc in locations]

        def demand_callback(from_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            return int(demands[from_node])

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

        # Set vehicle capacities
        vehicle_capacities = [int(vehicle.capacity) for vehicle in vehicles]
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            vehicle_capacities,  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity",
        )

        # Set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.time_limit.seconds = int(vrp_input.time_limit_seconds)

        # Solve
        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            # Extract routes for all vehicles
            routes = []
            total_distance = 0.0
            total_load = 0.0

            for vehicle_id in range(n_vehicles):
                route = []
                route_distance = 0.0
                route_load = 0.0
                index = routing.Start(vehicle_id)

                while not routing.IsEnd(index):
                    node = manager.IndexToNode(index)
                    route.append(
                        {
                            "location": locations[node].name,
                            "index": node,
                            "demand": locations[node].demand,
                            "coordinates": {
                                "lat": locations[node].lat,
                                "lng": locations[node].lng,
                                "x": locations[node].x,
                                "y": locations[node].y,
                            },
                        }
                    )
                    route_load += locations[node].demand

                    previous_index = index
                    index = solution.Value(routing.NextVar(index))
                    if not routing.IsEnd(index):
                        from_node = manager.IndexToNode(previous_index)
                        to_node = manager.IndexToNode(index)
                        route_distance += distance_matrix[from_node][to_node]

                # Add return to depot
                if route:
                    depot_node = manager.IndexToNode(routing.End(vehicle_id))
                    if route[-1]["index"] != depot_node:
                        route.append(
                            {
                                "location": locations[depot_node].name,
                                "index": depot_node,
                                "demand": locations[depot_node].demand,
                                "coordinates": {
                                    "lat": locations[depot_node].lat,
                                    "lng": locations[depot_node].lng,
                                    "x": locations[depot_node].x,
                                    "y": locations[depot_node].y,
                                },
                            }
                        )
                        # Add distance back to depot
                        last_node = route[-2]["index"]
                        route_distance += distance_matrix[last_node][depot_node]

                if len(route) > 1:  # Only include routes with actual stops
                    routes.append(
                        {
                            "vehicle_id": vehicle_id,
                            "route": route,
                            "distance": route_distance,
                            "load": route_load,
                            "capacity": vehicles[vehicle_id].capacity,
                            "utilization": route_load / vehicles[vehicle_id].capacity
                            if vehicles[vehicle_id].capacity > 0
                            else 0,
                        }
                    )
                    total_distance += route_distance
                    total_load += route_load

            execution_time = time.time() - start_time

            return OptimizationResult(
                status=OptimizationStatus.OPTIMAL,
                objective_value=total_distance,
                variables={
                    "routes": routes,
                    "total_distance": total_distance,
                    "total_load": total_load,
                    "num_vehicles_used": len(routes),
                    "num_locations_served": sum(
                        len(route_data["route"]) - 1  # type: ignore[misc,arg-type]
                        for route_data in routes
                        if isinstance(route_data, dict) and "route" in route_data
                    ),  # Exclude depot returns
                },
                execution_time=execution_time,
                solver_info={
                    "solver_name": "OR-Tools Routing",
                    "search_strategy": "PATH_CHEAPEST_ARC",
                    "vehicles_available": n_vehicles,
                },
            )
        else:
            return OptimizationResult(
                status=OptimizationStatus.INFEASIBLE,
                error_message="No solution found within time limit",
                execution_time=time.time() - start_time,
            )

    except Exception as e:
        return OptimizationResult(
            status=OptimizationStatus.ERROR,
            error_message=f"VRP solving error: {str(e)}",
            execution_time=time.time() - start_time,
        )


def register_routing_tools(mcp: FastMCP[Any]) -> None:
    """Register routing optimization tools with MCP server."""

    @mcp.tool()
    def solve_traveling_salesman_problem(
        locations: list[dict[str, Any]],
        distance_matrix: list[list[float]] | None = None,
        start_location: int = 0,
        return_to_start: bool = True,
        time_limit_seconds: float = 30.0,
    ) -> dict[str, Any]:
        """Solve Traveling Salesman Problem (TSP) to find the shortest route visiting all locations.

        Args:
            locations: List of location dictionaries with name and coordinates
            distance_matrix: Optional pre-calculated distance matrix
            start_location: Index of starting location (default: 0)
            return_to_start: Whether to return to starting location (default: True)
            time_limit_seconds: Maximum solving time in seconds (default: 30.0)

        Returns:
            Optimization result with route and total distance
        """
        input_data = {
            "locations": locations,
            "distance_matrix": distance_matrix,
            "start_location": start_location,
            "return_to_start": return_to_start,
            "time_limit_seconds": time_limit_seconds,
        }

        result = solve_traveling_salesman(input_data)
        return result.model_dump()

    @mcp.tool()
    def solve_vehicle_routing_problem(
        locations: list[dict[str, Any]],
        vehicles: list[dict[str, Any]],
        distance_matrix: list[list[float]] | None = None,
        time_matrix: list[list[int]] | None = None,
        depot: int = 0,
        time_limit_seconds: float = 30.0,
    ) -> dict[str, Any]:
        """Solve Vehicle Routing Problem (VRP) to optimize routes for multiple vehicles.

        Args:
            locations: List of location dictionaries with name, coordinates, and demand
            vehicles: List of vehicle dictionaries with capacity constraints
            distance_matrix: Optional pre-calculated distance matrix
            time_matrix: Optional pre-calculated time matrix
            depot: Index of depot location (default: 0)
            time_limit_seconds: Maximum solving time in seconds (default: 30.0)

        Returns:
            Optimization result with routes for all vehicles
        """
        input_data = {
            "locations": locations,
            "vehicles": vehicles,
            "distance_matrix": distance_matrix,
            "time_matrix": time_matrix,
            "depot": depot,
            "time_limit_seconds": time_limit_seconds,
        }

        result = solve_vehicle_routing(input_data)
        return result.model_dump()
