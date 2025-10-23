#!/bin/bash

# Quick test for Product Hunt and Yahoo Finance tools
BASE_URL="http://localhost:8000"
API_KEY="adk_f41585c7f146484e873ed8216d895871"

echo "========================================="
echo "Quick Tool Test"
echo "========================================="

# Test 1: Create Finance Agent
echo -e "\n1. Creating Finance Agent..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/agents/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "name": "FinanceAgent",
    "persona": {
      "name": "Finance Expert",
      "description": "Financial data specialist",
      "personality": "analytical",
      "expertise": ["finance"],
      "communication_style": "professional",
      "language": "en"
    },
    "tools": ["yahoo_finance_data"]
  }')

echo "$RESPONSE"
FINANCE_AGENT=$(echo "$RESPONSE" | jq -r '.message' | grep -oP 'agent_\w+')
echo "Finance Agent ID: $FINANCE_AGENT"

# Test 2: Create Product Hunt Agent
echo -e "\n2. Creating Product Hunt Agent..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/agents/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "name": "ProductHuntAgent",
    "persona": {
      "name": "Product Hunter",
      "description": "Product discovery specialist",
      "personality": "enthusiastic",
      "expertise": ["products"],
      "communication_style": "friendly",
      "language": "en"
    },
    "tools": ["product_hunt_search"]
  }')

echo "$RESPONSE"
PH_AGENT=$(echo "$RESPONSE" | jq -r '.message' | grep -oP 'agent_\w+')
echo "Product Hunt Agent ID: $PH_AGENT"

# Test 3: Yahoo Finance Query
echo -e "\n3. Testing Yahoo Finance - Bitcoin Price..."
echo "Agent: $FINANCE_AGENT"
echo "Query: Get Bitcoin (BTC-USD) price data"
echo "---"

curl -N -X POST "$BASE_URL/api/v1/streaming/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$FINANCE_AGENT\",
    \"message\": \"Get me the current Bitcoin (BTC-USD) price data for today\",
    \"conversation_id\": \"test-btc-1\",
    \"stream\": true
  }"

echo -e "\n"

# Test 4: Product Hunt Query
echo -e "\n4. Testing Product Hunt - AI Tools Search..."
echo "Agent: $PH_AGENT"
echo "Query: Search for AI tools"
echo "---"

curl -N -X POST "$BASE_URL/api/v1/streaming/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$PH_AGENT\",
    \"message\": \"Search Product Hunt for AI productivity tools\",
    \"conversation_id\": \"test-ph-1\",
    \"stream\": true
  }"

echo -e "\n"

# Test 5: Yahoo Finance - Apple Stock
echo -e "\n5. Testing Yahoo Finance - Apple Stock..."
echo "Agent: $FINANCE_AGENT"
echo "Query: Get Apple stock data"
echo "---"

curl -N -X POST "$BASE_URL/api/v1/streaming/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_id\": \"$FINANCE_AGENT\",
    \"message\": \"Get Apple (AAPL) stock data for the past week\",
    \"conversation_id\": \"test-aapl-1\",
    \"stream\": true
  }"

echo -e "\n"
echo "========================================="
echo "Tests Complete!"
echo "========================================="
echo ""
echo "Check server logs for tool execution details:"
echo "  - Look for 'Fetching Yahoo Finance data for'"
echo "  - Look for 'Product Hunt search for:'"
echo ""
