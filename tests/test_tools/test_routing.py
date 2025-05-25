"""Tests for routing optimization tools."""

import pytest
from mcp_optimizer.tools.routing import solve_traveling_salesman, solve_vehicle_routing


class TestTSP:
    """Test Traveling Salesman Problem solver."""

    def test_simple_tsp_with_coordinates(self):
        """Test TSP with coordinate-based locations."""
        input_data = {
            "locations": [
                {"name": "A", "x": 0, "y": 0},
                {"name": "B", "x": 1, "y": 0},
                {"name": "C", "x": 1, "y": 1},
                {"name": "D", "x": 0, "y": 1}
            ],
            "start_location": 0,
            "return_to_start": True,
            "time_limit_seconds": 10
        }
        
        result = solve_traveling_salesman(input_data)
        
        assert result.status == "optimal"
        assert result.objective_value is not None
        assert result.objective_value > 0
        assert "route" in result.variables
        assert len(result.variables["route"]) == 5  # 4 locations + return to start
        assert result.variables["route"][0]["location"] == "A"  # Start at A
        assert result.variables["route"][-1]["location"] == "A"  # Return to A

    def test_tsp_with_distance_matrix(self):
        """Test TSP with provided distance matrix."""
        input_data = {
            "locations": [
                {"name": "City1"},
                {"name": "City2"},
                {"name": "City3"}
            ],
            "distance_matrix": [
                [0, 10, 15],
                [10, 0, 20],
                [15, 20, 0]
            ],
            "start_location": 0,
            "return_to_start": True
        }
        
        result = solve_traveling_salesman(input_data)
        
        assert result.status == "optimal"
        assert result.objective_value is not None
        assert "route" in result.variables
        assert len(result.variables["route"]) == 4  # 3 locations + return

    def test_tsp_no_return(self):
        """Test TSP without returning to start."""
        input_data = {
            "locations": [
                {"name": "A", "x": 0, "y": 0},
                {"name": "B", "x": 1, "y": 0},
                {"name": "C", "x": 2, "y": 0}
            ],
            "start_location": 0,
            "return_to_start": False
        }
        
        result = solve_traveling_salesman(input_data)
        
        assert result.status == "optimal"
        assert "route" in result.variables
        assert len(result.variables["route"]) == 3  # No return to start

    def test_tsp_insufficient_locations(self):
        """Test TSP with insufficient locations."""
        input_data = {
            "locations": [
                {"name": "A", "x": 0, "y": 0}
            ]
        }
        
        result = solve_traveling_salesman(input_data)
        
        assert result.status == "error"
        assert "At least 2 locations required" in result.error_message

    def test_tsp_invalid_distance_matrix(self):
        """Test TSP with invalid distance matrix."""
        input_data = {
            "locations": [
                {"name": "A"},
                {"name": "B"}
            ],
            "distance_matrix": [
                [0, 10],
                [10]  # Invalid: missing element
            ]
        }
        
        result = solve_traveling_salesman(input_data)
        
        assert result.status == "error"
        assert "Distance matrix dimensions" in result.error_message


