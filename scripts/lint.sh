#!/bin/bash
# Lint and type check

set -e

echo "🔍 Linting code with ruff..."
uv run ruff check src/ tests/

echo "🔍 Type checking with mypy..."
uv run mypy src/

echo "✅ Code linting completed!" 