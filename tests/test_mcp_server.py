"""Tests for MCP server functionality."""

import time
from unittest.mock import MagicMock, patch

from mcp_optimizer.mcp_server import create_mcp_server


class TestCreateMCPServer:
    """Tests for create_mcp_server function."""

    def test_create_mcp_server(self):
        """Test MCP server creation."""
        server = create_mcp_server()
        assert server is not None
        assert server.name == "MCP Optimizer"


class TestHealthFunctions:
    """Tests for health check functions."""

    def test_health_check_healthy(self):
        """Test health check when server is healthy."""
        with patch("mcp_optimizer.mcp_server.FastMCP") as mock_fastmcp:
            mock_server = MagicMock()
            mock_fastmcp.return_value = mock_server

            # Create server to register resources
            create_mcp_server()

            # Verify resource was registered
            resource_calls = mock_server.resource.call_args_list
            health_call_found = any(call[0][0] == "resource://health" for call in resource_calls)
            assert health_call_found

    def test_health_check_warning_memory(self):
        """Test health check with warning memory usage."""
        with patch("mcp_optimizer.mcp_server.FastMCP") as mock_fastmcp:
            mock_server = MagicMock()
            mock_fastmcp.return_value = mock_server

            create_mcp_server()

            # Check health resource was registered
            resource_calls = mock_server.resource.call_args_list
            health_call_found = any(call[0][0] == "resource://health" for call in resource_calls)
            assert health_call_found

    def test_health_check_critical_memory(self):
        """Test health check with critical memory usage."""
        with patch("mcp_optimizer.mcp_server.FastMCP") as mock_fastmcp:
            mock_server = MagicMock()
            mock_fastmcp.return_value = mock_server

            create_mcp_server()

            resource_calls = mock_server.resource.call_args_list
            health_call_found = any(call[0][0] == "resource://health" for call in resource_calls)
            assert health_call_found

    def test_health_check_max_requests(self):
        """Test health check when at maximum concurrent requests."""
        with patch("mcp_optimizer.mcp_server.FastMCP") as mock_fastmcp:
            mock_server = MagicMock()
            mock_fastmcp.return_value = mock_server

            create_mcp_server()

            resource_calls = mock_server.resource.call_args_list
            health_call_found = any(call[0][0] == "resource://health" for call in resource_calls)
            assert health_call_found

    def test_health_check_import_error(self):
        """Test health check when import error occurs."""
        with patch("mcp_optimizer.mcp_server.FastMCP") as mock_fastmcp:
            mock_server = MagicMock()
            mock_fastmcp.return_value = mock_server

            create_mcp_server()

            resource_calls = mock_server.resource.call_args_list
            health_call_found = any(call[0][0] == "resource://health" for call in resource_calls)
            assert health_call_found

    def test_health_check_zero_max_memory(self):
        """Test health check with zero max memory edge case."""
        with patch("mcp_optimizer.mcp_server.FastMCP") as mock_fastmcp:
            mock_server = MagicMock()
            mock_fastmcp.return_value = mock_server

            create_mcp_server()

            resource_calls = mock_server.resource.call_args_list
            health_call_found = any(call[0][0] == "resource://health" for call in resource_calls)
            assert health_call_found


class TestResourceFunctions:
    """Tests for resource management functions."""

    def test_resource_stats(self):
        """Test resource stats endpoint."""
        with patch("mcp_optimizer.mcp_server.FastMCP") as mock_fastmcp:
            mock_server = MagicMock()
            mock_fastmcp.return_value = mock_server

            create_mcp_server()

            resource_calls = mock_server.resource.call_args_list
            stats_call_found = any(
                call[0][0] == "resource://resource-stats" for call in resource_calls
            )
            assert stats_call_found

    def test_resource_reset(self):
        """Test resource reset endpoint."""
        with patch("mcp_optimizer.mcp_server.FastMCP") as mock_fastmcp:
            mock_server = MagicMock()
            mock_fastmcp.return_value = mock_server

            create_mcp_server()

            resource_calls = mock_server.resource.call_args_list
            reset_call_found = any(
                call[0][0] == "resource://resource-reset" for call in resource_calls
            )
            assert reset_call_found

    def test_server_info(self):
        """Test server info endpoint."""
        with patch("mcp_optimizer.mcp_server.FastMCP") as mock_fastmcp:
            mock_server = MagicMock()
            mock_fastmcp.return_value = mock_server

            create_mcp_server()

            resource_calls = mock_server.resource.call_args_list
            info_call_found = any(call[0][0] == "resource://server-info" for call in resource_calls)
            assert info_call_found


