#!/bin/bash

# MCP Optimizer Build Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="${IMAGE_NAME:-mcp-optimizer}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-ghcr.io}"
REPO_NAME="${REPO_NAME:-mcp-optimizer}"
FULL_IMAGE_NAME="${REGISTRY}/${REPO_NAME}:${IMAGE_TAG}"

echo -e "${GREEN}🏗️  Building MCP Optimizer Docker image...${NC}"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is available${NC}"

# Build the image
echo -e "${YELLOW}🔨 Building image: ${FULL_IMAGE_NAME}${NC}"
docker build \
    --target production \
    --tag "${IMAGE_NAME}:${IMAGE_TAG}" \
    --tag "${FULL_IMAGE_NAME}" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    .

echo -e "${GREEN}✅ Image built successfully!${NC}"

# Show image info
echo -e "${YELLOW}📊 Image information:${NC}"
docker images "${IMAGE_NAME}:${IMAGE_TAG}"

# Test the image
echo -e "${YELLOW}🧪 Testing the image...${NC}"
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" python -c "from mcp_optimizer.mcp_server import create_mcp_server; print('✅ MCP Server can be created')"; then
    echo -e "${GREEN}✅ Image test passed!${NC}"
else
    echo -e "${RED}❌ Image test failed!${NC}"
    exit 1
fi

# Push to registry (if specified)
if [ "${PUSH_IMAGE:-false}" = "true" ]; then
    echo -e "${YELLOW}📤 Pushing image to registry...${NC}"
    docker push "${FULL_IMAGE_NAME}"
    echo -e "${GREEN}✅ Image pushed successfully!${NC}"
fi

echo -e "${GREEN}🎉 Build completed successfully!${NC}"
echo -e "${YELLOW}To run the container locally:${NC}"
echo -e "docker run -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}" 