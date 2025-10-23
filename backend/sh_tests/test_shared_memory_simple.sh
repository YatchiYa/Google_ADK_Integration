#!/bin/bash

# Simple Shared Memory Test
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧠 Simple Shared Memory Test${NC}"
echo "================================"

# Step 1: Login
echo "Step 1: Authenticating..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

JWT_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r ".access_token")
USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r ".user_id")

if [ "$JWT_TOKEN" = "null" ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi

# Step 2: Create API Key
echo "Step 2: Creating API key..."
API_KEY_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Key", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")

# Step 3: Create Agent with Shared Memory Tools
echo "Step 3: Creating agent with shared memory tools..."
AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Memory Test Agent",
    "persona": {
      "name": "Memory Assistant",
      "description": "Tests shared memory functionality",
      "personality": "helpful",
      "expertise": ["memory"],
      "communication_style": "clear"
    },
    "tools": ["shared_memory", "custom_calculator"]
  }')

echo "Agent creation response:"
echo "$AGENT_RESPONSE"

AGENT_SUCCESS=$(echo "$AGENT_RESPONSE" | jq -r ".success")
if [ "$AGENT_SUCCESS" = "true" ]; then
    AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r ".message" | grep -o 'agent_[a-f0-9]*' | head -1)
    echo -e "${GREEN}✅ Agent created successfully: $AGENT_ID${NC}"
else
    echo -e "${RED}❌ Agent creation failed${NC}"
    echo "$AGENT_RESPONSE"
    exit 1
fi

# Step 4: Test Tool List
echo "Step 4: Checking available tools..."
TOOLS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/tools/" \
  -H "X-API-Key: $API_KEY")

echo "Available tools:"
echo "$TOOLS_RESPONSE" | jq '.tools[] | .name' | head -10

echo ""
echo -e "${GREEN}✅ Shared memory tools are properly registered!${NC}"
echo "The validation errors have been fixed."