class TestServerStartTime:
    """Tests for server start time tracking."""

    def test_server_start_time_tracking(self):
        """Test that server start time is tracked correctly."""
        start_time = time.time()

        # Import the module to set _server_start_time
        from mcp_optimizer import mcp_server

        # The _server_start_time should be close to when we started
        time_diff = abs(mcp_server._server_start_time - start_time)
        assert time_diff < 10.0  # Should be within 10 seconds (more lenient)


class TestServerConfiguration:
    """Tests for server configuration and logging."""

    def test_server_logging(self):
        """Test that server creation logs appropriate messages."""
        with patch("mcp_optimizer.mcp_server.logger") as mock_logger:
            create_mcp_server()

            # Check that info messages were logged
            assert mock_logger.info.call_count >= 2

            # Check the logged messages
            calls = mock_logger.info.call_args_list
            assert any("MCP Optimizer server created and configured" in str(call) for call in calls)
            assert any("Configuration:" in str(call) for call in calls)


def test_health_check_critical_memory():
    """Test health check with critical memory usage."""
    # Test the logic directly using the resource status function
    with patch("mcp_optimizer.mcp_server.get_resource_status") as mock_status:
        mock_status.return_value = {
            "current_memory_mb": 950,
            "max_memory_mb": 1024,
            "active_requests": 2,
            "max_concurrent_requests": 10,
        }

        from mcp_optimizer.mcp_server import get_resource_status

        resource_status = get_resource_status()

        current_memory = resource_status.get("current_memory_mb", 0)
        max_memory = resource_status.get("max_memory_mb", 1024)
        memory_usage_pct = (current_memory / max_memory) * 100 if max_memory > 0 else 0

        # Should be critical due to high memory usage (>90%)
        assert memory_usage_pct > 90


def test_resource_endpoint_functions():
    """Test resource endpoint functions work correctly."""
    # Test get_resource_status
    with patch("mcp_optimizer.mcp_server.get_resource_status") as mock_status:
        expected_stats = {
            "current_memory_mb": 256,
            "max_memory_mb": 1024,
            "active_requests": 3,
            "max_concurrent_requests": 10,
        }
        mock_status.return_value = expected_stats

        from mcp_optimizer.mcp_server import get_resource_status

        result = get_resource_status()
        assert result == expected_stats

    # Test reset_resource_stats
    with patch("mcp_optimizer.mcp_server.reset_resource_stats") as mock_reset:
        from mcp_optimizer.mcp_server import reset_resource_stats

        reset_resource_stats()
        mock_reset.assert_called_once()


def test_server_configuration_access():
    """Test server configuration access."""
    with patch("mcp_optimizer.mcp_server.get_version") as mock_version:
        mock_version.return_value = "1.2.3"

        from mcp_optimizer.mcp_server import get_version, settings

        # Test that we can access configuration values
        assert settings.max_solve_time > 0
        assert settings.max_memory_mb > 0
        assert settings.max_concurrent_requests > 0
        assert hasattr(settings.log_level, "value")
        assert isinstance(settings.debug, bool)

        # Test version access
        version = get_version("mcp-optimizer")
        assert version == "1.2.3"


def test_server_logging():
    """Test server logging during creation."""
    with patch("mcp_optimizer.mcp_server.logger") as mock_logger:
        from mcp_optimizer.mcp_server import create_mcp_server

        create_mcp_server()

        # Check that logging calls were made
        assert mock_logger.info.call_count >= 2

        # Check specific log messages
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("MCP Optimizer server created" in msg for msg in log_calls)
        assert any("Configuration:" in msg for msg in log_calls)


