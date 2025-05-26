#!/bin/bash
# Format code with ruff

set -e

echo "🎨 Formatting code with ruff..."
uv run ruff format .
uv run ruff check --fix .

echo "✅ Code formatting completed!" 