#!/bin/bash

# MCP Optimizer Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="mcp-optimizer"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-ghcr.io}"
REPO_NAME="${REPO_NAME:-mcp-optimizer}"

echo -e "${GREEN}🚀 Starting MCP Optimizer deployment...${NC}"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl is not installed or not in PATH${NC}"
    exit 1
fi

# Check if we can connect to cluster
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Kubernetes cluster connection verified${NC}"

# Create namespace if it doesn't exist
echo -e "${YELLOW}📦 Creating namespace...${NC}"
kubectl apply -f k8s/namespace.yaml

# Apply ConfigMap
echo -e "${YELLOW}⚙️  Applying configuration...${NC}"
kubectl apply -f k8s/configmap.yaml

# Apply Deployment
echo -e "${YELLOW}🏗️  Deploying application...${NC}"
envsubst < k8s/deployment.yaml | kubectl apply -f -

# Apply Service
echo -e "${YELLOW}🌐 Creating service...${NC}"
kubectl apply -f k8s/service.yaml

# Apply HPA
echo -e "${YELLOW}📈 Setting up autoscaling...${NC}"
kubectl apply -f k8s/hpa.yaml

# Apply Ingress (optional)
if [ -f "k8s/ingress.yaml" ]; then
    echo -e "${YELLOW}🌍 Setting up ingress...${NC}"
    kubectl apply -f k8s/ingress.yaml
fi

# Wait for deployment to be ready
echo -e "${YELLOW}⏳ Waiting for deployment to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/mcp-optimizer -n $NAMESPACE

# Get deployment status
echo -e "${GREEN}📊 Deployment status:${NC}"
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

echo -e "${GREEN}✅ MCP Optimizer deployed successfully!${NC}"

# Show logs
echo -e "${YELLOW}📝 Recent logs:${NC}"
kubectl logs -n $NAMESPACE deployment/mcp-optimizer --tail=20 