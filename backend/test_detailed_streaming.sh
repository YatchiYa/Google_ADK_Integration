#!/bin/bash

# Detailed Streaming Test - Shows actual responses
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔍 Detailed Streaming Test${NC}"
echo "================================="

# Authentication
JWT_TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}' | jq -r '.access_token')
API_KEY=$(curl -s -X POST "http://localhost:8000/auth/api-keys" -H "Authorization: Bearer $JWT_TOKEN" -H "Content-Type: application/json" -d '{"name": "Detailed Test", "permissions": ["*"]}' | jq -r '.api_key')

# Create agent
AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" -d '{
  "name": "Detailed Test Agent",
  "persona": {
    "name": "Memory Expert",
    "description": "Expert in shared memory operations",
    "personality": "precise and detailed",
    "expertise": ["memory management", "data persistence"],
    "communication_style": "technical and thorough"
  },
  "tools": ["shared_memory", "cross_agent_memory", "session_memory_bridge", "custom_calculator"]
}')

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r '.message' | grep -o 'agent_[a-f0-9]*')
echo -e "${GREEN}✅ Agent created: $AGENT_ID${NC}"

# Start conversation
CONV_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" -d "{
  \"user_id\": \"admin\",
  \"agent_id\": \"$AGENT_ID\",
  \"message\": \"Hello! Please list all the tools you have available and describe what each one does.\"
}")

SESSION_ID=$(echo "$CONV_RESPONSE" | jq -r '.message' | grep -o 'session_[a-f0-9]*')
echo -e "${GREEN}Session created: $SESSION_ID${NC}"

echo -e "\n${YELLOW}=== Testing Tool Availability ===${NC}"
echo "Sending message to check available tools..."

RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "What tools do you have? Please be specific about each tool."}')

echo "Raw streaming response:"
echo "$RESPONSE"

echo -e "\n${YELLOW}=== Testing Shared Memory Creation ===${NC}"
echo "Testing shared memory tool..."

MEMORY_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Please use your shared_memory tool to create a shared memory entry with this information: I am working on a machine learning project called MLOps Pipeline using Python and TensorFlow. Set the scope to user and importance to 0.9"}')

echo "Shared memory creation response:"
echo "$MEMORY_RESPONSE"

# Check if shared memory tool was mentioned
if echo "$MEMORY_RESPONSE" | grep -q "shared_memory\|shared memory\|memory"; then
    echo -e "${GREEN}✅ Shared memory tool is working!${NC}"
else
    echo -e "${RED}❌ Shared memory tool not working${NC}"
fi

echo -e "\n${BLUE}Test Complete${NC}"
