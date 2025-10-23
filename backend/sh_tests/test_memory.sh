#!/bin/bash

# ============================================================================
# Google ADK Multi-Agent FastAPI Server - Comprehensive Test Suite
# ============================================================================
# 
# This script tests all 20 endpoints of the Google ADK Multi-Agent API
# Demonstrates full functionality including:
# - Authentication (JWT + API Keys)
# - Agent Management (Simple + Tools + Teams)
# - Memory Management (Create + Search)
# - Streaming Conversations (SSE + WebSocket)
# - Tool Integration and Usage Analytics
# 
# Prerequisites:
# - Server running on localhost:8000
# - curl installed
# - jq installed (for JSON parsing)
# 
# Usage: ./test_all_endpoints.sh
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TEST_COUNT=0
PASSED_COUNT=0
FAILED_COUNT=0

# Function to print test headers
print_test() {
    TEST_COUNT=$((TEST_COUNT + 1))
    echo ""
    echo "============================================================================"
    echo -e "${BLUE}TEST $TEST_COUNT: $1${NC}"
    echo "============================================================================"
}

# Function to check test result
check_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED: $1${NC}"
        PASSED_COUNT=$((PASSED_COUNT + 1))
    else
        echo -e "${RED}❌ FAILED: $1${NC}"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
}

# Function to extract JSON field
extract_json() {
    echo "$1" | jq -r "$2" 2>/dev/null || echo "null"
}

echo "🚀 Starting Google ADK Multi-Agent API Test Suite"
echo "Server: http://localhost:8000"
echo "Time: $(date)"
echo ""

# ============================================================================
# TEST 1: Health Check
# ============================================================================
print_test "Health Check - Verify server is running and all managers are active"

HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "Request: GET /health"
echo "Response: $HEALTH_RESPONSE"

STATUS=$(extract_json "$HEALTH_RESPONSE" ".status")
if [ "$STATUS" = "healthy" ]; then
    check_result "Health Check"
else
    echo "❌ Server not healthy: $STATUS"
    exit 1
fi

# ============================================================================
# TEST 2: Authentication - Login
# ============================================================================
print_test "Authentication - Login with default admin credentials"

LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

echo "Request: POST /auth/login"
echo "Payload: {\"username\": \"admin\", \"password\": \"admin123\"}"
echo "Response: $LOGIN_RESPONSE"

JWT_TOKEN=$(extract_json "$LOGIN_RESPONSE" ".access_token")
USER_ID=$(extract_json "$LOGIN_RESPONSE" ".user_id")

if [ "$JWT_TOKEN" != "null" ] && [ "$JWT_TOKEN" != "" ]; then
    check_result "Authentication Login"
    echo "JWT Token: ${JWT_TOKEN:0:50}..."
    echo "User ID: $USER_ID"
else
    echo "❌ Failed to get JWT token"
    exit 1
fi

# ============================================================================
# TEST 3: Create API Key
# ============================================================================
print_test "Create API Key - Generate API key using JWT token"

API_KEY_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Suite API Key", "permissions": ["*"]}')

echo "Request: POST /auth/api-keys"
echo "Headers: Authorization: Bearer [JWT_TOKEN]"
echo "Payload: {\"name\": \"Test Suite API Key\", \"permissions\": [\"*\"]}"
echo "Response: $API_KEY_RESPONSE"

API_KEY=$(extract_json "$API_KEY_RESPONSE" ".api_key")

if [ "$API_KEY" != "null" ] && [ "$API_KEY" != "" ]; then
    check_result "API Key Creation"
    echo "API Key: $API_KEY"
else
    echo "❌ Failed to create API key"
    exit 1
fi

# ============================================================================
# TEST 4: Create Simple Agent
# ============================================================================
print_test "Create Simple Agent - Basic agent without tools"

SIMPLE_AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple Assistant",
    "persona": {
      "name": "AI Assistant",
      "description": "A helpful AI assistant for general tasks",
      "personality": "friendly and professional",
      "expertise": ["general knowledge", "problem solving"],
      "communication_style": "professional"
    }
  }')

echo "Request: POST /api/v1/agents/"
echo "Headers: X-API-Key: $API_KEY"
echo "Response: $SIMPLE_AGENT_RESPONSE"

SIMPLE_AGENT_SUCCESS=$(extract_json "$SIMPLE_AGENT_RESPONSE" ".success")
SIMPLE_AGENT_MESSAGE=$(extract_json "$SIMPLE_AGENT_RESPONSE" ".message")

if [ "$SIMPLE_AGENT_SUCCESS" = "true" ]; then
    check_result "Simple Agent Creation"
    SIMPLE_AGENT_ID=$(echo "$SIMPLE_AGENT_MESSAGE" | grep -o 'agent_[a-f0-9]*' | head -1)
    echo "Agent ID: $SIMPLE_AGENT_ID"
else
    echo "❌ Failed to create simple agent"
    exit 1
fi

# ============================================================================
# TEST 5: Create Agent with Tools
# ============================================================================
print_test "Create Agent with Tools - Research agent with Google Search and Calculator"

