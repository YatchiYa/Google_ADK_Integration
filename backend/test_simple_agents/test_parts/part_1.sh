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
      "description": "Expert product researcher specializing in discovering trending products, analyzing market opportunities, and evaluating product-market fit across various industries",
      "personality": "curious, trend-aware, and strategically minded",
      "expertise": ["product discovery", "market analysis", "trend identification", "competitive intelligence", "user experience evaluation", "product strategy"],
      "communication_style": "enthusiastic and insightful, providing actionable product intelligence with market context"
    }, 
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.9,
      "max_output_tokens": 2048
    },
    "tools": ["product_hunt_search", "text_analyzer", "custom_calculator"]
  }')

AGENT_SUCCESS=$(echo "$AGENT_RESPONSE" | jq -r ".success")
if [ "$AGENT_SUCCESS" != "true" ]; then
    echo -e "${RED}❌ Failed to create agent${NC}"
    exit 1
fi

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r ".message" | grep -o 'agent_[a-f0-9]*')
echo -e "${GREEN}✅ Agent created: $AGENT_ID${NC}"
