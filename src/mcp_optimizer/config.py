"""Configuration management for MCP Optimizer server."""

from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TransportMode(str, Enum):
    """Transport mode for the server."""

    STDIO = "stdio"
    SSE = "sse"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogFormat(str, Enum):
    """Log output formats."""

    JSON = "json"
    TEXT = "text"


class SolverType(str, Enum):
    """Available solver types."""

    CBC = "CBC"
    GLPK = "GLPK"
    GUROBI = "GUROBI"
    CPLEX = "CPLEX"


class Settings(BaseSettings):
    """Application settings."""

    # Transport configuration
    transport_mode: TransportMode = Field(
        default=TransportMode.STDIO,
        description="Server transport mode",
    )
    server_port: int = Field(
        default=8000,
        description="Server port (for SSE and HTTP modes)",
        ge=1,
        le=65535,
    )
    server_host: str = Field(
        default="127.0.0.1",  # nosec B104 - localhost only by default for security
        description="Server host (for SSE and HTTP modes)",
    )

    # Solver configuration
    default_solver: SolverType = Field(
        default=SolverType.CBC,
        description="Default solver for optimization problems",
    )
    max_solve_time: int = Field(
        default=300,
        description="Maximum solve time in seconds",
        ge=1,
    )
    max_memory_mb: int = Field(
        default=1024,
        description="Maximum memory usage in MB",
        ge=128,
    )

    # Logging configuration
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level",
    )
    log_format: LogFormat = Field(
        default=LogFormat.JSON,
        description="Log output format",
    )

    # Development settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    reload: bool = Field(
        default=False,
        description="Enable auto-reload for development",
    )

    # Security settings
    max_concurrent_requests: int = Field(
        default=10,
        description="Maximum concurrent optimization requests",
        ge=1,
    )
    request_timeout: int = Field(
        default=600,
        description="Request timeout in seconds",
        ge=30,
    )

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
