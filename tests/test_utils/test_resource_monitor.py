"""Tests for resource monitoring utilities."""

import time
from unittest.mock import MagicMock, patch

import psutil
import pytest

from mcp_optimizer.utils.resource_monitor import (
    ConcurrencyLimitError,
    MemoryExceededError,
    ResourceMonitor,
    get_resource_status,
    reset_resource_stats,
    resource_monitor,
    with_resource_limits,
)


class TestResourceMonitor:
    """Tests for ResourceMonitor class."""

    def test_init(self):
        """Test ResourceMonitor initialization."""
        monitor = ResourceMonitor()
        assert monitor.active_requests == 0
        assert monitor.total_requests == 0
        assert monitor.failed_requests == 0
        assert monitor.memory_warnings == 0
        assert monitor._process is None
        assert monitor._last_memory_check == 0.0
        assert monitor._cached_memory_mb == 0.0

    def test_get_memory_usage_mb_success(self):
        """Test successful memory usage retrieval."""
        monitor = ResourceMonitor()

        # Mock psutil.Process
        mock_process = MagicMock()
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 1024 * 1024 * 100  # 100MB
        mock_process.memory_info.return_value = mock_memory_info

        with patch("psutil.Process", return_value=mock_process):
            memory_mb = monitor.get_memory_usage_mb()
            assert memory_mb == 100.0
            assert monitor._cached_memory_mb == 100.0

    def test_get_memory_usage_mb_cached(self):
        """Test memory usage caching."""
        monitor = ResourceMonitor()
        monitor._cached_memory_mb = 50.0
        monitor._last_memory_check = time.time()

        # Should return cached value without calling psutil
        memory_mb = monitor.get_memory_usage_mb()
        assert memory_mb == 50.0

    def test_get_memory_usage_mb_exception_handling(self):
        """Test memory usage exception handling."""
        monitor = ResourceMonitor()

        # Mock psutil to raise exceptions
        with patch("psutil.Process", side_effect=psutil.NoSuchProcess(123)):
            memory_mb = monitor.get_memory_usage_mb()
            assert memory_mb == 0.0
            assert monitor._process is None

        with patch("psutil.Process", side_effect=psutil.AccessDenied()):
            memory_mb = monitor.get_memory_usage_mb()
            assert memory_mb == 0.0

        with patch("psutil.Process", side_effect=psutil.ZombieProcess(123)):
            memory_mb = monitor.get_memory_usage_mb()
            assert memory_mb == 0.0

    def test_is_memory_available_sufficient(self):
        """Test memory availability check when sufficient."""
        monitor = ResourceMonitor()

        with patch.object(monitor, "get_memory_usage_mb", return_value=100.0):
            with patch("mcp_optimizer.config.settings.max_memory_mb", 1000):
                assert monitor.is_memory_available(50.0) is True
                assert monitor.memory_warnings == 0

    def test_is_memory_available_insufficient(self):
        """Test memory availability check when insufficient."""
        monitor = ResourceMonitor()

        with patch.object(monitor, "get_memory_usage_mb", return_value=900.0):
            with patch("mcp_optimizer.config.settings.max_memory_mb", 1000):
                assert monitor.is_memory_available(200.0) is False
                assert monitor.memory_warnings == 1

    def test_is_memory_available_exception_handling(self):
        """Test memory availability exception handling."""
        monitor = ResourceMonitor()

        with patch.object(monitor, "get_memory_usage_mb", side_effect=Exception("Test error")):
            assert monitor.is_memory_available(100.0) is True  # Should allow operation

    @pytest.mark.asyncio
    async def test_acquire_semaphore_success(self):
        """Test successful semaphore acquisition."""
        monitor = ResourceMonitor()

        result = await monitor.acquire_semaphore(timeout_seconds=1.0)
        assert result is True
        assert monitor.active_requests == 1

        # Cleanup
        monitor.release_semaphore()

    @pytest.mark.asyncio
    async def test_acquire_semaphore_timeout(self):
        """Test semaphore acquisition timeout."""
        monitor = ResourceMonitor()

        # Fill up all semaphores
        with patch("mcp_optimizer.config.settings.max_concurrent_requests", 1):
            monitor = ResourceMonitor()  # Recreate with new settings
            await monitor.acquire_semaphore()

            # This should timeout
            result = await monitor.acquire_semaphore(timeout_seconds=0.1)
            assert result is False

    def test_release_semaphore(self):
        """Test semaphore release."""
        monitor = ResourceMonitor()
        monitor.active_requests = 5

        monitor.release_semaphore()
        assert monitor.active_requests == 4

        # Test that it doesn't go below 0
        monitor.active_requests = 0
        monitor.release_semaphore()
        assert monitor.active_requests == 0

    def test_get_stats(self):
        """Test statistics retrieval."""
        monitor = ResourceMonitor()
        monitor.active_requests = 2
        monitor.total_requests = 10
        monitor.failed_requests = 1
        monitor.memory_warnings = 3

        with patch.object(monitor, "get_memory_usage_mb", return_value=150.0):
            with patch("mcp_optimizer.config.settings.max_memory_mb", 1000):
                with patch("mcp_optimizer.config.settings.max_concurrent_requests", 5):
                    stats = monitor.get_stats()

                    assert stats["active_requests"] == 2
                    assert stats["total_requests"] == 10
                    assert stats["failed_requests"] == 1
                    assert stats["memory_warnings"] == 3
                    assert stats["current_memory_mb"] == 150.0
                    assert stats["max_memory_mb"] == 1000
                    assert stats["max_concurrent_requests"] == 5


