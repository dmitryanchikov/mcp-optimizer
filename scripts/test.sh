#!/bin/bash
# Run test suite

set -e

echo "🧪 Running test suite..."

# Test 1: Server creation and import (catches initialization errors)
echo "🔧 Testing server creation and imports..."
uv run python3 -c "
from mcp_optimizer.mcp_server import create_mcp_server
server = create_mcp_server()
print('✅ Server created successfully')
"

uv run python3 -c "
import main
print('✅ Main module imported successfully')
"

# Test 2: Run pytest suite
echo "🧪 Running pytest suite..."
if uv run pytest tests/ -v --cov=src/mcp_optimizer --cov-report=term-missing --cov-report=html 2>/dev/null; then
    echo "✅ Full test suite with coverage completed"
else
    echo "⚠️  Coverage not available, running basic tests..."
    uv run pytest tests/ -v
fi

echo "✅ Tests completed!"
echo "📊 Coverage report generated in htmlcov/" 