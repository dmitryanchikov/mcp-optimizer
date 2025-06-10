"""Solvers package with safe OR-Tools import."""

import logging

logger = logging.getLogger(__name__)

try:
    from .ortools_solver import ORToolsSolver
except ImportError as e:
    logger.warning(f"OR-Tools solver not available: {e}")
    from .fallback_solver import FallbackSolver

    ORToolsSolver = FallbackSolver  # type: ignore[misc,assignment]

__all__ = ["ORToolsSolver"]
