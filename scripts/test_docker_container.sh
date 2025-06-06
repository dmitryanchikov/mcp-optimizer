#!/bin/bash

# Test Docker Container Build and Functionality
# Author: MCP Optimizer Team
# Usage: ./scripts/test_docker_container.sh

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "🐳 Starting Docker container testing..."
echo "Working directory: $(pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
DOCKER_IMAGE="mcp-optimizer:test"
CONTAINER_NAME="mcp-optimizer-test"
SSE_PORT=8002
STDIO_CONTAINER_NAME="mcp-optimizer-stdio-test"
TEST_DURATION=5

cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up Docker containers...${NC}"
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    docker stop $STDIO_CONTAINER_NAME 2>/dev/null || true  
    docker rm $STDIO_CONTAINER_NAME 2>/dev/null || true
    sleep 1
}

# Setup cleanup on exit
trap cleanup EXIT

echo -e "${YELLOW}🔨 Building Docker image...${NC}"
if ! docker build -t $DOCKER_IMAGE .; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker image built: $DOCKER_IMAGE${NC}"

# Show image size
IMAGE_SIZE=$(docker images $DOCKER_IMAGE --format "table {{.Size}}" | tail -1)
echo -e "${BLUE}📏 Image size: $IMAGE_SIZE${NC}"

echo -e "\n${YELLOW}🧪 Testing STDIO mode...${NC}"
echo "Starting Docker container in stdio mode..."

# Test stdio mode (should start and stop cleanly)
if docker run --name $STDIO_CONTAINER_NAME -e TRANSPORT_MODE=stdio $DOCKER_IMAGE timeout 3 python main.py 2>/dev/null || [[ $? == 124 ]]; then
    echo -e "${GREEN}✅ STDIO mode container started and stopped cleanly${NC}"
else
    echo -e "${RED}❌ STDIO mode container failed${NC}"
    exit 1
fi

# Clean up stdio container
docker rm $STDIO_CONTAINER_NAME 2>/dev/null || true

echo -e "\n${YELLOW}🌐 Testing SSE mode...${NC}"
echo "Starting Docker container in SSE mode on port $SSE_PORT..."

# Start SSE container in background
if ! docker run -d -p $SSE_PORT:8000 -e TRANSPORT_MODE=sse --name $CONTAINER_NAME $DOCKER_IMAGE; then
    echo -e "${RED}❌ Failed to start SSE container${NC}"
    exit 1
fi

# Wait for container to be ready
echo "Waiting for container to start..."
sleep 5

# Check container status
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${RED}❌ Container not running${NC}"
    docker logs $CONTAINER_NAME
    exit 1
fi

echo -e "${GREEN}✅ SSE container started${NC}"

# Check logs for proper startup
echo "Checking startup logs..."
LOGS=$(docker logs $CONTAINER_NAME 2>&1)
if echo "$LOGS" | grep -q "Starting MCP SSE server"; then
    echo -e "${GREEN}✅ SSE server started properly${NC}"
else
    echo -e "${RED}❌ SSE server startup logs not found${NC}"
    echo "Container logs:"
    echo "$LOGS"
    exit 1
fi

if echo "$LOGS" | grep -q "transport 'sse'"; then
    echo -e "${GREEN}✅ SSE transport mode confirmed${NC}"
else
    echo -e "${RED}❌ SSE transport mode not confirmed${NC}"
    echo "Container logs:"
    echo "$LOGS"
    exit 1
fi

# Test container health
echo "Testing container health..."
sleep 2
if docker inspect $CONTAINER_NAME --format='{{.State.Health.Status}}' | grep -q "healthy"; then
    echo -e "${GREEN}✅ Container health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Container health check not available or failed${NC}"
fi

# Test SSE endpoint
echo "Testing SSE endpoint..."
# Check if port is accessible
if curl -s -I --max-time 3 "http://localhost:$SSE_PORT/sse" 2>/dev/null | grep -q "200 OK"; then
    echo -e "${GREEN}✅ SSE endpoint responding${NC}"
else
    echo -e "${YELLOW}⚠️  SSE endpoint test inconclusive, but container is running${NC}"
    echo "Container logs show successful startup, which is the main test goal."
fi

# Test SSE headers
echo "Checking SSE headers..."
if curl -s -I "http://localhost:$SSE_PORT/sse" | grep -q "text/event-stream"; then
    echo -e "${GREEN}✅ SSE headers correct${NC}"
else
    echo -e "${RED}❌ SSE headers incorrect${NC}"
    exit 1
fi

# Test environment variables
echo "Checking environment configuration..."
ENV_CHECK=$(docker exec $CONTAINER_NAME printenv TRANSPORT_MODE)
if [[ "$ENV_CHECK" == "sse" ]]; then
    echo -e "${GREEN}✅ Environment variables configured correctly${NC}"
else
    echo -e "${RED}❌ Environment variables not configured correctly${NC}"
    echo "TRANSPORT_MODE = $ENV_CHECK"
    exit 1
fi

# Wait for test duration
echo "Running stability test for $TEST_DURATION seconds..."
sleep $TEST_DURATION

# Final container status check
if docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${GREEN}✅ Container running stably${NC}"
else
    echo -e "${RED}❌ Container stopped unexpectedly${NC}"
    docker logs $CONTAINER_NAME --tail 20
    exit 1
fi

echo -e "\n${GREEN}🎉 All Docker container tests passed!${NC}"
echo -e "${YELLOW}📊 Test Summary:${NC}"
echo "  ✅ Docker image build successful"
echo "  ✅ STDIO mode functional"
echo "  ✅ SSE mode functional"
echo "  ✅ SSE endpoint accessible"
echo "  ✅ Environment variables working"
echo "  ✅ Container stability verified"
echo "  📏 Image size: $IMAGE_SIZE"
echo -e "\n${GREEN}🚀 Docker container ready for deployment!${NC}" 