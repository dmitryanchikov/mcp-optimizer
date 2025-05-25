#!/bin/bash
# Run test suite

set -e

echo "🧪 Running test suite..."
uv run pytest tests/ -v --cov=src/mcp_optimizer --cov-report=term-missing --cov-report=html

echo "✅ Tests completed!"
echo "📊 Coverage report generated in htmlcov/" 