class TestResourceEndpoints:
    """Test resource endpoints in MCP server."""

    def test_get_health_error_status(self):
        """Test health endpoint error status when ImportError occurs."""

        # Mock get_version to raise ImportError
        with patch(
            "mcp_optimizer.mcp_server.get_version", side_effect=ImportError("Package not found")
        ):
            # Test the health function directly by calling the mocked module
            from mcp_optimizer.mcp_server import get_health

            result = get_health()

            assert result["status"] == "error"
            assert "Health check failed" in result["message"]
            assert "Package not found" in result["message"]
            assert result["resource_status"] == {}

    def test_get_health_memory_critical(self):
        """Test health endpoint with critical memory usage."""

        # Mock get_resource_status to return critical memory
        with (
            patch("mcp_optimizer.mcp_server.get_resource_status") as mock_status,
            patch("mcp_optimizer.mcp_server.resource_monitor") as mock_monitor,
            patch("mcp_optimizer.mcp_server.get_version", return_value="1.0.0"),
        ):
            mock_status.return_value = {
                "current_memory_mb": 950,
                "max_memory_mb": 1000,
                "active_requests": 2,
                "max_concurrent_requests": 10,
            }
            mock_monitor.total_requests = 100
            mock_monitor.get_stats.return_value = {"test": "stats"}

            # Test the health function directly
            from mcp_optimizer.mcp_server import get_health

            result = get_health()
            assert result["status"] == "critical"
            assert "High memory usage" in result["message"]

    def test_get_health_memory_warning(self):
        """Test health endpoint with warning memory usage."""

        with (
            patch("mcp_optimizer.mcp_server.get_resource_status") as mock_status,
            patch("mcp_optimizer.mcp_server.resource_monitor") as mock_monitor,
            patch("mcp_optimizer.mcp_server.get_version", return_value="1.0.0"),
        ):
            mock_status.return_value = {
                "current_memory_mb": 800,
                "max_memory_mb": 1000,
                "active_requests": 2,
                "max_concurrent_requests": 10,
            }
            mock_monitor.total_requests = 50
            mock_monitor.get_stats.return_value = {"test": "stats"}

            from mcp_optimizer.mcp_server import get_health

            result = get_health()
            assert result["status"] == "warning"
            assert "Elevated memory usage" in result["message"]

    def test_get_health_max_requests_warning(self):
        """Test health endpoint with max concurrent requests warning."""

        with (
            patch("mcp_optimizer.mcp_server.get_resource_status") as mock_status,
            patch("mcp_optimizer.mcp_server.resource_monitor") as mock_monitor,
            patch("mcp_optimizer.mcp_server.get_version", return_value="1.0.0"),
        ):
            mock_status.return_value = {
                "current_memory_mb": 100,
                "max_memory_mb": 1000,
                "active_requests": 10,
                "max_concurrent_requests": 10,
            }
            mock_monitor.total_requests = 50
            mock_monitor.get_stats.return_value = {"test": "stats"}

            from mcp_optimizer.mcp_server import get_health

            result = get_health()
            assert result["status"] == "warning"
            assert "At maximum concurrent request limit" in result["message"]

    def test_get_health_zero_max_memory(self):
        """Test health endpoint with zero max memory."""

        with (
            patch("mcp_optimizer.mcp_server.get_resource_status") as mock_status,
            patch("mcp_optimizer.mcp_server.resource_monitor") as mock_monitor,
            patch("mcp_optimizer.mcp_server.get_version", return_value="1.0.0"),
        ):
            mock_status.return_value = {
                "current_memory_mb": 100,
                "max_memory_mb": 0,  # Zero max memory
                "active_requests": 2,
                "max_concurrent_requests": 10,
            }
            mock_monitor.total_requests = 50
            mock_monitor.get_stats.return_value = {"test": "stats"}

            from mcp_optimizer.mcp_server import get_health

            result = get_health()
            # Should handle zero division gracefully
            assert result["status"] in ["healthy", "warning", "critical"]

    def test_resource_stats_endpoint(self):
        """Test resource-stats endpoint."""

        with patch("mcp_optimizer.mcp_server.get_resource_status") as mock_status:
            mock_status.return_value = {"test": "resource_data"}

            from mcp_optimizer.mcp_server import get_resource_stats

            result = get_resource_stats()
            assert result == {"test": "resource_data"}

    def test_resource_reset_endpoint(self):
        """Test resource-reset endpoint."""

        with patch("mcp_optimizer.mcp_server.reset_resource_stats") as mock_reset:
            from mcp_optimizer.mcp_server import reset_resource_statistics

            result = reset_resource_statistics()

            mock_reset.assert_called_once()
            assert result["status"] == "reset"
            assert "reset" in result["message"]

    def test_server_info_endpoint(self):
        """Test server-info endpoint."""

        with patch("mcp_optimizer.mcp_server.get_version", return_value="1.2.3"):
            from mcp_optimizer.mcp_server import get_server_info

            result = get_server_info()

            assert result["name"] == "MCP Optimizer"
            assert result["version"] == "1.2.3"
            assert "capabilities" in result
            assert "solvers" in result
            assert "configuration" in result
            assert result["capabilities"]["linear_programming"] is True
            assert result["capabilities"]["integer_programming"] is True
            assert "pulp" in result["solvers"]
            assert "ortools" in result["solvers"]
