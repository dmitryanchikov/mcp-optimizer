#!/bin/bash
# Format code with ruff

set -e

echo "🎨 Formatting code with ruff..."
uv run ruff format src/ tests/
uv run ruff check --fix src/ tests/

echo "✅ Code formatting completed!" 