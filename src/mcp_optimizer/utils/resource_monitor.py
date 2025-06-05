"""Resource monitoring and concurrency control for MCP Optimizer."""

import asyncio
import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import psutil

from mcp_optimizer.config import settings

logger = logging.getLogger(__name__)


class ResourceMonitor:
    """Monitor system resources and control concurrency."""

    def __init__(self) -> None:
        """Initialize resource monitor."""
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
        self.active_requests = 0
        self.total_requests = 0
        self.failed_requests = 0
        self.memory_warnings = 0

        # Cache process for better performance
        self._process: psutil.Process | None = None
        self._last_memory_check: float = 0.0
        self._cached_memory_mb: float = 0.0

        # Cache interval: check memory max once per second
        self._memory_cache_interval = 1.0

    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB with caching."""
        current_time = time.time()

        # Return cached value if recent enough
        if current_time - self._last_memory_check < self._memory_cache_interval:
            return self._cached_memory_mb

        try:
            if self._process is None:
                self._process = psutil.Process()

            # Get memory info only once and cache it
            memory_info = self._process.memory_info()
            self._cached_memory_mb = memory_info.rss / 1024 / 1024
            self._last_memory_check = current_time

            return self._cached_memory_mb

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Process might have changed, reset cache
            self._process = None
            return 0.0

    def is_memory_available(self, required_mb: float) -> bool:
        """Check if enough memory is available for the operation."""
        try:
            current_memory = self.get_memory_usage_mb()
            available = current_memory + required_mb <= settings.max_memory_mb

            if not available:
                self.memory_warnings += 1
                logger.warning(
                    f"Memory limit would be exceeded: current={current_memory:.1f}MB, "
                    f"required={required_mb:.1f}MB, limit={settings.max_memory_mb}MB"
                )

            return available
        except Exception as e:
            logger.error(f"Error checking memory availability: {e}")
            return True  # Allow operation if we can't check

    async def acquire_semaphore(self, timeout_seconds: float = 30.0) -> bool:
        """Acquire semaphore with timeout."""
        try:
            await asyncio.wait_for(self.semaphore.acquire(), timeout=timeout_seconds)
            self.active_requests += 1
            return True
        except TimeoutError:
            logger.warning(f"Failed to acquire semaphore within {timeout_seconds}s")
            return False

    def release_semaphore(self) -> None:
        """Release semaphore."""
        self.semaphore.release()
        self.active_requests = max(0, self.active_requests - 1)

    def get_stats(self) -> dict[str, Any]:
        """Get resource monitoring statistics."""
        return {
            "active_requests": self.active_requests,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "memory_warnings": self.memory_warnings,
            "current_memory_mb": self.get_memory_usage_mb(),
            "max_memory_mb": settings.max_memory_mb,
            "max_concurrent_requests": settings.max_concurrent_requests,
        }


# Global instance
resource_monitor = ResourceMonitor()


class MemoryExceededError(Exception):
    """Raised when memory usage would exceed limits."""

    pass


class ConcurrencyLimitError(Exception):
    """Raised when concurrent request limit is exceeded."""

    pass


def with_resource_limits(
    timeout_seconds: float = 60.0, estimated_memory_mb: float = 100.0
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to enforce resource limits on functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                resource_monitor.total_requests += 1

                # Check memory before starting
                if not resource_monitor.is_memory_available(estimated_memory_mb):
                    resource_monitor.failed_requests += 1
                    raise MemoryExceededError(
                        f"Insufficient memory: need {estimated_memory_mb}MB, "
                        f"limit {settings.max_memory_mb}MB"
                    )

                # Acquire semaphore
                if not await resource_monitor.acquire_semaphore(timeout_seconds):
                    resource_monitor.failed_requests += 1
                    raise ConcurrencyLimitError(
                        f"Too many concurrent requests. Max: {settings.max_concurrent_requests}"
                    )

                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time

                    logger.debug(
                        f"Function {func.__name__} completed in {execution_time:.2f}s, "
                        f"memory: {resource_monitor.get_memory_usage_mb():.1f}MB"
                    )

                    return result

                except Exception as e:
                    resource_monitor.failed_requests += 1
                    execution_time = time.time() - start_time

                    logger.error(
                        f"Function {func.__name__} failed after {execution_time:.2f}s: {e}"
                    )
                    raise

                finally:
                    resource_monitor.release_semaphore()

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                resource_monitor.total_requests += 1

                # Check memory before starting
                if not resource_monitor.is_memory_available(estimated_memory_mb):
                    resource_monitor.failed_requests += 1
                    raise MemoryExceededError(
                        f"Insufficient memory: need {estimated_memory_mb}MB, "
                        f"limit {settings.max_memory_mb}MB"
                    )

                # For sync functions, we can't use async semaphore
                # Just check current count
                if resource_monitor.active_requests >= settings.max_concurrent_requests:
                    resource_monitor.failed_requests += 1
                    raise ConcurrencyLimitError(
                        f"Too many concurrent requests. Max: {settings.max_concurrent_requests}"
                    )

                resource_monitor.active_requests += 1
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time

                    logger.debug(
                        f"Function {func.__name__} completed in {execution_time:.2f}s, "
                        f"memory: {resource_monitor.get_memory_usage_mb():.1f}MB"
                    )

                    return result

                except Exception as e:
                    resource_monitor.failed_requests += 1
                    execution_time = time.time() - start_time

                    logger.error(
                        f"Function {func.__name__} failed after {execution_time:.2f}s: {e}"
                    )
                    raise

                finally:
                    resource_monitor.active_requests = max(0, resource_monitor.active_requests - 1)

            return sync_wrapper

    return decorator


def get_resource_status() -> dict[str, Any]:
    """Get current resource status for health checks."""
    return resource_monitor.get_stats()


def reset_resource_stats() -> None:
    """Reset resource statistics (for testing)."""
    resource_monitor.total_requests = 0
    resource_monitor.failed_requests = 0
    resource_monitor.memory_warnings = 0