RESEARCH_AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Assistant",
    "persona": {
      "name": "Research Expert",
      "description": "Specialized in research and analysis",
      "personality": "analytical and thorough",
      "expertise": ["research", "data analysis", "web search"],
      "communication_style": "academic"
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.3,
      "max_output_tokens": 2048
    },
    "tools": ["google_search", "custom_calculator", "text_analyzer"]
  }')

echo "Request: POST /api/v1/agents/"
echo "Tools: [\"google_search\", \"custom_calculator\", \"text_analyzer\"]"
echo "Response: $RESEARCH_AGENT_RESPONSE"

RESEARCH_AGENT_SUCCESS=$(extract_json "$RESEARCH_AGENT_RESPONSE" ".success")
RESEARCH_AGENT_MESSAGE=$(extract_json "$RESEARCH_AGENT_RESPONSE" ".message")

if [ "$RESEARCH_AGENT_SUCCESS" = "true" ]; then
    check_result "Research Agent with Tools Creation"
    RESEARCH_AGENT_ID=$(echo "$RESEARCH_AGENT_MESSAGE" | grep -o 'agent_[a-f0-9]*' | head -1)
    echo "Agent ID: $RESEARCH_AGENT_ID"
else
    echo "❌ Failed to create research agent"
    exit 1
fi

# ============================================================================
# TEST 6: List Agents
# ============================================================================
print_test "List Agents - Retrieve all created agents"

AGENTS_LIST_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY")

echo "Request: GET /api/v1/agents/"
echo "Response: ${AGENTS_LIST_RESPONSE:0:200}..."

AGENTS_COUNT=$(extract_json "$AGENTS_LIST_RESPONSE" ".total")

if [ "$AGENTS_COUNT" -ge "2" ]; then
    check_result "List Agents"
    echo "Total Agents: $AGENTS_COUNT"
else
    echo "❌ Expected at least 2 agents, got: $AGENTS_COUNT"
    exit 1
fi

# ============================================================================
# TEST 7: Start Conversation
# ============================================================================
print_test "Start Conversation - Initialize chat session with simple agent"

CONVERSATION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$SIMPLE_AGENT_ID\",
    \"message\": \"Hello! Can you help me with a simple question?\"
  }")

echo "Request: POST /api/v1/conversations/start"
echo "Agent: $SIMPLE_AGENT_ID"
echo "Response: $CONVERSATION_RESPONSE"

CONVERSATION_SUCCESS=$(extract_json "$CONVERSATION_RESPONSE" ".success")
CONVERSATION_MESSAGE=$(extract_json "$CONVERSATION_RESPONSE" ".message")

if [ "$CONVERSATION_SUCCESS" = "true" ]; then
    check_result "Start Conversation"
    SESSION_ID=$(echo "$CONVERSATION_MESSAGE" | grep -o 'session_[a-f0-9]*' | head -1)
    echo "Session ID: $SESSION_ID"
else
    echo "❌ Failed to start conversation"
    exit 1
fi

# ============================================================================
# TEST 8: Streaming Conversation
# ============================================================================
print_test "Streaming Conversation - Send message with real-time streaming response"

echo "Request: POST /api/v1/streaming/send?session_id=$SESSION_ID"
echo "Message: What is 2 + 2?"
echo "Streaming Response:"

STREAMING_OUTPUT=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "What is 2 + 2?"}' \
  --no-buffer | head -10)

echo "$STREAMING_OUTPUT"

if echo "$STREAMING_OUTPUT" | grep -q "data:"; then
    check_result "Streaming Conversation"
    echo "✅ Received streaming events successfully"
else
    echo "❌ No streaming data received"
    exit 1
fi

# ============================================================================
# TEST 9: Agent with Tools Streaming
# ============================================================================
print_test "Agent with Tools Streaming - Test research agent with tool calls"

RESEARCH_CONVERSATION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$RESEARCH_AGENT_ID\",
    \"message\": \"Can you search for information about AI trends?\"
  }")

RESEARCH_SESSION_ID=$(extract_json "$RESEARCH_CONVERSATION_RESPONSE" ".message" | grep -o 'session_[a-f0-9]*' | head -1)

echo "Request: POST /api/v1/streaming/send?session_id=$RESEARCH_SESSION_ID"
echo "Message: Please use your search tools to find the latest AI trends"
echo "Streaming Response (with tool calls):"

RESEARCH_STREAMING_OUTPUT=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$RESEARCH_SESSION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Please use your search tools to find the latest AI trends"}' \
  --no-buffer | head -15)

echo "$RESEARCH_STREAMING_OUTPUT"

if echo "$RESEARCH_STREAMING_OUTPUT" | grep -q "tool_call"; then
    check_result "Agent with Tools Streaming"
    echo "✅ Tool calls detected in streaming response"
else
    check_result "Agent with Tools Streaming (no tool calls detected)"
fi

# ============================================================================

RESEARCH_STREAMING_OUTPUT=$(curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$RESEARCH_SESSION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "What was the last search result?"}' \
  --no-buffer | head -15)

echo "$RESEARCH_STREAMING_OUTPUT"


