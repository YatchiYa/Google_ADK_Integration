#!/bin/bash

# Final comprehensive test for Product Hunt and Yahoo Finance tools
BASE_URL="http://localhost:8000"
API_KEY="adk_f41585c7f146484e873ed8216d895871"

echo "========================================="
echo "Product Hunt & Yahoo Finance Tool Test"
echo "========================================="

# Create Finance Agent
echo -e "\n[1/6] Creating Finance Agent..."
FINANCE_AGENT=$(curl -s -X POST "$BASE_URL/api/v1/agents/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "name": "FinanceExpert",
    "persona": {
      "name": "Finance Expert",
      "description": "Expert in financial markets and stock analysis. Use yahoo_finance_data tool to get real-time market data.",
      "personality": "analytical and precise",
      "expertise": ["stocks", "cryptocurrency", "market analysis"],
      "communication_style": "professional",
      "language": "en"
    },
    "tools": ["yahoo_finance_data", "custom_calculator"]
  }' | jq -r '.message' | grep -oP 'agent_\w+')

echo "✓ Finance Agent: $FINANCE_AGENT"

# Create Product Hunt Agent
echo -e "\n[2/6] Creating Product Hunt Agent..."
PH_AGENT=$(curl -s -X POST "$BASE_URL/api/v1/agents/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "name": "ProductHunter",
    "persona": {
      "name": "Product Hunter",
      "description": "Expert in discovering and analyzing products on Product Hunt. Use product_hunt_search tool to find products.",
      "personality": "enthusiastic and knowledgeable",
      "expertise": ["product discovery", "tech trends", "startups"],
      "communication_style": "friendly",
      "language": "en"
    },
    "tools": ["product_hunt_search"]
  }' | jq -r '.message' | grep -oP 'agent_\w+')

echo "✓ Product Hunt Agent: $PH_AGENT"

# Test 1: Yahoo Finance - Bitcoin
echo -e "\n[3/6] Testing Yahoo Finance - Bitcoin (BTC-USD)..."
echo "Starting conversation..."

SESSION_ID=$(curl -s -X POST "$BASE_URL/api/v1/streaming/start" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$FINANCE_AGENT\",
    \"user_id\": \"test-user\",
    \"metadata\": {\"test\": \"bitcoin\"}
  }" | jq -r '.session_id')

echo "Session ID: $SESSION_ID"
echo "Sending message and streaming response..."
echo "---"

curl -N -X POST "$BASE_URL/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "message": "Use the yahoo_finance_data tool to get Bitcoin (BTC-USD) price data for today with 1 hour intervals"
  }'

echo -e "\n---"

# Test 2: Yahoo Finance - Apple Stock
echo -e "\n[4/6] Testing Yahoo Finance - Apple Stock (AAPL)..."
echo "Starting conversation..."

SESSION_ID=$(curl -s -X POST "$BASE_URL/api/v1/streaming/start" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$FINANCE_AGENT\",
    \"user_id\": \"test-user\",
    \"metadata\": {\"test\": \"apple\"}
  }" | jq -r '.session_id')

echo "Session ID: $SESSION_ID"
echo "Sending message and streaming response..."
echo "---"

curl -N -X POST "$BASE_URL/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "message": "Get Apple (AAPL) stock data for the past week using yahoo_finance_data tool"
  }'

echo -e "\n---"

# Test 3: Product Hunt - AI Tools
echo -e "\n[5/6] Testing Product Hunt - AI Tools Search..."
echo "Starting conversation..."

SESSION_ID=$(curl -s -X POST "$BASE_URL/api/v1/streaming/start" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$PH_AGENT\",
    \"user_id\": \"test-user\",
    \"metadata\": {\"test\": \"producthunt\"}
  }" | jq -r '.session_id')

echo "Session ID: $SESSION_ID"
echo "Sending message and streaming response..."
echo "---"

curl -N -X POST "$BASE_URL/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "message": "Use product_hunt_search tool to search for AI productivity tools"
  }'

echo -e "\n---"

# Test 4: Yahoo Finance - Gold Futures
echo -e "\n[6/6] Testing Yahoo Finance - Gold Futures (GC=F)..."
echo "Starting conversation..."

SESSION_ID=$(curl -s -X POST "$BASE_URL/api/v1/streaming/start" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$FINANCE_AGENT\",
    \"user_id\": \"test-user\",
    \"metadata\": {\"test\": \"gold\"}
  }" | jq -r '.session_id')

echo "Session ID: $SESSION_ID"
echo "Sending message and streaming response..."
echo "---"

curl -N -X POST "$BASE_URL/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "message": "Get gold futures (GC=F) data for today using the yahoo_finance_data tool"
  }'

echo -e "\n---"

echo -e "\n========================================="
echo "✓ All Tests Complete!"
echo "========================================="
echo ""
echo "Agents Created:"
echo "  - Finance Expert: $FINANCE_AGENT"
echo "  - Product Hunter: $PH_AGENT"
echo ""
echo "Tools Tested:"
echo "  ✓ yahoo_finance_data (BTC-USD, AAPL, GC=F)"
echo "  ✓ product_hunt_search (AI tools)"
echo ""
echo "Check server logs for tool execution:"
echo "  grep 'Fetching Yahoo Finance' logs"
echo "  grep 'Product Hunt' logs"
echo ""