class TestGlobalFunctions:
    """Tests for global utility functions."""

    def test_get_resource_status(self):
        """Test get_resource_status function."""
        with patch.object(resource_monitor, "get_stats", return_value={"test": "data"}):
            status = get_resource_status()
            assert status == {"test": "data"}

    def test_reset_resource_stats(self):
        """Test reset_resource_stats function."""
        resource_monitor.total_requests = 100
        resource_monitor.failed_requests = 10
        resource_monitor.memory_warnings = 5

        reset_resource_stats()

        assert resource_monitor.total_requests == 0
        assert resource_monitor.failed_requests == 0
        assert resource_monitor.memory_warnings == 0


class TestWithResourceLimitsDecorator:
    """Tests for with_resource_limits decorator."""

    @pytest.mark.asyncio
    async def test_async_function_success(self):
        """Test decorator with successful async function."""

        @with_resource_limits(timeout_seconds=10.0, estimated_memory_mb=50.0)
        async def test_async_func():
            return "success"

        # Mock memory check to return True
        with patch.object(resource_monitor, "is_memory_available", return_value=True):
            with patch.object(resource_monitor, "acquire_semaphore", return_value=True):
                with patch.object(resource_monitor, "release_semaphore"):
                    result = await test_async_func()
                    assert result == "success"

    @pytest.mark.asyncio
    async def test_async_function_memory_exceeded(self):
        """Test decorator with memory exceeded error."""

        @with_resource_limits(timeout_seconds=10.0, estimated_memory_mb=1000.0)
        async def test_async_func():
            return "success"

        with patch.object(resource_monitor, "is_memory_available", return_value=False):
            with pytest.raises(MemoryExceededError):
                await test_async_func()

    @pytest.mark.asyncio
    async def test_async_function_concurrency_limit(self):
        """Test decorator with concurrency limit error."""

        @with_resource_limits(timeout_seconds=0.1, estimated_memory_mb=50.0)
        async def test_async_func():
            return "success"

        with patch.object(resource_monitor, "is_memory_available", return_value=True):
            with patch.object(resource_monitor, "acquire_semaphore", return_value=False):
                with pytest.raises(ConcurrencyLimitError):
                    await test_async_func()

    @pytest.mark.asyncio
    async def test_async_function_exception_handling(self):
        """Test decorator with function exception."""

        @with_resource_limits(timeout_seconds=10.0, estimated_memory_mb=50.0)
        async def test_async_func():
            raise ValueError("Test error")

        with patch.object(resource_monitor, "is_memory_available", return_value=True):
            with patch.object(resource_monitor, "acquire_semaphore", return_value=True):
                with patch.object(resource_monitor, "release_semaphore"):
                    with pytest.raises(ValueError, match="Test error"):
                        await test_async_func()

    def test_sync_function_success(self):
        """Test decorator with successful sync function."""

        @with_resource_limits(timeout_seconds=10.0, estimated_memory_mb=50.0)
        def test_sync_func():
            return "success"

        with patch.object(resource_monitor, "is_memory_available", return_value=True):
            with patch("mcp_optimizer.config.settings.max_concurrent_requests", 10):
                result = test_sync_func()
                assert result == "success"

    def test_sync_function_memory_exceeded(self):
        """Test decorator with memory exceeded error for sync function."""

        @with_resource_limits(timeout_seconds=10.0, estimated_memory_mb=1000.0)
        def test_sync_func():
            return "success"

        with patch.object(resource_monitor, "is_memory_available", return_value=False):
            with pytest.raises(MemoryExceededError):
                test_sync_func()

    def test_sync_function_concurrency_limit(self):
        """Test decorator with concurrency limit for sync function."""

        @with_resource_limits(timeout_seconds=10.0, estimated_memory_mb=50.0)
        def test_sync_func():
            return "success"

        with patch.object(resource_monitor, "is_memory_available", return_value=True):
            with patch("mcp_optimizer.config.settings.max_concurrent_requests", 1):
                # Set active requests to max
                resource_monitor.active_requests = 1

                with pytest.raises(ConcurrencyLimitError):
                    test_sync_func()

                # Reset for cleanup
                resource_monitor.active_requests = 0

    def test_sync_function_exception_handling(self):
        """Test decorator with sync function exception."""

        @with_resource_limits(timeout_seconds=10.0, estimated_memory_mb=50.0)
        def test_sync_func():
            raise ValueError("Test error")

        with patch.object(resource_monitor, "is_memory_available", return_value=True):
            with patch("mcp_optimizer.config.settings.max_concurrent_requests", 10):
                with pytest.raises(ValueError, match="Test error"):
                    test_sync_func()


class TestExceptions:
    """Tests for custom exception classes."""

    def test_memory_exceeded_error(self):
        """Test MemoryExceededError exception."""
        error = MemoryExceededError("Test message")
        assert str(error) == "Test message"

    def test_concurrency_limit_error(self):
        """Test ConcurrencyLimitError exception."""
        error = ConcurrencyLimitError("Test message")
        assert str(error) == "Test message"
