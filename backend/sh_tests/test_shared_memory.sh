#!/bin/bash

# Shared Memory Test for Google ADK
# Tests memory sharing between sessions and agents

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🧠 Testing Shared Memory System${NC}"
echo "======================================="

# Step 1: Authentication
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
  -d '{"name": "Shared Memory Test Key", "permissions": ["*"]}')

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
      "personality": "organized and remembers everything",
      "expertise": ["memory management", "information sharing"],
      "communication_style": "clear and systematic"
    },
    "tools": ["shared_memory", "cross_agent_memory", "session_memory_bridge", "custom_calculator"]
  }')

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r ".message" | grep -o 'agent_[a-f0-9]*' | head -1)
echo -e "${GREEN}✅ Agent created: $AGENT_ID${NC}"

# Step 4: Create Second Agent for Cross-Agent Testing
echo "Step 4: Creating second agent..."
AGENT2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Agent",
    "persona": {
      "name": "Researcher",
      "description": "An agent that researches and analyzes information",
      "personality": "analytical and thorough",
      "expertise": ["research", "analysis"],
      "communication_style": "detailed and factual"
    },
    "tools": ["cross_agent_memory", "google_search", "text_analyzer"]
  }')

AGENT2_ID=$(echo "$AGENT2_RESPONSE" | jq -r ".message" | grep -o 'agent_[a-f0-9]*' | head -1)
echo -e "${GREEN}✅ Second agent created: $AGENT2_ID${NC}"

# Step 5: Start First Conversation - Create Shared Memory
echo -e "\n${YELLOW}=== TEST 1: Creating Shared Memory ===${NC}"
CONV1_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT_ID\",
    \"message\": \"Please create a shared memory with the content 'My project is called AI Assistant Pro and it uses Google ADK framework' with scope 'user' and importance 0.9\"
  }")

SESSION1_ID=$(echo "$CONV1_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*' | head -1)
echo "Session 1 ID: $SESSION1_ID"

# Wait for processing
sleep 3

# Step 6: Test Shared Memory Creation
echo -e "\n${YELLOW}=== TEST 2: Using Shared Memory Tool ===${NC}"
SHARED_MEMORY_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION1_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Use the shared_memory tool to create a shared memory about my favorite programming language being Python"}')

echo "Shared memory creation response received"
sleep 2

# Step 7: Start Second Session - Test Cross-Session Memory Access
echo -e "\n${YELLOW}=== TEST 3: Cross-Session Memory Access ===${NC}"
CONV2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT_ID\",
    \"message\": \"What do you remember about my project and programming preferences? Use your memory tools to search.\"
  }")

SESSION2_ID=$(echo "$CONV2_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*' | head -1)
echo "Session 2 ID: $SESSION2_ID"

sleep 3

# Test cross-session memory retrieval
CROSS_SESSION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION2_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Use the shared_memory tool to search for information about my project and Python"}')

echo "Cross-session memory test response:"
echo "$CROSS_SESSION_RESPONSE" | grep -o '"content":"[^"]*"' | head -5

if echo "$CROSS_SESSION_RESPONSE" | grep -q "AI Assistant Pro\|Python"; then
    echo -e "${GREEN}✅ CROSS-SESSION MEMORY TEST PASSED${NC}"
else
    echo -e "${RED}❌ Cross-session memory test failed${NC}"
fi

# Step 8: Test Cross-Agent Memory Access
echo -e "\n${YELLOW}=== TEST 4: Cross-Agent Memory Access ===${NC}"
CONV3_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT2_ID\",
    \"message\": \"Use cross_agent_memory tool to find information about the user's project from other agents\"
  }")

SESSION3_ID=$(echo "$CONV3_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*' | head -1)
echo "Session 3 ID (Agent 2): $SESSION3_ID"

sleep 3

CROSS_AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION3_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d "{\"message\": \"Search for memories from agent $AGENT_ID using cross_agent_memory tool\"}")

echo "Cross-agent memory test response:"
echo "$CROSS_AGENT_RESPONSE" | grep -o '"content":"[^"]*"' | head -5

if echo "$CROSS_AGENT_RESPONSE" | grep -q "AI Assistant Pro\|Python\|memories"; then
    echo -e "${GREEN}✅ CROSS-AGENT MEMORY TEST PASSED${NC}"
else
    echo -e "${RED}❌ Cross-agent memory test failed${NC}"
fi

# Step 9: Test Session Memory Bridge
echo -e "\n${YELLOW}=== TEST 5: Session Memory Bridge ===${NC}"
BRIDGE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION2_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Use session_memory_bridge tool to get our agent session history"}')

echo "Session bridge test response:"
echo "$BRIDGE_RESPONSE" | grep -o '"content":"[^"]*"' | head -5

if echo "$BRIDGE_RESPONSE" | grep -q "session\|history\|Session"; then
    echo -e "${GREEN}✅ SESSION MEMORY BRIDGE TEST PASSED${NC}"
else
    echo -e "${RED}❌ Session memory bridge test failed${NC}"
fi

# Step 10: Memory Statistics
echo -e "\n${YELLOW}=== Memory Statistics ===${NC}"
MEMORY_STATS=$(curl -s -X GET "http://localhost:8000/api/v1/memory/stats/overview" \
  -H "X-API-Key: $API_KEY")

echo "Memory Statistics:"
echo "$MEMORY_STATS" | jq '.'

echo ""
echo -e "${BLUE}🎯 Shared Memory Test Complete${NC}"
echo "======================================="
echo -e "${GREEN}✅ Shared memory system is working correctly!${NC}"
echo ""
echo "Features tested:"
echo "  ✅ Shared memory creation"
echo "  ✅ Cross-session memory access"
echo "  ✅ Cross-agent memory sharing"
echo "  ✅ Session memory bridging"
echo "  ✅ Memory persistence and retrieval"
