#!/bin/bash

# Comprehensive Test Suite for MCP Optimizer
# Author: MCP Optimizer Team
# Usage: ./scripts/test_all.sh [--skip-docker] [--skip-package]

# Note: We don't use 'set -e' here because we want to continue running tests even if one fails

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Parse command line arguments
SKIP_DOCKER=false
SKIP_PACKAGE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --skip-package)
            SKIP_PACKAGE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--skip-docker] [--skip-package]"
            echo "  --skip-docker   Skip Docker container tests"
            echo "  --skip-package  Skip local package tests"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${PURPLE}🧪 MCP Optimizer Comprehensive Test Suite${NC}"
echo -e "${BLUE}=======================================${NC}"
echo "Working directory: $(pwd)"
echo "Started at: $(date)"

START_TIME=$(date +%s)

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TEST_RESULTS=()

run_test() {
    local test_name="$1"
    local test_script="$2"
    
    echo -e "\n${YELLOW}🔧 Running: $test_name${NC}"
    echo "----------------------------------------"
    
    if [[ -x "$test_script" ]]; then
        if "$test_script"; then
            echo -e "${GREEN}✅ $test_name: PASSED${NC}"
            TEST_RESULTS+=("✅ $test_name: PASSED")
            ((TESTS_PASSED++))
        else
            echo -e "${RED}❌ $test_name: FAILED${NC}"
            TEST_RESULTS+=("❌ $test_name: FAILED")
            ((TESTS_FAILED++))
        fi
    else
        echo -e "${RED}❌ $test_name: Script not found or not executable${NC}"
        TEST_RESULTS+=("❌ $test_name: Script not found")
        ((TESTS_FAILED++))
    fi
}

# Make scripts executable
chmod +x "$SCRIPT_DIR"/test_*.sh 2>/dev/null || true

# Run tests based on flags
if [[ "$SKIP_PACKAGE" != "true" ]]; then
    run_test "Local Package Tests" "$SCRIPT_DIR/test_local_package.sh"
fi

if [[ "$SKIP_DOCKER" != "true" ]]; then
    run_test "Docker Container Tests" "$SCRIPT_DIR/test_docker_container.sh"
fi

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Print final results
echo -e "\n${PURPLE}📊 Test Suite Results${NC}"
echo -e "${BLUE}=====================${NC}"
echo "Completed at: $(date)"
echo "Duration: ${DURATION}s"
echo ""

for result in "${TEST_RESULTS[@]}"; do
    echo "  $result"
done

echo ""
echo -e "${YELLOW}Summary:${NC}"
echo "  Tests passed: $TESTS_PASSED"
echo "  Tests failed: $TESTS_FAILED"
echo "  Total tests:  $((TESTS_PASSED + TESTS_FAILED))"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "\n${GREEN}🎉 All tests passed! MCP Optimizer is ready for deployment.${NC}"
    exit 0
else
    echo -e "\n${RED}💥 Some tests failed. Please review the output above.${NC}"
    exit 1
fi 