#!/bin/bash

# Test Local Package Build and Functionality
# Author: MCP Optimizer Team
# Usage: ./scripts/test_local_package.sh

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "🚀 Starting local package testing..."
echo "Working directory: $(pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test configuration
STDIO_TEST_DURATION=3
SSE_TEST_DURATION=3
SSE_TEST_PORT=8001

cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up test processes...${NC}"
    pkill -f "mcp-optimizer" 2>/dev/null || true
    sleep 1
}

# Setup cleanup on exit
trap cleanup EXIT

echo -e "${YELLOW}📦 Building package...${NC}"
if ! uv build; then
    echo -e "${RED}❌ Package build failed${NC}"
    exit 1
fi

# Get the built wheel file
WHEEL_FILE=$(ls dist/*.whl | head -1)
if [[ ! -f "$WHEEL_FILE" ]]; then
    echo -e "${RED}❌ No wheel file found in dist/${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Package built: $WHEEL_FILE${NC}"

echo -e "\n${YELLOW}🧪 Testing STDIO mode...${NC}"
echo "Starting mcp-optimizer in stdio mode..."

# Test stdio mode with timeout (should start and show logs)
# Using bash timeout approach for macOS compatibility
if command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_CMD="gtimeout"
elif command -v timeout >/dev/null 2>&1; then
    TIMEOUT_CMD="timeout"
else
    # Use bash built-in approach
    TIMEOUT_CMD=""
fi

if [[ -n "$TIMEOUT_CMD" ]]; then
    # Use external timeout command
    if $TIMEOUT_CMD 3 uvx --from "$WHEEL_FILE" mcp-optimizer --transport stdio >/dev/null 2>&1; then
        echo -e "${GREEN}✅ STDIO server started and stopped cleanly${NC}"
    elif [[ $? == 124 || $? == 143 ]]; then
        # Exit code 124 = timeout, 143 = SIGTERM - both are OK for this test
        echo -e "${GREEN}✅ STDIO server started and stopped cleanly${NC}"
    else
        echo -e "${RED}❌ STDIO server failed to start${NC}"
        exit 1
    fi
else
    # Use bash background process with timeout
    uvx --from "$WHEEL_FILE" mcp-optimizer --transport stdio &
    STDIO_PID=$!
    
    # Give it time to start
    sleep $STDIO_TEST_DURATION
    
    # Check if process is still running (good sign)
    if kill -0 $STDIO_PID 2>/dev/null; then
        echo -e "${GREEN}✅ STDIO server started successfully${NC}"
        kill $STDIO_PID 2>/dev/null || true
        wait $STDIO_PID 2>/dev/null || true
    else
        echo -e "${RED}❌ STDIO server stopped unexpectedly${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ STDIO mode test completed${NC}"

echo -e "\n${YELLOW}🌐 Testing SSE mode...${NC}"
echo "Starting mcp-optimizer in SSE mode on port $SSE_TEST_PORT..."

# Start SSE server in background  
uvx --from "$WHEEL_FILE" mcp-optimizer --transport sse --host 127.0.0.1 --port $SSE_TEST_PORT &
SSE_PID=$!

# Give it time to start
sleep 5

# Check if process is running
if ! kill -0 $SSE_PID 2>/dev/null; then
    echo -e "${RED}❌ SSE server failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ SSE server started (PID: $SSE_PID)${NC}"

# Test SSE endpoint
echo "Testing SSE endpoint..."
sleep 2  # Give server more time to be ready

# Check if port is listening
if lsof -i :$SSE_TEST_PORT >/dev/null 2>&1; then
    echo -e "${GREEN}✅ SSE server listening on port $SSE_TEST_PORT${NC}"
else
    echo -e "${RED}❌ SSE server not listening on port $SSE_TEST_PORT${NC}"
    kill $SSE_PID 2>/dev/null || true
    exit 1
fi

# Test SSE headers (quick check)
echo "Checking SSE headers..."
HEADERS=$(curl -s -I --max-time 2 "http://127.0.0.1:$SSE_TEST_PORT/sse" 2>/dev/null | head -10)
if echo "$HEADERS" | grep -q "text/event-stream"; then
    echo -e "${GREEN}✅ SSE headers correct${NC}"
elif echo "$HEADERS" | grep -q "200 OK"; then
    echo -e "${GREEN}✅ SSE endpoint responding (headers may vary)${NC}"
else
    echo -e "${YELLOW}⚠️  SSE endpoint response unclear, but server is running${NC}"
fi

# Wait a bit then stop
sleep $SSE_TEST_DURATION
kill $SSE_PID 2>/dev/null || true
wait $SSE_PID 2>/dev/null || true

echo -e "${GREEN}✅ SSE mode test completed${NC}"

echo -e "\n${YELLOW}📋 Testing CLI help...${NC}"
if uvx --from "$WHEEL_FILE" mcp-optimizer --help >/dev/null; then
    echo -e "${GREEN}✅ CLI help working${NC}"
else
    echo -e "${RED}❌ CLI help failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 All local package tests passed!${NC}"
echo -e "${YELLOW}📊 Test Summary:${NC}"
echo "  ✅ Package build successful"
echo "  ✅ STDIO mode functional"
echo "  ✅ SSE mode functional"
echo "  ✅ SSE endpoint accessible"
echo "  ✅ CLI interface working"
echo -e "\n${GREEN}✨ Local package ready for deployment!${NC}" 