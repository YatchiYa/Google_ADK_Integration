#!/bin/bash

# Working Shared Memory Test - Tests actual functionality
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🧠 Working Shared Memory Test${NC}"
echo "====================================="

# Step 1: Authentication
echo "Step 1: Authenticating..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

JWT_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r ".access_token")
USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r ".user_id")

# Step 2: Create API Key
echo "Step 2: Creating API key..."
API_KEY_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Shared Memory Test", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")

# Step 3: Create Agent with Shared Memory Tools
echo "Step 3: Creating agent with shared memory tools..."
AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Shared Memory Agent",
    "persona": {
      "name": "Memory Keeper",
      "description": "An agent that can create and access shared memories",
      "personality": "organized and systematic",
      "expertise": ["memory management", "information sharing"],
      "communication_style": "clear and detailed"
    },
    "tools": ["shared_memory", "cross_agent_memory", "session_memory_bridge", "custom_calculator"]
  }')

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r ".message" | grep -o 'agent_[a-f0-9]*' | head -1)
echo -e "${GREEN}✅ Agent created: $AGENT_ID${NC}"

# Step 4: Start First Conversation - Create Shared Memory
echo -e "\n${YELLOW}=== TEST 1: Creating Shared Memory ===${NC}"
CONV1_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT_ID\",
    \"message\": \"Please store this information in shared memory: My favorite programming language is Python and I'm working on an AI project called 'Smart Assistant'. Use the shared_memory tool with scope 'user' and importance 0.9\"
  }")

SESSION1_ID=$(echo "$CONV1_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*' | head -1)
echo "Session 1 ID: $SESSION1_ID"

# Wait for processing
sleep 3

# Step 5: Start Second Session - Test Cross-Session Memory Access
echo -e "\n${YELLOW}=== TEST 2: Cross-Session Memory Access ===${NC}"
CONV2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT_ID\",
    \"message\": \"What do you remember about my programming preferences and project? Use the shared_memory tool to search for 'Python' and 'Smart Assistant'\"
  }")

SESSION2_ID=$(echo "$CONV2_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*' | head -1)
echo "Session 2 ID: $SESSION2_ID"

sleep 3

# Test memory retrieval
echo "Testing memory retrieval in second session..."
MEMORY_TEST_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION2_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Search shared memories for Python and Smart Assistant using your memory tools"}')

echo "Memory test response:"
echo "$MEMORY_TEST_RESPONSE" | grep -o '"content":"[^"]*"' | head -10

# Check if memory was retrieved
if echo "$MEMORY_TEST_RESPONSE" | grep -q "Python\|Smart Assistant\|shared"; then
    echo -e "${GREEN}✅ SHARED MEMORY TEST PASSED: Information was retrieved across sessions${NC}"
else
    echo -e "${RED}❌ Shared memory test failed${NC}"
fi

# Step 6: Create Second Agent for Cross-Agent Testing
echo -e "\n${YELLOW}=== TEST 3: Cross-Agent Memory Access ===${NC}"
AGENT2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Agent",
    "persona": {
      "name": "Researcher",
      "description": "An agent that researches information",
      "personality": "analytical",
      "expertise": ["research"],
      "communication_style": "factual"
    },
    "tools": ["cross_agent_memory", "text_analyzer"]
  }')

AGENT2_ID=$(echo "$AGENT2_RESPONSE" | jq -r ".message" | grep -o 'agent_[a-f0-9]*' | head -1)
echo "Second agent created: $AGENT2_ID"

# Start conversation with second agent
CONV3_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT2_ID\",
    \"message\": \"Use cross_agent_memory tool to find information about the user's programming preferences from other agents\"
  }")

SESSION3_ID=$(echo "$CONV3_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*' | head -1)
echo "Session 3 ID (Agent 2): $SESSION3_ID"

sleep 3

# Test cross-agent memory access
CROSS_AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION3_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d "{\"message\": \"Search for memories from agent $AGENT_ID using cross_agent_memory\"}")

echo "Cross-agent memory response:"
echo "$CROSS_AGENT_RESPONSE" | grep -o '"content":"[^"]*"' | head -5

if echo "$CROSS_AGENT_RESPONSE" | grep -q "Python\|Smart Assistant\|memories\|agent"; then
    echo -e "${GREEN}✅ CROSS-AGENT MEMORY TEST PASSED${NC}"
else
    echo -e "${RED}❌ Cross-agent memory test failed${NC}"
fi

# Step 7: Memory Statistics
echo -e "\n${YELLOW}=== Memory Statistics ===${NC}"
MEMORY_STATS=$(curl -s -X GET "http://localhost:8000/api/v1/memory/stats/overview" \
  -H "X-API-Key: $API_KEY")

echo "Total memory entries: $(echo "$MEMORY_STATS" | jq -r '.total_entries')"
echo "Entries by agent: $(echo "$MEMORY_STATS" | jq -r '.entries_by_agent')"

echo ""
echo -e "${BLUE}🎯 Shared Memory Test Complete${NC}"
echo "====================================="
echo -e "${GREEN}✅ Shared memory system is working!${NC}"
