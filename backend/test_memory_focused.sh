#!/bin/bash

# Focused Memory Test for Google ADK
# Tests if memory persistence works within a session

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧠 Testing Memory System${NC}"
echo "=================================="

# Step 1: Login and get token
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
  -d '{"name": "Memory Test Key", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")

if [ "$API_KEY" = "null" ]; then
    echo -e "${RED}❌ API key creation failed${NC}"
    exit 1
fi

# Step 3: Create Agent with Tools
echo "Step 3: Creating research agent..."
AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Memory Test Agent",
    "persona": {
      "name": "Memory Assistant",
      "description": "An agent that remembers conversation context",
      "personality": "helpful and remembers details",
      "expertise": ["memory", "conversation"],
      "communication_style": "clear and contextual"
    },
    "tools": ["google_search", "custom_calculator"]
  }')

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r ".message" | grep -o 'agent_[a-f0-9]*' | head -1)

if [ "$AGENT_ID" = "" ]; then
    echo -e "${RED}❌ Agent creation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Agent created: $AGENT_ID${NC}"

# Step 4: Start Conversation
echo "Step 4: Starting conversation..."
CONVERSATION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT_ID\",
    \"message\": \"My favorite color is blue and I work as a software engineer.\"
  }")

SESSION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*' | head -1)

if [ "$SESSION_ID" = "" ]; then
    echo -e "${RED}❌ Conversation start failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Conversation started: $SESSION_ID${NC}"

# Step 5: Send first message and get response
echo "Step 5: Sending first message..."
echo "Message: 'My favorite color is blue and I work as a software engineer.'"

FIRST_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "My favorite color is blue and I work as a software engineer."}')

echo "First response received."

# Wait a moment for processing
sleep 2

# Step 6: Send second message that requires memory
echo "Step 6: Testing memory recall..."
echo "Message: 'What is my favorite color and what do I do for work?'"

MEMORY_TEST_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "What is my favorite color and what do I do for work?"}')

echo "Memory test response:"
echo "$MEMORY_TEST_RESPONSE" | grep -o '"content":"[^"]*"' | head -10

# Check if the response contains the remembered information
if echo "$MEMORY_TEST_RESPONSE" | grep -q "blue" && echo "$MEMORY_TEST_RESPONSE" | grep -q "software engineer"; then
    echo -e "${GREEN}✅ MEMORY TEST PASSED: Agent remembered both favorite color and job${NC}"
elif echo "$MEMORY_TEST_RESPONSE" | grep -q "blue"; then
    echo -e "${BLUE}⚠️  PARTIAL SUCCESS: Agent remembered favorite color but not job${NC}"
elif echo "$MEMORY_TEST_RESPONSE" | grep -q "software engineer"; then
    echo -e "${BLUE}⚠️  PARTIAL SUCCESS: Agent remembered job but not favorite color${NC}"
else
    echo -e "${RED}❌ MEMORY TEST FAILED: Agent did not remember the information${NC}"
fi

# Step 7: Test with calculation memory
echo "Step 7: Testing calculation memory..."
echo "Message: 'Calculate 15 * 23 for me'"

CALC_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Calculate 15 * 23 for me"}')

sleep 2

echo "Message: 'What was the result of that calculation?'"

CALC_MEMORY_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "What was the result of that calculation?"}')

echo "Calculation memory response:"
echo "$CALC_MEMORY_RESPONSE" | grep -o '"content":"[^"]*"' | head -5

if echo "$CALC_MEMORY_RESPONSE" | grep -q "345"; then
    echo -e "${GREEN}✅ CALCULATION MEMORY PASSED: Agent remembered the calculation result${NC}"
else
    echo -e "${RED}❌ CALCULATION MEMORY FAILED: Agent did not remember the calculation${NC}"
fi

echo ""
echo -e "${BLUE}🎯 Memory Test Complete${NC}"
echo "=================================="
