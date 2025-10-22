#!/bin/bash

# ============================================================================
# Product Discovery Agent Test - Product Hunt and Market Research Specialist
# ============================================================================
# Tests an agent with multiple product discovery tools:
# - product_hunt_search: Product Hunt API for product discovery
# - text_analyzer: Analysis of product descriptions and reviews
# - custom_calculator: Market metrics and scoring calculations
# - load_memory: Memory operations for product insights
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🚀 Testing Product Discovery Agent with Product Hunt and Analysis Tools"
echo "Server: http://localhost:8000"
echo "Time: $(date)"
echo ""

# ============================================================================
# Step 1: Authentication
# ============================================================================
echo -e "${BLUE}Step 1: Authenticating...${NC}"

LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

JWT_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r ".access_token")
USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r ".user_id")

if [ "$JWT_TOKEN" = "null" ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi

# Create API Key
API_KEY_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Product Agent Test", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")
echo -e "${GREEN}✅ Authentication successful${NC}"

# ============================================================================
# Step 2: Create Product Discovery Agent with Multiple Tools
# ============================================================================
echo -e "${BLUE}Step 2: Creating Product Discovery Agent...${NC}"

AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Hunter Pro",
    "persona": {
      "name": "Innovation Scout",
      "description": "Expert in Giving detailled products like amazon product description",
      "personality": "curious, trend-aware, and strategically minded",
      "expertise": ["product description", "market analysis", "trend identification", "competitive intelligence", "user experience evaluation", "product strategy"],
      "communication_style": "concise and insightful, providing actionable product intelligence with market context"
    }, 
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.9,
      "max_output_tokens": 2048
    },
    "tools": ["text_analyzer", "custom_calculator"]
  }')

AGENT_SUCCESS=$(echo "$AGENT_RESPONSE" | jq -r ".success")
if [ "$AGENT_SUCCESS" != "true" ]; then
    echo -e "${RED}❌ Failed to create agent${NC}"
    exit 1
fi

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r ".message" | grep -o 'agent_[a-f0-9]*')
echo -e "${GREEN}✅ Agent created: $AGENT_ID${NC}"

sleep 10
# ============================================================================
# Step 3: Start Conversation Session
# ============================================================================
echo -e "${BLUE}Step 3: Starting conversation session...${NC}"

CONVERSATION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT_ID\",
    \"message\": \"Hello! I'm ready to discover and analyze products and market opportunities.\",
    \"context\": {
      \"test_type\": \"product_agent\",
      \"session_name\": \"Product Discovery Session\"
    }
  }")

CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*')
echo -e "${GREEN}✅ Conversation started: $CONVERSATION_ID${NC}"


sleep 10

# ============================================================================
# Interaction 1: AI and Productivity Tools Discovery
# ============================================================================
echo ""
echo -e "${YELLOW}🤖 INTERACTION 1: AI and Productivity Tools Discovery${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "I want you to create 5 products description for me about healthy fitness products that i will sell on amazon .",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 15
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 1 completed${NC}"
 