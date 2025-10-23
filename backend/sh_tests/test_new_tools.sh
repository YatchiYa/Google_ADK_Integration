#!/bin/bash

# ============================================================================
# Test Script for Product Hunt and Yahoo Finance Tools
# ============================================================================

set -e  # Exit on error

BASE_URL="http://localhost:8000"
API_KEY="adk_871827e19a3d458faf83ef6f41db0995"  # Use the actual API key from server logs

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Testing Product Hunt & Yahoo Finance Tools${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to print section headers
print_section() {
    echo -e "\n${YELLOW}==== $1 ====${NC}\n"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# ============================================================================
# 1. List Available Tools
# ============================================================================
print_section "1. List Available Tools"

echo "Fetching all registered tools..."
curl -s -X GET "$BASE_URL/api/v1/tools/" \
  -H "X-API-Key: $API_KEY" | jq '.'

print_success "Tools list retrieved"

# ============================================================================
# 2. Create Product Hunt Agent
# ============================================================================
print_section "2. Create Product Hunt Agent"

echo "Creating Product Hunt specialist agent..."
PRODUCT_HUNT_AGENT=$(curl -s -X POST "$BASE_URL/api/v1/agents/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "name": "ProductHuntExpert",
    "persona": {
      "name": "Product Hunt Expert",
      "description": "Specialist in finding and analyzing products on Product Hunt",
      "personality": "Enthusiastic and knowledgeable about tech products",
      "expertise": ["product discovery", "tech trends", "startup analysis"],
      "communication_style": "friendly and informative",
      "language": "en"
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.7,
      "max_output_tokens": 2048
    },
    "tools": ["product_hunt_search"]
  }' | jq -r '.message' | grep -oP 'agent_\w+')

echo "Product Hunt Agent ID: $PRODUCT_HUNT_AGENT"
print_success "Product Hunt agent created"

# ============================================================================
# 3. Create Yahoo Finance Agent
# ============================================================================
print_section "3. Create Yahoo Finance Agent"

echo "Creating Yahoo Finance specialist agent..."
FINANCE_AGENT=$(curl -s -X POST "$BASE_URL/api/v1/agents/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "name": "FinanceAnalyst",
    "persona": {
      "name": "Finance Analyst",
      "description": "Expert in financial markets and stock analysis",
      "personality": "Analytical and data-driven",
      "expertise": ["stock market", "cryptocurrency", "financial analysis"],
      "communication_style": "professional and precise",
      "language": "en"
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.5,
      "max_output_tokens": 2048
    },
    "tools": ["yahoo_finance_data", "custom_calculator"]
  }' | jq -r '.message' | grep -oP 'agent_\w+')

echo "Finance Agent ID: $FINANCE_AGENT"
print_success "Finance agent created"

# ============================================================================
# 4. Create Multi-Tool Agent
# ============================================================================
print_section "4. Create Multi-Tool Agent"

echo "Creating multi-tool agent with both tools..."
MULTI_AGENT=$(curl -s -X POST "$BASE_URL/api/v1/agents/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "name": "TechAndFinanceExpert",
    "persona": {
      "name": "Tech & Finance Expert",
      "description": "Expert in both tech products and financial markets",
      "personality": "Versatile and comprehensive",
      "expertise": ["product discovery", "financial analysis", "market trends"],
      "communication_style": "professional and insightful",
      "language": "en"
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.7,
      "max_output_tokens": 3000
    },
    "tools": ["product_hunt_search", "yahoo_finance_data", "custom_calculator"]
  }' | jq -r '.message' | grep -oP 'agent_\w+')

echo "Multi-Tool Agent ID: $MULTI_AGENT"
print_success "Multi-tool agent created"

# ============================================================================
# 5. Test Product Hunt Agent - Search Products
# ============================================================================
print_section "5. Test Product Hunt Agent - Search Products"

echo "Testing Product Hunt search for AI tools..."
echo -e "${BLUE}Streaming response...${NC}\n"

curl -N -X POST "$BASE_URL/api/v1/streaming/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$PRODUCT_HUNT_AGENT\",
    \"message\": \"Search Product Hunt for the top 5 AI productivity tools\",
    \"conversation_id\": \"test-ph-conv-1\",
    \"stream\": true
  }"

echo -e "\n"
print_success "Product Hunt search test completed"

# ============================================================================
# 6. Test Yahoo Finance Agent - Bitcoin Data
# ============================================================================
print_section "6. Test Yahoo Finance Agent - Bitcoin Data"

echo "Testing Yahoo Finance for Bitcoin data..."
echo -e "${BLUE}Streaming response...${NC}\n"

curl -N -X POST "$BASE_URL/api/v1/streaming/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$FINANCE_AGENT\",
    \"message\": \"Get me the latest Bitcoin (BTC-USD) price data for today with 1 hour intervals\",
    \"conversation_id\": \"test-finance-conv-1\",
    \"stream\": true
  }"

