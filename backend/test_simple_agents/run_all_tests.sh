#!/bin/bash

# ============================================================================
# Master Test Runner - Execute All Simple Agent Tests
# ============================================================================
# Runs all individual agent tests in sequence with proper spacing and logging
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Test tracking
TOTAL_TESTS=5
COMPLETED_TESTS=0
FAILED_TESTS=0

echo "============================================================================"
echo -e "${CYAN}🚀 GOOGLE ADK SIMPLE AGENT TEST SUITE${NC}"
echo "============================================================================"
echo "Running comprehensive tests for 5 different agent types"
echo "Each agent demonstrates multiple tool integration and streaming capabilities"
echo "Time: $(date)"
echo ""

# Function to run individual test
run_test() {
    local test_name="$1"
    local test_script="$2"
    
    echo ""
    echo "============================================================================"
    echo -e "${BLUE}Starting Test: $test_name${NC}"
    echo "============================================================================"
    
    if [ -f "$test_script" ]; then
        chmod +x "$test_script"
        if ./"$test_script"; then
            echo -e "${GREEN}✅ $test_name PASSED${NC}"
            COMPLETED_TESTS=$((COMPLETED_TESTS + 1))
        else
            echo -e "${RED}❌ $test_name FAILED${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        echo -e "${RED}❌ Test script not found: $test_script${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    echo ""
    echo -e "${YELLOW}Waiting 5 seconds before next test...${NC}"
    sleep 5
}

# Check if server is running
echo -e "${BLUE}Checking server status...${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Server is running on localhost:8000${NC}"
else
    echo -e "${RED}❌ Server is not running. Please start the server first.${NC}"
    exit 1
fi

# Run all tests
run_test "Calculation Agent Test" "test_calculation_agent.sh"
run_test "Analysis Agent Test" "test_analysis_agent.sh"
run_test "Research Agent Test" "test_research_agent.sh"
run_test "Finance Agent Test" "test_finance_agent.sh"
run_test "Product Discovery Agent Test" "test_product_agent.sh"

# Final summary
echo ""
echo "============================================================================"
echo -e "${CYAN}🎯 FINAL TEST SUMMARY${NC}"
echo "============================================================================"
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$COMPLETED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}"
    echo "All agent types successfully demonstrated:"
    echo "✅ Mathematical calculations and statistical analysis"
    echo "✅ Text analysis and content evaluation"
    echo "✅ Web research and information synthesis"
    echo "✅ Financial data analysis and investment strategies"
    echo "✅ Product discovery and market intelligence"
    echo ""
    echo -e "${BLUE}Your Google ADK Multi-Agent system is fully functional!${NC}"
else
    echo -e "${RED}⚠️  Some tests failed. Please check the logs above.${NC}"
    exit 1
fi