class TestVRP:
    """Test Vehicle Routing Problem solver."""

    def test_simple_vrp(self):
        """Test VRP with basic setup."""
        input_data = {
            "locations": [
                {"name": "Depot", "x": 0, "y": 0, "demand": 0},
                {"name": "Customer1", "x": 1, "y": 0, "demand": 10},
                {"name": "Customer2", "x": 0, "y": 1, "demand": 15},
                {"name": "Customer3", "x": 1, "y": 1, "demand": 20}
            ],
            "vehicles": [
                {"capacity": 30},
                {"capacity": 25}
            ],
            "depot": 0,
            "time_limit_seconds": 10
        }
        
        result = solve_vehicle_routing(input_data)
        
        assert result.status == "optimal"
        assert result.objective_value is not None
        assert "routes" in result.variables
        assert result.variables["num_vehicles_used"] <= 2
        assert result.variables["total_load"] == 45  # Sum of all demands

    def test_vrp_with_distance_matrix(self):
        """Test VRP with provided distance matrix."""
        input_data = {
            "locations": [
                {"name": "Depot", "demand": 0},
                {"name": "Customer1", "demand": 10},
                {"name": "Customer2", "demand": 15}
            ],
            "vehicles": [
                {"capacity": 30}
            ],
            "distance_matrix": [
                [0, 5, 8],
                [5, 0, 3],
                [8, 3, 0]
            ],
            "depot": 0
        }
        
        result = solve_vehicle_routing(input_data)
        
        assert result.status == "optimal"
        assert "routes" in result.variables
        assert len(result.variables["routes"]) == 1  # One vehicle used

    def test_vrp_capacity_constraint(self):
        """Test VRP with tight capacity constraints."""
        input_data = {
            "locations": [
                {"name": "Depot", "x": 0, "y": 0, "demand": 0},
                {"name": "Customer1", "x": 1, "y": 0, "demand": 20},
                {"name": "Customer2", "x": 0, "y": 1, "demand": 25}
            ],
            "vehicles": [
                {"capacity": 20},  # Can only serve one customer each
                {"capacity": 25}
            ],
            "depot": 0
        }
        
        result = solve_vehicle_routing(input_data)
        
        assert result.status == "optimal"
        assert result.variables["num_vehicles_used"] == 2  # Both vehicles needed

    def test_vrp_insufficient_capacity(self):
        """Test VRP with insufficient total capacity."""
        input_data = {
            "locations": [
                {"name": "Depot", "x": 0, "y": 0, "demand": 0},
                {"name": "Customer1", "x": 1, "y": 0, "demand": 50}
            ],
            "vehicles": [
                {"capacity": 30}  # Insufficient capacity
            ],
            "depot": 0
        }
        
        result = solve_vehicle_routing(input_data)
        
        assert result.status == "infeasible"

    def test_vrp_no_vehicles(self):
        """Test VRP with no vehicles."""
        input_data = {
            "locations": [
                {"name": "Depot", "x": 0, "y": 0, "demand": 0},
                {"name": "Customer1", "x": 1, "y": 0, "demand": 10}
            ],
            "vehicles": [],
            "depot": 0
        }
        
        result = solve_vehicle_routing(input_data)
        
        assert result.status == "error"
        assert "At least 1 vehicle required" in result.error_message

    def test_vrp_insufficient_locations(self):
        """Test VRP with insufficient locations."""
        input_data = {
            "locations": [
                {"name": "Depot", "x": 0, "y": 0, "demand": 0}
            ],
            "vehicles": [
                {"capacity": 30}
            ],
            "depot": 0
        }
        
        result = solve_vehicle_routing(input_data)
        
        assert result.status == "error"
        assert "At least 2 locations required" in result.error_message


class TestDistanceCalculation:
    """Test distance calculation functions."""

    def test_euclidean_distance(self):
        """Test Euclidean distance calculation."""
        from mcp_optimizer.tools.routing import calculate_distance_matrix
        
        locations = [
            {"name": "A", "x": 0, "y": 0},
            {"name": "B", "x": 3, "y": 4}  # Distance should be 5
        ]
        
        matrix = calculate_distance_matrix(locations)
        
        assert len(matrix) == 2
        assert len(matrix[0]) == 2
        assert matrix[0][0] == 0  # Distance to self
        assert matrix[1][1] == 0  # Distance to self
        assert abs(matrix[0][1] - 5.0) < 1e-6  # 3-4-5 triangle
        assert abs(matrix[1][0] - 5.0) < 1e-6  # Symmetric

    def test_haversine_distance(self):
        """Test haversine distance calculation."""
        from mcp_optimizer.tools.routing import haversine_distance
        
        # Distance between New York and Los Angeles (approximately)
        ny_lat, ny_lng = 40.7128, -74.0060
        la_lat, la_lng = 34.0522, -118.2437
        
        distance = haversine_distance(ny_lat, ny_lng, la_lat, la_lng)
        
        # Should be approximately 3944 km
        assert 3900 < distance < 4000

    def test_missing_coordinates(self):
        """Test error handling for missing coordinates."""
        from mcp_optimizer.tools.routing import calculate_distance_matrix
        
        locations = [
            {"name": "A", "x": 0, "y": 0},
            {"name": "B"}  # Missing coordinates
        ]
        
        with pytest.raises(ValueError, match="Insufficient coordinate data"):
            calculate_distance_matrix(locations) 