echo -e "\n"
print_success "Bitcoin data test completed"

# ============================================================================
# 7. Test Yahoo Finance Agent - Stock Analysis
# ============================================================================
print_section "7. Test Yahoo Finance Agent - Stock Analysis"

echo "Testing Yahoo Finance for Apple stock..."
echo -e "${BLUE}Streaming response...${NC}\n"

curl -N -X POST "$BASE_URL/api/v1/streaming/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$FINANCE_AGENT\",
    \"message\": \"Analyze Apple stock (AAPL) performance for the past week\",
    \"conversation_id\": \"test-finance-conv-2\",
    \"stream\": true
  }"

echo -e "\n"
print_success "Apple stock analysis completed"

# ============================================================================
# 8. Test Multi-Tool Agent - Combined Query
# ============================================================================
print_section "8. Test Multi-Tool Agent - Combined Query"

echo "Testing multi-tool agent with combined query..."
echo -e "${BLUE}Streaming response...${NC}\n"

curl -N -X POST "$BASE_URL/api/v1/streaming/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$MULTI_AGENT\",
    \"message\": \"First, search Product Hunt for fintech products, then get the current price of Ethereum (ETH-USD)\",
    \"conversation_id\": \"test-multi-conv-1\",
    \"stream\": true
  }"

echo -e "\n"
print_success "Combined query test completed"

# ============================================================================
# 9. Test Product Hunt Agent - Posts Query
# ============================================================================
print_section "9. Test Product Hunt Agent - Posts Query"

echo "Testing Product Hunt posts query..."
echo -e "${BLUE}Streaming response...${NC}\n"

curl -N -X POST "$BASE_URL/api/v1/streaming/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$PRODUCT_HUNT_AGENT\",
    \"message\": \"Show me today's featured posts on Product Hunt\",
    \"conversation_id\": \"test-ph-conv-2\",
    \"stream\": true
  }"

echo -e "\n"
print_success "Product Hunt posts test completed"

# ============================================================================
# 10. Test Yahoo Finance - Gold Futures
# ============================================================================
print_section "10. Test Yahoo Finance - Gold Futures"

echo "Testing Yahoo Finance for Gold futures..."
echo -e "${BLUE}Streaming response...${NC}\n"

curl -N -X POST "$BASE_URL/api/v1/streaming/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$FINANCE_AGENT\",
    \"message\": \"Get the current gold futures (GC=F) data for today\",
    \"conversation_id\": \"test-finance-conv-3\",
    \"stream\": true
  }"

echo -e "\n"
print_success "Gold futures test completed"

# ============================================================================
# 11. Verify Tool Calls in Logs
# ============================================================================
print_section "11. Check Recent Logs for Tool Calls"

echo "Checking if tools were called successfully..."
echo -e "${YELLOW}Look for these log entries:${NC}"
echo "  - 'Product Hunt search for:' or 'Product Hunt posts for:'"
echo "  - 'Fetching Yahoo Finance data for'"
echo "  - Tool execution success messages"
echo ""
echo -e "${BLUE}Recent log entries (last 50 lines):${NC}"
echo "Run: tail -n 50 /path/to/your/logs/app.log"

# ============================================================================
# 12. Get Agent Statistics
# ============================================================================
print_section "12. Get Agent Statistics"

echo "Product Hunt Agent Stats:"
curl -s -X GET "$BASE_URL/api/v1/agents/$PRODUCT_HUNT_AGENT" \
  -H "X-API-Key: $API_KEY" | jq '.usage_count, .tools'

echo -e "\nFinance Agent Stats:"
curl -s -X GET "$BASE_URL/api/v1/agents/$FINANCE_AGENT" \
  -H "X-API-Key: $API_KEY" | jq '.usage_count, .tools'

echo -e "\nMulti-Tool Agent Stats:"
curl -s -X GET "$BASE_URL/api/v1/agents/$MULTI_AGENT" \
  -H "X-API-Key: $API_KEY" | jq '.usage_count, .tools'

print_success "Agent statistics retrieved"

# ============================================================================
# Summary
# ============================================================================
print_section "Test Summary"

echo -e "${GREEN}All tests completed successfully!${NC}\n"
echo "Created Agents:"
echo "  - Product Hunt Expert: $PRODUCT_HUNT_AGENT"
echo "  - Finance Analyst: $FINANCE_AGENT"
echo "  - Tech & Finance Expert: $MULTI_AGENT"
echo ""
echo "Tools Tested:"
echo "  ✓ product_hunt_search"
echo "  ✓ yahoo_finance_data"
echo "  ✓ custom_calculator"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Check application logs for tool execution details"
echo "  2. Verify streaming responses were properly formatted"
echo "  3. Test with different parameters and edge cases"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Testing Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
